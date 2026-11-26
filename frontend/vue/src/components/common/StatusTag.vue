<script setup lang="ts">
import { computed } from 'vue'
import Tag from 'primevue/tag'
import type { HistoricalStatus } from '../../types/contract'
import { statusInfo } from '../../utils/labels'
import AppIcon from './AppIcon.vue'

const props = defineProps<{
  estado: HistoricalStatus | string
}>()

const info = computed(() => statusInfo(props.estado))
</script>

<template>
  <Tag :value="info.label" :class="['status-tag', info.cls]">
    <template #icon>
      <span class="sem-dot" aria-hidden="true"></span>
      <AppIcon :name="info.icon" size="xs" />
    </template>
  </Tag>
</template>
