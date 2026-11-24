<script setup lang="ts">
import { computed } from 'vue'
import Accordion from 'primevue/accordion'
import AccordionContent from 'primevue/accordioncontent'
import AccordionHeader from 'primevue/accordionheader'
import AccordionPanel from 'primevue/accordionpanel'
import StatusTag from '../components/common/StatusTag.vue'
import { useFrontendData } from '../composables/useFrontendData'
import { INSTITUCION } from '../config/site'
import { GLOSSARY_TERMS } from '../utils/glossary'

const data = useFrontendData()

const institutions = computed(() =>
  Array.from(new Set(data.fuentes.map((item) => item.institucion).filter(Boolean))),
)
</script>

<template>
  <div class="about-page">
    <section class="surface-card content-panel">
      <span class="section-kicker">PROPÓSITO DEL CATÁLOGO</span>
      <h2>¿Qué es este catálogo?</h2>
      <p>
        El Catálogo General de Indicadores de Desempeño reúne las fichas técnicas de los
        indicadores seleccionados para dar seguimiento y evaluar el cumplimiento de los
        objetivos, estrategias y metas del Plan Veracruzano de Desarrollo (PVD) 2025–2030.
      </p>
      <p>
        Consulta definiciones, metas, fuentes y series históricas para comparar avances,
        fortalecer la rendición de cuentas y apoyar decisiones basadas en evidencia para el
        bienestar de las y los veracruzanos.
      </p>
    </section>

    <section class="surface-card content-panel">
      <span class="section-kicker">GLOSARIO Y CONCEPTOS</span>
      <h2>Cómo leer un indicador</h2>
      <Accordion :value="['lineaBase']" multiple class="glossary-accordion">
        <AccordionPanel v-for="item in GLOSSARY_TERMS" :key="item.key" :value="item.key">
          <AccordionHeader>{{ item.term }}</AccordionHeader>
          <AccordionContent>
            <p class="glossary-definition">{{ item.definition }}</p>
          </AccordionContent>
        </AccordionPanel>
      </Accordion>
    </section>

    <section class="surface-card content-panel">
      <span class="section-kicker">DISPONIBILIDAD</span>
      <h2>Estado de los datos</h2>
      <div class="status-guide-grid">
        <article class="status-guide-item">
          <StatusTag estado="procesado" />
          <p>
            Indicadores cuya serie histórica oficial ya fue extraída, validada e integrada al
            catálogo para su consulta gráfica, tabla de observaciones y descarga en CSV.
          </p>
        </article>
        <article class="status-guide-item">
          <StatusTag estado="fuente_identificada" />
          <p>
            Indicadores cuya ficha técnica y fuente oficial ya están documentadas, mientras los
            datos históricos se encuentran en proceso de extracción e integración.
          </p>
        </article>
      </div>
    </section>

    <section class="surface-card content-panel">
      <span class="section-kicker">CRITERIOS TÉCNICOS</span>
      <h2>Fuentes y criterios</h2>
      <p>
        Las series publicadas provienen directamente de tabulados y reportes oficiales de
        {{ institutions.join(' y ') }} para {{ data.resumen.entidad }}.
      </p>
      <p>
        Las gráficas muestran solo periodos publicados; no se interpolan años faltantes.
      </p>
    </section>

    <section class="surface-card content-panel">
      <span class="section-kicker">ATENCIÓN</span>
      <h2>Contacto</h2>
      <p>
        Para dudas o comentarios sobre el catálogo, contacta al {{ INSTITUCION }}.
      </p>
      <!-- TODO: agregar correo, teléfono, dirección y aviso de privacidad oficiales -->
    </section>
  </div>
</template>
