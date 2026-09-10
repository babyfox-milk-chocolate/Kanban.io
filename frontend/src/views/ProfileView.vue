<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/axois'

const profile = ref(null)
const loading = ref(false)
const error = ref('')

// редактирование профиля
const editEmail = ref('')
const editUsername = ref('')
const savedMsg = ref('')

// смена пароля
const oldPassword = ref('')
const newPassword = ref('')
const pwMsg = ref('')
const pwError = ref('')

const fileInput = ref(null)      
const uploading = ref(false)

function pickFile() {
  fileInput.value.click()        
}

async function uploadAvatar(event) {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('avatar', file)   

  uploading.value = true
  try {
    const { data } = await api.post('/auth/avatar/', formData)
    profile.value.avatar = data.avatar   
  } catch (e) {
    error.value = 'Не удалось загрузить аватар'
  } finally {
    uploading.value = false
    event.target.value = ''   
  }
}

async function fetchProfile() {
  loading.value = true
  try {
    const { data } = await api.get('/auth/profile/')
    profile.value = data
    editEmail.value = data.email
    editUsername.value = data.username
  } catch (e) {
    error.value = 'Не удалось загрузить профиль'
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  savedMsg.value = ''
  error.value = ''
  try {
    const { data } = await api.patch('/auth/profile/', {
      email: editEmail.value,
      username: editUsername.value,
    })
    profile.value = data
    savedMsg.value = 'Сохранено'
    setTimeout(() => (savedMsg.value = ''), 2000)
  } catch (e) {
    const d = e.response?.data
    error.value = d ? Object.values(d).flat().join(' ') : 'Ошибка сохранения'
  }
}

async function changePassword() {
  pwMsg.value = ''
  pwError.value = ''
  try {
    await api.post('/auth/change-password/', {
      old_password: oldPassword.value,
      new_password: newPassword.value,
    })
    pwMsg.value = 'Пароль изменён'
    oldPassword.value = ''
    newPassword.value = ''
  } catch (e) {
    const d = e.response?.data
    pwError.value = d ? Object.values(d).flat().join(' ') : 'Ошибка смены пароля'
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

onMounted(fetchProfile)
</script>

<template>
  <div v-if="profile" class="max-w-2xl mx-auto space-y-6">
    <h1 class="text-2xl font-bold">Личный кабинет</h1>

    <!-- статистика -->
    <div class="flex items-center gap-6">
      <div class="relative">
        <img v-if="profile.avatar" :src="profile.avatar" alt="avatar"
          class="w-20 h-20 rounded-full object-cover" />
        <div v-else class="w-20 h-20 rounded-full bg-indigo-500 flex items-center justify-center text-white text-2xl font-bold">
          {{ profile.username.charAt(0).toUpperCase() }}
        </div>
        <button @click="pickFile" :disabled="uploading"
          class="absolute -bottom-1 -right-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-full w-7 h-7 flex items-center justify-center text-sm shadow hover:bg-gray-50">
          {{ uploading ? '…' : '📷' }}
        </button>
        <!-- скрытый input, открывается по клику на 📷 -->
        <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="uploadAvatar" />
      </div>

      <div class="grid grid-cols-2 gap-4 flex-1">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-5 text-center">
          <div class="text-3xl font-bold text-indigo-600">{{ profile.boards_count }}</div>
          <div class="text-sm text-gray-500 mt-1">проектов</div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-5 text-center">
          <div class="text-3xl font-bold text-indigo-600">{{ profile.tasks_count }}</div>
          <div class="text-sm text-gray-500 mt-1">задач</div>
        </div>
      </div>
    </div>

    <p class="text-sm text-gray-500">
      В системе с {{ formatDate(profile.date_joined) }}
    </p>

    <!-- редактирование профиля -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-4">
      <h2 class="font-semibold">Данные профиля</h2>
      <div v-if="error" class="text-sm text-red-600 bg-red-50 dark:bg-red-900/30 p-2 rounded">{{ error }}</div>
      <div>
        <label class="block text-sm text-gray-500 mb-1">Имя пользователя</label>
        <input v-model="editUsername"
          class="w-full border rounded px-3 py-2 bg-white dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div>
        <label class="block text-sm text-gray-500 mb-1">Email</label>
        <input v-model="editEmail" type="email"
          class="w-full border rounded px-3 py-2 bg-white dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div class="flex items-center gap-3">
        <button @click="saveProfile" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">Сохранить</button>
        <span v-if="savedMsg" class="text-sm text-green-600">{{ savedMsg }}</span>
      </div>
    </div>

    <!-- смена пароля -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-4">
      <h2 class="font-semibold">Смена пароля</h2>
      <div v-if="pwError" class="text-sm text-red-600 bg-red-50 dark:bg-red-900/30 p-2 rounded">{{ pwError }}</div>
      <div v-if="pwMsg" class="text-sm text-green-600 bg-green-50 dark:bg-green-900/30 p-2 rounded">{{ pwMsg }}</div>
      <input v-model="oldPassword" type="password" placeholder="Текущий пароль"
        class="w-full border rounded px-3 py-2 bg-white dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <input v-model="newPassword" type="password" placeholder="Новый пароль"
        class="w-full border rounded px-3 py-2 bg-white dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <button @click="changePassword" class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">Изменить пароль</button>
    </div>
  </div>

  <div v-else-if="loading" class="text-gray-500">Загрузка...</div>
</template>