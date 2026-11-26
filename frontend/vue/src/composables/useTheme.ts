import { readonly, ref } from 'vue'

const THEME_STORAGE_KEY = 'cgid:theme'
const LIGHT_THEME_COLOR = '#7a1737'
const DARK_THEME_COLOR = '#0f1316'

const isDarkRef = ref(false)
let initialized = false

function applyTheme(dark: boolean) {
  isDarkRef.value = dark
  if (typeof document === 'undefined') return

  document.documentElement.classList.toggle('app-dark', dark)
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) {
    meta.setAttribute('content', dark ? DARK_THEME_COLOR : LIGHT_THEME_COLOR)
  }
}

export function initTheme() {
  if (initialized) return
  initialized = true

  let stored: string | null = null
  try {
    stored = window.localStorage.getItem(THEME_STORAGE_KEY)
  } catch {
    stored = null
  }

  applyTheme(stored === 'dark')
}

export function useTheme() {
  if (!initialized) {
    initTheme()
  }

  function toggleTheme() {
    const next = !isDarkRef.value
    applyTheme(next)
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, next ? 'dark' : 'light')
    } catch {
      // ignore storage errors
    }
  }

  return {
    isDark: readonly(isDarkRef),
    toggleTheme,
  }
}
