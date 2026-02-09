<template>
  <div class="relative h-screen w-screen overflow-hidden bg-[var(--bg-primary)] text-white font-sans">
    <div class="relative z-10 flex flex-col h-full p-4 gap-4">
      <!-- Header -->
      <header class="h-12 bg-[var(--bg-secondary)] border border-[var(--border-dark)] flex items-center justify-between px-4 flex-shrink-0">
        <div class="flex items-center gap-4">
          <router-link to="/terminal" class="flex items-center gap-2 text-white cursor-pointer flex-shrink-0">
            <div class="w-8 h-8 bg-[var(--accent-red)] flex items-center justify-center">
              <span class="text-white font-bold text-sm">ζ</span>
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
        <div class="p-8 max-w-4xl mx-auto w-full space-y-8">
          <!-- Profile Header -->
          <div class="flex flex-col md:flex-row items-center md:items-start gap-6 pb-8 border-b border-[var(--border-dark)]">
            <div class="relative group">
              <div class="w-32 h-32 bg-[var(--bg-tertiary)] border-2 border-[var(--border-dark)] flex items-center justify-center text-[var(--accent-red)] font-bold text-2xl font-anton relative overflow-hidden">
                <span v-if="!profile.avatar">{{ profile.name.substring(0, 2).toUpperCase() }}</span>
                <img v-else :src="profile.avatar" alt="Avatar" class="w-full h-full object-cover" />
              </div>
              <button @click="triggerAvatarUpload" class="absolute bottom-0 right-0 w-10 h-10 bg-[var(--accent-red)] hover:bg-red-700 flex items-center justify-center transition-colors border border-[var(--border-dark)]">
                <CameraIcon class="w-5 h-5 text-white" />
              </button>
              <input ref="avatarInput" type="file" accept="image/*" @change="handleAvatarChange" class="hidden" />
            </div>
            <div class="flex-1 text-center md:text-left">
              <h2 class="text-2xl font-anton text-white mb-2 uppercase tracking-wider">{{ profile.name }}</h2>
              <div class="flex flex-wrap items-center justify-center md:justify-start gap-2 mb-4">
                <span class="text-xs text-[var(--accent-red)] font-mono bg-[var(--accent-red)]/10 px-2 py-1 border border-[var(--accent-red)]/30">{{ profile.accountType }}</span>
                <span class="text-xs text-[var(--text-muted)]">•</span>
                <span class="text-xs text-[var(--text-muted)] font-mono">ID: {{ profile.userId }}</span>
              </div>
              <p class="text-sm text-[var(--text-secondary)]">{{ profile.bio || 'Добавьте описание профиля' }}</p>
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
                  v-model="profile.name"
                  type="text"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors font-mono"
                  placeholder="Введите имя"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Email</label>
                <input
                  v-model="profile.email"
                  type="email"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors font-mono"
                  placeholder="email@example.com"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Телефон</label>
                <input
                  v-model="profile.phone"
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
                  v-model="profile.bio"
                  rows="3"
                  class="w-full bg-[var(--bg-tertiary)] border border-[var(--border-dark)] py-2.5 px-4 text-sm text-white focus:border-[var(--accent-red)] outline-none transition-colors resize-none font-mono"
                  placeholder="Краткое описание о себе..."
                ></textarea>
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--text-muted)] uppercase mb-2 font-mono">Часовой пояс</label>
                <select
                  v-model="profile.timezone"
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
                  v-model="profile.language"
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
                  v-model="profile.currency"
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
                    <input type="checkbox" v-model="profile.notifications.email" class="w-4 h-4 border border-[var(--border-dark)] bg-[var(--bg-tertiary)] accent-[var(--accent-red)]" />
                    <span class="group-hover:text-white transition-colors">Email уведомления</span>
                  </label>
                  <label class="flex items-center gap-3 text-sm text-[var(--text-secondary)] cursor-pointer group">
                    <input type="checkbox" v-model="profile.notifications.push" class="w-4 h-4 border border-[var(--border-dark)] bg-[var(--bg-tertiary)] accent-[var(--accent-red)]" />
                    <span class="group-hover:text-white transition-colors">Push уведомления</span>
                  </label>
                  <label class="flex items-center gap-3 text-sm text-[var(--text-secondary)] cursor-pointer group">
                    <input type="checkbox" v-model="profile.notifications.sms" class="w-4 h-4 border border-[var(--border-dark)] bg-[var(--bg-tertiary)] accent-[var(--accent-red)]" />
                    <span class="group-hover:text-white transition-colors">SMS уведомления</span>
                  </label>
                </div>
              </div>
            </div>
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
              class="px-6 py-2.5 bg-[var(--accent-red)] hover:bg-red-700 text-white text-sm font-bold transition-colors border border-[var(--accent-red)] flex items-center gap-2 font-oswald uppercase tracking-wider"
            >
              <SaveIcon class="w-4 h-4" />
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { defineComponent, h } from 'vue';

const router = useRouter();
const avatarInput = ref<HTMLInputElement | null>(null);

const profile = ref({
  name: 'Алексей Трейдер',
  email: 'alex.trader@example.com',
  phone: '+7 (999) 123-45-67',
  bio: 'Профессиональный трейдер с опытом работы на финансовых рынках',
  avatar: null as string | null,
  accountType: 'Pro Аккаунт',
  userId: 'AT-2024-001',
  timezone: 'UTC+03:00',
  language: 'ru',
  currency: 'RUB',
  notifications: {
    email: true,
    push: true,
    sms: false
  }
});

const triggerAvatarUpload = () => {
  avatarInput.value?.click();
};

const handleAvatarChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = (e) => {
      profile.value.avatar = e.target?.result as string;
    };
    reader.readAsDataURL(input.files[0]);
  }
};

const saveProfile = () => {
  // Здесь должна быть логика сохранения профиля
  alert('Профиль успешно сохранён!');
};

// Icon components
const CameraIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z' }),
    h('circle', { cx: '12', cy: '13', r: '4' })
  ])
});

const SaveIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z' }),
    h('polyline', { points: '17 21 17 13 7 13 7 21' }),
    h('polyline', { points: '7 3 7 8 15 8' })
  ])
});
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
