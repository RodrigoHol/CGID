<script setup lang="ts">
import { computed, ref } from 'vue'
import Popover from 'primevue/popover'
import { GLOSSARY_BY_KEY } from '../../utils/glossary'
import AppIcon from './AppIcon.vue'

const props = withDefaults(
  defineProps<{
    termKey?: string
    title?: string
    text?: string
    size?: 'xs' | 'sm' | 'md'
  }>(),
  {
    termKey: undefined,
    title: undefined,
    text: undefined,
    size: 'sm',
  },
)

const popoverRef = ref<InstanceType<typeof Popover> | null>(null)
const isOpen = ref(false)

const resolvedTitle = computed(() => {
  if (props.title) return props.title
  if (props.termKey && GLOSSARY_BY_KEY[props.termKey]) {
    return GLOSSARY_BY_KEY[props.termKey].term
  }
  return 'Ayuda'
})

const resolvedText = computed(() => {
  if (props.text) return props.text
  if (props.termKey && GLOSSARY_BY_KEY[props.termKey]) {
    return GLOSSARY_BY_KEY[props.termKey].definition
  }
  return ''
})

function togglePopover(event: Event) {
  popoverRef.value?.toggle(event)
}
</script>

<template>
  <span class="help-hint-wrap">
    <button
      type="button"
      class="help-hint-btn"
      :aria-label="`Explicación de ${resolvedTitle}`"
      :aria-expanded="isOpen"
      aria-haspopup="dialog"
      v-tooltip.top="resolvedText"
      @click.prevent.stop="togglePopover"
    >
      <AppIcon name="help" :size="props.size" />
    </button>

    <Popover
      ref="popoverRef"
      class="help-popover"
      @show="isOpen = true"
      @hide="isOpen = false"
    >
      <div class="help-popover__body">
        <strong class="help-popover__title">{{ resolvedTitle }}</strong>
        <p class="help-popover__text">{{ resolvedText }}</p>
      </div>
    </Popover>
  </span>
</template>
