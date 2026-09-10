<script setup>
import { RouterView, RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import Sidebar from '@/components/Sidebar.vue'

const auth = useAuthStore()
const theme = useThemeStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <!-- залогинен: двухпанельный layout -->
    <div v-if="auth.isAuthenticated" class="flex h-screen">
      <Sidebar />
      <div class="flex-1 flex flex-col overflow-hidden">
        <header class="flex items-center justify-between px-6 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <RouterLink to="/profile" class="font-semibold hover:text-indigo-500">
            {{ auth.user?.username }}
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