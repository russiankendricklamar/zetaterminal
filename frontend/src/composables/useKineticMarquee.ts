import { onUnmounted } from 'vue'
import { gsap } from 'gsap'

export interface MarqueeTrack {
  el: HTMLElement
  direction: 1 | -1
}

const SPEED_FACTOR = 0.6
const MAX_STRETCH = 1.3
const STRETCH_FACTOR = 0.004
const STRETCH_DECAY_DURATION = 0.4

/**
 * Scroll-driven marquee: letters move only when scrolling.
 * Also applies scaleY "stretch" effect proportional to scroll velocity.
 * When scroll stops, everything freezes and scaleY returns to 1.
 */
export function useKineticMarquee() {
  const trackData: Array<{
    el: HTMLElement
    inner: HTMLElement
    direction: 1 | -1
    offset: number
    contentWidth: number
  }> = []

  let lastScrollTop = 0
  let scrollContainer: HTMLElement | null = null
  let bgLayerEl: HTMLElement | null = null
  let idleTimer: ReturnType<typeof setTimeout> | null = null
  let stretchTween: gsap.core.Tween | null = null

  function initTracks(tracks: MarqueeTrack[], container: HTMLElement, bgLayer: HTMLElement) {
    destroy()

    scrollContainer = container
    bgLayerEl = bgLayer
    lastScrollTop = container.scrollTop

    tracks.forEach((track) => {
      const inner = track.el.querySelector('.marquee-inner') as HTMLElement
      if (!inner) return

      const contentWidth = inner.scrollWidth / 2
      if (contentWidth <= 0) return

      trackData.push({
        el: track.el,
        inner,
        direction: track.direction,
        offset: 0,
        contentWidth,
      })
    })

    container.addEventListener('scroll', onScroll, { passive: true })
  }

  function onScroll() {
    if (!scrollContainer || !bgLayerEl) return

    const currentScrollTop = scrollContainer.scrollTop
    const delta = currentScrollTop - lastScrollTop
    lastScrollTop = currentScrollTop

    const absDelta = Math.abs(delta)

    // Move letters proportionally to scroll delta
    trackData.forEach((td) => {
      td.offset += delta * td.direction * SPEED_FACTOR
      // Wrap for seamless loop
      td.offset = ((td.offset % td.contentWidth) + td.contentWidth) % td.contentWidth
      td.inner.style.transform = `translateX(${-td.offset}px)`
    })

    // Stretch letters vertically based on velocity
    const stretch = 1 + Math.min(absDelta * STRETCH_FACTOR, MAX_STRETCH - 1)

    // Kill any ongoing decay animation
    if (stretchTween) {
      stretchTween.kill()
      stretchTween = null
    }

    bgLayerEl.style.setProperty('--stretch', String(stretch))

    // Schedule stretch decay when scroll stops
    if (idleTimer) clearTimeout(idleTimer)
    idleTimer = setTimeout(decayStretch, 80)
  }

  function decayStretch() {
    if (!bgLayerEl) return

    const currentStretch = parseFloat(bgLayerEl.style.getPropertyValue('--stretch') || '1')
    if (currentStretch <= 1.001) return

    stretchTween = gsap.to(bgLayerEl, {
      '--stretch': 1,
      duration: STRETCH_DECAY_DURATION,
      ease: 'power2.out',
      overwrite: true,
    })
  }

  function destroy() {
    if (scrollContainer) {
      scrollContainer.removeEventListener('scroll', onScroll)
    }
    if (idleTimer) clearTimeout(idleTimer)
    if (stretchTween) stretchTween.kill()

    trackData.forEach((td) => {
      td.inner.style.transform = ''
    })
    trackData.length = 0

    if (bgLayerEl) {
      bgLayerEl.style.removeProperty('--stretch')
    }

    scrollContainer = null
    bgLayerEl = null
  }

  onUnmounted(() => {
    destroy()
  })

  return {
    initTracks,
    destroy,
  }
}
