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
    const { id, username, password, role, status } = body

    // 验证必填字段
    if (!id) {
      return {
        success: false,
        error: '用户ID为必填项'
      }
    }

    // 检查用户是否存在
    const existingUser = await executeQuery(
      'SELECT id, username, email, role, status FROM system_users WHERE id = ?',
      [id]
    ) as any[]

    if (existingUser.length === 0) {
      return {
        success: false,
        error: '用户不存在'
      }
    }

    const currentUser = existingUser[0]

    // 验证用户名格式（如果提供）
    if (username !== undefined && username !== currentUser.username) {
      if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
        return { 
          success: false, 
          error: '用户名只能包含字母、数字和下划线，长度3-20位' 
        }
      }

      // 检查新用户名是否已被其他用户使用
      const usernameCheck = await executeQuery(
        'SELECT id FROM system_users WHERE username = ? AND id != ?',
        [username, id]
      ) as any[]

      if (usernameCheck.length > 0) {
        return {
          success: false,
          error: '用户名已被使用'
        }
    }
    }

    // 验证密码强度（如果提供）
    if (password !== undefined && password !== '' && password.length < 6) {
      return { 
        success: false, 
        error: '密码长度至少6位' 
      }
    }

    // 验证角色（如果提供）
    if (role !== undefined && !['admin', 'user'].includes(role)) {
      return {
        success: false,
        error: '角色只能是admin或user'
      }
    }

    // 验证状态（如果提供）
    if (status !== undefined && !['active', 'inactive'].includes(status)) {
      return {
        success: false,
        error: '状态只能是active或inactive'
      }
    }

    // 构建更新SQL
    const updateFields: string[] = []
    const updateValues: any[] = []

    if (username !== undefined) {
      updateFields.push('username = ?')
      updateValues.push(username)
    }

    if (password !== undefined && password !== '') {
      // 加密密码
      const salt = crypto.randomBytes(16).toString('hex')
      const hashedPassword = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex')
      const finalPassword = `${salt}:${hashedPassword}`
      
      updateFields.push('password = ?')
      updateValues.push(finalPassword)
    }

    if (role !== undefined) {
      updateFields.push('role = ?')
      updateValues.push(role)
    }

    if (status !== undefined) {
      updateFields.push('status = ?')
      updateValues.push(status)
    }

    if (updateFields.length === 0) {
      return {
        success: false,
        error: '没有需要更新的字段'
      }
    }

    // 执行更新
    updateValues.push(id)
    await executeQuery(
      `UPDATE system_users SET ${updateFields.join(', ')} WHERE id = ?`,
      updateValues
    )

    // 获取更新后的用户信息
    const updatedUser = await executeQuery(
      'SELECT id, username, email, role, status, created_at, updated_at FROM system_users WHERE id = ?',
      [id]
    ) as any[]

    return {
      success: true,
      message: '用户更新成功',
      data: updatedUser[0]
    }
  } catch (error: any) {
    console.error('Error updating system user:', error)
    return {
      success: false,
      error: error.message
    }
  }
})
