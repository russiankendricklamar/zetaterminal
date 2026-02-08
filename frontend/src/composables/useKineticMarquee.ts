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
 * Detect whether #app is the scroll container (desktop: height:100% overflow:auto)
 * or if scroll goes through window (mobile: height:auto).
 */
export function getScrollContainer(): HTMLElement | Window {
  const app = document.getElementById('app')
  if (!app) return window

  const style = getComputedStyle(app)
  const isScroller =
    style.height !== 'auto' &&
    app.scrollHeight > app.clientHeight &&
    (style.overflowY === 'auto' || style.overflowY === 'scroll')

  return isScroller ? app : window
}

function getScrollTop(target: HTMLElement | Window): number {
  if (target instanceof Window) return window.scrollY
  return target.scrollTop
}

/**
 * Scroll-driven marquee: letters move only when scrolling.
 * Also applies scaleY "stretch" effect proportional to scroll velocity.
 * When scroll stops, everything freezes and scaleY returns to 1.
 *
 * Automatically detects scroll container: #app on desktop, window on mobile.
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
  let scrollTarget: HTMLElement | Window | null = null
  let bgLayerEl: HTMLElement | null = null
  let idleTimer: ReturnType<typeof setTimeout> | null = null
  let stretchTween: gsap.core.Tween | null = null

  function initTracks(tracks: MarqueeTrack[], _container: HTMLElement, bgLayer: HTMLElement) {
    destroy()

    scrollTarget = getScrollContainer()
    bgLayerEl = bgLayer
    lastScrollTop = getScrollTop(scrollTarget)

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

    scrollTarget.addEventListener('scroll', onScroll, { passive: true })
  }

  function onScroll() {
    if (!scrollTarget || !bgLayerEl) return

    const currentScrollTop = getScrollTop(scrollTarget)
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
    if (scrollTarget) {
      scrollTarget.removeEventListener('scroll', onScroll)
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

    scrollTarget = null
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
