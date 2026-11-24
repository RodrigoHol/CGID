import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import Tooltip from 'primevue/tooltip'
import 'primeicons/primeicons.css'
import './styles/main.css'
import App from './App.vue'
import { router } from './router'
import { IapPreset } from './theme/preset'

const app = createApp(App)

app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: IapPreset,
    options: {
      darkModeSelector: false,
    },
  },
  locale: {
    emptyMessage: 'Sin opciones disponibles',
    emptyFilterMessage: 'Sin resultados',
    emptySearchMessage: 'Sin resultados',
  },
})
app.directive('tooltip', Tooltip)

app.mount('#app')
