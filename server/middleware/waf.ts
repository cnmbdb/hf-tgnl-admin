import { checkRateLimit, getClientIp } from '../utils/rateLimit'

export default defineEventHandler((event) => {
  const url = getRequestURL(event)
  const path = url.pathname
  const ip = getClientIp(event)

  // 忽略静态资源
  const isStatic = path.startsWith('/_nuxt') || path.startsWith('/assets') || path.startsWith('/public')
  if (isStatic) return

  // API 速率限制：每 IP 每分钟 120 次
  if (path.startsWith('/api')) {
    const ok = checkRateLimit(ip, 'api', 120, 60 * 1000)
    if (!ok) {
      throw createError({ statusCode: 429, statusMessage: '请求过于频繁，请稍后再试' })
    }
  }
})
