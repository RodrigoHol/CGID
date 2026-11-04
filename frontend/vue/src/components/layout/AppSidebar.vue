<script setup lang="ts">
defineProps<{ active: 'dashboard' | 'indicadores' | 'fuentes' }>()
defineEmits<{ navigate: [view: 'dashboard' | 'indicadores' | 'fuentes'] }>()
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand__mark">P</div>
      <div>
        <strong>CGID Veracruz</strong>
        <span>Veracruz 2025–2030</span>
      </div>
    </div>

    <nav class="sidebar__nav" aria-label="Navegación principal">
      <button :class="{ active: active === 'dashboard' }" @click="$emit('navigate', 'dashboard')">
        <span class="nav-icon">⌂</span>        <span>Inicio</span>
      </button>
      <button :class="{ active: active === 'indicadores' }" @click="$emit('navigate', 'indicadores')">
        <span class="nav-icon">▦</span><span>Indicadores</span>
      </button>
      <button :class="{ active: active === 'fuentes' }" @click="$emit('navigate', 'fuentes')">
        <span class="nav-icon">↗</span><span>Fuentes y cobertura</span>
      </button>
    </nav>

    <div class="sidebar__footer">
      <div class="sidebar__footer-icon">i</div>
      <div>
        <strong>MVP en construcción</strong>
        <span>15 indicadores prioritarios</span>
      </div>
    </div>
  </aside>
</template>
