import { ref, onMounted, onUnmounted } from 'vue'

export interface UseFullPageSliderOptions {
  totalSlides: number
  onSlideChange: (from: number, to: number, direction: 'up' | 'down') => void
  wheelThreshold?: number
  touchThreshold?: number
  cooldownMs?: number
}

export function useFullPageSlider(options: UseFullPageSliderOptions) {
  const {
    totalSlides,
    onSlideChange,
    wheelThreshold = 80,
    touchThreshold = 50,
    cooldownMs = 1000,
  } = options

  const currentSlide = ref(0)
  const isTransitioning = ref(false)

  let wheelAccumulator = 0
  let wheelResetTimer: ReturnType<typeof setTimeout> | null = null
  let touchStartY = 0

  function goToSlide(index: number) {
    if (isTransitioning.value) return
    if (index < 0 || index >= totalSlides) return
    if (index === currentSlide.value) return

    const direction: 'up' | 'down' = index > currentSlide.value ? 'down' : 'up'
    const from = currentSlide.value

    isTransitioning.value = true
    currentSlide.value = index
    onSlideChange(from, index, direction)

    setTimeout(() => {
      isTransitioning.value = false
    }, cooldownMs)
  }

  function nextSlide() {
    if (currentSlide.value < totalSlides - 1) {
      goToSlide(currentSlide.value + 1)
    }
  }

  function prevSlide() {
    if (currentSlide.value > 0) {
      goToSlide(currentSlide.value - 1)
    }
  }

  function handleWheel(e: WheelEvent) {
    e.preventDefault()
    if (isTransitioning.value) return

    wheelAccumulator += e.deltaY

    if (wheelResetTimer) clearTimeout(wheelResetTimer)
    wheelResetTimer = setTimeout(() => {
      wheelAccumulator = 0
    }, 200)

    if (Math.abs(wheelAccumulator) > wheelThreshold) {
      if (wheelAccumulator > 0) {
        nextSlide()
      } else {
        prevSlide()
      }
      wheelAccumulator = 0
    }
  }

  function handleTouchStart(e: TouchEvent) {
    touchStartY = e.touches[0].clientY
  }

  function handleTouchEnd(e: TouchEvent) {
    if (isTransitioning.value) return
    const delta = touchStartY - e.changedTouches[0].clientY
    if (Math.abs(delta) > touchThreshold) {
      if (delta > 0) {
        nextSlide()
      } else {
        prevSlide()
      }
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (isTransitioning.value) return

    switch (e.key) {
      case 'ArrowDown':
      case 'PageDown':
        e.preventDefault()
        nextSlide()
        break
      case 'ArrowUp':
      case 'PageUp':
        e.preventDefault()
        prevSlide()
        break
      case 'Home':
        e.preventDefault()
        goToSlide(0)
        break
      case 'End':
        e.preventDefault()
        goToSlide(totalSlides - 1)
        break
    }
  }

  onMounted(() => {
    window.addEventListener('wheel', handleWheel, { passive: false })
    window.addEventListener('touchstart', handleTouchStart, { passive: true })
    window.addEventListener('touchend', handleTouchEnd, { passive: true })
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('wheel', handleWheel)
    window.removeEventListener('touchstart', handleTouchStart)
    window.removeEventListener('touchend', handleTouchEnd)
    window.removeEventListener('keydown', handleKeydown)
    if (wheelResetTimer) clearTimeout(wheelResetTimer)
  })

  return {
    currentSlide,
    isTransitioning,
    goToSlide,
    nextSlide,
    prevSlide,
  }
}
