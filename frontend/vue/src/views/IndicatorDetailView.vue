<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HistoricalChart from '../components/indicators/HistoricalChart.vue'
import { loadFrontendData } from '../services/data.service'

const route = useRoute()
const router = useRouter()
const data = loadFrontendData()
const indicator = computed(() => data.indicadores.find((item) => item.id === route.params.id))
const series = computed(() => indicator.value ? data.historicos[indicator.value.id]?.datos ?? [] : [])
const source = computed(() => indicator.value ? data.fuentes.find((item) => item.idIndicador === indicator.value?.id) : undefined)
const latest = computed(() => series.value.at(-1))
const first = computed(() => series.value[0])
const variation = computed(() => latest.value && first.value ? latest.value.valor - first.value.valor : null)
const variationLabel = computed(() => variation.value === null ? 'Sin histórico' : `${variation.value > 0 ? '+' : ''}${variation.value.toFixed(4)} puntos`)

function formatValue(value: number | null | undefined) {
  return value === null || value === undefined ? '—' : `${value.toLocaleString('es-MX', { maximumFractionDigits: 4 })}${indicator.value?.unidadMedida ? ` ${indicator.value.unidadMedida}` : ''}`
}
</script>

<template>
  <main v-if="indicator" class="detail-page">
    <button class="back-link" @click="router.push('/indicadores')">← Volver al catálogo</button>
    <section class="detail-hero">
      <div>
        <span class="detail-kicker">{{ indicator.clave }}</span>
        <h1>{{ indicator.nombre }}</h1>
        <p>{{ indicator.descripcion }}</p>
      </div>
      <span class="detail-status" :class="`detail-status--${indicator.estadoHistorico}`">
        {{ indicator.tieneHistorico ? 'Histórico disponible' : 'Fuente identificada' }}
      </span>
    </section>

    <section class="detail-metrics">
      <article><span>Línea base</span><strong>{{ formatValue(indicator.lineaBase.valor) }}</strong><small>{{ indicator.lineaBase.anio || 'No disponible' }}</small></article>
      <article><span>Meta 2030</span><strong>{{ formatValue(indicator.meta2030) }}</strong><small>Objetivo del PVD</small></article>
      <article><span>Último valor</span><strong>{{ latest ? formatValue(latest.valor) : '—' }}</strong><small>{{ latest?.anio || 'Sin periodo' }}</small></article>
      <article><span>Variación observada</span><strong :class="{ 'metric-negative': variation !== null && variation < 0, 'metric-positive': variation !== null && variation > 0 }">{{ variationLabel }}</strong><small>{{ first?.anio || '—' }} a {{ latest?.anio || '—' }}</small></article>
    </section>

    <section class="detail-card detail-chart-card">
      <div class="detail-card__header">
        <div><span class="detail-kicker">EVOLUCIÓN HISTÓRICA</span><h2>Serie disponible para {{ data.resumen.entidad }}</h2></div>
        <span class="unit-label">{{ indicator.unidadMedida || 'Valor del indicador' }}</span>
      </div>
      <HistoricalChart :points="series" :baseline="indicator.lineaBase" :target="indicator.meta2030" :direction="indicator.sentido" />
    </section>

    <div class="detail-columns">
      <section class="detail-card">
        <div class="detail-card__header"><div><span class="detail-kicker">OBSERVACIONES</span><h2>Datos publicados</h2></div></div>
        <div class="observation-table">
          <div class="observation-table__head"><span>Periodo</span><span>Valor</span></div>
          <div v-for="point in [...series].reverse()" :key="point.anio" class="observation-row"><strong>{{ point.anio }}</strong><span>{{ formatValue(point.valor) }}</span></div>
        </div>
      </section>
      <section class="detail-card detail-facts">
        <div class="detail-card__header"><div><span class="detail-kicker">FICHA TÉCNICA</span><h2>Interpretación</h2></div></div>
        <dl>
          <div><dt>Sentido</dt><dd>{{ indicator.sentido || 'No especificado' }}</dd></div>
          <div><dt>Eje rector</dt><dd>{{ indicator.ejeRector || 'No especificado' }}</dd></div>
          <div><dt>Entidad</dt><dd>{{ data.resumen.entidad }}</dd></div>
          <div><dt>Fórmula</dt><dd>{{ indicator.formula || 'No especificada' }}</dd></div>
        </dl>
      </section>
    </div>

    <section class="detail-card detail-source">
      <div class="detail-card__header"><div><span class="detail-kicker">PROCEDENCIA</span><h2>Fuente de información</h2></div></div>
      <div class="source-detail">
        <div><strong>{{ source?.institucion || 'Fuente identificada' }}</strong><p>{{ source?.nombre || indicator.fuente.medioVerificacion }}</p><small>{{ source?.observaciones || indicator.fuente.observaciones }}</small></div>
        <a :href="source?.url || indicator.fuente.url" target="_blank" rel="noreferrer">Consultar fuente ↗</a>
      </div>
    </section>
  </main>
  <main v-else class="detail-not-found"><h1>Indicador no encontrado</h1><button @click="router.push('/indicadores')">Volver al catálogo</button></main>
</template>

<style scoped>
.detail-page { max-width: 1188px; margin: 0 auto; padding: 0 46px 55px; }
.back-link { margin: 0 0 18px; padding: 0; border: 0; color: #7a1737; background: none; cursor: pointer; font-size: 14px; font-weight: 700; }
.detail-hero { display: flex; align-items: flex-start; justify-content: space-between; gap: 25px; padding: 28px 32px; border-left: 5px solid #b28854; background: #fff; box-shadow: 0 8px 24px #422a3012; }
.detail-kicker { display: block; margin-bottom: 8px; color: #7a1737; font-size: 11px; font-weight: 700; letter-spacing: .1em; }
.detail-hero h1 { max-width: 850px; margin: 0; color: #292929; font-size: clamp(24px, 3vw, 33px); font-weight: 500; line-height: 1.2; }
.detail-hero p { max-width: 860px; margin: 13px 0 0; color: #646464; font-size: 14px; line-height: 1.6; }
.detail-status { flex: 0 0 auto; padding: 8px 11px; border-radius: 99px; color: #7a1737; background: #f5e9ed; font-size: 12px; font-weight: 700; }
.detail-status--procesado { color: #267c78; background: #e5f3f1; }
.detail-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 18px 0; }
.detail-metrics article { min-height: 114px; padding: 18px; border: 1px solid #e1e1e1; background: #fff; }
.detail-metrics span, .detail-metrics small { display: block; color: #6e6e6e; font-size: 12px; }
.detail-metrics strong { display: block; margin: 12px 0 4px; color: #7a1737; font-size: 25px; font-weight: 500; }
.detail-metrics small { color: #999; }
.metric-positive { color: #267c78 !important; }
.metric-negative { color: #b28854 !important; }
.detail-card { margin-bottom: 18px; padding: 25px; border: 1px solid #e1e1e1; background: #fff; box-shadow: 0 8px 24px #422a3008; }
.detail-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; margin-bottom: 19px; }
.detail-card h2 { margin: 0; color: #292929; font-size: 20px; font-weight: 500; }
.unit-label { padding: 7px 10px; color: #7a1737; background: #f5e9ed; font-size: 12px; }
.detail-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.observation-table__head, .observation-row { display: grid; grid-template-columns: 1fr 1fr; padding: 12px 9px; border-bottom: 1px solid #eee; font-size: 13px; }
.observation-table__head { color: #6e6e6e; font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
.observation-row span { color: #7a1737; font-weight: 700; }
.detail-facts dl { margin: 0; }
.detail-facts dl div { display: grid; grid-template-columns: 105px 1fr; gap: 12px; padding: 10px 0; border-bottom: 1px solid #eee; }
.detail-facts dt { color: #6e6e6e; font-size: 12px; }
.detail-facts dd { margin: 0; color: #292929; font-size: 13px; }
.source-detail { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 17px; background: #faf8f8; }
.source-detail strong { color: #7a1737; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; }
.source-detail p { margin: 7px 0; color: #292929; font-size: 14px; }
.source-detail small { color: #6e6e6e; font-size: 12px; }
.source-detail a { flex: 0 0 auto; padding: 10px 13px; border: 1px solid #b28854; color: #7a1737; font-size: 13px; font-weight: 700; text-decoration: none; }
.detail-not-found { padding: 70px 46px; text-align: center; }
.detail-not-found button { padding: 10px 14px; border: 0; color: #fff; background: #7a1737; cursor: pointer; }
@media (max-width: 800px) { .detail-page { padding: 0 20px 35px; } .detail-hero { flex-direction: column; padding: 23px; } .detail-metrics { grid-template-columns: repeat(2, 1fr); } .detail-columns { grid-template-columns: 1fr; } }
@media (max-width: 450px) { .detail-metrics { grid-template-columns: 1fr; } .detail-card { padding: 19px; } .source-detail { align-items: flex-start; flex-direction: column; } }
</style>
