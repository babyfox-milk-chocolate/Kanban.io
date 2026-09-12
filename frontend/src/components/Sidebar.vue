<script setup>
import { computed, ref } from 'vue'
import { useProjectsStore } from '@/stores/projects'
import { useRoute, useRouter, RouterLink } from 'vue-router'

const store = useProjectsStore()
const route = useRoute()
const router = useRouter()

const projects = computed(() => store.projects)

// создание
const newTitle = ref('')
const adding = ref(false)
async function createProject() {
  if (!newTitle.value.trim()) return
  await store.create(newTitle.value)
  newTitle.value = ''
  adding.value = false
}

// удаление
async function deleteProject(project) {
  if (!confirm(`Удалить проект «${project.title}»? Все задачи внутри удалятся тоже.`)) return
  await store.remove(project.id)
  if (route.params.id == project.id) router.push('/')
}

// редактирование
const editingId = ref(null)
const editTitle = ref('')
function startEdit(p) { editingId.value = p.id; editTitle.value = p.title }
async function saveEdit(p) {
  const title = editTitle.value.trim()
  if (title && title !== p.title) await store.rename(p.id, title)
  editingId.value = null
}

// грузим список один раз
store.fetch()
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
        <!-- режим редактирования -->
        <input v-if="editingId === p.id" v-model="editTitle"
          @keyup.enter="saveEdit(p)" @keyup.esc="editingId = null" @blur="saveEdit(p)" autofocus
          class="w-full bg-gray-800 border border-indigo-400 rounded px-3 py-2 text-sm focus:outline-none" />

        <!-- обычный режим -->
        <template v-else>
          <RouterLink :to="`/boards/${p.id}`" @dblclick="startEdit(p)"
            class="block px-3 py-2 pr-8 rounded text-sm truncate"
            :class="route.params.id == p.id ? 'bg-gray-700 font-medium' : 'hover:bg-gray-800 text-gray-300'">
            {{ p.title }}
          </RouterLink>
          <button @click="deleteProject(p)"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition text-xs">
            ✕
          </button>
        </template>
      </div>
      <p v-if="projects.length === 0" class="px-3 py-2 text-xs text-gray-500">Проектов пока нет</p>
    </nav>
  </aside>
</template>