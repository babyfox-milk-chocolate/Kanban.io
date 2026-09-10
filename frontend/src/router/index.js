import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/auth'

import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import BoardDetailView from '@/views/BoardDetailView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue'), meta: { requiresAuth: true } },
  {
    path: '/boards/:id',
    name: 'board-detail',
    component: BoardDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// перехватывать каждую навигацию до её выполнения
router.beforeEach((to) => {
  const auth = useAuthStore()

  // приватный роут + не залогинен → на логин
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  // уже залогинен, но лезет на логин/регистрацию → на главную
  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    return { name: 'boards' }
  }
})

export default router