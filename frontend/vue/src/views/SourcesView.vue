<script setup lang="ts">
import type { FrontendData } from '../types/contract'

defineProps<{ data: FrontendData }>()
</script>

<template>
  <section class="content-panel">
    <div class="content-panel__header"><div><span class="section-kicker">TRAZABILIDAD</span><h2>Fuentes de los indicadores</h2></div><span class="table-caption">{{ data.fuentes.length }} fuentes registradas</span></div>
    <div class="source-list">
      <div class="source-table__header"><span>Fuente e institución</span><span>Entidad y cobertura</span><span>Acción</span></div>
      <article v-for="source in data.fuentes" :key="source.idIndicador" class="source-row">
        <div><strong>{{ source.institucion }}</strong><h3>{{ source.nombre }}</h3></div>
        <span class="source-row__coverage">{{ source.entidad }}<br />{{ source.periodos.length }} periodos disponibles</span>
        <a class="source-row__link" :href="source.url" target="_blank" rel="noreferrer">Consultar fuente <span>↗</span></a>
      </article>
    </div>
  </section>
</template>
