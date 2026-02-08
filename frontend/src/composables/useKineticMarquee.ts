import { ref, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'

export interface MarqueeRow {
  el: HTMLElement
  direction: 1 | -1
  speedMultiplier: number
}

export function useKineticMarquee() {
  const rows = ref<MarqueeRow[]>([])
  const tweens: gsap.core.Tween[] = []
  let lastScrollY = 0
  let lastTime = 0
  let velocity = 0
  let rafId = 0
  let decayId = 0

  function init(rowConfigs: MarqueeRow[]) {
    rows.value = rowConfigs

    rowConfigs.forEach((row) => {
      const track = row.el.querySelector('.marquee-track') as HTMLElement
      if (!track) return

      const trackWidth = track.scrollWidth / 2

      const tween = gsap.to(track, {
        x: row.direction === 1 ? -trackWidth : trackWidth,
        duration: 25 + Math.random() * 10,
        ease: 'none',
        repeat: -1,
        modifiers: {
          x: gsap.utils.unitize((x: number) => {
            const val = parseFloat(x)
            return ((val % trackWidth) + trackWidth) % trackWidth - (row.direction === 1 ? trackWidth : 0)
          }),
        },
      })

      tweens.push(tween)
    })
  }

  function onScroll() {
    const now = performance.now()
    const dt = now - lastTime
    const dy = window.scrollY - lastScrollY

    if (dt > 0) {
      velocity = Math.abs(dy / dt) * 1000
    }

    lastScrollY = window.scrollY
    lastTime = now

    tweens.forEach((tween, i) => {
      const multiplier = rows.value[i]?.speedMultiplier ?? 1
      const boost = 1 + (velocity / 300) * multiplier
      const clamped = Math.min(boost, 8)
      gsap.to(tween, { timeScale: clamped, duration: 0.15, overwrite: true })
    })

    if (decayId) cancelAnimationFrame(decayId)
    scheduleDecay()
  }

  function scheduleDecay() {
    decayId = requestAnimationFrame(() => {
      decayId = requestAnimationFrame(() => {
        tweens.forEach((tween) => {
          gsap.to(tween, { timeScale: 1, duration: 0.8, ease: 'power2.out', overwrite: true })
        })
      })
    })
  }

  function boostAll(targetScale: number, duration: number) {
    tweens.forEach((tween) => {
      gsap.to(tween, { timeScale: targetScale, duration, overwrite: true })
    })
  }

  function resetSpeed(duration: number) {
    tweens.forEach((tween) => {
      gsap.to(tween, { timeScale: 1, duration, ease: 'power2.out', overwrite: true })
    })
  }

  function destroy() {
    tweens.forEach((t) => t.kill())
    tweens.length = 0
    if (rafId) cancelAnimationFrame(rafId)
    if (decayId) cancelAnimationFrame(decayId)
  }

  onMounted(() => {
    lastScrollY = window.scrollY
    lastTime = performance.now()
    window.addEventListener('scroll', onScroll, { passive: true })
  })

  onUnmounted(() => {
    window.removeEventListener('scroll', onScroll)
    destroy()
  })

  return {
    init,
    boostAll,
    resetSpeed,
    destroy,
  }
}
