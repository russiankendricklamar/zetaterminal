import { ref, onMounted } from 'vue'
import { isTauri } from '@/utils/apiBase'

interface UpdateInfo {
  available: boolean
  version: string
  body: string
  downloading: boolean
  progress: number
}

export function useAutoUpdater() {
  const updateInfo = ref<UpdateInfo>({
    available: false,
    version: '',
    body: '',
    downloading: false,
    progress: 0,
  })
  const error = ref<string | null>(null)

  async function checkForUpdates() {
    if (!isTauri()) return

    try {
      const { check } = await import('@tauri-apps/plugin-updater')
      const update = await check()

      if (update) {
        updateInfo.value = {
          ...updateInfo.value,
          available: true,
          version: update.version,
          body: update.body ?? '',
        }
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    }
  }

  async function downloadAndInstall() {
    if (!isTauri() || !updateInfo.value.available) return

    try {
      updateInfo.value = { ...updateInfo.value, downloading: true }

      const { check } = await import('@tauri-apps/plugin-updater')
      const { relaunch } = await import('@tauri-apps/plugin-process')

      const update = await check()
      if (!update) return

      let totalLength = 0
      let downloaded = 0
      await update.downloadAndInstall((event) => {
        if (event.event === 'Started' && event.data.contentLength) {
          totalLength = event.data.contentLength
        } else if (event.event === 'Progress' && totalLength > 0) {
          downloaded += event.data.chunkLength
          updateInfo.value = {
            ...updateInfo.value,
            progress: Math.min(100, Math.round((downloaded / totalLength) * 100)),
          }
        }
      })

      await relaunch()
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
      updateInfo.value = { ...updateInfo.value, downloading: false }
    }
  }

  onMounted(() => {
    checkForUpdates()
  })

  return {
    updateInfo,
    error,
    checkForUpdates,
    downloadAndInstall,
  }
}
