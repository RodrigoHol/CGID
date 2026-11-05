<script setup lang="ts">
defineProps<{ active: 'dashboard' | 'indicadores' | 'fuentes' }>()
defineEmits<{ navigate: [view: 'dashboard' | 'indicadores' | 'fuentes'] }>()
</script>

<template>
  <header class="app-navigation">
    <button class="app-navigation__brand" type="button" @click="$emit('navigate', 'dashboard')">
      <span class="app-navigation__mark">CG</span>
      <span><strong>CGID</strong><small>Veracruz 2025–2030</small></span>
    </button>
    <nav aria-label="Navegación principal">
      <button :class="{ active: active === 'dashboard' }" type="button" @click="$emit('navigate', 'dashboard')">Inicio</button>
      <button :class="{ active: active === 'indicadores' }" type="button" @click="$emit('navigate', 'indicadores')">Indicadores</button>
      <button :class="{ active: active === 'fuentes' }" type="button" @click="$emit('navigate', 'fuentes')">Fuentes y cobertura</button>
    </nav>
    <span class="app-navigation__context"><i></i> Veracruz</span>
  </header>
</template>
