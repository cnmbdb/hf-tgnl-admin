import { executeQuery } from '../utils/database'

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { chat_id, new_balance } = body

    if (!chat_id || new_balance === undefined) {
      throw createError({
        statusCode: 400,
        statusMessage: 'chat_id和new_balance参数是必需的'
      })
    }

    console.log(`设置用户 ${chat_id} 的余额为 ${new_balance} (${new_balance / 1000000} TRX)`)

    // 更新数据库中的余额
    // 先检查用户是否存在
    const checkResult: any = await executeQuery(
      'SELECT id, amount FROM transactions WHERE chat_id = ?',
      [chat_id]
    )

    if (checkResult.length > 0) {
      // 用户存在,更新余额
      await executeQuery(
        'UPDATE transactions SET amount = ?, updated_at = NOW() WHERE chat_id = ?',
        [new_balance, chat_id]
      )
      console.log(`用户 ${chat_id} 余额已更新: ${checkResult[0].amount} -> ${new_balance}`)
    } else {
      // 用户不存在,插入新记录
      await executeQuery(
        'INSERT INTO transactions (chat_id, amount, created_at, updated_at) VALUES (?, ?, NOW(), NOW())',
        [chat_id, new_balance]
      )
      console.log(`新用户 ${chat_id} 余额已设置为: ${new_balance}`)
    }

    return {
      success: true,
      message: '余额设置成功',
      data: {
        chat_id,
        new_balance,
        balance_trx: new_balance / 1000000,
        timestamp: new Date().toISOString()
      }
    }
  } catch (error) {
    console.error('设置余额失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: '设置余额失败: ' + (error as Error).message
    })
  }
})