<script setup lang="ts">
import { useRoute } from 'vue-router'
import logoMark from '../../assets/logo-iap.png'
import AppIcon from '../common/AppIcon.vue'

const props = defineProps<{
  collapsed: boolean
  mobileOpen: boolean
}>()

const emit = defineEmits<{
  toggleCollapse: []
  closeMobile: []
}>()

const route = useRoute()

const primaryNav = [
  {
    to: '/',
    label: 'Inicio',
    icon: 'dashboard',
    isActive: (path: string) => path === '/',
  },
  {
    to: '/indicadores',
    label: 'Indicadores',
    icon: 'monitoring',
    isActive: (path: string) => path.startsWith('/indicadores'),
  },
  {
    to: '/fuentes',
    label: 'Fuentes y cobertura',
    icon: 'database',
    isActive: (path: string) => path === '/fuentes',
  },
]

const supportNav = {
  to: '/acerca',
  label: 'Metodología y ayuda',
  icon: 'menu_book',
  isActive: (path: string) => path === '/acerca',
}
</script>

<template>
  <div
    v-if="props.mobileOpen"
    class="sidebar-backdrop"
    aria-hidden="true"
    @click="emit('closeMobile')"
  ></div>

  <aside
    class="app-sidebar"
    :class="{
      'app-sidebar--collapsed': props.collapsed,
      'app-sidebar--mobile-open': props.mobileOpen,
    }"
    aria-label="Barra lateral de navegación"
  >
    <div class="app-sidebar__top">
      <RouterLink
        class="sidebar-brand"
        to="/"
        aria-label="Ir al inicio del Catálogo de Indicadores PVD"
        v-tooltip.right="props.collapsed ? 'CGID · IAP Veracruz' : undefined"
      >
        <span class="sidebar-brand__logo">
          <img :src="logoMark" alt="IAP Veracruz" />
        </span>
        <span v-if="!props.collapsed" class="sidebar-brand__text">
          <strong>CGID</strong>
          <small>Veracruz 2025–2030</small>
        </span>
      </RouterLink>

      <button
        type="button"
        class="sidebar-close-mobile"
        aria-label="Cerrar menú"
        @click="emit('closeMobile')"
      >
        <AppIcon name="close" size="md" />
      </button>
    </div>

    <nav class="sidebar-nav" aria-label="Navegación principal">
      <RouterLink
        v-for="item in primaryNav"
        :key="item.to"
        :to="item.to"
        class="sidebar-link"
        :class="{ 'is-active': item.isActive(route.path) }"
        :aria-current="item.isActive(route.path) ? 'page' : undefined"
        v-tooltip.right="props.collapsed ? item.label : undefined"
      >
        <AppIcon :name="item.icon" size="md" :filled="item.isActive(route.path)" />
        <span v-if="!props.collapsed" class="sidebar-link__label">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <RouterLink
        :to="supportNav.to"
        class="sidebar-link"
        :class="{ 'is-active': supportNav.isActive(route.path) }"
        :aria-current="supportNav.isActive(route.path) ? 'page' : undefined"
        v-tooltip.right="props.collapsed ? supportNav.label : undefined"
      >
        <AppIcon :name="supportNav.icon" size="md" :filled="supportNav.isActive(route.path)" />
        <span v-if="!props.collapsed" class="sidebar-link__label">{{ supportNav.label }}</span>
      </RouterLink>

      <button
        type="button"
        class="sidebar-collapse-btn"
        :aria-label="props.collapsed ? 'Expandir barra lateral' : 'Contraer barra lateral'"
        :aria-expanded="!props.collapsed"
        v-tooltip.right="props.collapsed ? 'Expandir menú' : undefined"
        @click="emit('toggleCollapse')"
      >
        <AppIcon :name="props.collapsed ? 'chevron_right' : 'chevron_left'" size="md" />
        <span v-if="!props.collapsed" class="sidebar-link__label">Contraer menú</span>
      </button>
    </div>
  </aside>
</template>
