<script setup>
import { RouterView, RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import Sidebar from '@/components/Sidebar.vue'
import { ref, onMounted, watch } from 'vue'
import api from './api/axois'

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()

const avatar = ref(null)

async function loadAvatar() {
  if (!auth.isAuthenticated) return
  try {
    const { data } = await api.get('/auth/profile/')
    avatar.value = data.avatar
  } catch { /* игнор */ }
}

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(loadAvatar)
// перезагрузим при логине (когда isAuthenticated меняется с false на true)
watch(() => auth.isAuthenticated, loadAvatar)
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <!-- залогинен: двухпанельный layout -->
    <div v-if="auth.isAuthenticated" class="flex h-screen">
      <Sidebar />
      <div class="flex-1 flex flex-col overflow-hidden">
        <header class="flex items-center justify-between px-6 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <RouterLink to="/profile" class="flex items-center gap-2 hover:opacity-80">
            <img v-if="avatar" :src="avatar" class="w-8 h-8 rounded-full object-cover" />
            <div v-else class="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white text-sm font-bold">
              {{ auth.user?.username?.charAt(0).toUpperCase() }}
            </div>
            <span class="font-semibold">{{ auth.user?.username }}</span>
          </RouterLink>
          <div class="flex items-center gap-4">
            <button @click="theme.toggle" class="text-xl" :title="theme.dark ? 'Светлая тема' : 'Тёмная тема'">
              {{ theme.dark ? '☀️' : '🌙' }}
            </button>
            <button @click="logout" class="text-sm text-red-500 hover:text-red-700">Выйти</button>
          </div>
        </header>
        <main class="flex-1 overflow-auto p-6">
          <RouterView />
        </main>
      </div>
    </div>

    <!-- не залогинен: центрированный контент (login/register) -->
    <main v-else class="max-w-3xl mx-auto p-6">
      <RouterView />
    </main>
  </div>
</template>