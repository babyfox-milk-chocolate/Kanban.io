<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { reactive } from 'vue'
import { useProjectsStore } from '../stores/projects'
import draggable from 'vuedraggable'
import api from '../api/axois'

const route = useRoute()

const store = useProjectsStore()
const board = computed(() => store.projects.find((p) => p.id == route.params.id))
const tasks = ref([])
const loading = ref(false)
const error = ref('')
const newDue = ref('')
const search = ref('')

const filteredTasks = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return tasks.value
  return tasks.value.filter((t) => t.title.toLowerCase().includes(q))
})

// какая колонка сейчас в режиме добавления (null / 'todo' / 'in_progress' / 'done')
const addingTo = ref(null)
const newTitle = ref('')

const columns = [
  { key: 'todo', label: 'Open', color: 'bg-teal-500' },
  { key: 'in_progress', label: 'In Progress', color: 'bg-blue-500' },
  { key: 'done', label: 'Done', color: 'bg-purple-500' },
]

async function onColumnChange(status) {
  const order = board_[status].map((t) => t.id)
  try {
    await api.post('/tasks/reorder/', { order, status })
    // обновим статус в исходном tasks у перемещённых задач
    board_[status].forEach((t) => { t.status = status })
  } catch (e) {
    error.value = 'Не удалось сохранить порядок'
    await fetchData()
  }
}

// геттеры/сеттеры для каждой колонки — draggable требует v-model на массив
function columnTasks(status) {
  return computed({
    get: () => filteredTasks.value.filter((t) => t.status === status),
    set: () => {},
  })
}

function isOverdue(task) {
  // просрочено, только если не выполнено
  return task.due_date && task.status !== 'done' && task.due_date < new Date().toISOString().slice(0, 10)
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

const board_ = reactive({ todo: [], in_progress: [], done: [] })

function distribute() {
  const q = search.value.trim().toLowerCase()
  const match = (t) => !q || t.title.toLowerCase().includes(q)
  board_.todo = tasks.value.filter((t) => t.status === 'todo' && match(t))
  board_.in_progress = tasks.value.filter((t) => t.status === 'in_progress' && match(t))
  board_.done = tasks.value.filter((t) => t.status === 'done' && match(t))
}

function syncColumns() {
  const q = search.value.trim().toLowerCase()
  const match = (t) => !q || t.title.toLowerCase().includes(q)
  board_.todo = tasks.value.filter((t) => t.status === 'todo' && match(t))
  board_.in_progress = tasks.value.filter((t) => t.status === 'in_progress' && match(t))
  board_.done = tasks.value.filter((t) => t.status === 'done' && match(t))
}

async function fetchData() {
  loading.value = true
  try {
    if (store.projects.length === 0) await store.fetch()   // на случай прямого захода
    const { data } = await api.get(`/tasks/?board=${route.params.id}`)
    tasks.value = data
    syncColumns()
  } catch (e) {
    console.log(e)
    error.value = 'Не удалось загрузить данные'
  } finally {
    loading.value = false
  }
}

// вызывается, когда карточка попадает в колонку (added) — обновляем статус
async function onAdd(event, newStatus) {
  const task = event.item.__draggable_context?.element
  if (!task || task.status === newStatus) return
  const prev = task.status
  task.status = newStatus // оптимистично
  try {
    await api.patch(`/tasks/${task.id}/`, { status: newStatus })
  } catch (e) {
    task.status = prev // откат при ошибке
    error.value = 'Не удалось переместить задачу'
  }
}

async function createTask(status) {
  if (!newTitle.value.trim()) return
  try {
    const { data } = await api.post('/tasks/', {
      board: route.params.id,
      title: newTitle.value,
      status,
      due_date: newDue.value || null,   // пустая строка → null
    })
    tasks.value.push(data)
    board_[status].push(data)
    newTitle.value = ''
    newDue.value = ''
    addingTo.value = null
  } catch (e) {
    error.value = 'Не удалось создать задачу'
  }
}

async function deleteTask(id) {
  try {
    await api.delete(`/tasks/${id}/`)
    tasks.value = tasks.value.filter((t) => t.id !== id)
    for(const key of ['todo', 'in_progress', 'done']){
      board_[key] = board_[key].filter((t) => t.id !== id)
    }
  } catch (e) {
    error.value = 'Не удалось удалить задачу'
  }
}

async function onDrop(newStatus) {
  // после дропа DOM-порядок уже актуален; собираем id задач этой колонки
  const columnIds = filteredTasks.value
    .filter((t) => t.status === newStatus)
    .map((t) => t.id)

  // локально проставим статус перетащенной задаче (на случай межколоночного переноса)
  // — vuedraggable уже подвинул её в массиве, но статус в объекте мог остаться старым
  try {
    await api.post('/tasks/reorder/', {
      order: columnIds,
      status: newStatus,
    })
    // подтягиваем актуальные позиции/статусы с сервера
    await fetchData()
  } catch (e) {
    error.value = 'Не удалось сохранить порядок'
    await fetchData() // откат к серверному состоянию
  }
}


// перезагружаем данные при переключении проекта в сайдбаре
watch(() => route.params.id, fetchData)
onMounted(fetchData)
</script>

<template>
  <div v-if="board">
    <h1 class="text-2xl font-bold mb-6">{{ board.title }}</h1>
    <div class="flex items-center gap-3 mb-6">
      <input v-model="search" placeholder="Поиск задач..."
        class="flex-1 max-w-xs border rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <button v-if="search" @click="search = ''" class="text-sm text-gray-400 hover:text-gray-600">Сбросить</button>
    </div>
    <div v-if="error" class="mb-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/30 p-2 rounded">{{ error }}</div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="col in columns" :key="col.key" class="flex flex-col">
        <!-- заголовок колонки -->
        <div :class="col.color" class="text-white rounded-t-lg px-4 py-3 flex items-center justify-between">
          <span class="font-semibold">{{ col.label }}</span>
          <span class="text-sm bg-white/25 rounded-full px-2">
            {{ board_[col.key].length }}
          </span>
        </div>

        <!-- тело колонки: сюда падают карточки -->
        <div class="flex-1 bg-gray-100 dark:bg-gray-800 rounded-b-lg p-2 min-h-[120px]">
          <draggable
            v-model="board_[col.key]"
            :group="{ name: 'tasks' }"
            item-key="id"
            class="space-y-2 min-h-[60px]"
            @change="onColumnChange(col.key)"
          >
            <template #item="{ element: task }">
            <div class="bg-white dark:bg-gray-700 rounded-lg shadow p-3 cursor-grab active:cursor-grabbing group">
              <div class="flex justify-between items-start gap-2">
                <span class="text-sm">{{ task.title }}</span>
                <button @click="deleteTask(task.id)"
                  class="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition text-xs">✕</button>
              </div>
              <div v-if="task.due_date" class="mt-2 text-xs flex items-center gap-1"
                :class="isOverdue(task) ? 'text-red-500 font-medium' : 'text-gray-400'">
                📅 {{ formatDate(task.due_date) }}
                <span v-if="isOverdue(task)">просрочено</span>
              </div>
            </div>
          </template>
          </draggable>

          <!-- кнопка "+" / поле добавления -->
          <div class="mt-2">
            <div v-if="addingTo === col.key" class="space-y-1">
              <input v-model="newTitle" placeholder="Название задачи" @keyup.enter="createTask(col.key)" autofocus
                class="w-full border rounded px-2 py-1 text-sm bg-white dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-1 focus:ring-indigo-400" />
              <input v-model="newDue" type="date"
                class="w-full border rounded px-2 py-1 text-sm bg-white dark:bg-gray-700 dark:border-gray-600" />
              <div class="flex gap-1">
                <button @click="createTask(col.key)" class="flex-1 bg-indigo-600 text-white rounded py-1 text-sm">OK</button>
                <button @click="addingTo = null" class="px-2 text-gray-400 text-sm">✕</button>
              </div>
            </div>
            <button v-else @click="addingTo = col.key; newTitle = ''"
              class="w-full py-1 rounded text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 flex justify-center">＋</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="text-gray-500">Загрузка...</div>
</template>