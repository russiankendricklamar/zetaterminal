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
    tasks.value.push({
      id,
      title,
      progress: 0,
      status: 'running',
      type
    })
    return id
  }

  // Обновить прогресс
  const updateProgress = (id: string, progress: number) => {
    const task = tasks.value.find(t => t.id === id)
    if (task) {
      task.progress = progress
      if (progress >= 100) {
        task.status = 'completed'
        // Удаляем выполненную задачу через 3 секунды, чтобы юзер успел порадоваться
        setTimeout(() => removeTask(id), 3000)
      }
    }
  }

  // Завершить с ошибкой
  const failTask = (id: string) => {
    const task = tasks.value.find(t => t.id === id)
    if (task) {
      task.status = 'error'
      setTimeout(() => removeTask(id), 5000)
    }
  }

  const removeTask = (id: string) => {
    tasks.value = tasks.value.filter(t => t.id !== id)
  }

  return { tasks, addTask, updateProgress, failTask }
})