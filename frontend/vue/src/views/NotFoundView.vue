<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import AppIcon from '../components/common/AppIcon.vue'
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
          <Button label="Ir al inicio" @click="router.push('/')">
            <template #icon>
              <AppIcon name="home" size="sm" />
            </template>
          </Button>
          <Button label="Ver indicadores" severity="secondary" outlined @click="router.push('/indicadores')">
            <template #icon>
              <AppIcon name="monitoring" size="sm" />
            </template>
          </Button>
        </template>
      </StatusState>
    </div>
  </section>
</template>
