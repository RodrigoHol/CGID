<script setup lang="ts">
import { computed } from 'vue'
import type { FrontendData } from '../types/contract'

const props = defineProps<{ data: FrontendData }>()
const emit = defineEmits<{ navigate: [view: 'indicadores' | 'fuentes'] }>()

const coveragePercent = computed(() => {
  if (!props.data.resumen.totalIndicadores) return 0
  return Math.round(
    (props.data.resumen.indicadoresConHistorico / props.data.resumen.totalIndicadores) * 100,
  )
})
</script>

<template>
  <div class="home-view">
    <section class="home-hero">
      <div class="home-hero__content">
        <span class="home-hero__label">CATÁLOGO GENERAL DE INDICADORES DE DESEMPEÑO</span>
        <h2>Datos para comprender el desarrollo de Veracruz</h2>
        <p>Consulta, compara y da seguimiento a los indicadores del Plan Veracruzano de Desarrollo 2025–2030.</p>
        <button class="home-hero__action" type="button" @click="emit('navigate', 'indicadores')">
          Explorar indicadores <span aria-hidden="true">→</span>
        </button>
      </div>
      <div class="home-hero__seal" aria-label="Plan Veracruzano de Desarrollo 2025-2030">PVD<small>25—30</small></div>
    </section>

    <section class="intro-panel">
      <div class="intro-panel__heading">
        <span class="section-kicker">¿QUÉ ES ESTE CATÁLOGO?</span>
        <h2>Información pública para dar seguimiento a los resultados</h2>
      </div>
      <div class="intro-panel__copy">
        <p>El Catálogo General de Indicadores de Desempeño reúne las fichas técnicas de los indicadores seleccionados para dar seguimiento y evaluar el cumplimiento de los objetivos, estrategias y metas del Plan Veracruzano de Desarrollo (PVD) 2025–2030.</p>
        <p>Consulta definiciones, metas, fuentes y series históricas para comparar avances, fortalecer la rendición de cuentas y apoyar decisiones basadas en evidencia para el bienestar de las y los veracruzanos.</p>
      </div>
    </section>

    <section class="metric-grid" aria-label="Resumen de indicadores">
      <article class="metric-card metric-card--primary"><span class="metric-card__label">Indicadores de Desarrollo</span><strong>{{ 148 }}</strong><span class="metric-card__detail"></span></article>
      <article class="metric-card"><span class="metric-card__label">Con histórico</span><strong>{{ data.resumen.indicadoresConHistorico }}</strong><span class="metric-card__detail metric-card__detail--positive">Series listas para consulta</span></article>
      <article class="metric-card"><span class="metric-card__label">Fuentes identificadas</span><strong>{{ data.resumen.porEstadoHistorico.fuente_identificada || 0 }}</strong><span class="metric-card__detail">Pendientes de extracción</span></article>
      <article class="metric-card"><span class="metric-card__label">Periodos disponibles</span><strong>{{ data.resumen.periodosHistoricos.length }}</strong><span class="metric-card__detail">{{ data.resumen.periodosHistoricos[0] }}–{{ data.resumen.periodosHistoricos.at(-1) }}</span></article>
    </section>

    <section class="content-panel">
      <div class="content-panel__header">
        <div><span class="section-kicker">EXPLORA LA INFORMACIÓN</span><h2>Un punto de partida para el análisis</h2></div>
        <button class="outline-button" type="button" @click="emit('navigate', 'indicadores')">Ver indicadores <span>→</span></button>
      </div>
      <div class="preview-grid">
        <button class="preview-card" type="button" @click="emit('navigate', 'indicadores')"><div><h3>Catálogo técnico</h3><p>Busca por clave, nombre, eje rector o disponibilidad histórica.</p></div><div class="preview-card__icon preview-card__icon--blue"><span class="material-symbols-outlined" aria-hidden="true">view_list</span></div></button>
        <button class="preview-card" type="button" @click="emit('navigate', 'indicadores')"><div><h3>Series históricas</h3><p>Consulta la evolución disponible para cada indicador de Veracruz.</p></div><div class="preview-card__icon preview-card__icon--teal"><span class="material-symbols-outlined" aria-hidden="true">history</span></div></button>
        <button class="preview-card" type="button" @click="emit('navigate', 'fuentes')"><div><h3>Fuentes trazables</h3><p>Conoce el origen y la cobertura de cada dato publicado.</p></div><div class="preview-card__icon preview-card__icon--gold"><span class="material-symbols-outlined" aria-hidden="true">monitoring</span></div></button>
      </div>
    </section>

    <section class="coverage-panel">
      <div class="coverage-panel__heading"><div><span class="section-kicker">ESTADO DE COBERTURA</span><h2>Avance de integración de datos</h2><p>Indicadores con una serie histórica lista para consulta en Veracruz.</p></div><strong>{{ coveragePercent }}<small>%</small></strong></div>
      <div class="coverage-bar" aria-label="Porcentaje de indicadores con histórico"><span :style="{ width: `${coveragePercent}%` }"></span></div>
      <div class="coverage-panel__legend"><span><i class="legend-dot legend-dot--ready"></i>{{ data.resumen.indicadoresConHistorico }} procesados</span><span><i class="legend-dot legend-dot--pending"></i>{{ data.resumen.indicadoresSinHistorico }} con fuente identificada</span></div>
    </section>
  </div>
</template>

<style scoped>
.home-hero { display: flex; align-items: center; justify-content: space-between; min-height: 330px; margin-bottom: 18px; padding: 48px 52px; overflow: hidden; color: #292929; background: #fff; box-shadow: 0 15px 34px #422a3020; }
.home-hero__content { max-width: 700px; }
.home-hero__label { display: block; margin-bottom: 13px; color: #7a1737; font-size: 11px; font-weight: 800; letter-spacing: .13em; }
.home-hero h2 { max-width: 680px; margin: 0; font-size: clamp(29px, 4vw, 48px); font-weight: 500; letter-spacing: -.045em; line-height: 1.05; }
.home-hero p { max-width: 610px; margin: 18px 0 23px; color: #646464; font-size: 16px; line-height: 1.55; }
.home-hero__action { padding: 12px 17px; border: 1px solid #fff8; border-radius: 4px; color: #7a1737; background: #fff; cursor: pointer; font-size: 13px; font-weight: 700; }
.home-hero__action span { margin-left: 8px; color: #b28854; font-size: 17px; }
.home-hero__seal { width: 108px; height: 108px; display: grid; place-content: center; flex: 0 0 108px; border: 1px solid #b28854; border-radius: 50%; color: #7a1737; text-align: center; font-size: 28px; font-weight: 800; line-height: .8; transform: rotate(-8deg); }
.home-hero__seal small { margin-top: 9px; color: #b28854; font-size: 11px; letter-spacing: .12em; }
.preview-card { width: 100%; border: 0; color: inherit; text-align: left; cursor: pointer; }
.preview-card:hover { border-color: #caaabb; box-shadow: 0 5px 16px #7a173712; }
@media (max-width: 720px) { .home-hero { min-height: 370px; padding: 34px 25px; } .home-hero__seal { display: none; } }
</style>
