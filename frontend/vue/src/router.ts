import { createRouter, createWebHistory } from 'vue-router'
import IndicatorDetailView from './views/IndicatorDetailView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/indicadores/:id', component: IndicatorDetailView },
    { path: '/:pathMatch(.*)*', component: { template: '<span />' } },
  ],
})
