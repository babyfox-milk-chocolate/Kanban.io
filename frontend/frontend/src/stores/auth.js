import {defineStore} from 'pinia'
import axios from 'axios'


export const useAuthStore = defineStore('auth', {
  state: () => ({
    // читаем из localStorage при старте — чтобы логин переживал перезагрузку страницы
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.access,
  },

  actions: {
    async login(username, password) {
      const { data } = await axios.post(
        'http://localhost:8000/api/auth/login/',
        { username, password }
      )
      this.setTokens(data.access, data.refresh)
      this.user = { username }
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    async register(username, email, password) {
      await axios.post('http://localhost:8000/api/auth/register/', {
        username, email, password,
      })
      // после регистрации сразу логинимся
      await this.login(username, password)
    },

    async refreshAccess() {
      const { data } = await axios.post(
        'http://localhost:8000/api/auth/refresh/',
        { refresh: this.refresh }
      )
      this.setTokens(data.access, this.refresh)
    },

    setTokens(access, refresh) {
      this.access = access
      this.refresh = refresh
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
    },

    logout() {
      this.access = null
      this.refresh = null
      this.user = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('user')
    },
  },
})