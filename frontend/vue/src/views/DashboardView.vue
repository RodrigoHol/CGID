<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import { useFrontendData } from '../composables/useFrontendData'
import { CATALOGO_TOTAL_INDICADORES } from '../config/site'
import { GLOSSARY_BY_KEY } from '../utils/glossary'

const router = useRouter()
const data = useFrontendData()

const coveragePercent = computed(() => {
  if (!data.resumen.totalIndicadores) return 0
  return Math.round(
    (data.resumen.indicadoresConHistorico / data.resumen.totalIndicadores) * 100,
  )
})

const firstPeriod = computed(() => data.resumen.periodosHistoricos[0] ?? '—')
const lastPeriod = computed(() => data.resumen.periodosHistoricos.at(-1) ?? '—')
</script>

<template>
  <div class="home-view">
    <section class="surface-card home-hero">
      <div class="home-hero__content">
        <span class="section-kicker">CATÁLOGO GENERAL DE INDICADORES DE DESEMPEÑO</span>
        <h2>Datos para comprender el desarrollo de Veracruz</h2>
        <p>
          Reúne las fichas técnicas de los indicadores que dan seguimiento a los objetivos y metas
          del Plan Veracruzano de Desarrollo 2025–2030: definiciones, metas, fuentes y series históricas.
        </p>
        <div class="home-hero__actions">
          <Button
            label="Explorar indicadores"
            icon="pi pi-arrow-right"
            iconPos="right"
            @click="router.push('/indicadores')"
          />
          <RouterLink class="home-hero__guide" to="/acerca">
            ¿Cómo leer los indicadores?
          </RouterLink>
        </div>
      </div>
    </section>

    <section class="metric-grid" aria-label="Resumen de indicadores">
      <article class="surface-card metric-card metric-card--primary">
        <span class="metric-card__label">
          Indicadores en el catálogo PVD
          <i
            class="pi pi-info-circle info-hint info-hint--light"
            tabindex="0"
            aria-label="Total de indicadores incluidos en el Plan Veracruzano de Desarrollo 2025–2030"
            v-tooltip.top="'Total de indicadores definidos en el Plan Veracruzano de Desarrollo 2025–2030.'"
          ></i>
        </span>
        <strong>{{ CATALOGO_TOTAL_INDICADORES }}</strong>
        <span class="metric-card__detail">
          {{ data.resumen.totalIndicadores }} prioritarios en esta etapa
        </span>
      </article>

      <article class="surface-card metric-card">
        <span class="metric-card__label">
          Con serie histórica
          <i
            class="pi pi-info-circle info-hint"
            tabindex="0"
            :aria-label="GLOSSARY_BY_KEY.conSerieHistorica.definition"
            v-tooltip.top="GLOSSARY_BY_KEY.conSerieHistorica.definition"
          ></i>
        </span>
        <strong>{{ data.resumen.indicadoresConHistorico }}</strong>
        <span class="metric-card__detail metric-card__detail--positive">Listos para consultar</span>
      </article>

      <article class="surface-card metric-card">
        <span class="metric-card__label">
          En integración
          <i
            class="pi pi-info-circle info-hint"
            tabindex="0"
            :aria-label="GLOSSARY_BY_KEY.enIntegracion.definition"
            v-tooltip.top="GLOSSARY_BY_KEY.enIntegracion.definition"
          ></i>
        </span>
        <strong>{{ data.resumen.indicadoresSinHistorico }}</strong>
        <span class="metric-card__detail">Fuente localizada, datos en preparación</span>
      </article>

      <article class="surface-card metric-card">
        <span class="metric-card__label">
          Periodo cubierto
          <i
            class="pi pi-info-circle info-hint"
            tabindex="0"
            :aria-label="GLOSSARY_BY_KEY.serieHistorica.definition"
            v-tooltip.top="GLOSSARY_BY_KEY.serieHistorica.definition"
          ></i>
        </span>
        <strong>{{ firstPeriod }}–{{ lastPeriod }}</strong>
        <span class="metric-card__detail">{{ data.resumen.periodosHistoricos.length }} años con datos</span>
      </article>
    </section>

    <section class="surface-card content-panel">
      <div class="content-panel__header">
        <div>
          <span class="section-kicker">EXPLORA LA INFORMACIÓN</span>
          <h2>Un punto de partida para el análisis</h2>
        </div>
      </div>

      <div class="explore-grid">
        <RouterLink class="explore-card" to="/indicadores">
          <div class="explore-card__body">
            <h3>Catálogo de indicadores</h3>
            <p>Busca por clave, nombre o eje rector y descarga los datos.</p>
          </div>
          <div class="explore-card__icon explore-card__icon--primary" aria-hidden="true">
            <i class="pi pi-list"></i>
          </div>
        </RouterLink>

        <RouterLink class="explore-card" to="/indicadores?estado=procesado">
          <div class="explore-card__body">
            <h3>Indicadores con serie histórica</h3>
            <p>Consulta la evolución disponible para cada indicador de Veracruz.</p>
          </div>
          <div class="explore-card__icon explore-card__icon--detail" aria-hidden="true">
            <i class="pi pi-chart-line"></i>
          </div>
        </RouterLink>

        <RouterLink class="explore-card" to="/fuentes">
          <div class="explore-card__body">
            <h3>Fuentes de información</h3>
            <p>Conoce el origen y la cobertura de cada dato publicado.</p>
          </div>
          <div class="explore-card__icon explore-card__icon--secondary" aria-hidden="true">
            <i class="pi pi-database"></i>
          </div>
        </RouterLink>
      </div>
    </section>

    <section class="surface-card coverage-panel">
      <div class="coverage-panel__heading">
        <div>
          <span class="section-kicker">ESTADO DE COBERTURA</span>
          <h2>Avance de integración de datos</h2>
          <p>Indicadores con una serie histórica lista para consulta en Veracruz.</p>
        </div>
        <strong>{{ coveragePercent }}<small>%</small></strong>
      </div>

      <ProgressBar
        :value="coveragePercent"
        :showValue="false"
        aria-label="Porcentaje de indicadores con serie histórica"
      />

      <div class="coverage-panel__legend">
        <span>
          <i class="legend-dot legend-dot--ready" aria-hidden="true"></i>
          {{ data.resumen.indicadoresConHistorico }} con serie histórica
        </span>
        <span>
          <i class="legend-dot legend-dot--pending" aria-hidden="true"></i>
          {{ data.resumen.indicadoresSinHistorico }} en integración
        </span>
      </div>
    </section>
  </div>
</template>
