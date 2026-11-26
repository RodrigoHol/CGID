import { createRouter, createWebHashHistory } from 'vue-router'
import { SITE_NAME } from './config/site'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    subtitle?: string
    section?: string
  }
}

export const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('./views/DashboardView.vue'),
      meta: {
        title: 'Panorama general',
        subtitle: 'Seguimiento visual del Catálogo de Indicadores PVD 2025–2030.',
      },
    },
    {
      path: '/indicadores',
      name: 'indicadores',
      component: () => import('./views/IndicatorsView.vue'),
      meta: {
        title: 'Indicadores',
        subtitle: 'Busca, filtra por eje o estado y descarga las series oficiales.',
      },
    },
    {
      path: '/indicadores/:id',
      name: 'indicator-detail',
      component: () => import('./views/IndicatorDetailView.vue'),
      meta: {
        title: 'Ficha del indicador',
        subtitle: 'Serie histórica, ficha técnica y fuente oficial verificable.',
        section: 'indicadores',
      },
    },
    {
      path: '/fuentes',
      name: 'fuentes',
      component: () => import('./views/SourcesView.vue'),
      meta: {
        title: 'Fuentes y cobertura',
        subtitle: 'Origen institucional, periodos disponibles y trazabilidad de cada serie.',
      },
    },
    {
      path: '/acerca',
      name: 'acerca',
      component: () => import('./views/AboutView.vue'),
      meta: {
        title: 'Metodología y ayuda',
        subtitle: 'Cómo interpretar los indicadores, glosario y criterios técnicos.',
      },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('./views/NotFoundView.vue'),
      meta: {
        title: 'Página no encontrada',
        subtitle: 'La ruta solicitada no forma parte del catálogo.',
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
