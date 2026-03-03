import { executeQuery } from '../utils/database'
import { requireAuth } from '../utils/auth'

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
    // 获取能量出租机器人统计数据
    const totalUsersResult = await executeQuery('SELECT COUNT(*) as count FROM transactions') as any[]
    const activeUsersResult = await executeQuery('SELECT COUNT(*) as count FROM transactions WHERE amount > 0') as any[]
    const totalEnergyResult = await executeQuery('SELECT SUM(amount) as total FROM transactions') as any[]
    
    const stats = {
      totalUsers: totalUsersResult[0]?.count || 0,
      activeUsers: activeUsersResult[0]?.count || 0,
      totalEnergyRented: totalEnergyResult[0]?.total || 0,
      botStatus: 'running',
      energyRentalGrowth: {
        labels: ['1月1日', '1月2日', '1月3日', '1月4日', '1月5日', '1月6日', '1月7日'],
        data: [1200000, 1350000, 1420000, 1580000, 1670000, 1750000, 1890000]
      },
      dailyTransactions: {
        labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
        data: [120, 150, 180, 220, 250, 280]
      }
    }

    return {
      success: true,
      data: stats
    }
  } catch (error) {
    throw createError({
      statusCode: 500,
      statusMessage: '获取统计数据失败'
    })
  }
})