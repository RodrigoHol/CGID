<script setup lang="ts">
import { onErrorCaptured, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import Toast from 'primevue/toast'
import AppIcon from './components/common/AppIcon.vue'
import StatusState from './components/common/StatusState.vue'
import AppFooter from './components/layout/AppFooter.vue'
import AppHeader from './components/layout/AppHeader.vue'
import AppNavigation from './components/layout/AppNavigation.vue'

const SIDEBAR_STORAGE_KEY = 'cgid:sidebar-collapsed'

const route = useRoute()
const mainRef = ref<HTMLElement | null>(null)
const renderError = ref('')
const sidebarCollapsed = ref(readStoredCollapse())
const mobileMenuOpen = ref(false)

function readStoredCollapse(): boolean {
  try {
    return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === 'true'
  } catch {
    return false
  }
}

function toggleSidebarCollapse() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  try {
    window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(sidebarCollapsed.value))
  } catch {
    // ignore storage quota/privacy mode errors
  }
}

watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false
  },
)

onErrorCaptured((cause) => {
  renderError.value = cause instanceof Error
    ? cause.message
    : 'No fue posible mostrar esta sección del catálogo.'
  return false
})

function skipToContent() {
  mainRef.value?.focus()
  mainRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function reloadPage() {
  window.location.reload()
}
</script>

<template>
  <div class="app-root" :class="{ 'app-root--collapsed': sidebarCollapsed }">
    <Toast position="bottom-right" />
    <a class="skip-link" href="#contenido" @click.prevent="skipToContent">Saltar al contenido</a>

    <div class="app-body">
      <AppNavigation
        :collapsed="sidebarCollapsed"
        :mobile-open="mobileMenuOpen"
        @toggle-collapse="toggleSidebarCollapse"
        @close-mobile="mobileMenuOpen = false"
      />

      <div class="app-workspace">
        <AppHeader
          :title="route.meta.title ?? 'CGID'"
          :subtitle="route.meta.subtitle ?? ''"
          @open-mobile-menu="mobileMenuOpen = true"
        />

        <main id="contenido" ref="mainRef" tabindex="-1" class="page-content">
          <StatusState
            v-if="renderError"
            type="error"
            title="Ocurrió un problema al mostrar la página"
            :message="renderError"
          >
            <template #actions>
              <Button label="Reintentar" @click="reloadPage">
                <template #icon>
                  <AppIcon name="refresh" size="sm" />
                </template>
              </Button>
            </template>
          </StatusState>
          <RouterView v-else />
        </main>
      </div>
    </div>

    <AppFooter />
  </div>
</template>
