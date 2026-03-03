import { executeQuery } from '../utils/database'

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    const chatId = query.chat_id as string

    if (!chatId) {
      throw createError({
        statusCode: 400,
        statusMessage: 'chat_id参数是必需的'
      })
    }

    // 从transactions表查询用户真实数据
    const sql = 'SELECT * FROM transactions WHERE chat_id = ? LIMIT 1'
    const result = await executeQuery(sql, [chatId])
    
    if (result && result.length > 0) {
      // 找到用户,返回真实数据
      const userData = result[0]
      return {
        success: true,
        data: {
          id: userData.id,
          chat_id: userData.chat_id,
          amount: userData.amount || 0,  // amount存储的是sun单位(1 TRX = 1000000 sun)
          created_at: userData.created_at
        }
      }
    } else {
      // 新用户,插入初始记录
      const insertSql = 'INSERT INTO transactions (chat_id, amount, created_at) VALUES (?, ?, NOW())'
      await executeQuery(insertSql, [chatId, 0])
      
      // 查询刚插入的记录
      const newUserResult = await executeQuery(sql, [chatId])
      
      return {
        success: true,
        data: {
          id: newUserResult[0].id,
          chat_id: chatId,
          amount: 0,
          created_at: newUserResult[0].created_at
        }
      }
    }
  } catch (error) {
    console.error('获取用户数据失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: '获取用户数据失败'
    })
  }
})