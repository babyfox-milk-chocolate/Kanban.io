import { createApp } from 'vue'
import {createPinia} from 'pinia'
import {useThemeStore} from '@/stores/theme'
import router from './router'
import './style.css'
import App from './App.vue'


const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount("#app")

useThemeStore().apply() // применить тему 

