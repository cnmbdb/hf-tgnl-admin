export default defineEventHandler((event) => {
  setResponseHeader(event, 'X-Robots-Tag', 'noindex, nofollow')
  setResponseHeader(event, 'X-Frame-Options', 'DENY')
  setResponseHeader(event, 'X-Content-Type-Options', 'nosniff')
  setResponseHeader(event, 'Referrer-Policy', 'no-referrer')
  setResponseHeader(event, 'Permissions-Policy', 'interest-cohort=()')
  setResponseHeader(event, 'Server', '')
  setResponseHeader(event, 'X-Powered-By', '')

  // 从挂载的 .env 动态读取配置（允许部署后修改 .env 即时生效）
  // 注意：Docker 的 env_file 修改不会自动注入到已运行容器的 process.env，
  // 所以这里优先读取 process.env，其次读取 .env 文件。
  const readEnvFile = (() => {
    let cache: Record<string, string> = {}
    let lastRead = 0
    const CACHE_MS = 2000
    return (key: string): string => {
      try {
        const now = Date.now()
        if (now - lastRead > CACHE_MS) {
          lastRead = now
          // eslint-disable-next-line @typescript-eslint/no-var-requires
          const fs = require('fs') as typeof import('fs')
          // eslint-disable-next-line @typescript-eslint/no-var-requires
          const path = require('path') as typeof import('path')
          const candidates = [
            path.join(process.cwd(), '.env'),
            path.join(process.cwd(), '../.env'),
            path.join(process.cwd(), '../../.env'),
          ]
          const found = candidates.find((p) => fs.existsSync(p))
          if (!found) {
            cache = {}
          } else {
            const content = fs.readFileSync(found, 'utf-8')
            const obj: Record<string, string> = {}
            for (const raw of content.split(/\r?\n/)) {
              const line = raw.trim()
              if (!line || line.startsWith('#')) continue
              const idx = line.indexOf('=')
              if (idx < 0) continue
              const k = line.slice(0, idx).trim()
              const v = line.slice(idx + 1).trim()
              if (k) obj[k] = v
            }
            cache = obj
          }
        }
        return cache[key] || ''
      } catch {
        return ''
      }
    }
  })()
  
  // 只有在开发环境且明确允许时才跳过检查（不再无条件跳过）
  const devBypass = (process.env.NODE_ENV === 'development') && (process.env.DEV_LOGIN_ENABLED === 'true')
  const skipSecurityCheck = devBypass && (process.env.ENFORCE_HOST_CHECK !== 'true')

  const url = getRequestURL(event)
  const path = url.pathname
  const base = ((process.env.APP_BASE_PATH || readEnvFile('APP_BASE_PATH') || '/') as string).replace(/\/+$/,'') || '/'
  const isStatic = path.startsWith('/_nuxt') || path.startsWith('/assets') || path.startsWith('/public') || path.startsWith('/avatars') || path === '/favicon.ico' || path === '/robots.txt' || path === '/logo.png'
  if (!isStatic) {
    const normalizedBase = base === '/' ? '/' : base.startsWith('/') ? base : `/${base}`
    if (!path.startsWith(normalizedBase)) {
      throw createError({ statusCode: 404, statusMessage: 'Not Found' })
    }
  }
  
  // 如果明确跳过安全检查，直接返回
  if (skipSecurityCheck) {
    return
  }
  
  const host = url.hostname || getRequestHeader(event, 'host') || ''
  const normalizeHost = (h: string) => {
    if (!h) return ''
    // IPv6 like [::1]:3000
    const withoutPort = h.startsWith('[')
      ? h.replace(/\]:\d+$/, ']')
      : h.replace(/:\d+$/, '')
    return withoutPort.toLowerCase()
  }
  const ipV4 = /^\d{1,3}(\.\d{1,3}){3}$/
  const ipV6 = /^\[[0-9a-fA-F:]+\]$/
  const h = normalizeHost(host)
  const isIP = ipV4.test(h) || ipV6.test(h)

  // 读取配置
  const enforce = (process.env.ENFORCE_HOST_CHECK || readEnvFile('ENFORCE_HOST_CHECK')) === 'true'  // 只有明确为 'true' 时才启用
  const domain = ((process.env.DOMAIN_NAME || readEnvFile('DOMAIN_NAME') || '') as string).toLowerCase().trim()
  const allowIp = (process.env.ALLOW_IP_ACCESS || readEnvFile('ALLOW_IP_ACCESS')) === 'true'  // 只有明确为 'true' 时才允许IP访问
  const extraHostsEnv = (process.env.ALLOWED_HOSTS || readEnvFile('ALLOWED_HOSTS') || 'localhost,127.0.0.1') as string
  let extraHosts = extraHostsEnv.split(',').map(s => s.trim().toLowerCase()).filter(Boolean)
  
  // 如果禁止IP访问，从白名单中移除所有IP地址
  if (!allowIp) {
    extraHosts = extraHosts.filter(x => !(ipV4.test(x) || ipV6.test(x)))
  }

  // 执行访问控制检查
  if (enforce) {
    // 1. IP访问控制：如果访问的是IP地址且不允许IP访问，直接拒绝
    if (isIP && !allowIp) {
      throw createError({ 
        statusCode: 403, 
        statusMessage: 'Forbidden: IP access is not allowed. Please use the configured domain name.' 
      })
    }
    
    // 2. 域名访问控制：如果配置了域名，必须匹配域名或白名单
    if (domain) {
      const plain = h.replace(/^\[|\]$/g, '')
      const matched = plain === domain || extraHosts.includes(plain)
      if (!matched) {
        throw createError({ 
          statusCode: 403, 
          statusMessage: `Forbidden: Access denied. Allowed domain: ${domain}` 
        })
      }
    } else if (!isIP) {
      // 如果配置了域名检查但没有设置域名，且访问的不是IP，也拒绝（防止未配置域名时被绕过）
      // 但允许白名单中的域名
      const plain = h.replace(/^\[|\]$/g, '')
      if (!extraHosts.includes(plain)) {
        throw createError({ 
          statusCode: 403, 
          statusMessage: 'Forbidden: Domain name check is enabled but no domain is configured.' 
        })
      }
    }
  } else {
    // 即使不强制域名检查，如果明确禁止IP访问，也要阻止IP访问
    if (isIP && !allowIp) {
      throw createError({ 
        statusCode: 403, 
        statusMessage: 'Forbidden: IP access is not allowed. Please use the configured domain name.' 
      })
    }
  }
})
