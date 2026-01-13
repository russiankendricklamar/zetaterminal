<template>
  <div class="relative h-screen w-screen overflow-hidden bg-black text-white font-sans">
    <!-- Mesh Gradient Background -->
    <div class="fixed inset-0 z-0 pointer-events-none">
      <div class="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] bg-blue-950/40 blur-[120px] rounded-full mix-blend-screen animate-blob"></div>
      <div class="absolute top-[20%] right-[-10%] w-[40vw] h-[40vw] bg-orange-600/15 blur-[120px] rounded-full mix-blend-screen animate-blob animation-delay-2000"></div>
      <div class="absolute bottom-[-20%] left-[20%] w-[60vw] h-[60vw] bg-slate-900/20 blur-[100px] rounded-full mix-blend-screen animate-blob animation-delay-4000"></div>
      <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150"></div>
    </div>

    <div class="relative z-10 flex flex-col h-full p-4 gap-4">
      <!-- Header -->
      <header class="h-10 glass-panel rounded-xl flex items-center justify-between px-4 flex-shrink-0 transition-all duration-300 z-50">
        <div class="flex items-center gap-4">
          <router-link to="/terminal" class="flex items-center gap-2 text-white cursor-pointer flex-shrink-0">
            <div class="p-1 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-md shadow-lg shadow-blue-500/20 flex items-center justify-center w-6 h-6">
              <span class="text-white font-bold text-sm">ζ</span>
            </div>
            <span class="font-bold tracking-tight text-sm bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 hidden lg:block">Дзета-Терминал</span>
          </router-link>
          <div class="h-4 w-[1px] bg-white/10"></div>
          <h1 class="text-sm font-bold text-white">Профиль</h1>
        </div>
        <button @click="$router.back()" class="px-3 py-1 text-xs text-gray-400 hover:text-white transition-colors">
          Назад
        </button>
      </header>

      <!-- Content -->
      <div class="flex-1 glass-panel rounded-2xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in overflow-y-auto custom-scrollbar">
        <div class="p-8 max-w-4xl mx-auto w-full space-y-8">
          <!-- Profile Header -->
          <div class="flex flex-col md:flex-row items-center md:items-start gap-6 pb-8 border-b border-white/5">
            <div class="relative group">
              <div class="w-32 h-32 rounded-full bg-gradient-to-br from-gray-100 to-gray-400 shadow-inner flex items-center justify-center text-black font-bold text-2xl border-4 border-white/20 relative overflow-hidden">
                <span v-if="!profile.avatar">{{ profile.name.substring(0, 2).toUpperCase() }}</span>
                <img v-else :src="profile.avatar" alt="Avatar" class="w-full h-full object-cover" />
              </div>
              <button @click="triggerAvatarUpload" class="absolute bottom-0 right-0 w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-500 flex items-center justify-center shadow-lg transition-colors border-2 border-black/20">
                <CameraIcon class="w-5 h-5 text-white" />
              </button>
              <input ref="avatarInput" type="file" accept="image/*" @change="handleAvatarChange" class="hidden" />
            </div>
            <div class="flex-1 text-center md:text-left">
              <h2 class="text-2xl font-bold text-white mb-2">{{ profile.name }}</h2>
              <div class="flex flex-wrap items-center justify-center md:justify-start gap-2 mb-4">
                <span class="text-xs text-emerald-400 font-mono bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">{{ profile.accountType }}</span>
                <span class="text-xs text-gray-500">•</span>
                <span class="text-xs text-gray-400">ID: {{ profile.userId }}</span>
              </div>
              <p class="text-sm text-gray-400">{{ profile.bio || 'Добавьте описание профиля' }}</p>
            </div>
          </div>

          <!-- Profile Form -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Basic Information -->
            <div class="space-y-4">
              <h3 class="text-lg font-bold text-white mb-4">Основная информация</h3>
              
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Имя</label>
                <input 
                  v-model="profile.name"
                  type="text"
                  class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 px-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-colors"
                  placeholder="Введите имя"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Email</label>
                <input 
                  v-model="profile.email"
                  type="email"
                  class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 px-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-colors"
                  placeholder="email@example.com"
                />
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Телефон</label>
                <input 
                  v-model="profile.phone"
                  type="tel"
                  class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 px-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-colors"
                  placeholder="+7 (999) 123-45-67"
                />
              </div>
            </div>

            <!-- Additional Information -->
            <div class="space-y-4">
              <h3 class="text-lg font-bold text-white mb-4">Дополнительно</h3>
              
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Описание</label>
                <textarea 
                  v-model="profile.bio"
                  rows="3"
                  class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 px-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-colors resize-none"
                  placeholder="Краткое описание о себе..."
                ></textarea>
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Часовой пояс</label>
                <select 
                  v-model="profile.timezone"
                  class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 px-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-colors"
                >
                  <option value="UTC+03:00">UTC+03:00 (Москва)</option>
                  <option value="UTC+00:00">UTC+00:00 (Лондон)</option>
                  <option value="UTC-05:00">UTC-05:00 (Восточное время)</option>
                  <option value="UTC+08:00">UTC+08:00 (Пекин)</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Язык интерфейса</label>
                <select 
                  v-model="profile.language"
                  class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 px-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-colors"
                >
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Preferences -->
          <div class="pt-6 border-t border-white/5">
            <h3 class="text-lg font-bold text-white mb-4">Предпочтения</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Валюта по умолчанию</label>
                <select 
                  v-model="profile.currency"
                  class="w-full bg-black/20 border border-white/10 rounded-xl py-2.5 px-4 text-sm text-white focus:border-indigo-500/50 outline-none transition-colors"
                >
                  <option value="RUB">RUB - Российский рубль</option>
                  <option value="RUB">RUB - Российский рубль</option>
                  <option value="EUR">EUR - Евро</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Уведомления</label>
                <div class="space-y-2">
                  <label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                    <input type="checkbox" v-model="profile.notifications.email" class="w-4 h-4 rounded border-white/20 bg-black/20 text-indigo-600 focus:ring-indigo-500" />
                    Email уведомления
                  </label>
                  <label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                    <input type="checkbox" v-model="profile.notifications.push" class="w-4 h-4 rounded border-white/20 bg-black/20 text-indigo-600 focus:ring-indigo-500" />
                    Push уведомления
                  </label>
                  <label class="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
                    <input type="checkbox" v-model="profile.notifications.sms" class="w-4 h-4 rounded border-white/20 bg-black/20 text-indigo-600 focus:ring-indigo-500" />
                    SMS уведомления
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Save Button -->
          <div class="flex justify-end gap-4 pt-6 border-t border-white/5">
            <button 
              @click="$router.back()"
              class="px-6 py-2.5 bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white rounded-xl text-sm font-bold transition-colors border border-white/10"
            >
              Отмена
            </button>
            <button 
              @click="saveProfile"
              class="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-bold transition-colors shadow-lg shadow-indigo-500/20 flex items-center gap-2"
            >
              <SaveIcon class="w-4 h-4" />
              Сохранить изменения
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
  console.log('Saving profile:', profile.value);
  // Можно добавить уведомление об успешном сохранении
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
.glass-panel {
  background: rgba(30, 30, 40, 0.4);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

@keyframes blob {
  0%, 100% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
