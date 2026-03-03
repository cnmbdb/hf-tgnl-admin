import { send } from 'h3'

export default defineEventHandler((event) => {
  const enabled = process.env.BASIC_AUTH_ENABLED === 'true'
  if (!enabled) return
  const url = getRequestURL(event)
  const path = url.pathname
  const isStatic = path.startsWith('/_nuxt') || path.startsWith('/assets') || path === '/robots.txt' || path === '/favicon.ico'
  const excludeEnv = (process.env.BASIC_AUTH_EXCLUDE || '/').split(',').map(s => s.trim()).filter(Boolean)
  const isExcluded = excludeEnv.includes(path)
  const isApi = path.startsWith('/api')
  if (isStatic || isApi || isExcluded) return
  const user = process.env.BASIC_AUTH_USER || ''
  const pass = process.env.BASIC_AUTH_PASS || ''
  const header = getRequestHeader(event, 'authorization') || ''
  const expected = 'Basic ' + Buffer.from(`${user}:${pass}`).toString('base64')
  if (!user || !pass || header !== expected) {
    setResponseHeader(event, 'WWW-Authenticate', 'Basic realm="Restricted"')
    setResponseHeader(event, 'Content-Type', 'text/html')
    setResponseStatus(event, 401)
    return send(event, '')
  }
})
