import { computed, ref } from 'vue'

const STORAGE_KEY = 'site-theme'
const theme = ref('light')
let initialized = false

const getSystemTheme = () =>
  window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'

const applyTheme = (nextTheme) => {
  const safeTheme = nextTheme === 'dark' ? 'dark' : 'light'
  theme.value = safeTheme

  document.documentElement.classList.toggle('dark', safeTheme === 'dark')
  document.body.classList.toggle('dark', safeTheme === 'dark')
  document.body.classList.toggle('light', safeTheme !== 'dark')
  document.documentElement.setAttribute('data-theme', safeTheme)
  document.body.setAttribute('data-theme', safeTheme)
}

const initTheme = () => {
  if (initialized || typeof window === 'undefined') return

  const saved = localStorage.getItem(STORAGE_KEY)
  const initialTheme = saved === 'dark' || saved === 'light' ? saved : 'light'
  applyTheme(initialTheme)
  initialized = true
}

const setTheme = (nextTheme) => {
  if (typeof window === 'undefined') return
  applyTheme(nextTheme)
  localStorage.setItem(STORAGE_KEY, theme.value)
}

const toggleTheme = () => {
  setTheme(theme.value === 'dark' ? 'light' : 'dark')
}

export function useTheme() {
  return {
    theme: computed(() => theme.value),
    isDark: computed(() => theme.value === 'dark'),
    initTheme,
    setTheme,
    toggleTheme,
  }
}
