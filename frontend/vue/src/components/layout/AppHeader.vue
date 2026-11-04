<script setup lang="ts">
defineProps<{ title: string; subtitle: string }>()
</script>

<template>
  <header class="topbar">
    <div>
      <p class="topbar__eyebrow">CGID · Plan Veracruzano de Desarrollo</p>
      <h1>{{ title }}</h1>
      <p class="topbar__subtitle">{{ subtitle }}</p>
    </div>
    <div class="topbar__context">
      <span class="context-dot"></span>
      <span>Datos de Veracruz</span>
    </div>
  </header>
</template>
