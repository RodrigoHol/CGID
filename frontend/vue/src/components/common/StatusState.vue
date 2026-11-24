<script setup lang="ts">
defineProps<{
  type: 'loading' | 'error' | 'empty'
  title: string
  message: string
}>()
</script>

<template>
  <section
    class="status-state"
    :class="`status-state--${type}`"
    :role="type === 'error' ? 'alert' : 'status'"
  >
    <div class="status-state__icon" aria-hidden="true">
      <i v-if="type === 'loading'" class="pi pi-spin pi-spinner"></i>
      <i v-else-if="type === 'error'" class="pi pi-exclamation-triangle"></i>
      <i v-else class="pi pi-inbox"></i>
    </div>
    <div class="status-state__body">
      <h2>{{ title }}</h2>
      <p>{{ message }}</p>
      <div v-if="$slots.actions" class="status-state__actions">
        <slot name="actions" />
      </div>
    </div>
  </section>
</template>
