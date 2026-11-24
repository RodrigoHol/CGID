import { createRouter, createWebHashHistory } from 'vue-router'
import { SITE_NAME } from './config/site'
import AboutView from './views/AboutView.vue'
import DashboardView from './views/DashboardView.vue'
import IndicatorDetailView from './views/IndicatorDetailView.vue'
import IndicatorsView from './views/IndicatorsView.vue'
import NotFoundView from './views/NotFoundView.vue'
import SourcesView from './views/SourcesView.vue'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    subtitle?: string
    hideHeader?: boolean
    section?: string
  }
}

export const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: {
        title: 'Inicio',
        subtitle: 'Una lectura clara del avance del catálogo prioritario para Veracruz.',
      },
    },
    {
      path: '/indicadores',
      name: 'indicadores',
      component: IndicatorsView,
      meta: {
        title: 'Indicadores',
        subtitle: 'Busca, filtra y descarga los indicadores prioritarios del PVD.',
      },
    },
    {
      path: '/indicadores/:id',
      name: 'indicator-detail',
      component: IndicatorDetailView,
      meta: {
        title: 'Indicador',
        hideHeader: true,
        section: 'indicadores',
      },
    },
    {
      path: '/fuentes',
      name: 'fuentes',
      component: SourcesView,
      meta: {
        title: 'Fuentes y cobertura',
        subtitle: 'Origen, periodos y estado de cada serie de datos.',
      },
    },
    {
      path: '/acerca',
      name: 'acerca',
      component: AboutView,
      meta: {
        title: 'Metodología y ayuda',
        subtitle: 'Cómo leer los indicadores, glosario y fuentes.',
      },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
      meta: {
        title: 'Página no encontrada',
        hideHeader: true,
      },
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.path === from.path) return
    return { top: 0 }
  },
})

router.afterEach((to) => {
  const title = to.meta.title ? `${to.meta.title} | ${SITE_NAME} · IAP Veracruz` : `${SITE_NAME} · IAP Veracruz`
  document.title = title
})
