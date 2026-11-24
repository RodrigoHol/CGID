<script setup lang="ts">
import { useRoute } from 'vue-router'
import logoHorizontal from '../../assets/logo-iap-horizontal.png'

const route = useRoute()

const navItems = [
  { to: '/', label: 'Inicio', isActive: (path: string) => path === '/' },
  { to: '/indicadores', label: 'Indicadores', isActive: (path: string) => path.startsWith('/indicadores') },
  { to: '/fuentes', label: 'Fuentes y cobertura', isActive: (path: string) => path === '/fuentes' },
  { to: '/acerca', label: 'Metodología y ayuda', isActive: (path: string) => path === '/acerca' },
]
</script>

<template>
  <header class="app-navigation">
    <RouterLink class="app-navigation__brand" to="/" aria-label="Ir al inicio del Catálogo de Indicadores PVD">
      <span class="app-navigation__logo">
        <img :src="logoHorizontal" alt="Instituto de Administración Pública de Veracruz" />
      </span>
      <span class="app-navigation__brand-text">
        <strong>CGID</strong>
        <small>Veracruz 2025–2030</small>
      </span>
    </RouterLink>

    <nav aria-label="Navegación principal">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :class="{ 'is-active': item.isActive(route.path) }"
        :aria-current="item.isActive(route.path) ? 'page' : undefined"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
  </header>
</template>
