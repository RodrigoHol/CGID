import { createRouter, createWebHashHistory } from 'vue-router'
import IndicatorDetailView from './views/IndicatorDetailView.vue'

export const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/indicadores/:id', component: IndicatorDetailView },
    { path: '/:pathMatch(.*)*', component: { template: '<span />' } },
  ],
})
