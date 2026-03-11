<!-- src/components/common/CommandPalette.vue -->
<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="palette-backdrop"
        @click="close"
      >
        <!-- Modal Container -->
        <div
          class="palette-modal"
          @click.stop
        >
          <!-- Search Input -->
          <div class="palette-header">
            <span class="search-icon">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              ><circle
                cx="11"
                cy="11"
                r="8"
              /><line
                x1="21"
                y1="21"
                x2="16.65"
                y2="16.65"
              /></svg>
            </span>
            <input 
              ref="searchInput"
              v-model="query"
              type="text" 
              placeholder="Введите команду или поиск..."
              class="palette-input"
              @keydown.down.prevent="navigate('down')"
              @keydown.up.prevent="navigate('up')"
              @keydown.enter.prevent="execute"
              @keydown.esc="close"
            >
            <span class="esc-badge">ESC</span>
          </div>

          <!-- Results List -->
          <div
            ref="paletteBody"
            class="palette-body custom-scroll"
          >
            <!-- No Results -->
            <div
              v-if="filteredCommands.length === 0"
              class="no-results"
            >
              Команды не найдены.
            </div>

            <!-- Groups -->
            <div
              v-for="(group, groupName) in groupedCommands"
              v-else
              :key="groupName"
              class="command-group"
            >
              <div class="group-title">
                {{ groupName }}
              </div>
              
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
                    <span
                      v-if="cmd.desc"
                      class="cmd-desc"
                    >— {{ cmd.desc }}</span>
                  </span>
                </div>
                <div
                  v-if="cmd.shortcut"
                  class="cmd-shortcut"
                >
                  {{ cmd.shortcut }}
                </div>
              </button>
            </div>
          </div>

          <!-- Footer -->
          <div class="palette-footer">
            <div class="footer-item">
              <span>↵</span> выбрать
            </div>
            <div class="footer-item">
              <span>↑↓</span> навигация
            </div>
            <div class="footer-item">
              <span>⌘K</span> открыть/закрыть
            </div>
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

// ================= РЕГИСТР КОМАНД =================
const commands: Command[] = [
  // ===== НАВИГАЦИЯ: Главная & Дашборд =====
  { 
    id: 'nav-home', 
    label: 'Главная страница', 
    group: 'Навигация', 
    icon: '🏠', 
    action: () => router.push('/') 
  },
  { 
    id: 'nav-docs', 
    label: 'Документация', 
    group: 'Навигация', 
    icon: '📚', 
    desc: 'Справочная информация',
    action: () => router.push('/docs') 
  },

  // ===== ПОРТФЕЛЬ И АНАЛИТИКА =====
  { 
    id: 'nav-port', 
    label: 'Портфель', 
    group: 'Портфель и аналитика', 
    icon: '💼', 
    desc: 'Управление портфелем',
    action: () => router.push('/portfolio') 
  },
{ 
    id: 'nav-greeks', 
    label: 'Греческие параметры', 
    group: 'Портфель и аналитика', 
    icon: '∑', 
    desc: 'Риск-метрики (Greeks)',
    action: () => router.push('/greeks') 
  },
  { 
    id: 'nav-reports', 
    label: 'Отчёты портфеля', 
    group: 'Портфель и аналитика', 
    icon: '📋', 
    action: () => router.push('/reports') 
  },
  { 
    id: 'nav-pnl', 
    label: 'PnL Attribution', 
    group: 'Портфель и аналитика', 
    icon: '📈', 
    desc: 'Декомпозиция прибылей/убытков',
    action: () => router.push('/analytics/pnl') 
  },

  // ===== УПРАВЛЕНИЕ РИСКАМИ =====
  { 
    id: 'nav-backtest', 
    label: 'Бэктестинг', 
    group: 'Управление рисками', 
    icon: '📈', 
    desc: 'Проверка торговых стратегий',
    action: () => router.push('/backtest') 
  },
  { 
    id: 'nav-stress', 
    label: 'Стресс-тестирование', 
    group: 'Управление рисками', 
    icon: '⚡', 
    desc: 'Анализ стресс-сценариев',
    action: () => router.push('/stress') 
  },
  {
    id: 'nav-hedging',
    label: 'Помощник по хеджированию',
    group: 'Управление рисками',
    icon: '🛡️',
    desc: 'Стратегии хеджирования',
    action: () => router.push('/hedging')
  },
  {
    id: 'nav-repo',
    label: 'REPO Analysis',
    group: 'Управление рисками',
    icon: '📊',
    desc: 'Concentration, collateral, systemic risk',
    action: () => router.push('/repo')
  },

  // ===== АНАЛИЗ РЫНОЧНЫХ РЕЖИМОВ =====
  { 
    id: 'nav-regimes', 
    label: 'Рыночные режимы', 
    group: 'Анализ режимов', 
    icon: '🌊', 
    desc: 'HMM анализ режимов рынка',
    action: () => router.push('/regimes') 
  },
  { 
    id: 'nav-regime-detail', 
    label: 'Детали режима', 
    group: 'Анализ режимов', 
    icon: '🔬', 
    desc: 'Детальный HMM анализ',
    action: () => router.push('/regime-details') 
  },
  { 
    id: 'nav-spectral-regimes', 
    label: 'Комплексный анализ режимов', 
    group: 'Анализ режимов', 
    icon: '🌀', 
    desc: 'Спектральная декомпозиция скрытых режимов',
    action: () => router.push('/spectral-regimes') 
  },

  // ===== ДОХОДНОСТЬ ОБЛИГАЦИЙ =====
  { 
    id: 'nav-yield', 
    label: 'Доходность облигаций', 
    group: 'Облигации', 
    icon: '📈', 
    desc: 'Анализ доходности',
    action: () => router.push('/fixed-income') 
  },
  { 
    id: 'nav-bond-val', 
    label: 'Оценка облигаций (DCF)', 
    group: 'Облигации', 
    icon: '💵', 
    desc: 'Справедливая стоимость',
    action: () => router.push('/bond-valuation') 
  },
  { 
    id: 'nav-zcyc', 
    label: 'Кривая КБД', 
    group: 'Облигации', 
    icon: '📉', 
    desc: 'Zero-Coupon Yield Curve',
    action: () => router.push('/zcyc-viewer') 
  },
  { 
    id: 'nav-bond-report', 
    label: 'Отчёт об оценке', 
    group: 'Облигации', 
    icon: '📄', 
    desc: 'Генератор отчётов',
    action: () => router.push('/bond-report') 
  },
  { 
    id: 'nav-vanila-bond', 
    label: 'Отчёт Vanila Bond', 
    group: 'Облигации', 
    icon: '📊', 
    desc: 'Обыкновенные облигации',
    action: () => router.push('/vanila-bond-report') 
  },
  { 
    id: 'nav-floater-bond', 
    label: 'Отчёт Floater Bond', 
    group: 'Облигации', 
    icon: '📋', 
    desc: 'Облигации с плавающей ставкой',
    action: () => router.push('/floater-bond-report') 
  },

  // ===== ОПЦИИ =====
  { 
    id: 'nav-opt', 
    label: 'Оценка опционов', 
    group: 'Производные инструменты', 
    icon: 'ƒ', 
    desc: 'Ценообразование опционов',
    action: () => router.push('/pricing/options') 
  },
  { 
    id: 'nav-opt-models', 
    label: 'Сравнение моделей опционов', 
    group: 'Производные инструменты', 
    icon: '📊', 
    desc: 'Black-Scholes vs другие',
    action: () => router.push('/pricing/options/models') 
  },
  { 
    id: 'nav-opt-greeks', 
    label: 'Greeks опционов', 
    group: 'Производные инструменты', 
    icon: '🎯', 
    desc: 'Анализ греческих параметров',
    action: () => router.push('/pricing/options/greeks') 
  },
  { 
    id: 'nav-opt-portfolio', 
    label: 'Портфель опционов', 
    group: 'Производные инструменты', 
    icon: '💼', 
    desc: 'Управление позициями',
    action: () => router.push('/pricing/options/portfolio') 
  },
  { 
    id: 'nav-vol-surf', 
    label: 'Поверхность волатильности', 
    group: 'Производные инструменты', 
    icon: '〰️', 
    desc: 'SABR/SVI моделирование',
    action: () => router.push('/analytics/volatility') 
  },

  // ===== СВОПЫ =====
  { 
    id: 'nav-swaps', 
    label: 'Оценка свопов', 
    group: 'Свопы', 
    icon: '🔄', 
    desc: 'IRS & Currency Swaps',
    action: () => router.push('/valuation/swaps') 
  },
  { 
    id: 'nav-swap-greeks', 
    label: 'Greeks свопов', 
    group: 'Свопы', 
    icon: '🎯', 
    desc: 'Риск-метрики свопов',
    action: () => router.push('/swap-greeks') 
  },
  { 
    id: 'nav-swap-stress', 
    label: 'Стресс-тест свопов', 
    group: 'Свопы', 
    icon: '⚡', 
    desc: 'Анализ стресс-сценариев',
    action: () => router.push('/stress/swaps') 
  },

  // ===== ФОРВАРДЫ =====
  { 
    id: 'nav-forwards', 
    label: 'Оценка форвардов', 
    group: 'Форварды', 
    icon: '➡️', 
    desc: 'Ценообразование форвардов',
    action: () => router.push('/valuation/forwards') 
  },
  { 
    id: 'nav-forward-curve', 
    label: 'Построение кривой форвардов', 
    group: 'Форварды', 
    icon: '📈', 
    desc: 'Forward Curve Builder',
    action: () => router.push('/forwards/curve') 
  },
  { 
    id: 'nav-forward-greeks', 
    label: 'Greeks форвардов', 
    group: 'Форварды', 
    icon: '🎯', 
    desc: 'Риск-метрики',
    action: () => router.push('/forwards/greeks') 
  },
  { 
    id: 'nav-forward-basis', 
    label: 'Анализ базиса', 
    group: 'Форварды', 
    icon: '📈', 
    desc: 'Basis Analysis',
    action: () => router.push('/forwards/basis') 
  },
  { 
    id: 'nav-forward-margin', 
    label: 'Маржа и финансирование', 
    group: 'Форварды', 
    icon: '💰', 
    desc: 'Margin & Financing',
    action: () => router.push('/forwards/margin') 
  },
  { 
    id: 'nav-forward-arbitrage', 
    label: 'Сканер арбитража', 
    group: 'Форварды', 
    icon: '🔍', 
    desc: 'Поиск арбитражных возможностей',
    action: () => router.push('/forwards/arbitrage') 
  },

  // ===== ДЕЙСТВИЯ =====
  { 
    id: 'act-reload', 
    label: 'Перезагрузить данные', 
    group: 'Действия', 
    icon: '🔄', 
    shortcut: '⌘R', 
    desc: 'Обновить страницу',
    action: () => window.location.reload() 
  },
  { 
    id: 'act-export-pdf', 
    label: 'Экспорт в PDF', 
    group: 'Действия', 
    icon: '📥', 
    desc: 'Сохранить как PDF',
    action: () => window.print() 
  },
  { 
    id: 'act-copy', 
    label: 'Копировать ссылку', 
    group: 'Действия', 
    icon: '📋', 
    desc: 'Скопировать URL в буфер',
    action: () => {
      navigator.clipboard.writeText(window.location.href)
      // Можно добавить уведомление
    } 
  },
  { 
    id: 'act-clear-cache', 
    label: 'Очистить кэш', 
    group: 'Действия', 
    icon: '🗑️', 
    desc: 'Очистить локальное хранилище',
    action: () => {
      if (confirm('Очистить весь кэш? Это удалит сохранённые настройки (авторизация сохранится).')) {
        const authKeys = ['zeta_access_token', 'zeta_refresh_token', 'zeta_auth_user']
        const saved: Record<string, string | null> = {}
        for (const key of authKeys) {
          saved[key] = localStorage.getItem(key)
        }
        localStorage.clear()
        for (const [key, value] of Object.entries(saved)) {
          if (value !== null) localStorage.setItem(key, value)
        }
        window.location.reload()
      }
    }
  },

  // ===== СИСТЕМА =====
  { 
    id: 'sys-theme', 
    label: 'Переключить тему', 
    group: 'Система', 
    icon: '🌙', 
    shortcut: '⌘T', 
    desc: 'Тёмная/Светлая тема',
    action: () => {
      const html = document.documentElement
      html.classList.toggle('dark')
      localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light')
    }
  },
  { 
    id: 'sys-fullscreen', 
    label: 'Полноэкранный режим', 
    group: 'Система', 
    icon: '⛶', 
    desc: 'Включить/выключить',
    action: () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {})
      } else {
        document.exitFullscreen()
      }
    }
  },
  { 
    id: 'sys-settings', 
    label: 'Настройки', 
    group: 'Система', 
    icon: '⚙️', 
    desc: 'Параметры приложения',
    action: () => router.push('/settings') 
  },
  { 
    id: 'sys-help', 
    label: 'Помощь и горячие клавиши', 
    group: 'Система', 
    icon: '❓', 
    desc: 'Справка по использованию',
    action: () => {
      alert(`Горячие клавиши:\n\n` +
            `⌘K / Ctrl+K - Открыть палитру команд\n` +
            `⌘R / Ctrl+R - Перезагрузить\n` +
            `⌘T / Ctrl+T - Переключить тему\n` +
            `ESC - Закрыть палитру\n` +
            `↑↓ - Навигация\n` +
            `Enter - Выполнить команду`)
    } 
  },
]

// ================= ЛОГИКА =================

const filteredCommands = computed(() => {
  if (!query.value.trim()) return commands
  const q = query.value.toLowerCase().trim()
  return commands.filter(c => 
    c.label.toLowerCase().includes(q) || 
    c.group.toLowerCase().includes(q) ||
    c.desc?.toLowerCase().includes(q) ||
    c.id.toLowerCase().includes(q)
  )
})

const groupedCommands = computed(() => {
  const groups: Record<string, Command[]> = {}
  filteredCommands.value.forEach(cmd => {
    if (!groups[cmd.group]) groups[cmd.group] = []
    groups[cmd.group].push(cmd)
  })
  // Сортируем группы в определённом порядке
  const groupOrder = [
    'Навигация',
    'Портфель и аналитика',
    'Управление рисками',
    'Анализ режимов',
    'Облигации',
    'Производные инструменты',
    'Свопы',
    'Форварды',
    'Действия',
    'Система'
  ]
  const sorted: Record<string, Command[]> = {}
  groupOrder.forEach(group => {
    if (groups[group]) sorted[group] = groups[group]
  })
  // Добавляем оставшиеся группы
  Object.keys(groups).forEach(group => {
    if (!sorted[group]) sorted[group] = groups[group]
  })
  return sorted
})

// Плоский список для навигации с клавиатуры
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

watch(query, () => {
  // При изменении запроса сбрасываем на первый элемент
  if (flatList.value.length > 0) {
    selectedId.value = flatList.value[0].id
  }
})

// Действия
const open = () => {
  isOpen.value = true
  query.value = ''
  selectedId.value = flatList.value[0]?.id || null
  nextTick(() => {
    searchInput.value?.focus()
    // Скролл в начало списка
    if (paletteBody.value) {
      paletteBody.value.scrollTop = 0
    }
  })
}

const close = () => {
  isOpen.value = false
  query.value = ''
}

const selectCommand = (cmd: Command) => {
  try {
    cmd.action()
    close()
  } catch (error) {
    console.error('Ошибка выполнения команды:', error)
    // Можно показать уведомление об ошибке
  }
}

const execute = () => {
  const cmd = flatList.value.find(c => c.id === selectedId.value)
  if (cmd) selectCommand(cmd)
}

const navigate = (dir: 'up' | 'down') => {
  const list = flatList.value
  if (list.length === 0) return
  
  const idx = list.findIndex(c => c.id === selectedId.value)
  if (idx === -1) {
    selectedId.value = list[0].id
    return
  }

  if (dir === 'down') {
    selectedId.value = list[idx + 1]?.id || list[0].id
  } else {
    selectedId.value = list[idx - 1]?.id || list[list.length - 1].id
  }
  
  // Автоскролл к выбранному элементу
  nextTick(() => {
    const selected = document.querySelector('.command-item.selected')
    if (selected && paletteBody.value) {
      const container = paletteBody.value
      const elementRect = (selected as HTMLElement).getBoundingClientRect()
      const containerRect = container.getBoundingClientRect()
      
      // Вычисляем позицию элемента относительно позиции скролла контейнера
      const elementTopRelative = elementRect.top - containerRect.top + container.scrollTop
      const elementBottomRelative = elementTopRelative + elementRect.height
      const containerBottom = container.scrollTop + container.clientHeight
      
      // Скролл вверх, если элемент выше viewport
      if (elementTopRelative < container.scrollTop) {
        container.scrollTop = elementTopRelative - 8 // 8px отступ сверху
      }
      // Скролл вниз, если элемент ниже viewport
      else if (elementBottomRelative > containerBottom) {
        container.scrollTop = elementBottomRelative - container.clientHeight + 8 // 8px отступ снизу
      }
    }
  })
}

// Глобальный обработчик клавиатуры
const onKeydown = (e: KeyboardEvent) => {
  // Открытие/закрытие палитры
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    isOpen.value ? close() : open()
    return
  }
  
  // Другие глобальные горячие клавиши
  if (isOpen.value) {
    // ESC уже обработан в template
    return
  }
  
  // Глобальные горячие клавиши (когда палитра закрыта)
  if ((e.metaKey || e.ctrlKey) && e.key === 'r' && !e.shiftKey) {
    e.preventDefault()
    window.location.reload()
  }
  
  if ((e.metaKey || e.ctrlKey) && e.key === 't') {
    e.preventDefault()
    const html = document.documentElement
    html.classList.toggle('dark')
    localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})

// Экспорт для использования извне (например, через ref)
defineExpose({
  open,
  close
})
</script>

<style scoped>
/* Backdrop */
.palette-backdrop {
  position: fixed; 
  inset: 0; 
  z-index: 9999;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex; 
  justify-content: center; 
  align-items: flex-start;
  padding-top: 100px;
}

/* Modal */
.palette-modal {
  width: 100%; 
  max-width: 700px;
  background: rgba(30, 41, 59, 0.95); /* Slate-800 с прозрачностью */
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 
    0 20px 50px rgba(0, 0, 0, 0.8),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  display: flex; 
  flex-direction: column;
  overflow: hidden;
}

/* Header & Input */
.palette-header {
  display: flex; 
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(0, 0, 0, 0.2);
}

.search-icon { 
  color: rgba(255,255,255,0.4); 
  margin-right: 12px; 
  display: flex; 
  flex-shrink: 0;
}

.palette-input {
  flex: 1; 
  background: transparent; 
  border: none; 
  outline: none;
  font-size: 16px; 
  color: #fff;
  font-weight: 500;
}

.palette-input::placeholder { 
  color: rgba(255,255,255,0.3); 
}

.esc-badge {
  font-size: 10px; 
  font-weight: bold; 
  color: rgba(255,255,255,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 4px; 
  padding: 3px 8px;
  font-family: monospace;
  margin-left: 12px;
  flex-shrink: 0;
}

/* Body - SCROLL CONTAINER */
.palette-body {
  max-height: 500px; 
  overflow-y: auto; 
  overflow-x: hidden;
  padding: 8px;
  scroll-behavior: smooth;
}

.command-group { 
  margin-bottom: 8px; 
}

.group-title {
  padding: 10px 16px 6px; 
  font-size: 10px; 
  font-weight: 700;
  color: rgba(255,255,255,0.35); 
  text-transform: uppercase; 
  letter-spacing: 0.1em;
  position: sticky;
  top: 0;
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(10px);
  z-index: 1;
}

.command-item {
  width: 100%; 
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  padding: 12px 16px;
  background: transparent; 
  border: none; 
  cursor: pointer;
  border-radius: 8px; 
  transition: all 0.15s ease;
  text-align: left;
  margin: 2px 0;
}

.command-item:hover {
  background: rgba(59, 130, 246, 0.2);
}

.command-item.selected {
  background: #3b82f6; /* Blue-500 */
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.command-item.selected .cmd-label,
.command-item.selected .cmd-icon, 
.command-item.selected .cmd-desc { 
  color: #fff; 
}

.command-item.selected .cmd-shortcut { 
  color: rgba(255,255,255,0.9); 
  background: rgba(255, 255, 255, 0.2);
}

.cmd-left { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  flex: 1; 
  min-width: 0;
}

.cmd-icon { 
  font-size: 18px; 
  width: 24px; 
  text-align: center; 
  flex-shrink: 0; 
  line-height: 1;
}

.cmd-label { 
  font-size: 14px; 
  color: #e2e8f0; 
  font-weight: 500; 
  flex: 1;
  min-width: 0;
}

.cmd-desc { 
  font-size: 12px; 
  color: rgba(255,255,255,0.4); 
  margin-left: 8px; 
  font-weight: 400; 
  white-space: nowrap;
}

.cmd-shortcut { 
  font-size: 11px; 
  color: rgba(255,255,255,0.35); 
  font-family: 'SF Mono', 'Menlo', monospace; 
  letter-spacing: 0.05em;
  background: rgba(255,255,255,0.08);
  padding: 4px 8px;
  border-radius: 4px;
  flex-shrink: 0;
  margin-left: 8px;
}

.no-results { 
  padding: 60px 20px; 
  text-align: center; 
  color: rgba(255,255,255,0.4); 
  font-size: 14px; 
}

/* Footer */
.palette-footer {
  padding: 12px 20px; 
  background: rgba(0,0,0,0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex; 
  gap: 20px; 
  font-size: 11px;
  flex-wrap: wrap;
}

.footer-item { 
  color: rgba(255,255,255,0.4); 
  display: flex; 
  align-items: center; 
  gap: 6px; 
}

.footer-item span {
  background: rgba(255,255,255,0.1); 
  border-radius: 4px;
  padding: 2px 6px; 
  font-family: 'SF Mono', 'Menlo', monospace;
  font-size: 10px;
  border: 1px solid rgba(255,255,255,0.05);
}

/* Animations */
.fade-enter-active, .fade-leave-active { 
  transition: opacity 0.2s ease; 
}

.fade-enter-from, .fade-leave-to { 
  opacity: 0; 
}

.fade-enter-active .palette-modal { 
  animation: scaleIn 0.2s cubic-bezier(0.16, 1, 0.3, 1); 
}

.fade-leave-active .palette-modal { 
  animation: scaleOut 0.15s ease-in; 
}

@keyframes scaleIn {
  from { 
    transform: scale(0.95) translateY(-10px); 
    opacity: 0; 
  }
  to { 
    transform: scale(1) translateY(0); 
    opacity: 1; 
  }
}

@keyframes scaleOut {
  from { 
    transform: scale(1) translateY(0); 
    opacity: 1; 
  }
  to { 
    transform: scale(0.95) translateY(-10px); 
    opacity: 0; 
  }
}

/* Custom Scroll */
.custom-scroll::-webkit-scrollbar { 
  width: 6px; 
}

.custom-scroll::-webkit-scrollbar-track { 
  background: transparent; 
}

.custom-scroll::-webkit-scrollbar-thumb { 
  background: rgba(255,255,255,0.15); 
  border-radius: 3px; 
}

.custom-scroll::-webkit-scrollbar-thumb:hover { 
  background: rgba(255,255,255,0.25); 
}

/* Responsive */
@media (max-width: 768px) {
  .palette-backdrop {
    padding-top: 0;
    align-items: stretch;
  }

  .palette-modal {
    max-width: 100%;
    border-radius: 0;
    height: 100vh;
    max-height: 100vh;
    border: none;
    /* Safe area for notch */
    padding-top: env(safe-area-inset-top, 0);
    padding-bottom: env(safe-area-inset-bottom, 0);
  }

  .palette-header {
    padding: 16px;
    padding-top: calc(16px + env(safe-area-inset-top, 0));
  }

  .palette-input {
    font-size: 16px; /* Prevent zoom on iOS */
  }

  .palette-body {
    max-height: none;
    flex: 1;
    padding: 8px;
  }

  .command-item {
    padding: 14px 16px;
    min-height: 48px; /* Touch target */
  }

  .cmd-icon {
    font-size: 20px;
    width: 28px;
  }

  .cmd-label {
    font-size: 14px;
  }

  .cmd-desc {
    display: none; /* Hide on mobile to save space */
  }

  .cmd-shortcut {
    display: none; /* Hide shortcuts on mobile */
  }

  .group-title {
    padding: 12px 16px 8px;
    font-size: 11px;
  }

  .palette-footer {
    padding: 12px 16px;
    padding-bottom: calc(12px + env(safe-area-inset-bottom, 0));
    gap: 12px;
  }

  .footer-item {
    font-size: 10px;
  }

  .esc-badge {
    display: none; /* Use touch to close instead */
  }
}

@media (max-width: 480px) {
  .palette-header {
    padding: 12px;
    padding-top: calc(12px + env(safe-area-inset-top, 0));
  }

  .search-icon {
    margin-right: 10px;
  }

  .search-icon svg {
    width: 18px;
    height: 18px;
  }

  .palette-input {
    font-size: 15px;
  }

  .palette-body {
    padding: 6px;
  }

  .command-item {
    padding: 12px 14px;
    border-radius: 6px;
  }

  .cmd-icon {
    font-size: 18px;
    width: 24px;
  }

  .cmd-label {
    font-size: 13px;
  }

  .group-title {
    padding: 10px 14px 6px;
    font-size: 10px;
  }

  .no-results {
    padding: 40px 16px;
    font-size: 13px;
  }

  .palette-footer {
    padding: 10px 14px;
    padding-bottom: calc(10px + env(safe-area-inset-bottom, 0));
    gap: 10px;
  }
}

@media (max-width: 375px) {
  .palette-header {
    padding: 10px;
    padding-top: calc(10px + env(safe-area-inset-top, 0));
  }

  .palette-input {
    font-size: 14px;
  }

  .command-item {
    padding: 10px 12px;
    min-height: 44px;
  }

  .cmd-icon {
    font-size: 16px;
    width: 22px;
    gap: 10px;
  }

  .cmd-label {
    font-size: 12px;
  }

  .group-title {
    padding: 8px 12px 5px;
    font-size: 9px;
  }

  .palette-footer {
    padding: 8px 12px;
    padding-bottom: calc(8px + env(safe-area-inset-bottom, 0));
    gap: 8px;
  }

  .footer-item {
    font-size: 9px;
  }

  .footer-item span {
    padding: 1px 4px;
    font-size: 8px;
  }
}
</style>
