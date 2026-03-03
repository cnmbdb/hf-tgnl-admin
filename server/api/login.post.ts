import { executeQuery } from '../utils/database'
import crypto from 'crypto'
import { checkRateLimit, recordFailure, clearFailures, isBlocked, getClientIp, shouldRequireCaptcha } from '../utils/rateLimit'

export default defineEventHandler(async (event) => {
  try {
    let username: string = ''
    let password: string = ''
    let captchaToken: string = ''
    let captchaAnswer: number = NaN
    try {
      const body = await readBody(event)
      username = body?.username || ''
      password = body?.password || ''
      captchaToken = body?.captchaToken || ''
      captchaAnswer = Number(body?.captchaAnswer)
    } catch (e) {
      const q = getQuery(event)
      username = (q.username as string) || ''
      password = (q.password as string) || ''
      captchaToken = (q.captchaToken as string) || ''
      captchaAnswer = Number(q.captchaAnswer as string)
    }
    const ip = getClientIp(event)

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
    const devEnabled = (process.env.DEV_LOGIN_ENABLED === 'true') || (loadEnv('DEV_LOGIN_ENABLED') === 'true') || (process.env.NODE_ENV === 'development') || (loadEnv('NODE_ENV') === 'development')
    const devUser = process.env.DEV_ADMIN_USER || loadEnv('DEV_ADMIN_USER') || 'admin'
    const devPass = process.env.DEV_ADMIN_PASS || loadEnv('DEV_ADMIN_PASS') || 'admin123'
    console.log('[Login] devEnabled:', devEnabled, 'user:', username)
    
    // 尝试从数据库验证用户
    try {
      const users = await executeQuery(
        'SELECT id, username, password, role, status FROM system_users WHERE username = ? AND status = ?',
        [username, 'active']
      ) as any[]

      if (users.length > 0) {
        const user = users[0]
        // 验证密码
        const [salt, hashedPassword] = user.password.split(':')
        const inputHash = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex')
        
        if (inputHash === hashedPassword) {
          // 更新最后登录时间
          await executeQuery(
            'UPDATE system_users SET last_login = NOW() WHERE id = ?',
            [user.id]
          )
          
          const userInfo = { id: user.id, username: user.username, role: user.role, status: user.status }
          setCookie(event, 'userInfo', JSON.stringify(userInfo), {
            httpOnly: false,
            secure: false,
            sameSite: 'lax',
            maxAge: 60 * 60 * 24 * 7,
            path: '/'
          })
          clearFailures(ip)
          return { success: true, message: '登录成功', data: userInfo }
        }
      }
    } catch (dbError) {
      console.log('[Login] 数据库验证失败，尝试开发模式:', dbError)
    }
    
    // 开发模式回退
    if (devEnabled && username === devUser && password === devPass) {
      console.log('[Login] 使用开发登录凭据')
      // 尝试更新数据库中的用户（如果存在）
      try {
        const devUsers = await executeQuery(
          'SELECT id FROM system_users WHERE username = ?',
          [devUser]
        ) as any[]
        
        if (devUsers.length > 0) {
          await executeQuery(
            'UPDATE system_users SET last_login = NOW() WHERE id = ?',
            [devUsers[0].id]
          )
        }
      } catch (e) {
        console.log('[Login] 更新开发用户登录时间失败:', e)
      }
      
      const userInfo = { id: 1, username: devUser, role: 'admin', status: 'active' }
      setCookie(event, 'userInfo', JSON.stringify(userInfo), {
        httpOnly: false,
        secure: false,
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 * 7,
        path: '/'
      })
      clearFailures(ip)
      return { success: true, message: '登录成功', data: userInfo }
    }

    const needCaptcha = shouldRequireCaptcha(ip, 15 * 60 * 1000)
    if (needCaptcha) {
      try {
        const secret = process.env.NUXT_SECRET_KEY || 'nuxt-secret'
        const decoded = JSON.parse(Buffer.from(String(captchaToken || ''), 'base64').toString('utf-8'))
        const { a, b, exp, ip: tip, h } = decoded || {}
        if (!a || !b || !exp || !tip || !h) {
          return { success: false, error: '需要验证码' }
        }
        if (tip !== ip) {
          return { success: false, error: '验证码无效' }
        }
        if (Date.now() > Number(exp)) {
          return { success: false, error: '验证码已过期' }
        }
        const expected = crypto.createHmac('sha256', secret).update(`${a}:${b}:${exp}:${tip}`).digest('hex')
        if (expected !== h) {
          return { success: false, error: '验证码无效' }
        }
        if (Number(captchaAnswer) !== Number(a) + Number(b)) {
          return { success: false, error: '验证码错误' }
        }
      } catch {
        return { success: false, error: '需要验证码' }
      }
    }

    if (isBlocked(ip)) {
      return {
        success: false,
        error: '登录已被临时封禁，请稍后再试'
      }
    }

    const allowed = checkRateLimit(ip, 'login', 10, 60 * 1000)
    if (!allowed) {
      return {
        success: false,
        error: '请求过于频繁，请稍后再试'
      }
    }

    // 验证必填字段
    if (!username || !password) {
      return {
        success: false,
        error: '用户名和密码为必填项'
      }
    }

    const res = recordFailure(ip, 15 * 60 * 1000)
    return {
      success: false,
      error: res.blocked ? '登录失败次数过多，已临时封禁' : '用户名或密码错误'
    }
  } catch (error: any) {
    console.error('Error during login:', error)
    return {
      success: false,
      error: (typeof error === 'string' ? error : (error?.message || JSON.stringify(error) || '登录过程中发生错误'))
    }
  }
})
