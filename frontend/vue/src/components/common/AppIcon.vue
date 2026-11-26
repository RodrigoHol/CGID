<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    name: string
    filled?: boolean
    size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
    spin?: boolean
    label?: string
  }>(),
  {
    filled: false,
    size: 'md',
    spin: false,
    label: undefined,
  },
)
</script>

<template>
  <span
    class="material-symbols-rounded app-icon"
    :class="[
      `app-icon--${props.size}`,
      { 'app-icon--filled': props.filled, 'app-icon--spin': props.spin },
    ]"
    :aria-hidden="props.label ? undefined : 'true'"
    :aria-label="props.label"
    :role="props.label ? 'img' : undefined"
  >{{ props.name }}</span>
</template>
