/**
 * 授权验证中间件
 * 检查用户是否已激活授权,未激活则重定向到授权页面
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  // 仅在客户端执行
  if (process.server) return

  try {
    // 调用授权状态检查API
    const status = await $fetch('/api/license/status')
    
    if (!status.isActive) {
      // 未激活授权,重定向到授权页面
      return navigateTo('/license')
    }
  } catch (error) {
    console.error('授权检查失败:', error)
    // 检查失败也重定向到授权页面
    return navigateTo('/license')
  }
})
