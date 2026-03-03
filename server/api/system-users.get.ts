import { requireAuth } from '../utils/auth'
import { executeQuery } from '../utils/database'
import crypto from 'crypto'

export default defineEventHandler(async (event) => {
  // 验证用户登录状态
  const user = await requireAuth(event)
  if (!user) {
    return {
      success: false,
      error: '未授权访问'
    }
  }
  try {
    const query = getQuery(event)
    const page = Math.max(1, Number(query.page) || 1)
    const limit = Math.max(1, Math.min(100, Number(query.limit) || 10)) // 1-100 之间
    const search = query.search as string || ''
    const status = query.status as string || ''
    const role = query.role as string || ''
    
    const offset = Math.max(0, (page - 1) * limit)

    // 如果系统用户表为空，则自动创建一个默认的管理员账号，方便首次登录后自行修改密码
    try {
      const countAllResult = await executeQuery(
        'SELECT COUNT(*) as total FROM system_users',
        []
      ) as any[]
      const totalAll = countAllResult[0]?.total || 0

      if (totalAll === 0) {
        // 从环境变量或 .env 中读取默认管理员账号和密码
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
          } catch {
            return ''
          }
        }

        const defaultUsername =
          process.env.DEV_ADMIN_USER ||
          loadEnv('DEV_ADMIN_USER') ||
          'admin'
        const defaultPassword =
          process.env.DEV_ADMIN_PASS ||
          loadEnv('DEV_ADMIN_PASS') ||
          'admin123'
        const defaultEmail =
          process.env.DEV_ADMIN_EMAIL ||
          loadEnv('DEV_ADMIN_EMAIL') ||
          'admin@example.com'

        // 使用与创建用户接口相同的加密方式
        const salt = crypto.randomBytes(16).toString('hex')
        const hashedPassword = crypto
          .pbkdf2Sync(defaultPassword, salt, 10000, 64, 'sha512')
          .toString('hex')
        const finalPassword = `${salt}:${hashedPassword}`

        await executeQuery(
          'INSERT INTO system_users (username, password, email, role, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, NOW(), NOW())',
          [defaultUsername, finalPassword, defaultEmail, 'admin', 'active']
        )
      }
    } catch (e) {
      console.error('ensure default admin failed:', e)
    }
    
    // 构建查询条件
    let whereConditions: string[] = []
    let queryParams: any[] = []
    
    if (search) {
      whereConditions.push('(username LIKE ? OR email LIKE ?)')
      const searchPattern = `%${search}%`
      queryParams.push(searchPattern, searchPattern)
    }
    
    if (status) {
      whereConditions.push('status = ?')
      queryParams.push(status)
    }
    
    if (role) {
      whereConditions.push('role = ?')
      queryParams.push(role)
    }
    
    const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : ''
    
    // 获取总数（带筛选条件）
    const countResult = await executeQuery(
      `SELECT COUNT(*) as total FROM system_users ${whereClause}`,
      queryParams
    ) as any[]
    const total = countResult[0]?.total || 0
    
    // 获取用户列表（LIMIT/OFFSET 直接内联，避免某些 MySQL 驱动对参数化 LIMIT 的限制）
    const usersQuery = `
      SELECT id, username, email, role, status, last_login, created_at, updated_at 
      FROM system_users 
      ${whereClause}
      ORDER BY created_at DESC 
      LIMIT ${limit} OFFSET ${offset}
    `
    console.log('System users query:', usersQuery, 'Params:', queryParams)
    const users = await executeQuery(
      usersQuery,
      queryParams
    ) as any[]
    
    // 获取统计数据
    const statsResult = await executeQuery(
      `SELECT 
        COUNT(*) as total_users,
        SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
        SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_count,
        SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_count,
        SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive_count
       FROM system_users`
    ) as any[]
    
    const stats = statsResult[0] || {
      total_users: 0,
      admin_count: 0,
      user_count: 0,
      active_count: 0,
      inactive_count: 0
    }
    
    return {
      success: true,
      data: {
        users: users.map(u => ({
          ...u,
          last_login: u.last_login ? new Date(u.last_login).toISOString() : null,
          created_at: u.created_at ? new Date(u.created_at).toISOString() : null,
          updated_at: u.updated_at ? new Date(u.updated_at).toISOString() : null
        })),
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit)
        },
        stats
      }
    }
  } catch (error: any) {
    console.error('Error fetching system users:', error)
    return { success: false, error: error.message }
  }
})
