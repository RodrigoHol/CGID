<script setup lang="ts">
import AppIcon from './AppIcon.vue'

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
      <AppIcon v-if="type === 'loading'" name="progress_activity" size="lg" spin />
      <AppIcon v-else-if="type === 'error'" name="error_outline" size="lg" />
      <AppIcon v-else name="inbox" size="lg" />
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
