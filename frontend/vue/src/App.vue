<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppHeader from './components/layout/AppHeader.vue'
import AppSidebar from './components/layout/AppSidebar.vue'
import StatusState from './components/common/StatusState.vue'
import { loadFrontendData } from './services/data.service'
import type { FrontendData } from './types/contract'

type View = 'dashboard' | 'indicadores' | 'fuentes'

const data = ref<FrontendData | null>(null)
const loading = ref(true)
const error = ref('')
const activeView = ref<View>('dashboard')
const indicatorSearch = ref('')
const coverageFilter = ref<'todos' | 'procesado' | 'fuente_identificada'>('todos')
const historyFilter = ref<'todos' | 'con_historico' | 'sin_historico'>('todos')

onMounted(() => {
  try {
    data.value = loadFrontendData()
  } catch (cause) {
    error.value = cause instanceof Error ? cause.message : 'No fue posible cargar los datos.'
  } finally {
    loading.value = false
  }
})

const page = computed(() => {
  if (activeView.value === 'indicadores') {
    return {
      title: 'Indicadores',
      subtitle: 'Consulta el avance y la información técnica de los indicadores prioritarios.',
    }
  }
  if (activeView.value === 'fuentes') {
    return {
      title: 'Fuentes y cobertura',
      subtitle: 'Conoce el origen, los periodos y el estado de cada serie de datos.',
    }
  }
  return {
    title: 'Resumen general',
    subtitle: 'Una lectura clara del avance del catálogo prioritario para Veracruz.',
  }
})

const filteredIndicators = computed(() => {
  if (!data.value) return []
  const query = indicatorSearch.value.trim().toLocaleLowerCase()
  return data.value.indicadores.filter((indicator) =>
    (coverageFilter.value === 'todos' || indicator.estadoHistorico === coverageFilter.value)
      && (historyFilter.value === 'todos'
        || (historyFilter.value === 'con_historico' && indicator.tieneHistorico)
        || (historyFilter.value === 'sin_historico' && !indicator.tieneHistorico))
      && (!query || [indicator.clave, indicator.nombre, indicator.ejeRector]
        .join(' ')
        .toLocaleLowerCase()
        .includes(query)),
  )
})

const coveragePercent = computed(() => {
  if (!data.value || data.value.resumen.totalIndicadores === 0) return 0
  return Math.round((data.value.resumen.indicadoresConHistorico / data.value.resumen.totalIndicadores) * 100)
})

function resetIndicatorFilters() {
  indicatorSearch.value = ''
  coverageFilter.value = 'todos'
  historyFilter.value = 'todos'
}
</script>

<template>
  <div class="app-shell">
    <AppSidebar :active="activeView" @navigate="activeView = $event" />
    <div class="app-content">
      <AppHeader :title="page.title" :subtitle="page.subtitle" />
      <main class="page-content">
        <StatusState
          v-if="loading"
          type="loading"
          title="Cargando información"
          message="Estamos preparando el catálogo de indicadores."
        />
        <StatusState
          v-else-if="error"
          type="error"
          title="No se pudo cargar el catálogo"
          :message="error"
        />
        <StatusState
          v-else-if="!data"
          type="empty"
          title="Sin información disponible"
          message="No hay datos procesados para mostrar."
        />
        <template v-else>
          <template v-if="activeView === 'dashboard'">
            <section class="welcome-card">
            <div>
              <span class="welcome-card__label">CATÁLOGO GENERAL DE INDICADORES DE DESEMPEÑO</span>
              <h2>Datos para comprender el desarrollo de Veracruz</h2>
              <p>Consulta, compara y da seguimiento a los indicadores del Plan Veracruzano de Desarrollo 2025–2030.</p>
            </div>
            <div class="welcome-card__seal">PVD<br /><small>25—30</small></div>
            </section>

            <section class="intro-panel">
              <div class="intro-panel__heading">
                <span class="section-kicker">¿QUÉ ES ESTE CATÁLOGO?</span>
                <h2>Información pública para dar seguimiento a los resultados</h2>
              </div>
              <div class="intro-panel__copy">
                <p>El Catálogo General de Indicadores de Desempeño reúne las fichas técnicas de los indicadores seleccionados para dar seguimiento y evaluar el cumplimiento de los objetivos, estrategias y metas del Plan Veracruzano de Desarrollo (PVD) 2025–2030.</p>
                <p>En esta plataforma puedes consultar sus definiciones, metas, fuentes y series históricas. La información ayuda a comparar avances, fortalecer la rendición de cuentas y apoyar decisiones basadas en evidencia para el bienestar de las y los veracruzanos.</p>
              </div>
            </section>

            <section class="metric-grid" aria-label="Resumen de indicadores">
            <article class="metric-card metric-card--primary">
              <span class="metric-card__label">Indicadores del MVP</span>
              <strong>{{ data.resumen.totalIndicadores }}</strong>
              <span class="metric-card__detail">Catálogo prioritario</span>
            </article>
            <article class="metric-card">
              <span class="metric-card__label">Con histórico</span>
              <strong>{{ data.resumen.indicadoresConHistorico }}</strong>
              <span class="metric-card__detail metric-card__detail--positive">Series listas para consulta</span>
            </article>
            <article class="metric-card">
              <span class="metric-card__label">Fuentes identificadas</span>
              <strong>{{ data.resumen.porEstadoHistorico.fuente_identificada || 0 }}</strong>
              <span class="metric-card__detail">Pendientes de extracción</span>
            </article>
            <article class="metric-card">
              <span class="metric-card__label">Periodos disponibles</span>
              <strong>{{ data.resumen.periodosHistoricos.length }}</strong>
              <span class="metric-card__detail">{{ data.resumen.periodosHistoricos[0] }}–{{ data.resumen.periodosHistoricos.at(-1) }}</span>
            </article>
            </section>

            <section class="content-panel">
            <div class="content-panel__header">
              <div>
                <span class="section-kicker">EXPLORA LA INFORMACIÓN</span>
                <h2>Un punto de partida para el análisis</h2>
              </div>
              <button class="outline-button" @click="activeView = 'indicadores'">Ver indicadores <span>→</span></button>
            </div>
            <div class="preview-grid">
              <article class="preview-card">
                <div class="preview-card__icon preview-card__icon--blue">▦</div>
                <div><h3>Catálogo técnico</h3><p>Busca por clave, nombre, eje rector o disponibilidad histórica.</p></div>
                <span class="preview-card__arrow">→</span>
              </article>
              <article class="preview-card">
                <div class="preview-card__icon preview-card__icon--teal">↗</div>
                <div><h3>Series históricas</h3><p>Consulta la evolución disponible para cada indicador de Veracruz.</p></div>
                <span class="preview-card__arrow">→</span>
              </article>
              <article class="preview-card">
                <div class="preview-card__icon preview-card__icon--gold">✓</div>
                <div><h3>Fuentes trazables</h3><p>Conoce el origen y la cobertura de cada dato publicado.</p></div>
                <span class="preview-card__arrow">→</span>
              </article>
            </div>
            </section>
            <section class="coverage-panel">
              <div class="coverage-panel__heading">
                <div>
                  <span class="section-kicker">ESTADO DE COBERTURA</span>
                  <h2>Avance de integración de datos</h2>
                  <p>Indicadores con una serie histórica lista para consulta en Veracruz.</p>
                </div>
                <strong>{{ coveragePercent }}<small>%</small></strong>
              </div>
              <div class="coverage-bar" aria-label="Porcentaje de indicadores con histórico">
                <span :style="{ width: `${coveragePercent}%` }"></span>
              </div>
              <div class="coverage-panel__legend">
                <span><i class="legend-dot legend-dot--ready"></i>{{ data.resumen.indicadoresConHistorico }} procesados</span>
                <span><i class="legend-dot legend-dot--pending"></i>{{ data.resumen.indicadoresSinHistorico }} con fuente identificada</span>
              </div>
            </section>
          </template>
          <section v-else-if="activeView === 'indicadores'" class="content-panel">
            <div class="content-panel__header">
              <div>
                <span class="section-kicker">CATÁLOGO PRIORITARIO</span>
                <h2>Indicadores del MVP</h2>
              </div>
              <span class="table-caption">{{ filteredIndicators.length }} de {{ data.indicadores.length }} indicadores</span>
            </div>
            <label class="catalog-search">
              <span class="catalog-search__icon">⌕</span>
              <span class="sr-only">Buscar indicadores</span>
              <input v-model="indicatorSearch" type="search" placeholder="Buscar por nombre, clave o eje rector" />
            </label>
            <div class="catalog-filters">
              <label>
                <span>Estado de cobertura</span>
                <select v-model="coverageFilter">
                  <option value="todos">Todos los estados</option>
                  <option value="procesado">Histórico disponible</option>
                  <option value="fuente_identificada">Fuente identificada</option>
                </select>
              </label>
              <label>
                <span>Histórico</span>
                <select v-model="historyFilter">
                  <option value="todos">Todos</option>
                  <option value="con_historico">Con histórico</option>
                  <option value="sin_historico">Sin histórico</option>
                </select>
              </label>
              <button v-if="indicatorSearch || coverageFilter !== 'todos' || historyFilter !== 'todos'" class="clear-filters" @click="resetIndicatorFilters">Limpiar filtros</button>
            </div>
            <div class="indicator-table" role="table" aria-label="Tabla de indicadores">
              <div class="indicator-table__header" role="row">
                <span>Indicador</span>
                <span>Eje rector</span>
                <span>Cobertura</span>
              </div>
              <div v-for="indicator in filteredIndicators" :key="indicator.id" class="indicator-row" role="row">
                <div class="indicator-row__identity">
                  <div class="indicator-row__key">{{ indicator.clave.split('-').at(-1) }}</div>
                  <div class="indicator-row__body">
                    <h3>{{ indicator.nombre }}</h3>
                    <span>{{ indicator.clave }}</span>
                  </div>
                </div>
                <div class="indicator-row__axis">{{ indicator.ejeRector }}</div>
                <div class="indicator-row__status" :class="`status--${indicator.estadoHistorico}`">
                  <span class="status-dot"></span>
                  {{ indicator.tieneHistorico ? 'Histórico disponible' : 'Fuente identificada' }}
                </div>
              </div>
            </div>
            <p v-if="filteredIndicators.length === 0" class="catalog-empty">No encontramos indicadores con esa búsqueda.</p>
          </section>
          <section v-else class="content-panel">
            <div class="content-panel__header">
              <div>
                <span class="section-kicker">TRAZABILIDAD</span>
                <h2>Fuentes de los indicadores</h2>
              </div>
              <span class="table-caption">{{ data.fuentes.length }} fuentes registradas</span>
            </div>
            <div class="source-list">
              <div class="source-table__header">
                <span>Fuente e institución</span>
                <span>Entidad y cobertura</span>
                <span>Acción</span>
              </div>
              <article v-for="source in data.fuentes" :key="source.idIndicador" class="source-row">
                <div>
                  <strong>{{ source.institucion }}</strong>
                  <h3>{{ source.nombre }}</h3>
                </div>
                <span class="source-row__coverage">{{ source.entidad }}<br />{{ source.periodos.length }} periodos disponibles</span>
                <a class="source-row__link" :href="source.url" target="_blank" rel="noreferrer">Consultar fuente <span>↗</span></a>
              </article>
            </div>
          </section>
        </template>
      </main>
    </div>
  </div>
</template>
