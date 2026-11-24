<script setup lang="ts">
import { computed } from 'vue'
import Tag from 'primevue/tag'
import type { HistoricalStatus } from '../../types/contract'
import { statusInfo } from '../../utils/labels'

const props = defineProps<{
  estado: HistoricalStatus | string
}>()

const info = computed(() => statusInfo(props.estado))
</script>

<template>
  <Tag :value="info.label" :icon="info.icon" :class="['status-tag', info.cls]" />
</template>
