<script setup lang="ts">
import { computed } from 'vue'
import logoHorizontal from '../../assets/logo-iap-horizontal.png'
import { useFrontendData } from '../../composables/useFrontendData'
import { INSTITUCION } from '../../config/site'
import { formatDate } from '../../utils/labels'

const data = useFrontendData()
const updatedLabel = computed(() => formatDate(data.resumen.fechaActualizacion))
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="app-footer">
    <div class="app-footer__inner">
      <div class="app-footer__brand">
        <div class="app-footer__logo-plate">
          <img class="app-footer__logo" :src="logoHorizontal" alt="Instituto de Administración Pública de Veracruz" />
        </div>
        <p class="app-footer__description">
          Catálogo General de Indicadores de Desempeño · Plan Veracruzano de Desarrollo 2025–2030
        </p>
      </div>

      <nav class="app-footer__nav" aria-label="Enlaces del sitio">
        <RouterLink to="/">Inicio</RouterLink>
        <RouterLink to="/indicadores">Indicadores</RouterLink>
        <RouterLink to="/fuentes">Fuentes y cobertura</RouterLink>
        <RouterLink to="/acerca">Metodología y ayuda</RouterLink>
      </nav>

      <div class="app-footer__meta">
        <p v-if="updatedLabel">Datos actualizados al {{ updatedLabel }}</p>
        <p>© {{ currentYear }} {{ INSTITUCION }}</p>
        <!-- TODO: contacto oficial y aviso de privacidad -->
      </div>
    </div>
  </footer>
</template>
