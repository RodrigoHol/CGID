<script setup lang="ts">
import { onErrorCaptured, ref } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import StatusState from './components/common/StatusState.vue'
import AppFooter from './components/layout/AppFooter.vue'
import AppHeader from './components/layout/AppHeader.vue'
import AppNavigation from './components/layout/AppNavigation.vue'

const route = useRoute()
const mainRef = ref<HTMLElement | null>(null)
const renderError = ref('')

onErrorCaptured((cause) => {
  renderError.value = cause instanceof Error
    ? cause.message
    : 'No fue posible mostrar esta sección del catálogo.'
  return false
})

function skipToContent() {
  mainRef.value?.focus()
  mainRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function reloadPage() {
  window.location.reload()
}
</script>

<template>
  <div class="app-shell">
    <a class="skip-link" href="#contenido" @click.prevent="skipToContent">Saltar al contenido</a>
    <AppNavigation />
    <div class="app-content">
      <AppHeader
        v-if="!route.meta.hideHeader"
        :title="route.meta.title ?? ''"
        :subtitle="route.meta.subtitle ?? ''"
      />
      <main
        id="contenido"
        ref="mainRef"
        tabindex="-1"
        class="page-content"
        :class="{ 'page-content--detail': route.meta.hideHeader }"
      >
        <StatusState
          v-if="renderError"
          type="error"
          title="Ocurrió un problema al mostrar la página"
          :message="renderError"
        >
          <template #actions>
            <Button label="Reintentar" icon="pi pi-refresh" @click="reloadPage" />
          </template>
        </StatusState>
        <RouterView v-else />
      </main>
    </div>
    <AppFooter />
  </div>
</template>
