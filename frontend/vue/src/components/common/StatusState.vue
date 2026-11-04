<script setup lang="ts">
defineProps<{
  type: 'loading' | 'error' | 'empty'
  title: string
  message: string
}>()
</script>

<template>
  <section class="status-state" :class="`status-state--${type}`" role="status">
    <div class="status-state__icon" aria-hidden="true">
      <span v-if="type === 'loading'" class="spinner"></span>
      <span v-else-if="type === 'error'">!</span>
      <span v-else>⌁</span>
    </div>
    <div>
      <h2>{{ title }}</h2>
      <p>{{ message }}</p>
    </div>
  </section>
</template>
