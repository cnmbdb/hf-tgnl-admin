import { executeQuery } from '../utils/database'
import { requireAdmin } from '../utils/auth'

interface ImportUser {
  tg_user_id: number
  username?: string
  first_name?: string
  last_name?: string
  phone_number?: string
  is_bot?: boolean
  is_premium?: boolean
  language_code?: string
  status?: 'active' | 'banned' | 'inactive'
  membership_type?: 'free' | 'vip' | 'premium'
  membership_expires?: string
  balance?: number
}

interface ImportResult {
  success: boolean
  message: string
  data?: {
    imported: number
    skipped: number
    errors: string[]
  }
}

export default defineEventHandler(async (event): Promise<ImportResult> => {
  // 验证管理员权限
  const user = await requireAdmin(event)
  if (!user) {
    return {
      success: false,
      message: '需要管理员权限'
    }
  }

  try {
    const body = await readBody(event)
    
    if (!body.users || !Array.isArray(body.users)) {
      return {
        success: false,
        message: '请提供有效的用户数据数组'
      }
    }

    const users: ImportUser[] = body.users
    let imported = 0
    let skipped = 0
    const errors: string[] = []

    for (const user of users) {
      try {
        // 验证必需字段
        if (!user.tg_user_id || typeof user.tg_user_id !== 'number') {
          errors.push(`用户 ${user.username || 'unknown'}: tg_user_id 是必需的且必须是数字`)
          continue
        }

        // 检查用户是否已存在
        const existingUser = await executeQuery(
          'SELECT id FROM tg_users WHERE tg_user_id = ?',
          [user.tg_user_id]
        ) as any[]

        if (existingUser.length > 0) {
          skipped++
          continue
        }

        // 插入用户数据
        const insertResult = await executeQuery(`
          INSERT INTO tg_users (
            tg_user_id, username, first_name, last_name, phone_number,
            is_bot, is_premium, language_code, status, membership_type,
            membership_expires, last_activity
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW())
        `, [
          user.tg_user_id,
          user.username || null,
          user.first_name || null,
          user.last_name || null,
          user.phone_number || null,
          user.is_bot ? 1 : 0,
          user.is_premium ? 1 : 0,
          user.language_code || 'en',
          user.status || 'active',
          user.membership_type || 'free',
          user.membership_expires || null
        ])

        // 如果提供了余额信息，插入到transactions表
        if (user.balance !== undefined && user.balance !== null) {
          const balanceAmount = Math.round(user.balance) // 直接使用提供的值
          await executeQuery(`
            INSERT INTO transactions (chat_id, amount) VALUES (?, ?)
            ON DUPLICATE KEY UPDATE amount = VALUES(amount)
          `, [user.tg_user_id, balanceAmount])
        }

        imported++
      } catch (userError: any) {
        errors.push(`用户 ${user.username || user.tg_user_id}: ${userError.message}`)
      }
    }

    return {
      success: true,
      message: `导入完成: ${imported} 个用户成功导入, ${skipped} 个用户已存在被跳过`,
      data: {
        imported,
        skipped,
        errors
      }
    }

  } catch (error: any) {
    console.error('Import users error:', error)
    return {
      success: false,
      message: `导入失败: ${error.message}`
    }
  }
})