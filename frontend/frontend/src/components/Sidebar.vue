<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../api/axois'
import {useRouter} from 'vue-router'

const route = useRoute()
const router = useRouter()

const projects = ref([])
const newTitle = ref('')
const adding = ref(false)

async function fetchProjects() {
  const { data } = await api.get('/boards/')
  projects.value = data
}

async function createProject() {
  if (!newTitle.value.trim()) return
  const { data } = await api.post('/boards/', { title: newTitle.value })
  projects.value.unshift(data)
  newTitle.value = ''
  adding.value = false
}

async function deleteProject(project) {
  if (!confirm(`Удалить проект «${project.title}»? Все задачи внутри удалятся тоже.`)) return
  try {
    await api.delete(`/boards/${project.id}/`)
    projects.value = projects.value.filter((p) => p.id !== project.id)
    // если удалили открытый проект — уводим на главную
    if (route.params.id == project.id) {
      router.push('/')
    }
  } catch (e) {
    console.error(e)
  }
}

// чтобы новый проект появлялся в списке и после создания на других экранах
defineExpose({ fetchProjects })
onMounted(fetchProjects)
</script>

<template>
  <aside class="w-64 bg-gray-900 text-gray-100 flex flex-col shrink-0">
    <div class="px-4 py-4 flex items-center justify-between">
      <h2 class="font-bold text-lg">Проекты</h2>
      <button @click="adding = !adding" class="w-7 h-7 rounded hover:bg-gray-700 flex items-center justify-center text-xl leading-none">+</button>
    </div>

    <div v-if="adding" class="px-4 pb-2">
      <input v-model="newTitle" placeholder="Название" @keyup.enter="createProject" autofocus
        class="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-400" />
    </div>

    <nav class="flex-1 overflow-auto px-2">
      <div v-for="p in projects" :key="p.id" class="group relative mb-1">
        <RouterLink :to="`/boards/${p.id}`"
          class="block px-3 py-2 pr-8 rounded text-sm truncate"
          :class="route.params.id == p.id ? 'bg-gray-700 font-medium' : 'hover:bg-gray-800 text-gray-300'">
          {{ p.title }}
        </RouterLink>
        <button @click="deleteProject(p)"
          class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition text-xs">
          ✕
        </button>
      </div>
      <p v-if="projects.length === 0" class="px-3 py-2 text-xs text-gray-500">Проектов пока нет</p>
    </nav>
  </aside>
</template>