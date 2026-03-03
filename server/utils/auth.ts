import { } from './database'

export interface UserPayload {
  id: number
  username: string
  role: string
}

// 简单的基于session的认证（生产环境建议使用JWT）
export async function requireAuth(event: any): Promise<UserPayload | null> {
  try {
    const userCookie = getCookie(event, 'userInfo') || parseCookies(event)['userInfo']
    if (!userCookie) return null
    const userInfo = typeof userCookie === 'string' ? JSON.parse(userCookie) : userCookie
    const loadEnv = (key: string) => {
      try {
        const fs = require('fs') as typeof import('fs')
        const path = require('path') as typeof import('path')
        const candidates = [
          path.join(process.cwd(), '.env'),
          path.join(process.cwd(), '../.env'),
          path.join(process.cwd(), '../../.env')
        ]
        const found = candidates.find(p => fs.existsSync(p))
        if (!found) return ''
        const content = fs.readFileSync(found, 'utf-8')
        const line = content.split('\n').find((l: string) => l.trim().startsWith(key + '='))
        if (!line) return ''
        return line.split('=', 2)[1]?.trim() || ''
      } catch { return '' }
    }
    const devUser = process.env.DEV_ADMIN_USER || loadEnv('DEV_ADMIN_USER') || 'admin'
    if (userInfo.username !== devUser) return null
    return { id: 1, username: devUser, role: 'admin' }
  } catch { return null }
}

export async function requireAdmin(event: any): Promise<UserPayload | null> {
  const user = await requireAuth(event)
  if (!user || user.role !== 'admin') return null
  return user
}
