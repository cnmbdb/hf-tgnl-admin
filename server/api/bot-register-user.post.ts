import { executeQuery } from '../utils/database'

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    // 支持两种数据格式：
    // 1. 机器人发送的格式：chat_id, user_nickname, username
    // 2. 标准格式：chat_id, username, first_name, last_name
    const { chat_id, username, user_nickname, first_name, last_name } = body

    if (!chat_id) {
      throw createError({
        statusCode: 400,
        statusMessage: 'chat_id参数是必需的'
      })
    }

    // 处理 user_nickname（机器人发送的格式）
    let finalFirstname = first_name || null
    let finalLastname = last_name || null
    
    if (user_nickname && !first_name && !last_name) {
      // 将 user_nickname 拆分为 first_name 和 last_name
      const nameParts = user_nickname.trim().split(/\s+/)
      finalFirstname = nameParts[0] || null
      finalLastname = nameParts.slice(1).join(' ') || null
    }

    // 检查用户是否已存在于 tg_users 表
    const existingUser = await executeQuery(
      'SELECT id FROM tg_users WHERE tg_user_id = ?',
      [chat_id]
    ) as any[]

    if (existingUser.length > 0) {
      // 更新现有用户信息
      await executeQuery(`
        UPDATE tg_users 
        SET username = ?, 
            first_name = ?, 
            last_name = ?,
            last_activity = NOW()
        WHERE tg_user_id = ?
      `, [username || null, finalFirstname, finalLastname, chat_id])

      // 确保 transactions 表中也有记录
      const existingTransaction = await executeQuery(
        'SELECT id FROM transactions WHERE chat_id = ?',
        [chat_id]
      ) as any[]

      if (existingTransaction.length === 0) {
        await executeQuery(
          'INSERT INTO transactions (chat_id, amount, created_at) VALUES (?, ?, NOW())',
          [chat_id, 0]
        )
      }

      return {
        success: true,
        message: '用户信息更新成功',
        action: 'updated',
        data: {
          chat_id,
          username: username || null,
          first_name: finalFirstname,
          last_name: finalLastname,
          updated_at: new Date().toISOString()
        }
      }
    } else {
      // 创建新用户
      await executeQuery(`
        INSERT INTO tg_users (
          tg_user_id, username, first_name, last_name,
          status, membership_type, last_activity, created_at
        ) VALUES (?, ?, ?, ?, 'active', 'free', NOW(), NOW())
      `, [
        chat_id,
        username || null,
        finalFirstname,
        finalLastname
      ])

      // 在 transactions 表中创建初始记录
      await executeQuery(
        'INSERT INTO transactions (chat_id, amount, created_at) VALUES (?, ?, NOW())',
        [chat_id, 0]
      )

      return {
        success: true,
        message: '用户注册成功',
        action: 'created',
        data: {
          chat_id,
          username: username || null,
          first_name: finalFirstname,
          last_name: finalLastname,
          amount: 0,
          created_at: new Date().toISOString()
        }
      }
    }
  } catch (error: any) {
    console.error('注册/更新用户失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: `注册/更新用户失败: ${error.message || '未知错误'}`
    })
  }
})