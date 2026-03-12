// src/stores/tasks.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Task {
  id: string
  title: string
  progress: number // 0 to 100
  status: 'pending' | 'running' | 'completed' | 'error'
  type: 'simulation' | 'upload' | 'calculation'
}

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])

  // Добавить новую задачу
  const addTask = (title: string, type: Task['type'] = 'calculation') => {
    const id = Date.now().toString()
    tasks.value = [...tasks.value, {
      id,
      title,
      progress: 0,
      status: 'running',
      type
    }]
    return id
  }

  // Обновить прогресс
  const updateProgress = (id: string, progress: number) => {
    const isCompleted = progress >= 100
    tasks.value = tasks.value.map(t =>
      t.id === id
        ? { ...t, progress, status: isCompleted ? 'completed' as const : t.status }
        : t
    )
    if (isCompleted) {
      // Удаляем выполненную задачу через 3 секунды, чтобы юзер успел порадоваться
      setTimeout(() => removeTask(id), 3000)
    }
  }

  // Завершить с ошибкой
  const failTask = (id: string) => {
    tasks.value = tasks.value.map(t =>
      t.id === id ? { ...t, status: 'error' as const } : t
    )
    setTimeout(() => removeTask(id), 5000)
  }

  const removeTask = (id: string) => {
    tasks.value = tasks.value.filter(t => t.id !== id)
  }

  return { tasks, addTask, updateProgress, failTask }
})

