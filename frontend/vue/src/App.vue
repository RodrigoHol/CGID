<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppNavigation from './components/layout/AppNavigation.vue'
import StatusState from './components/common/StatusState.vue'
import DashboardView from './views/DashboardView.vue'
import IndicatorDetailView from './views/IndicatorDetailView.vue'
import IndicatorsView from './views/IndicatorsView.vue'
import SourcesView from './views/SourcesView.vue'
import { loadFrontendData } from './services/data.service'
import type { FrontendData } from './types/contract'

type View = 'dashboard' | 'indicadores' | 'fuentes'

const route = useRoute()
const router = useRouter()
const data = ref<FrontendData | null>(null)
const loading = ref(true)
const error = ref('')
const activeView = ref<View>(route.path === '/indicadores' ? 'indicadores' : route.path === '/fuentes' ? 'fuentes' : 'dashboard')
const isDetail = computed(() => route.path.startsWith('/indicadores/'))

const page = computed(() => ({
  dashboard: { title: 'Resumen general', subtitle: 'Una lectura clara del avance del catálogo prioritario para Veracruz.' },
  indicadores: { title: 'Indicadores', subtitle: 'Consulta el avance y la información técnica de los indicadores prioritarios.' },
  fuentes: { title: 'Fuentes y cobertura', subtitle: 'Conoce el origen, los periodos y el estado de cada serie de datos.' },
}[activeView.value]))

onMounted(() => {
  try {
    data.value = loadFrontendData()
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'No fue posible cargar los datos.'
  } finally {
    loading.value = false
  }
})

function navigate(view: View) {
  activeView.value = view
  router.push(view === 'dashboard' ? '/' : `/${view}`)
}
</script>

<template>
  <div class="app-shell">
    <AppNavigation :active="isDetail ? 'indicadores' : activeView" @navigate="navigate" />
    <div class="app-content">
      <AppHeader v-if="!isDetail" :title="page.title" :subtitle="page.subtitle" />
      <main class="page-content" :class="{ 'page-content--detail': isDetail }">
        <StatusState v-if="loading" type="loading" title="Cargando información" message="Estamos preparando el catálogo de indicadores." />
        <StatusState v-else-if="error" type="error" title="No se pudo cargar el catálogo" :message="error" />
        <StatusState v-else-if="!data" type="empty" title="Sin información disponible" message="No hay datos procesados para mostrar." />
        <IndicatorDetailView v-else-if="isDetail" />
        <DashboardView v-else-if="activeView === 'dashboard'" :data="data" @navigate="navigate" />
        <IndicatorsView v-else-if="activeView === 'indicadores'" :data="data" />
        <SourcesView v-else :data="data" />
      </main>
    </div>
  </div>
</template>
