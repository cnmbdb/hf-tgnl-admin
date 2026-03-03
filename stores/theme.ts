import { defineStore } from 'pinia'

export type ThemeMode = 'light' | 'dark'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: 'dark' as ThemeMode
  }),

  getters: {
    isDark: (state) => state.mode === 'dark',
    isLight: (state) => state.mode === 'light'
  },

  actions: {
    toggle() {
      this.mode = this.mode === 'dark' ? 'light' : 'dark'
      this.applyTheme()
      this.saveToStorage()
    },

    setMode(mode: ThemeMode) {
      this.mode = mode
      this.applyTheme()
      this.saveToStorage()
    },

    applyTheme() {
      if (typeof document !== 'undefined') {
        const root = document.documentElement
        if (this.mode === 'dark') {
          root.classList.add('dark')
          root.classList.remove('light')
        } else {
          root.classList.add('light')
          root.classList.remove('dark')
        }
      }
    },

    loadFromStorage() {
      if (typeof window !== 'undefined') {
        const saved = localStorage.getItem('theme-mode')
        if (saved === 'light' || saved === 'dark') {
          this.mode = saved
        }
        this.applyTheme()
      }
    },

    saveToStorage() {
      if (typeof window !== 'undefined') {
        localStorage.setItem('theme-mode', this.mode)
      }
    }
  }
})
