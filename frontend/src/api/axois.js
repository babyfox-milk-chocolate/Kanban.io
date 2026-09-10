import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'


const api = axios.create({
    baseURL: 'http://localhost:8000/api'
})

// подставляем access-токен в каждый запрос
api.interceptors.request.use((config) => {
    const auth = useAuthStore()
    if(auth.access){
        config.headers.Authorization = `Bearer ${auth.access}`
    }
    return config
})

// 401 (протух access) → пробуем refresh → повторяем запрос
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const auth = useAuthStore()
        const original = error.config

        if(error.response?.status === 401 && !original._retry && auth.refresh){
            original._retry = true
            try{
                await auth.refreshAccess()
                original.headers.Authorization = `Bearer ${auth.access}`
                return api(original)
            }catch {
                auth.logout()
                router.push('/login') // если не удалось обновить access - перекидываем на страницу с логином
            }
        }
        return Promise.reject(error)
    }
)

export default api