<!-- src/components/common/ScrubInput.vue -->
<template>
  <div 
    class="scrub-container"
    :class="{ dragging: isDragging }"
    @mousedown="startDrag"
  >
    <!-- Label (Prefix) -->
    <span v-if="prefix" class="scrub-prefix">{{ prefix }}</span>
    
    <!-- Value Display -->
    <span class="scrub-value">{{ formattedValue }}</span>
    
    <!-- Suffix -->
    <span v-if="suffix" class="scrub-suffix">{{ suffix }}</span>

    <!-- Hidden Input for manual edit (Optional - double click to edit) -->
    <!-- Пока сделаем только drag -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: Number, required: true },
  step: { type: Number, default: 1 },      // Шаг изменения (1, 0.1, 0.01)
  min: { type: Number, default: -Infinity },
  max: { type: Number, default: Infinity },
  decimals: { type: Number, default: 0 },  // Кол-во знаков после запятой
  prefix: { type: String, default: '' },
  suffix: { type: String, default: '' },
  sensitivity: { type: Number, default: 1 } // Чувствительность мыши
})

const emit = defineEmits(['update:modelValue', 'change'])

const isDragging = ref(false)
let startX = 0
let startValue = 0

const formattedValue = computed(() => {
  return props.modelValue.toFixed(props.decimals)
})

const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  startX = e.clientX
  startValue = props.modelValue
  
  document.body.style.cursor = 'ew-resize'
  document.body.style.userSelect = 'none' // Запрет выделения текста при драге
  
  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', stopDrag)
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  
  const dx = e.clientX - startX
  // Формула: Новое = Старое + (Смещение * Чувствительность * Шаг)
  let newValue = startValue + (dx * props.sensitivity * props.step)
  
  // Ограничения
  if (newValue < props.min) newValue = props.min
  if (newValue > props.max) newValue = props.max
  
  // Округление до шага (чтобы не было 15.00000001)
  // Но для плавности лучше передавать сырое, а форматировать при отображении
  emit('update:modelValue', newValue)
  emit('change', newValue)
}

const stopDrag = () => {
  isDragging.value = false
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
}

onUnmounted(() => {
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.scrub-container {
  display: inline-flex;
  align-items: center;
  cursor: ew-resize; /* Курсор <- -> */
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 13px;
  color: #fff;
  transition: all 0.2s;
  user-select: none;
}

.scrub-container:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: #3b82f6; /* Blue highlight */
}

.scrub-container.dragging {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  color: #3b82f6;
}

.scrub-value {
  margin: 0 2px;
  font-weight: 600;
}

.scrub-prefix, .scrub-suffix {
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
}
</style>