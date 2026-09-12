import {defineStore} from 'pinia'
import {ref} from 'vue'
import api from '../api/axois'

export const useProjectsStore = defineStore('projects', () => {
    const projects = ref([])

    async function fetch(){
        const {data} = await api.get('/boards/')
        projects.value = data
    }

    async function create(title) {
        const { data } = await api.post('/boards/', { title })
        projects.value.unshift(data)
        return data
    }

    async function rename(id, title) {
        const { data } = await api.patch(`/boards/${id}/`, { title })
        const p = projects.value.find((x) => x.id === id)
        if (p) p.title = data.title   // меняем в общем массиве — увидят все
        return data
    }

    async function remove(id) {
        await api.delete(`/boards/${id}/`)
        projects.value = projects.value.filter((p) => p.id !== id)
    }

    return { projects, fetch, create, rename, remove }
})