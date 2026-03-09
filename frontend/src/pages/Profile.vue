<template>
  <div class="relative h-screen w-screen overflow-hidden bg-[var(--bg-primary)] text-white font-sans">
    <div class="relative z-10 flex flex-col h-full p-4 gap-4">
      <!-- Header -->
      <header class="h-12 bg-[var(--bg-secondary)] border border-[var(--border-dark)] flex items-center justify-between px-4 flex-shrink-0">
        <div class="flex items-center gap-4">
          <router-link to="/terminal" class="flex items-center gap-2 text-white cursor-pointer flex-shrink-0">
            <div class="w-8 h-8 bg-[var(--accent-red)] flex items-center justify-center">
              <span class="text-white font-bold text-sm">&zeta;</span>
            </div>
            <span class="font-anton tracking-tight text-sm hidden lg:block">ДЗЕТА-ТЕРМИНАЛ</span>
          </router-link>
          <div class="h-4 w-[1px] bg-[var(--border-dark)]"></div>
          <h1 class="text-sm font-bold text-white font-oswald uppercase tracking-wider">Профиль</h1>
        </div>
        <button @click="$router.back()" class="px-4 py-2 text-xs text-[var(--text-muted)] hover:text-white transition-colors border border-[var(--border-dark)] hover:border-[var(--accent-red)] font-mono uppercase">
          Назад
        </button>
      </header>

      <!-- Content -->
      <div class="flex-1 bg-[var(--bg-secondary)] border border-[var(--border-dark)] overflow-hidden flex flex-col overflow-y-auto custom-scrollbar">
        <!-- Loading -->
        <div v-if="loading" class="flex-1 flex items-center justify-center">
          <span class="text-[var(--text-muted)] font-mono text-sm">Загрузка профиля...</span>
        </div>

        <!-- Error -->
        <div v-else-if="loadError" class="flex-1 flex items-center justify-center">
          <div class="text-center space-y-4">
            <p class="text-[var(--accent-red)] font-mono text-sm">{{ loadError }}</p>
            <button @click="loadProfile" class="px-4 py-2 text-xs text-white bg-[var(--accent-red)] hover:bg-red-700 transition-colors font-oswald uppercase">
              Повторить
            </button>
          </div>
        </div>

        <!-- Profile form -->
        <div v-else class="p-8 max-w-4xl mx-auto w-full space-y-8">
          <!-- Profile Header -->
          <div class="flex flex-col md:flex-row items-center md:items-start gap-6 pb-8 border-b border-[var(--border-dark)]">
            <div class="relative group">
              <div class="w-32 h-32 bg-[var(--bg-tertiary)] border-2 border-[var(--border-dark)] flex items-center justify-center text-[var(--accent-red)] font-bold text-2xl font-anton relative overflow-hidden">
                <span v-if="!avatarPreview">{{ initials }}</span>
                <img v-else :src="avatarPreview" alt="Avatar" class="w-full h-full object-cover" />
              </div>
              <button @click="triggerAvatarUpload" class="absolute bottom-0 right-0 w-10 h-10 bg-[var(--accent-red)] hover:bg-red-700 flex items-center justify-center transition-colors border border-[var(--border-dark)]">
                <CameraIcon class="w-5 h-5 text-white" />
              </button>
              <input ref="avatarInput" type="file" accept="image/*" @change="handleAvatarChange" class="hidden" />
            </div>
            <div class="flex-1 text-center md:text-left">
              <h2 class="text-2xl font-anton text-white mb-2 uppercase tracking-wider">{{ form.display_name || form.username }}</h2>
              <div class="flex flex-wrap items-center justify-center md:justify-start gap-2 mb-4">
                <span class="text-xs text-[var(--accent-red)] font-mono bg-[var(--accent-red)]/10 px-2 py-1 border border-[var(--accent-red)]/30">{{ form.role === 'admin' ? 'Admin' : 'User' }}</span>
                <span class="text-xs text-[var(--text-muted)]">&bull;</span>
                <span class="text-xs text-[var(--text-muted)] font-mono">{{ form.domain_handle }}</span>
              </div>
              <p class="text-sm text-[var(--text-secondary)]">{{ form.bio || 'Добавьте описание профиля' }}</p>
            </div>
          </div>

          <!-- Profile Form -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Basic Information -->
            <div class="space-y-4">
              <h3 class="text-lg font-oswald text-white mb-4 uppercase tracking-wider border-l-2 border-[var(--accent-red)] pl-3">Основная информация</h3>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Имя</label>
                <input
                  v-model="form.display_name"
                  type="text"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors font-mono"
                  placeholder="Введите имя"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors font-mono"
                  placeholder="email@example.com"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Телефон</label>
                <input
                  v-model="form.phone"
                  type="tel"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors font-mono"
                  placeholder="+7 (999) 123-45-67"
                />
              </div>
            </div>

            <!-- Additional Information -->
            <div class="space-y-4">
              <h3 class="text-lg font-oswald text-white mb-4 uppercase tracking-wider border-l-2 border-[var(--accent-red)] pl-3">Дополнительно</h3>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Описание</label>
                <textarea
                  v-model="form.bio"
                  rows="3"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors resize-none font-mono"
                  placeholder="Краткое описание о себе..."
                ></textarea>
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Часовой пояс</label>
                <select
                  v-model="prefs.timezone"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors font-mono"
                >
                  <option value="UTC+03:00">UTC+03:00 (Москва)</option>
                  <option value="UTC+00:00">UTC+00:00 (Лондон)</option>
                  <option value="UTC-05:00">UTC-05:00 (Восточное время)</option>
                  <option value="UTC+08:00">UTC+08:00 (Пекин)</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Язык интерфейса</label>
                <select
                  v-model="prefs.language"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors font-mono"
                >
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Preferences -->
          <div class="pt-6 border-t border-[var(--border-dark)]">
            <h3 class="text-lg font-oswald text-white mb-4 uppercase tracking-wider border-l-2 border-[var(--accent-red)] pl-3">Предпочтения</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Валюта по умолчанию</label>
                <select
                  v-model="prefs.currency"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors font-mono"
                >
                  <option value="RUB">RUB - Российский рубль</option>
                  <option value="USD">USD - Доллар США</option>
                  <option value="EUR">EUR - Евро</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Уведомления</label>
                <div class="space-y-2">
                  <label class="flex items-center gap-3 text-sm text-[var(--text-secondary)] cursor-pointer group">
                    <input type="checkbox" v-model="prefs.notifications.email" class="w-4 h-4 border border-[var(--border-dark)] bg-[var(--bg-tertiary)] accent-[var(--accent-red)]" />
                    <span class="group-hover:text-white transition-colors">Email уведомления</span>
                  </label>
                  <label class="flex items-center gap-3 text-sm text-[var(--text-secondary)] cursor-pointer group">
                    <input type="checkbox" v-model="prefs.notifications.push" class="w-4 h-4 border border-[var(--border-dark)] bg-[var(--bg-tertiary)] accent-[var(--accent-red)]" />
                    <span class="group-hover:text-white transition-colors">Push уведомления</span>
                  </label>
                  <label class="flex items-center gap-3 text-sm text-[var(--text-secondary)] cursor-pointer group">
                    <input type="checkbox" v-model="prefs.notifications.sms" class="w-4 h-4 border border-[var(--border-dark)] bg-[var(--bg-tertiary)] accent-[var(--accent-red)]" />
                    <span class="group-hover:text-white transition-colors">SMS уведомления</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Status message -->
          <div v-if="saveMessage" class="text-center">
            <span :class="saveError ? 'text-[var(--accent-red)]' : 'text-green-500'" class="font-mono text-sm">{{ saveMessage }}</span>
          </div>

          <!-- Save Button -->
          <div class="flex justify-end gap-4 pt-6 border-t border-[var(--border-dark)]">
            <button
              @click="$router.back()"
              class="px-6 py-2.5 bg-[var(--bg-tertiary)] hover:bg-[var(--border-dark)] text-[var(--text-secondary)] hover:text-white text-sm font-bold transition-colors border border-[var(--border-dark)] font-oswald uppercase tracking-wider"
            >
              Отмена
            </button>
            <button
              @click="saveProfile"
              :disabled="saving"
              class="px-6 py-2.5 bg-[var(--accent-red)] hover:bg-red-700 text-white text-sm font-bold transition-colors border border-[var(--accent-red)] flex items-center gap-2 font-oswald uppercase tracking-wider disabled:opacity-50"
            >
              <SaveIcon class="w-4 h-4" />
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, defineComponent, h } from 'vue'
import { getAuthUser, getProfile, updateProfile } from '@/services/authService'

const avatarInput = ref<HTMLInputElement | null>(null)
const avatarPreview = ref<string | null>(null)

const loading = ref(true)
const loadError = ref('')
const saving = ref(false)
const saveMessage = ref('')
const saveError = ref(false)

const form = reactive({
  username: '',
  domain_handle: '',
  display_name: '',
  email: '',
  phone: '',
  bio: '',
  role: '',
})

const prefs = reactive({
  timezone: 'UTC+03:00',
  language: 'ru',
  currency: 'RUB',
  notifications: {
    email: true,
    push: true,
    sms: false,
  },
})

const initials = computed(() => {
  const name = form.display_name || form.username || ''
  return name.substring(0, 2).toUpperCase()
})

async function loadProfile() {
  const authUser = getAuthUser()
  if (!authUser) {
    loadError.value = 'Необходимо авторизоваться'
    loading.value = false
    return
  }

  loading.value = true
  loadError.value = ''
  try {
    const data = await getProfile(authUser.username)
    form.username = data.username
    form.domain_handle = data.domain_handle
    form.display_name = data.display_name || ''
    form.email = data.email
    form.phone = data.phone || ''
    form.bio = data.bio || ''
    form.role = data.role

    if (data.preferences) {
      prefs.timezone = data.preferences.timezone || 'UTC+03:00'
      prefs.language = data.preferences.language || 'ru'
      prefs.currency = data.preferences.currency || 'RUB'
      if (data.preferences.notifications) {
        prefs.notifications.email = data.preferences.notifications.email ?? true
        prefs.notifications.push = data.preferences.notifications.push ?? true
        prefs.notifications.sms = data.preferences.notifications.sms ?? false
      }
    }
  } catch (err) {
    loadError.value = err instanceof Error ? err.message : 'Ошибка загрузки профиля'
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  saving.value = true
  saveMessage.value = ''
  saveError.value = false
  try {
    await updateProfile(form.username, {
      display_name: form.display_name || null,
      email: form.email || null,
      phone: form.phone || null,
      bio: form.bio || null,
      preferences: {
        timezone: prefs.timezone,
        language: prefs.language,
        currency: prefs.currency,
        notifications: { ...prefs.notifications },
      },
    })
    saveMessage.value = 'Профиль сохранён'
    saveError.value = false
    setTimeout(() => { saveMessage.value = '' }, 3000)
  } catch (err) {
    saveMessage.value = err instanceof Error ? err.message : 'Ошибка сохранения'
    saveError.value = true
  } finally {
    saving.value = false
  }
}

function triggerAvatarUpload() {
  avatarInput.value?.click()
}

function handleAvatarChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const reader = new FileReader()
    reader.onload = (e) => {
      avatarPreview.value = e.target?.result as string
    }
    reader.readAsDataURL(input.files[0])
  }
}

onMounted(loadProfile)

// Icon components
const CameraIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z' }),
    h('circle', { cx: '12', cy: '13', r: '4' })
  ])
})

const SaveIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z' }),
    h('polyline', { points: '17 21 17 13 7 13 7 21' }),
    h('polyline', { points: '7 3 7 8 15 8' })
  ])
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--border-dark);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

select option {
  background: var(--bg-secondary);
  color: white;
}
</style>
