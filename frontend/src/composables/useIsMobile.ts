// src/composables/useIsMobile.ts
import { ref, onMounted, onUnmounted, computed } from 'vue'

export interface MobileBreakpoints {
  isMobile: boolean       // < 768px
  isTablet: boolean       // 768px - 1024px
  isSmallMobile: boolean  // < 480px
  isTinyMobile: boolean   // < 375px
}

export function useIsMobile() {
  const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)

  const isMobile = computed(() => windowWidth.value < 768)
  const isTablet = computed(() => windowWidth.value >= 768 && windowWidth.value < 1024)
  const isSmallMobile = computed(() => windowWidth.value < 480)
  const isTinyMobile = computed(() => windowWidth.value < 375)
  const isDesktop = computed(() => windowWidth.value >= 1024)

  const handleResize = () => {
    windowWidth.value = window.innerWidth
  }

  onMounted(() => {
    window.addEventListener('resize', handleResize, { passive: true })
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })

  return {
    windowWidth,
    isMobile,
    isTablet,
    isSmallMobile,
    isTinyMobile,
    isDesktop
  }
}
