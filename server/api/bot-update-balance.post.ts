import { executeQuery } from '../utils/database'
import type { RowDataPacket } from 'mysql2'

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { chat_id, amount } = body

    if (!chat_id || amount === undefined) {
      throw createError({
        statusCode: 400,
        statusMessage: 'chat_id和amount参数是必需的'
      })
    }

    // 查询是否已存在该用户
    const findQuery = 'SELECT * FROM transactions WHERE chat_id = ?'
    const existingUser = await executeQuery(findQuery, [chat_id]) as RowDataPacket[]

    let newBalance = 0

    if (existingUser && existingUser.length > 0) {
      // 用户存在，更新余额
      const updateQuery = 'UPDATE transactions SET amount = amount + ? WHERE chat_id = ?'
      await executeQuery(updateQuery, [amount, chat_id])
      
      // 查询更新后的余额
      const balanceQuery = 'SELECT amount FROM transactions WHERE chat_id = ?'
      const result = await executeQuery(balanceQuery, [chat_id]) as RowDataPacket[]
      newBalance = result[0].amount
    } else {
      // 用户不存在，插入新记录
      const insertQuery = 'INSERT INTO transactions (chat_id, amount) VALUES (?, ?)'
      await executeQuery(insertQuery, [chat_id, amount])
      newBalance = amount
    }

    console.log(`成功更新用户 ${chat_id} 的余额，增加 ${amount / 1000000} TRX，当前余额：${newBalance / 1000000} TRX`)

    return {
      success: true,
      message: '余额更新成功',
      new_balance: newBalance,
      data: {
        chat_id,
        amount_added: amount,
        current_balance: newBalance,
        timestamp: new Date().toISOString()
      }
    }
  } catch (error) {
    console.error('更新余额失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: '更新余额失败'
    })
  }
})