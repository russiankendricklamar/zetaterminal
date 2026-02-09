<template>
  <Teleport to="body">
    <div v-if="isOpen" class="command-overlay">
      <!-- Backdrop -->
      <div class="command-backdrop" @click="onClose"></div>

      <!-- Modal -->
      <div class="command-modal">
        <!-- Search Input -->
        <div class="command-search">
          <SearchIcon class="w-5 h-5 text-[#DC2626]" />
          <input
            ref="inputRef"
            type="text"
            v-model="query"
            @input="handleInput"
            placeholder="ВВЕДИТЕ КОМАНДУ ИЛИ ТИКЕР..."
            class="search-input font-mono"
          />
          <span class="esc-badge font-mono">ESC</span>
        </div>

        <!-- Results List -->
        <div ref="listRef" class="command-list custom-scrollbar">
          <div v-if="displayItems.length === 0" class="command-empty font-mono">
            <p>НИЧЕГО НЕ НАЙДЕНО ПО ЗАПРОСУ "{{ query }}"</p>
          </div>
          <div
            v-for="(item, index) in displayItems"
            :key="item.id"
            @click="handleSelect(item)"
            @mouseenter="selectedIndex = index"
            :class="['command-item', { 'command-item-active': index === selectedIndex }]"
          >
            <div class="command-item-left">
              <div :class="['command-icon', { 'command-icon-active': index === selectedIndex }]">
                <HashIcon v-if="item.type === 'command'" class="w-3.5 h-3.5" />
                <span v-else class="font-oswald">{{ item.label.substring(0, 2) }}</span>
              </div>
              <div class="command-info">
                <div class="command-label font-oswald">{{ item.label }}</div>
                <div class="command-desc font-mono">{{ item.description }}</div>
              </div>
            </div>

            <div class="command-item-right">
              <span v-if="item.code" class="command-code font-mono">{{ item.code }}</span>
              <div v-if="index === selectedIndex" class="command-enter font-mono">
                <CornerDownLeftIcon class="w-2.5 h-2.5" /> ENTER
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="command-footer font-mono">
          <div class="footer-hints">
            <span><b>↑↓</b> НАВИГАЦИЯ</span>
            <span><b>↵</b> ВЫБРАТЬ</span>
          </div>
          <div class="footer-label">КОМАНДНАЯ СТРОКА</div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
import { Teleport } from 'vue';
import { SearchResult } from '@/types/terminal';

interface Props {
  isOpen: boolean;
  items: SearchResult[];
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  select: [item: SearchResult];
}>();

const query = ref('');
const selectedIndex = ref(0);
const inputRef = ref<HTMLInputElement | null>(null);
const listRef = ref<HTMLDivElement | null>(null);

const displayItems = computed(() => {
  return props.items.filter(item =>
    item.label.toLowerCase().includes(query.value.toLowerCase()) ||
    item.code?.toLowerCase().includes(query.value.toLowerCase())
  );
});

const handleInput = () => {
  selectedIndex.value = 0;
};

const handleSelect = (item: SearchResult) => {
  emit('select', item);
  emit('close');
};

const onClose = () => emit('close');

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    nextTick(() => {
      inputRef.value?.focus();
      query.value = '';
      selectedIndex.value = 0;
    });
  }
});

const handleKeyDown = (e: KeyboardEvent) => {
  if (!props.isOpen) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    selectedIndex.value = (selectedIndex.value + 1) % displayItems.value.length;
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    selectedIndex.value = (selectedIndex.value - 1 + displayItems.value.length) % displayItems.value.length;
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (displayItems.value[selectedIndex.value]) {
      handleSelect(displayItems.value[selectedIndex.value]);
    }
  } else if (e.key === 'Escape') {
    onClose();
  }
};

watch(() => selectedIndex.value, () => {
  nextTick(() => {
    if (listRef.value && listRef.value.children[selectedIndex.value]) {
      listRef.value.children[selectedIndex.value].scrollIntoView({
        block: 'nearest',
      });
    }
  });
});

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown);
});

// Icon components
const SearchIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>' };
const HashIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/></svg>' };
const CornerDownLeftIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 10 4 15 9 20"/><path d="M20 4v7a4 4 0 0 1-4 4H4"/></svg>' };
</script>

<style scoped>
/* ============================================
   COMMAND PALETTE - BRUTALIST
   ============================================ */
.command-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  padding-left: 16px;
  padding-right: 16px;
}

.command-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
}

.command-modal {
  position: relative;
  width: 100%;
  max-width: 640px;
  background: #0a0a0a;
  border: 1px solid #262626;
  display: flex;
  flex-direction: column;
  max-height: 60vh;
  overflow: hidden;
}

/* Search */
.command-search {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #1a1a1a;
  background: #050505;
  gap: 12px;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: #f5f5f5;
  letter-spacing: 0.1em;
}

.search-input::placeholder {
  color: #3f3f3f;
}

.esc-badge {
  font-size: 10px;
  padding: 4px 8px;
  background: #1a1a1a;
  border: 1px solid #262626;
  color: #525252;
  letter-spacing: 0.1em;
}

/* List */
.command-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.command-empty {
  padding: 48px 16px;
  text-align: center;
  color: #3f3f3f;
  font-size: 11px;
  letter-spacing: 0.1em;
}

.command-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.command-item:hover {
  background: #111111;
}

.command-item-active {
  background: rgba(220, 38, 38, 0.1);
  border-color: rgba(220, 38, 38, 0.3);
}

.command-item-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.command-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  border: 1px solid #262626;
  color: #525252;
  font-size: 11px;
}

.command-icon-active {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.command-info {
  display: flex;
  flex-direction: column;
}

.command-label {
  font-size: 13px;
  font-weight: 500;
  color: #f5f5f5;
  letter-spacing: 0.05em;
}

.command-item-active .command-label {
  color: #f5f5f5;
}

.command-desc {
  font-size: 10px;
  color: #525252;
  margin-top: 2px;
}

.command-item-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.command-code {
  font-size: 10px;
  padding: 4px 8px;
  background: #1a1a1a;
  border: 1px solid #262626;
  color: #525252;
  letter-spacing: 0.1em;
}

.command-item-active .command-code {
  background: rgba(220, 38, 38, 0.2);
  border-color: rgba(220, 38, 38, 0.3);
  color: #DC2626;
}

.command-enter {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: #DC2626;
  letter-spacing: 0.1em;
}

/* Footer */
.command-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #050505;
  border-top: 1px solid #1a1a1a;
  font-size: 10px;
  color: #3f3f3f;
  letter-spacing: 0.1em;
}

.footer-hints {
  display: flex;
  gap: 16px;
}

.footer-hints b {
  color: #525252;
}

.footer-label {
  color: #DC2626;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .command-overlay {
    padding-top: 10vh;
    padding-left: 12px;
    padding-right: 12px;
  }

  .command-modal {
    max-height: 70vh;
  }

  .command-search {
    padding: 12px;
  }

  .search-input {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .command-overlay {
    padding-top: 8vh;
    padding-left: 8px;
    padding-right: 8px;
  }

  .command-item {
    padding: 10px 12px;
  }

  .command-icon {
    width: 28px;
    height: 28px;
  }

  .command-label {
    font-size: 12px;
  }

  .command-desc {
    display: none;
  }
}
</style>
