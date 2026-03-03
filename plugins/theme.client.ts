export default defineNuxtPlugin(() => {
  const themeStore = useThemeStore()
  
  // 初始化主题
  themeStore.loadFromStorage()
  
  // 监听主题变化
  watch(() => themeStore.mode, () => {
    themeStore.applyTheme()
  }, { immediate: true })
})
