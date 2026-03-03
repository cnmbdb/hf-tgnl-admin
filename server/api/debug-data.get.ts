import { defineEventHandler } from 'h3'
import { executeQuery } from '../utils/database'

export default defineEventHandler(async (event) => {
  try {
    const systemUsers = await executeQuery('SELECT * FROM system_users LIMIT 10')
    const users = await executeQuery('SELECT * FROM users LIMIT 10')
    const transactions = await executeQuery('SELECT * FROM transactions LIMIT 10')
    
    return {
      success: true,
      data: {
        system_users: systemUsers,
        users: users,
        transactions: transactions
      }
    }
  } catch (error: any) {
    return {
      success: false,
      error: error?.message || '',
      code: error?.code || '',
      detail: typeof error === 'string' ? error : JSON.stringify(error)
    }
  }
})
