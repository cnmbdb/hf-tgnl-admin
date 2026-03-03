export default defineNuxtRouteMiddleware((to, from) => {
  // 检查登录状态
  const isLoggedIn = useCookie('isLoggedIn', {
    default: () => false
  })

  // 如果未登录且不是在登录页面，则重定向到登录页面
  if (!isLoggedIn.value && to.path !== '/') {
    return navigateTo('/')
  }

  // 如果已登录且在登录页面，则重定向到仪表板页面
  if (isLoggedIn.value && to.path === '/') {
    return navigateTo('/dashboard')
  }
})