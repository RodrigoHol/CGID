import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'
import './styles/main.css'
import App from './App.vue'
import { initTheme } from './composables/useTheme'
import { router } from './router'
import { IapPreset } from './theme/preset'

initTheme()

const app = createApp(App)

app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: IapPreset,
    options: {
      darkModeSelector: '.app-dark',
    },
  },
  locale: {
    emptyMessage: 'Sin opciones disponibles',
    emptyFilterMessage: 'Sin resultados',
    emptySearchMessage: 'Sin resultados',
  },
})
app.use(ToastService)
app.directive('tooltip', Tooltip)

app.mount('#app')
