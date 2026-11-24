<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import StatusState from '../components/common/StatusState.vue'

const router = useRouter()
</script>

<template>
  <section class="not-found-page">
    <div class="surface-card">
      <StatusState
        type="empty"
        title="Página no encontrada"
        message="La dirección solicitada no existe o no forma parte de este catálogo."
      >
        <template #actions>
          <Button label="Ir al inicio" icon="pi pi-home" @click="router.push('/')" />
          <Button label="Ver indicadores" icon="pi pi-list" severity="secondary" outlined @click="router.push('/indicadores')" />
        </template>
      </StatusState>
    </div>
  </section>
</template>
