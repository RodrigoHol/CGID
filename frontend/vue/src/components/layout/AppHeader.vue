<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Breadcrumb from 'primevue/breadcrumb'
import { useFrontendData } from '../../composables/useFrontendData'
import { formatDate } from '../../utils/labels'

const props = defineProps<{ title: string; subtitle: string }>()
const route = useRoute()
const data = useFrontendData()

const updatedLabel = computed(() => formatDate(data.resumen.fechaActualizacion))
const showBreadcrumb = computed(() => route.path !== '/')
const home = { icon: 'pi pi-home', route: '/', label: 'Inicio' }
const items = computed(() => [{ label: props.title }])
</script>

<template>
  <header class="topbar">
    <div class="topbar__main">
      <Breadcrumb v-if="showBreadcrumb" :home="home" :model="items" class="topbar__breadcrumb">
        <template #item="{ item }">
          <RouterLink v-if="item.route" :to="item.route" class="p-breadcrumb-item-link">
            <i v-if="item.icon" :class="item.icon" aria-hidden="true"></i>
            <span>{{ item.label }}</span>
          </RouterLink>
          <span v-else class="p-breadcrumb-item-link p-breadcrumb-item-link--current" aria-current="page">
            {{ item.label }}
          </span>
        </template>
      </Breadcrumb>
      <p class="topbar__eyebrow">Plan Veracruzano de Desarrollo 2025–2030</p>
      <h1>{{ title }}</h1>
      <p class="topbar__subtitle">{{ subtitle }}</p>
    </div>

    <div v-if="updatedLabel" class="topbar__updated">
      <i class="pi pi-calendar" aria-hidden="true"></i>
      <span>Datos actualizados al {{ updatedLabel }}</span>
    </div>
  </header>
</template>
