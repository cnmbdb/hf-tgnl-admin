import { executeQuery } from '../utils/database'
import { requireAdmin } from '../utils/auth'
import crypto from 'crypto'

export default defineEventHandler(async (event) => {
  // 验证管理员权限
  const user = await requireAdmin(event)
  if (!user) {
    return {
      success: false,
      error: '需要管理员权限'
    }
  }
  try {
    const body = await readBody(event)
    const { username, password, email, role = 'user', status = 'active' } = body

    // 验证必填字段
    if (!username || !password) {
      return {
        success: false,
        error: '用户名和密码为必填项'
      }
    }

    // 验证用户名格式
    if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
      return {
        success: false,
        error: '用户名只能包含字母、数字和下划线，长度3-20位'
      }
    }

    // 验证密码强度
    if (password.length < 6) {
      return {
        success: false,
        error: '密码长度至少6位'
      }
    }

    // 验证邮箱格式
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return {
        success: false,
        error: '邮箱格式不正确'
      }
    }

    // 验证角色
    if (!['admin', 'user'].includes(role)) {
      return {
        success: false,
        error: '角色只能是admin或user'
      }
    }

    // 验证状态
    if (!['active', 'inactive'].includes(status)) {
      return {
        success: false,
        error: '状态只能是active或inactive'
      }
    }

    // 检查用户名是否已存在
    const existingUser = await executeQuery(
      'SELECT id FROM system_users WHERE username = ?',
      [username]
    ) as any[]

    if (existingUser.length > 0) {
      return {
        success: false,
        error: '用户名已存在'
      }
    }

    // 检查邮箱是否已存在
    if (email) {
      const existingEmail = await executeQuery(
        'SELECT id FROM system_users WHERE email = ?',
        [email]
      ) as any[]

      if (existingEmail.length > 0) {
        return {
          success: false,
          error: '邮箱已存在'
        }
      }
    }

    // 加密密码
    const salt = crypto.randomBytes(16).toString('hex')
    const hashedPassword = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex')
    const finalPassword = `${salt}:${hashedPassword}`

    // 插入新用户
    const result = await executeQuery(
      'INSERT INTO system_users (username, password, email, role, status) VALUES (?, ?, ?, ?, ?)',
      [username, finalPassword, email, role, status]
    ) as any

    // 获取新创建的用户信息
    const newUser = await executeQuery(
      'SELECT id, username, email, role, status, created_at FROM system_users WHERE id = ?',
      [result.insertId]
    ) as any[]

    return {
      success: true,
      message: '用户创建成功',
      data: newUser[0]
    }
  } catch (error: any) {
    console.error('Error creating system user:', error)
    return {
      success: false,
      error: error.message
    }
  }
})