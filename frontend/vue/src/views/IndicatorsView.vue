<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FrontendData } from '../types/contract'

const props = defineProps<{ data: FrontendData }>()
const router = useRouter()
const search = ref('')
const coverage = ref<'todos' | 'procesado' | 'fuente_identificada'>('todos')
const history = ref<'todos' | 'con_historico' | 'sin_historico'>('todos')

const filteredIndicators = computed(() => {
  const query = search.value.trim().toLocaleLowerCase()
  return props.data.indicadores.filter((indicator) =>
    (coverage.value === 'todos' || indicator.estadoHistorico === coverage.value)
      && (history.value === 'todos'
        || (history.value === 'con_historico' && indicator.tieneHistorico)
        || (history.value === 'sin_historico' && !indicator.tieneHistorico))
      && (!query || [indicator.clave, indicator.nombre, indicator.ejeRector].join(' ').toLocaleLowerCase().includes(query)),
  )
})

function resetFilters() {
  search.value = ''
  coverage.value = 'todos'
  history.value = 'todos'
}

function openIndicator(id: string) {
  router.push(`/indicadores/${id}`)
}
</script>

<template>
  <section class="content-panel">
    <div class="content-panel__header"><div><span class="section-kicker">CATÁLOGO PRIORITARIO</span><h2>Indicadores del MVP</h2></div><span class="table-caption">{{ filteredIndicators.length }} de {{ data.indicadores.length }} indicadores</span></div>
    <label class="catalog-search"><span class="catalog-search__icon">⌕</span><span class="sr-only">Buscar indicadores</span><input v-model="search" type="search" placeholder="Buscar por nombre, clave o eje rector" /></label>
    <div class="catalog-filters">
      <label><span>Estado de cobertura</span><select v-model="coverage"><option value="todos">Todos los estados</option><option value="procesado">Histórico disponible</option><option value="fuente_identificada">Fuente identificada</option></select></label>
      <label><span>Histórico</span><select v-model="history"><option value="todos">Todos</option><option value="con_historico">Con histórico</option><option value="sin_historico">Sin histórico</option></select></label>
      <button v-if="search || coverage !== 'todos' || history !== 'todos'" class="clear-filters" type="button" @click="resetFilters">Limpiar filtros</button>
    </div>
    <div class="indicator-table" role="table" aria-label="Tabla de indicadores">
      <div class="indicator-table__header" role="row"><span>Indicador</span><span>Eje rector</span><span>Cobertura</span></div>
      <div v-for="indicator in filteredIndicators" :key="indicator.id" class="indicator-row" role="row" tabindex="0" @click="openIndicator(indicator.id)" @keydown.enter="openIndicator(indicator.id)">
        <div class="indicator-row__identity"><div class="indicator-row__key">{{ indicator.clave.split('-').at(-1) }}</div><div class="indicator-row__body"><h3>{{ indicator.nombre }}</h3><span>{{ indicator.clave }}</span></div></div>
        <div class="indicator-row__axis">{{ indicator.ejeRector }}</div>
        <div class="indicator-row__status" :class="`status--${indicator.estadoHistorico}`"><span class="status-dot"></span>{{ indicator.tieneHistorico ? 'Histórico disponible' : 'Fuente identificada' }}</div>
      </div>
    </div>
    <p v-if="filteredIndicators.length === 0" class="catalog-empty">No encontramos indicadores con esa búsqueda.</p>
  </section>
</template>
