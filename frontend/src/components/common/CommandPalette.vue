<!-- src/components/common/CommandPalette.vue -->
<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div v-if="isOpen" class="palette-backdrop" @click="close">
        
        <!-- Modal Container -->
        <div class="palette-modal" @click.stop>
          
          <!-- Search Input -->
          <div class="palette-header">
            <span class="search-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </span>
            <input 
              ref="searchInput"
              v-model="query"
              type="text" 
              placeholder="Type a command or search..."
              class="palette-input"
              @keydown.down.prevent="navigate('down')"
              @keydown.up.prevent="navigate('up')"
              @keydown.enter.prevent="execute"
              @keydown.esc="close"
            />
            <span class="esc-badge">ESC</span>
          </div>

          <!-- Results List -->
          <div ref="paletteBody" class="palette-body custom-scroll">
            
            <!-- No Results -->
            <div v-if="filteredCommands.length === 0" class="no-results">
              No matching commands found.
            </div>

            <!-- Groups -->
            <div v-else v-for="(group, groupName) in groupedCommands" :key="groupName" class="command-group">
              <div class="group-title">{{ groupName }}</div>
              
              <button
                v-for="cmd in group"
                :key="cmd.id"
                class="command-item"
                :class="{ selected: selectedId === cmd.id }"
                @click="selectCommand(cmd)"
                @mouseenter="selectedId = cmd.id"
              >
                <div class="cmd-left">
                  <span class="cmd-icon">{{ cmd.icon }}</span>
                  <span class="cmd-label">
                    {{ cmd.label }}
                    <span v-if="cmd.desc" class="cmd-desc">— {{ cmd.desc }}</span>
                  </span>
                </div>
                <div v-if="cmd.shortcut" class="cmd-shortcut">{{ cmd.shortcut }}</div>
              </button>
            </div>

          </div>

          <!-- Footer -->
          <div class="palette-footer">
            <div class="footer-item"><span>↵</span> to select</div>
            <div class="footer-item"><span>↑↓</span> to navigate</div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

// Типы
type Command = {
  id: string
  label: string
  group: string
  icon: string
  desc?: string
  shortcut?: string
  action: () => void
}

const router = useRouter()
const isOpen = ref(false)
const query = ref('')
const searchInput = ref<HTMLInputElement | null>(null)
const paletteBody = ref<HTMLDivElement | null>(null)
const selectedId = ref<string | null>(null)

// ================= COMMANDS REGISTRY =================
const commands: Command[] = [
  // ===== NAVIGATION: Home & Dashboard =====
  { id: 'nav-home', label: 'Go to Home', group: 'Navigation', icon: '🏠', action: () => router.push('/') },
  { id: 'nav-dash', label: 'Go to Dashboard', group: 'Navigation', icon: '📊', action: () => router.push('/dashboard') },

  // ===== PORTFOLIO ANALYTICS =====
  { id: 'nav-port', label: 'Portfolio Optimization', group: 'Portfolio Analytics', icon: '💼', action: () => router.push('/portfolio') },
  { id: 'nav-mc', label: 'Monte Carlo Simulation', group: 'Portfolio Analytics', icon: '🎲', desc: 'Стохастическое моделирование', action: () => router.push('/monte-carlo') },
  { id: 'nav-greeks', label: 'Risk Metrics (Greeks)', group: 'Portfolio Analytics', icon: '∑', action: () => router.push('/greeks') },
  { id: 'nav-reports', label: 'Portfolio Reports', group: 'Portfolio Analytics', icon: '📋', action: () => router.push('/reports') },
  { id: 'nav-settings', label: 'Portfolio Settings', group: 'Portfolio Analytics', icon: '⚙️', action: () => router.push('/settings') },

  // ===== RISK MANAGEMENT =====
  { id: 'nav-backtest', label: 'Backtesting', group: 'Risk Management', icon: '📈', desc: 'Проверка стратегии', action: () => router.push('/backtest') },
  { id: 'nav-stress', label: 'Stress Testing', group: 'Risk Management', icon: '⚡', desc: 'Стресс-сценарии', action: () => router.push('/stress') },

  // ===== MARKET RESEARCH (HMM) =====
  { id: 'nav-regimes', label: 'Market Regimes', group: 'Market Research', icon: '🌊', desc: 'Режимы рынка (HMM)', action: () => router.push('/regimes') },
  { id: 'nav-regime-detail', label: 'Regime Details', group: 'Market Research', icon: '🔬', desc: 'Детальный анализ', action: () => router.push('/regime-details') },
  { id: 'nav-fixed-income', label: 'Fixed Income Analytics', group: 'Market Research', icon: '📊', desc: 'Доходности облигаций', action: () => router.push('/fixed-income') },

  // ===== FIXED INCOME (Bonds) =====
  { id: 'nav-bond-val', label: 'Bond Valuation (DCF)', group: 'Fixed Income', icon: '💵', desc: 'Оценка облигаций', action: () => router.push('/bond-valuation') },
  { id: 'nav-zcyc', label: 'Zero-Coupon Yield Curve', group: 'Fixed Income', icon: '📉', desc: 'Кривая КБД', action: () => router.push('/zcyc-viewer') },
  { id: 'nav-bond-report', label: 'Bond Report Generator', group: 'Fixed Income', icon: '📄', desc: 'Отчет об оценке', action: () => router.push('/bond-report') },

  // ===== DERIVATIVES (Coming Soon) =====
  { id: 'nav-opt', label: 'Option Pricing', group: 'Derivatives', icon: 'ƒ', desc: 'Справедливая стоимость', action: () => alert('Coming soon...') },
  { id: 'nav-swaps', label: 'Swap Valuation', group: 'Derivatives', icon: '🔄', desc: 'IRS & Currency Swaps', action: () => alert('Coming soon...') },
  { id: 'nav-vol-surf', label: 'Volatility Surface', group: 'Derivatives', icon: '〰️', desc: 'SABR/SVI моделирование', action: () => alert('Coming soon...') },
  { id: 'nav-forwards', label: 'Forward Pricing', group: 'Derivatives', icon: '➡️', desc: 'Оценка форвардов', action: () => alert('Coming soon...') },
  { id: 'nav-margin', label: 'Derivatives Margin', group: 'Derivatives', icon: '💰', desc: 'Расчет маржи', action: () => alert('Coming soon...') },

  // ===== ACTIONS =====
  { id: 'act-reload', label: 'Reload Data', group: 'Actions', icon: '🔄', shortcut: 'Cmd+R', action: () => window.location.reload() },
  { id: 'act-export-pdf', label: 'Export as PDF', group: 'Actions', icon: '📥', desc: 'Сохранить PDF', action: () => window.print() },
  { id: 'act-copy', label: 'Copy Link', group: 'Actions', icon: '📋', desc: 'Скопировать ссылку', action: () => navigator.clipboard.writeText(window.location.href) },

  // ===== SYSTEM & SETTINGS =====
  { id: 'sys-theme', label: 'Toggle Dark Mode', group: 'System', icon: '🌙', shortcut: 'Cmd+T', action: () => {
    const html = document.documentElement
    html.classList.toggle('dark')
    localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light')
  }},
  { id: 'sys-fullscreen', label: 'Toggle Fullscreen', group: 'System', icon: '⛶', action: () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => console.log(err))
    } else {
      document.exitFullscreen()
    }
  }},
  { id: 'sys-help', label: 'Help & Shortcuts', group: 'System', icon: '❓', action: () => alert('Cmd/Ctrl + K: Toggle Command Palette\nCmd/Ctrl + R: Reload\nArrows: Navigate\nEnter: Execute') },
]

// ================= LOGIC =================

const filteredCommands = computed(() => {
  if (!query.value) return commands
  const q = query.value.toLowerCase()
  return commands.filter(c => 
    c.label.toLowerCase().includes(q) || 
    c.group.toLowerCase().includes(q) ||
    c.desc?.toLowerCase().includes(q)
  )
})

const groupedCommands = computed(() => {
  const groups: Record<string, Command[]> = {}
  filteredCommands.value.forEach(cmd => {
    if (!groups[cmd.group]) groups[cmd.group] = []
    groups[cmd.group].push(cmd)
  })
  return groups
})

// Flattened list for keyboard navigation
const flatList = computed(() => {
  return Object.values(groupedCommands.value).flat()
})

watch(filteredCommands, (newVal) => {
  if (newVal.length > 0) {
    selectedId.value = newVal[0].id
  } else {
    selectedId.value = null
  }
})

// Actions
const open = () => {
  isOpen.value = true
  query.value = ''
  selectedId.value = flatList.value[0]?.id || null
  nextTick(() => searchInput.value?.focus())
}

const close = () => {
  isOpen.value = false
}

const selectCommand = (cmd: Command) => {
  cmd.action()
  close()
}

const execute = () => {
  const cmd = flatList.value.find(c => c.id === selectedId.value)
  if (cmd) selectCommand(cmd)
}

const navigate = (dir: 'up' | 'down') => {
  const list = flatList.value
  const idx = list.findIndex(c => c.id === selectedId.value)
  if (idx === -1) return

  if (dir === 'down') {
    selectedId.value = list[idx + 1]?.id || list[0].id
  } else {
    selectedId.value = list[idx - 1]?.id || list[list.length - 1].id
  }
  
  // Auto-scroll to selected element with getBoundingClientRect
  nextTick(() => {
    const selected = document.querySelector('.command-item.selected')
    if (selected && paletteBody.value) {
      const container = paletteBody.value
      const elementRect = (selected as HTMLElement).getBoundingClientRect()
      const containerRect = container.getBoundingClientRect()
      
      // Calculate position of element relative to container's scroll position
      const elementTopRelative = elementRect.top - containerRect.top + container.scrollTop
      const elementBottomRelative = elementTopRelative + elementRect.height
      const containerBottom = container.scrollTop + container.clientHeight
      
      // Scroll up if item is above viewport
      if (elementTopRelative < container.scrollTop) {
        container.scrollTop = elementTopRelative - 8 // 8px padding from top
      }
      // Scroll down if item is below viewport
      else if (elementBottomRelative > containerBottom) {
        container.scrollTop = elementBottomRelative - container.clientHeight + 8 // 8px padding from bottom
      }
    }
  })
}

// Global Keyboard Listener
const onKeydown = (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    isOpen.value ? close() : open()
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
/* Backdrop */
.palette-backdrop {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex; justify-content: center; align-items: flex-start;
  padding-top: 100px;
}

/* Modal */
.palette-modal {
  width: 100%; max-width: 650px;
  background: #1e293b; /* Slate-800 */
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
  display: flex; flex-direction: column;
  overflow: hidden;
}

/* Header & Input */
.palette-header {
  display: flex; align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.search-icon { color: rgba(255,255,255,0.4); margin-right: 12px; display: flex; }
.palette-input {
  flex: 1; background: transparent; border: none; outline: none;
  font-size: 16px; color: #fff;
}
.palette-input::placeholder { color: rgba(255,255,255,0.3); }
.esc-badge {
  font-size: 10px; font-weight: bold; color: rgba(255,255,255,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 4px; padding: 2px 6px;
}

/* Body - SCROLL CONTAINER */
.palette-body {
  max-height: 500px; 
  overflow-y: auto; 
  overflow-x: hidden;
  padding: 8px;
  scroll-behavior: smooth;
}

.command-group { margin-bottom: 8px; }
.group-title {
  padding: 8px 12px 4px; font-size: 10px; font-weight: 700;
  color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.1em;
}

.command-item {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px;
  background: transparent; border: none; cursor: pointer;
  border-radius: 8px; transition: all 0.15s;
  text-align: left;
}
.command-item:hover {
  background: rgba(59, 130, 246, 0.3);
}
.command-item.selected {
  background: #3b82f6; /* Blue-500 */
}
.command-item.selected .cmd-label,
.command-item.selected .cmd-icon, 
.command-item.selected .cmd-desc { color: #fff; }
.command-item.selected .cmd-shortcut { color: rgba(255,255,255,0.8); }

.cmd-left { display: flex; align-items: center; gap: 12px; flex: 1; }
.cmd-icon { font-size: 16px; width: 20px; text-align: center; flex-shrink: 0; }
.cmd-label { font-size: 14px; color: #e2e8f0; font-weight: 500; }
.cmd-desc { font-size: 12px; color: rgba(255,255,255,0.4); margin-left: 8px; font-weight: 400; }
.cmd-shortcut { 
  font-size: 10px; 
  color: rgba(255,255,255,0.35); 
  font-family: monospace; 
  letter-spacing: 0.05em;
  background: rgba(255,255,255,0.05);
  padding: 2px 6px;
  border-radius: 3px;
  flex-shrink: 0;
}

.no-results { padding: 40px 20px; text-align: center; color: rgba(255,255,255,0.4); font-size: 14px; }

/* Footer */
.palette-footer {
  padding: 8px 16px; background: rgba(0,0,0,0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex; gap: 16px; font-size: 11px;
}
.footer-item { color: rgba(255,255,255,0.4); display: flex; align-items: center; gap: 4px; }
.footer-item span {
  background: rgba(255,255,255,0.1); border-radius: 3px;
  padding: 1px 4px; font-family: monospace;
}

/* Animations */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-enter-active .palette-modal { animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1); }
.fade-leave-active .palette-modal { animation: scaleIn 0.2s reverse; }

@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

/* Custom Scroll */
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
.custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }

/* Responsive */
@media (max-width: 768px) {
  .palette-modal { max-width: 90%; }
  .palette-backdrop { padding-top: 50px; }
}
</style>