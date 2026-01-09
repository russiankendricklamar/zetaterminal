<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4">
      <!-- Backdrop -->
      <div 
        class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" 
        @click="onClose"
      ></div>

      <!-- Modal -->
      <div class="relative w-full max-w-2xl glass-panel rounded-2xl overflow-hidden shadow-2xl animate-fade-in flex flex-col max-h-[60vh]">
        <!-- Search Input -->
        <div class="flex items-center px-4 py-4 border-b border-white/10 bg-white/5">
          <SearchIcon class="w-5 h-5 text-gray-400 mr-3" />
          <input
            ref="inputRef"
            type="text"
            v-model="query"
            @input="handleInput"
            placeholder="Введите команду или тикер..."
            class="flex-1 bg-transparent border-none outline-none text-lg text-white placeholder-gray-500 font-medium uppercase"
          />
          <div class="flex items-center gap-2">
            <span class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-gray-400 border border-white/5">ESC</span>
          </div>
        </div>

        <!-- Results List -->
        <div 
          ref="listRef"
          class="overflow-y-auto custom-scrollbar p-2 scroll-smooth"
        >
          <div v-if="displayItems.length === 0" class="py-12 text-center text-gray-500">
            <p>Ничего не найдено по запросу "{{ query }}"</p>
          </div>
          <div
            v-for="(item, index) in displayItems"
            :key="item.id"
            @click="handleSelect(item)"
            @mouseenter="selectedIndex = index"
            :class="`flex items-center justify-between px-4 py-3 rounded-xl cursor-pointer transition-colors group ${
              index === selectedIndex ? 'bg-indigo-500/20 border border-indigo-500/30' : 'hover:bg-white/5 border border-transparent'
            }`"
          >
            <div class="flex items-center gap-4">
              <div :class="`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                index === selectedIndex ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/20' : 'bg-white/10 text-gray-400'
              }`">
                <HashIcon v-if="item.type === 'command'" class="w-3.5 h-3.5" />
                <span v-else>{{ item.label.substring(0, 2) }}</span>
              </div>
              <div>
                <div :class="`font-bold text-sm ${index === selectedIndex ? 'text-white' : 'text-gray-300'}`">{{ item.label }}</div>
                <div class="text-[10px] text-gray-500 flex items-center gap-1">
                  {{ item.description }}
                </div>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <span v-if="item.code" class="text-[10px] font-mono font-bold bg-white/10 px-1.5 py-0.5 rounded text-gray-400 border border-white/5">
                {{ item.code }}
              </span>
              <div v-if="index === selectedIndex" class="text-[10px] text-indigo-300 font-mono flex items-center gap-1 animate-pulse">
                <CornerDownLeftIcon class="w-2.5 h-2.5" /> Enter
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer -->
        <div class="px-4 py-2 bg-black/40 border-t border-white/5 flex justify-between items-center text-[10px] text-gray-500">
          <div class="flex gap-4">
            <span><b class="text-gray-300">↑↓</b> навигация</span>
            <span><b class="text-gray-300">↵</b> выбрать</span>
          </div>
          <div>
            Командная строка
          </div>
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
