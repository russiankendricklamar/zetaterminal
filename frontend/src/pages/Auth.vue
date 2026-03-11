<template>
  <div class="auth-root">
    <div class="bg-noise" />

    <!-- Back link -->
    <a
      class="back-link font-mono"
      @click.prevent="$router.push('/')"
    >
      &larr; ZETA TERMINAL
    </a>

    <!-- Main container -->
    <div class="auth-container">
      <div class="auth-header">
        <h1 class="auth-title font-anton">
          ACCESS
        </h1>
        <div class="auth-underline" />
      </div>

      <!-- Tabs -->
      <div class="auth-tabs">
        <button
          class="auth-tab font-oswald"
          :class="{ active: mode === 'login' }"
          @click="switchMode('login')"
        >
          ВХОД
        </button>
        <button
          class="auth-tab font-oswald"
          :class="{ active: mode === 'register' }"
          @click="switchMode('register')"
        >
          РЕГИСТРАЦИЯ
        </button>
      </div>

      <!-- Login form -->
      <form
        v-if="mode === 'login'"
        class="auth-form"
        @submit.prevent="handleLogin"
      >
        <div class="auth-field">
          <label class="auth-label font-mono">USERNAME</label>
          <input
            v-model="loginForm.username"
            type="text"
            class="auth-input font-mono"
            placeholder="username"
            autocomplete="username"
            required
          >
        </div>
        <div class="auth-field">
          <label class="auth-label font-mono">PASSWORD</label>
          <input
            v-model="loginForm.password"
            type="password"
            class="auth-input font-mono"
            placeholder="password"
            autocomplete="current-password"
            required
          >
        </div>
        <button
          type="submit"
          class="auth-submit font-oswald"
          :disabled="loading"
        >
          {{ loading ? statusText : 'ВОЙТИ' }}
        </button>
        <p
          class="auth-switch font-mono"
          @click="switchMode('register')"
        >
          Нет аккаунта? Регистрация &rarr;
        </p>
      </form>

      <!-- Register form -->
      <form
        v-if="mode === 'register'"
        class="auth-form"
        @submit.prevent="handleRegister"
      >
        <div class="auth-field">
          <label class="auth-label font-mono">USERNAME</label>
          <input
            v-model="registerForm.username"
            type="text"
            class="auth-input font-mono"
            placeholder="username"
            autocomplete="username"
            required
          >
          <span
            v-if="registerForm.username"
            class="auth-hint font-mono"
          >
            {{ registerForm.username.toLowerCase() }}@zetaterminal.dev
          </span>
        </div>
        <div class="auth-field">
          <label class="auth-label font-mono">EMAIL</label>
          <input
            v-model="registerForm.email"
            type="email"
            class="auth-input font-mono"
            placeholder="email@example.com"
            autocomplete="email"
            required
          >
        </div>
        <div class="auth-field">
          <label class="auth-label font-mono">PASSWORD</label>
          <input
            v-model="registerForm.password"
            type="password"
            class="auth-input font-mono"
            placeholder="min 6 chars"
            autocomplete="new-password"
            required
          >
        </div>
        <div class="auth-field">
          <label class="auth-label font-mono">CONFIRM PASSWORD</label>
          <input
            v-model="registerForm.confirmPassword"
            type="password"
            class="auth-input font-mono"
            placeholder="repeat password"
            autocomplete="new-password"
            required
          >
        </div>
        <button
          type="submit"
          class="auth-submit font-oswald"
          :disabled="loading"
        >
          {{ loading ? statusText : 'ЗАРЕГИСТРИРОВАТЬСЯ' }}
        </button>
        <p
          class="auth-switch font-mono"
          @click="switchMode('login')"
        >
          &larr; Уже есть аккаунт? Войти
        </p>
      </form>

      <!-- Messages -->
      <div
        v-if="errorMsg"
        class="auth-message auth-error font-mono"
      >
        {{ errorMsg }}
      </div>
      <div
        v-if="successMsg"
        class="auth-message auth-success font-mono"
      >
        {{ successMsg }}
      </div>

      <!-- Backend URL override -->
      <div
        class="server-toggle font-mono"
        @click="showServerUrl = !showServerUrl"
      >
        SERVER {{ showServerUrl ? '▾' : '▸' }}
      </div>
      <div
        v-if="showServerUrl"
        class="server-field"
      >
        <input
          v-model="serverUrl"
          type="text"
          class="auth-input font-mono"
          placeholder="https://zeta-terminal-backend.onrender.com"
          @blur="saveServerUrl"
          @keydown.enter="saveServerUrl"
        >
        <span class="auth-hint font-mono">URL бэкенда (пустое = по умолчанию)</span>
      </div>
    </div>

    <!-- Activation Modal -->
    <teleport to="body">
      <transition name="modal-fade">
        <div
          v-if="showActivationModal"
          class="modal-overlay"
          @click.self="closeModal"
        >
          <div class="modal-card">
            <h2 class="modal-title font-anton">
              АКТИВАЦИЯ
            </h2>
            <div class="modal-underline" />
            <p class="modal-desc font-mono">
              Введите инвайт-код, отправленный администратором
            </p>
            <form
              class="auth-form"
              @submit.prevent="handleActivate"
            >
              <div class="auth-field">
                <label class="auth-label font-mono">INVITE CODE</label>
                <input
                  v-model="activateCode"
                  type="text"
                  class="auth-input auth-input-code font-mono"
                  placeholder="XXXXXXXX"
                  maxlength="8"
                  required
                >
              </div>
              <button
                type="submit"
                class="auth-submit font-oswald"
                :disabled="loading"
              >
                {{ loading ? statusText : 'АКТИВИРОВАТЬ' }}
              </button>
            </form>
            <div
              v-if="modalError"
              class="auth-message auth-error font-mono"
            >
              {{ modalError }}
            </div>
            <div
              v-if="modalSuccess"
              class="auth-message auth-success font-mono"
            >
              {{ modalSuccess }}
            </div>
            <p
              class="modal-close font-mono"
              @click="closeModal"
            >
              ЗАКРЫТЬ
            </p>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  register as authRegister,
  activate as authActivate,
  login as authLogin,
} from '@/services/authService'
import { getApiBaseUrl, setApiBaseUrl } from '@/utils/apiBase'

const router = useRouter()

const showServerUrl = ref(false)
const serverUrl = ref(getApiBaseUrl())

function saveServerUrl() {
  setApiBaseUrl(serverUrl.value.trim())
  window.location.reload()
}

const mode = ref<'login' | 'register'>('login')
const loading = ref(false)
const statusText = ref('LOADING...')
const errorMsg = ref('')
const successMsg = ref('')

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', email: '', password: '', confirmPassword: '' })

const showActivationModal = ref(false)
const activateCode = ref('')
const modalError = ref('')
const modalSuccess = ref('')

function switchMode(m: 'login' | 'register') {
  mode.value = m
  errorMsg.value = ''
  successMsg.value = ''
}

function closeModal() {
  showActivationModal.value = false
  activateCode.value = ''
  modalError.value = ''
  modalSuccess.value = ''
}

async function handleLogin() {
  errorMsg.value = ''
  successMsg.value = ''
  loading.value = true
  statusText.value = 'LOADING...'
  try {
    await authLogin({ username: loginForm.username, password: loginForm.password })
    router.push('/portfolio')
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : 'Login failed'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''
  if (registerForm.password !== registerForm.confirmPassword) {
    errorMsg.value = 'Пароли не совпадают'
    return
  }
  loading.value = true
  statusText.value = 'LOADING...'
  try {
    const result = await authRegister({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
    })
    successMsg.value = result.message
    registerForm.username = ''
    registerForm.email = ''
    registerForm.password = ''
    registerForm.confirmPassword = ''
    showActivationModal.value = true
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : 'Registration failed'
  } finally {
    loading.value = false
  }
}

async function handleActivate() {
  modalError.value = ''
  modalSuccess.value = ''
  loading.value = true
  statusText.value = 'LOADING...'
  try {
    const result = await authActivate(activateCode.value)
    modalSuccess.value = result.message
    activateCode.value = ''
    setTimeout(() => {
      closeModal()
      mode.value = 'login'
      successMsg.value = 'Аккаунт активирован. Войдите.'
    }, 1500)
  } catch (e: unknown) {
    modalError.value = e instanceof Error ? e.message : 'Activation failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-root {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 48px 24px;
  -webkit-font-smoothing: antialiased;
}

.back-link {
  position: absolute;
  top: 24px;
  left: 24px;
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  cursor: pointer;
  text-decoration: none;
  transition: color var(--transition-fast);
  z-index: 10;
}

.back-link:hover {
  color: var(--accent-red);
}

.auth-container {
  width: 100%;
  max-width: 440px;
}

.auth-header {
  text-align: center;
  margin-bottom: 48px;
}

.auth-title {
  font-size: clamp(3rem, 8vw, 5rem);
  color: var(--accent-red);
  text-transform: uppercase;
  margin: 0;
}

.auth-underline {
  width: 64px;
  height: 4px;
  background: var(--accent-red);
  margin: 16px auto 0;
}

.auth-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-medium);
  margin-bottom: 32px;
}

.auth-tab {
  flex: 1;
  padding: 12px 0;
  background: transparent;
  border: none;
  color: var(--text-tertiary);
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color var(--transition-fast), border-color var(--transition-fast);
}

.auth-tab:hover {
  color: var(--text-primary);
}

.auth-tab.active {
  color: var(--text-primary);
  border-bottom-color: var(--accent-red);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.auth-label {
  font-size: 10px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.15em;
}

.auth-input {
  background: var(--bg-secondary);
  border: 1px solid var(--border-medium);
  color: var(--text-primary);
  padding: 12px 14px;
  font-size: 14px;
  border-radius: var(--radius-sm);
  outline: none;
  transition: border-color var(--transition-fast);
}

.auth-input:focus {
  border-color: var(--accent-red);
}

.auth-input::placeholder {
  color: var(--text-muted);
}

.auth-input-code {
  text-align: center;
  font-size: 20px;
  letter-spacing: 0.3em;
  text-transform: uppercase;
}

.auth-hint {
  font-size: 11px;
  color: var(--accent-red);
  opacity: 0.8;
}

.auth-submit {
  padding: 14px;
  background: var(--accent-red);
  color: #000;
  border: none;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast), opacity var(--transition-fast);
}

.auth-submit:hover:not(:disabled) {
  background: var(--accent-red-hover);
}

.auth-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.auth-switch {
  text-align: center;
  font-size: 12px;
  color: var(--text-tertiary);
  cursor: pointer;
  margin: 8px 0 0;
  transition: color var(--transition-fast);
}

.auth-switch:hover {
  color: var(--accent-red);
}

.auth-message {
  margin-top: 16px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  text-align: center;
}

.auth-error {
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  color: var(--accent-red);
}

.auth-success {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

/* ══════ SERVER URL ══════ */
.server-toggle {
  margin-top: 24px;
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.15em;
  cursor: pointer;
  text-align: center;
  transition: color var(--transition-fast);
}

.server-toggle:hover {
  color: var(--text-tertiary);
}

.server-field {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ══════ MODAL ══════ */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.modal-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  padding: 48px 40px;
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.modal-title {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  color: var(--accent-red);
  text-transform: uppercase;
  margin: 0;
}

.modal-underline {
  width: 48px;
  height: 3px;
  background: var(--accent-red);
  margin: 12px auto 24px;
}

.modal-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0 0 24px;
  line-height: 1.6;
}

.modal-close {
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  margin-top: 20px;
  letter-spacing: 0.1em;
  transition: color var(--transition-fast);
}

.modal-close:hover {
  color: var(--text-primary);
}

/* ══════ MODAL TRANSITION ══════ */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@media (max-width: 480px) {
  .auth-root {
    padding: 24px 16px;
  }

  .modal-card {
    padding: 32px 24px;
  }
}
</style>
