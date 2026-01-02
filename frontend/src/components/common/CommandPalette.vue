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
          <div class="palette-body custom-scroll">
            
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
const selectedId = ref<string | null>(null)

// ================= COMMANDS REGISTRY =================
// Здесь мы определяем все доступные команды
const commands: Command[] = [
  // Navigation
  { id: 'nav-home', label: 'Go to Home', group: 'Navigation', icon: '🏠', action: () => router.push('/') },
  { id: 'nav-dash', label: 'Go to Dashboard', group: 'Navigation', icon: '📊', action: () => router.push('/dashboard') },
  { id: 'nav-port', label: 'Go to Portfolio', group: 'Navigation', icon: '💼', action: () => router.push('/portfolio') },
  { id: 'nav-opt',  label: 'Option Pricing', group: 'Navigation', icon: 'ƒ', desc: 'Calc fair value', action: () => router.push('/pricing/options') },
  { id: 'nav-hmm',  label: 'Market Regimes', group: 'Navigation', icon: '🌊', action: () => router.push('/regimes') },
  { id: 'nav-rep',  label: 'Reports', group: 'Navigation', icon: '📋', action: () => router.push('/reports') },
  
  // Actions
  { id: 'act-mc',   label: 'Run Monte Carlo', group: 'Actions', icon: '🎲', desc: 'Start simulation', action: () => console.log('Running MC...') },
  { id: 'act-recalc', label: 'Recalculate Greeks', group: 'Actions', icon: '∑', action: () => console.log('Recalc Greeks...') },
  { id: 'act-pdf',  label: 'Export PDF', group: 'Actions', icon: '📄', action: () => console.log('Exporting...') },
  
  // Settings / System
  { id: 'sys-theme', label: 'Toggle Theme', group: 'System', icon: '🌗', shortcut: 'Cmd+T', action: () => console.log('Toggle theme') },
  { id: 'sys-set',   label: 'Settings', group: 'System', icon: '⚙️', action: () => router.push('/settings') },
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
  
  // Auto-scroll to element could be added here
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
  width: 100%; max-width: 600px;
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

/* Body */
.palette-body {
  max-height: 400px; overflow-y: auto; padding: 8px;
}
.command-group { margin-bottom: 8px; }
.group-title {
  padding: 8px 12px 4px; font-size: 11px; font-weight: 600;
  color: rgba(255,255,255,0.3); text-transform: uppercase; letter-spacing: 0.05em;
}

.command-item {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px;
  background: transparent; border: none; cursor: pointer;
  border-radius: 8px; transition: all 0.1s;
  text-align: left;
}
.command-item.selected {
  background: #3b82f6; /* Blue-500 */
}
.command-item.selected .cmd-label,
.command-item.selected .cmd-icon, 
.command-item.selected .cmd-desc { color: #fff; }
.command-item.selected .cmd-shortcut { color: rgba(255,255,255,0.8); }

.cmd-left { display: flex; align-items: center; gap: 12px; }
.cmd-icon { font-size: 16px; width: 20px; text-align: center; }
.cmd-label { font-size: 14px; color: #e2e8f0; font-weight: 500; }
.cmd-desc { font-size: 12px; color: rgba(255,255,255,0.4); margin-left: 8px; font-weight: 400; }
.cmd-shortcut { font-size: 11px; color: rgba(255,255,255,0.3); font-family: monospace; letter-spacing: 0.05em; }

.no-results { padding: 20px; text-align: center; color: rgba(255,255,255,0.4); font-size: 14px; }

/* Footer */
.palette-footer {
  padding: 8px 16px; background: rgba(0,0,0,0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex; gap: 16px;
}
.footer-item { font-size: 11px; color: rgba(255,255,255,0.4); display: flex; align-items: center; gap: 4px; }
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
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
</style>
