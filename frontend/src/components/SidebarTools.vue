<template>
  <div class="sidebar-tools-container">
    <div class="tools-grid">
      <button @click="goToSettings" class="tool-btn" title="Параметры">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
      </button>

      <button @click="openHelp" class="tool-btn" title="Справка">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
      </button>

      <button @click="openAbout" class="tool-btn" title="О приложении">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
      </button>
    </div>
  </div>

  <Teleport to="body">
    <!-- Help Modal -->
    <div v-if="showHelp" class="modal-overlay" @click="showHelp = false">
      <div class="glass-modal" @click.stop>
        <div class="modal-header">
           <h3>Справка и Поддержка</h3>
           <button @click="showHelp = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="info-row">
             <span class="label">Support Email</span>
             <a href="#" class="link">quant-support@example.com</a>
          </div>
          <div class="info-row">
             <span class="label">Documentation</span>
             <a href="#" class="link">docs.internal/quant-pro</a>
          </div>
        </div>
      </div>
    </div>

    <!-- About Modal -->
    <div v-if="showAbout" class="modal-overlay" @click="showAbout = false">
      <div class="glass-modal" @click.stop>
        <div class="modal-header">
           <h3>О приложении</h3>
           <button @click="showAbout = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body center">
          <div class="app-logo">QUANT<span class="highlight">PRO</span></div>
          <div class="version">v1.2.0 (Build 2026)</div>
          <p class="copyright">© 2026 Quantitative Finance Team. <br>All rights reserved.</p>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showHelp = ref(false)
const showAbout = ref(false)

const goToSettings = () => router.push('/settings')
const openHelp = () => showHelp.value = true
const openAbout = () => showAbout.value = true
</script>

<style scoped>
/* ============================================
   SIDEBAR TOOL BUTTONS
   ============================================ */
.sidebar-tools-container {
  border-top: 1px solid rgba(255,255,255,0.05); padding: 16px 20px;
}

.tools-grid {
  display: flex; justify-content: space-between; gap: 10px;
}

.tool-btn {
  width: 42px; height: 42px; border-radius: 12px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.6); cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.tool-btn:hover {
  background: rgba(255,255,255,0.1); color: #fff; transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.icon { width: 20px; height: 20px; }

/* ============================================
   GLASS MODALS (VISION PRO STYLE)
   ============================================ */
.modal-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
}

.glass-modal {
  width: 360px; background: rgba(30, 32, 40, 0.85);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
  animation: modalPop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

@keyframes modalPop {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.modal-header {
  padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex; justify-content: space-between; align-items: center;
}
.modal-header h3 { margin: 0; font-size: 14px; color: #fff; font-weight: 600; }

.close-btn {
  background: transparent; border: none; color: rgba(255,255,255,0.5); cursor: pointer; font-size: 16px;
}
.close-btn:hover { color: #fff; }

.modal-body { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.modal-body.center { align-items: center; text-align: center; }

/* Modal Content Styles */
.info-row { display: flex; flex-direction: column; gap: 4px; }
.label { font-size: 11px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.05em; }
.link { color: #60a5fa; text-decoration: none; font-size: 13px; }
.link:hover { text-decoration: underline; }

.app-logo { font-size: 20px; font-weight: 700; color: #fff; letter-spacing: 0.05em; }
.highlight { color: #00d9ff; }
.version { font-family: monospace; font-size: 12px; color: rgba(255,255,255,0.5); background: rgba(255,255,255,0.05); padding: 4px 8px; border-radius: 6px; margin-top: 8px; }
.copyright { font-size: 11px; color: rgba(255,255,255,0.3); margin: 8px 0 0 0; line-height: 1.4; }
</style>