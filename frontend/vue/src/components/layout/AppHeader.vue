<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Breadcrumb from 'primevue/breadcrumb'
import { useFrontendData } from '../../composables/useFrontendData'
import { useTheme } from '../../composables/useTheme'
import { formatDate } from '../../utils/labels'
import AppIcon from '../common/AppIcon.vue'

const props = defineProps<{ title: string; subtitle: string }>()
const emit = defineEmits<{ openMobileMenu: [] }>()

const route = useRoute()
const router = useRouter()
const data = useFrontendData()
const { isDark, toggleTheme } = useTheme()

const globalSearch = ref('')

const updatedLabel = computed(() => formatDate(data.resumen.fechaActualizacion))
const showBreadcrumb = computed(() => route.path !== '/')
const isDetailRoute = computed(() => route.name === 'indicator-detail')

const indicatorTitle = computed(() => {
  if (!isDetailRoute.value) return ''
  const item = data.indicadores.find((ind) => ind.id === route.params.id)
  if (!item) return 'Indicador'
  return item.nombre.length > 48 ? `${item.nombre.slice(0, 45)}…` : item.nombre
})

const home = { icon: 'home', route: '/', label: 'Inicio' }
const breadcrumbItems = computed(() => {
  if (isDetailRoute.value) {
    return [
      { label: 'Indicadores', route: '/indicadores' },
      { label: indicatorTitle.value },
    ]
  }
  return [{ label: props.title }]
})

watch(
  () => route.query.q,
  (q) => {
    if (route.name === 'indicadores') {
      globalSearch.value = typeof q === 'string' ? q : ''
    } else {
      globalSearch.value = ''
    }
  },
  { immediate: true },
)

function submitGlobalSearch() {
  const q = globalSearch.value.trim()
  if (route.name === 'indicadores') {
    const nextQuery = { ...route.query }
    if (q) {
      nextQuery.q = q
    } else {
      delete nextQuery.q
    }
    router.replace({ path: '/indicadores', query: nextQuery })
    return
  }
  router.push(q ? { path: '/indicadores', query: { q } } : { path: '/indicadores' })
}
</script>

<template>
  <header class="topbar">
    <div class="topbar__left">
      <button
        type="button"
        class="mobile-menu-btn"
        aria-label="Abrir menú de navegación"
        @click="emit('openMobileMenu')"
      >
        <AppIcon name="menu" size="md" />
      </button>

      <div class="topbar__main">
        <Breadcrumb v-if="showBreadcrumb" :home="home" :model="breadcrumbItems" class="topbar__breadcrumb">
          <template #separator>
            <AppIcon name="chevron_right" size="xs" />
          </template>
          <template #item="{ item }">
            <RouterLink v-if="item.route" :to="item.route" class="p-breadcrumb-item-link">
              <AppIcon v-if="item.icon" :name="item.icon" size="xs" />
              <span>{{ item.label }}</span>
            </RouterLink>
            <span v-else class="p-breadcrumb-item-link p-breadcrumb-item-link--current" aria-current="page">
              {{ item.label }}
            </span>
          </template>
        </Breadcrumb>

        <div v-else class="topbar__kicker">
          <span>Plan Veracruzano de Desarrollo 2025–2030</span>
        </div>

        <h1 v-if="!isDetailRoute">{{ title }}</h1>
        <p v-if="!isDetailRoute && subtitle" class="topbar__subtitle">{{ subtitle }}</p>
      </div>
    </div>

    <div class="topbar__right">
      <form class="global-search" role="search" @submit.prevent="submitGlobalSearch">
        <label class="sr-only" for="global-indicator-search">Buscar indicador en el catálogo</label>
        <input
          id="global-indicator-search"
          v-model="globalSearch"
          type="search"
          placeholder="Buscar indicador o tema..."
        />
        <button type="submit" class="global-search__btn" aria-label="Buscar en indicadores">
          <AppIcon name="search" size="sm" />
        </button>
      </form>

      <button
        type="button"
        class="theme-toggle-btn"
        :aria-pressed="isDark"
        :aria-label="isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
        @click="toggleTheme"
      >
        <AppIcon :name="isDark ? 'light_mode' : 'dark_mode'" size="sm" />
        <span>{{ isDark ? 'Modo claro' : 'Modo oscuro' }}</span>
      </button>

      <div v-if="updatedLabel" class="topbar__updated" title="Última fecha de corte de los datos">
        <AppIcon name="calendar_today" size="xs" />
        <span>Actualizado: {{ updatedLabel }}</span>
      </div>
    </div>
  </header>
</template>
