import { onUnmounted } from 'vue'
import { gsap } from 'gsap'

export interface MarqueeTrack {
  el: HTMLElement
  direction: 1 | -1
}

/**
 * Creates infinite horizontal marquee animations for letter rows.
 * Each track moves continuously; on slide change we can boost/reset speed.
 */
export function useKineticMarquee() {
  const tweens: gsap.core.Tween[] = []

  function initTracks(tracks: MarqueeTrack[]) {
    destroy()

    tracks.forEach((track) => {
      const inner = track.el.querySelector('.marquee-inner') as HTMLElement
      if (!inner) return

      const contentWidth = inner.scrollWidth / 2

      const tween = gsap.to(inner, {
        x: track.direction === 1 ? -contentWidth : contentWidth,
        duration: 18 + Math.random() * 8,
        ease: 'none',
        repeat: -1,
        modifiers: {
          x: gsap.utils.unitize((x: string) => {
            const val = parseFloat(x)
            return ((val % contentWidth) + contentWidth) % contentWidth - (track.direction === 1 ? contentWidth : 0)
          }),
        },
      })

      tweens.push(tween)
    })
  }

  function boostAll(scale: number, duration: number) {
    tweens.forEach((tween) => {
      gsap.to(tween, { timeScale: scale, duration, overwrite: true })
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
  }

  onUnmounted(() => {
    destroy()
  })

  return {
    initTracks,
    boostAll,
    resetSpeed,
    destroy,
  }
}
