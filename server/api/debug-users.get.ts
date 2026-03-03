import { executeQuery } from '../utils/database'

export default defineEventHandler(async (event) => {
  try {
    // 直接查询所有用户
    const allUsersQuery = 'SELECT * FROM tg_users ORDER BY created_at DESC'
    const allUsers = await executeQuery(allUsersQuery) as any[]
    
    // 查询所有交易记录
    const allTransactionsQuery = 'SELECT * FROM transactions'
    const allTransactions = await executeQuery(allTransactionsQuery) as any[]
    
    return {
      success: true,
      data: {
        users: allUsers,
        transactions: allTransactions,
        userCount: allUsers.length,
        transactionCount: allTransactions.length
      }
    }
  } catch (error: any) {
    console.error('Debug users error:', error)
    return {
      success: false,
      error: error.message
    }
  }
})