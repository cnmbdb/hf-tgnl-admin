import { executeQuery } from '../utils/database'
import { requireAuth } from '../utils/auth'

export default defineEventHandler(async (event) => { 
  // 验证用户登录状态(暂时注释以便调试)
  // const user = await requireAuth(event)
  // if (!user) {
  //   return {
  //     success: false,
  //     error: '未授权访问'
  //   }
  // }
  
  try {
    const query = getQuery(event)
    const page = parseInt(query.page as string) || 1
    const limit = parseInt(query.limit as string) || 10
    const offset = (page - 1) * limit
    const startDate = query.startDate as string
    const endDate = query.endDate as string
    
    console.log('查询订单数据, page:', page, 'limit:', limit, 'startDate:', startDate, 'endDate:', endDate)
    
    // 构建时间范围条件
    let dateCondition = ''
    if (startDate && endDate) {
      dateCondition = `WHERE DATE(created_at) >= '${startDate}' AND DATE(created_at) <= '${endDate}'`
    }
    
    // 从数据库获取订单记录
    // 如果 limit >= 1000，表示是用于图表统计，不限制数量
    const limitClause = limit >= 1000 ? '' : `LIMIT ${limit} OFFSET ${offset}`
    const ordersQuery = `
      SELECT id, order_number, chat_id, username, plan, amount, status, 
             payment_method, created_at, updated_at
      FROM orders 
      ${dateCondition}
      ORDER BY created_at DESC 
      ${limitClause}
    `
    const orders = await executeQuery(ordersQuery) as any[]
    
    console.log('查询到订单数:', orders.length)
    
    const totalQuery = `SELECT COUNT(*) as count FROM orders ${dateCondition}`
    const totalResult = await executeQuery(totalQuery) as any[]
    const total = totalResult[0]?.count || 0
    
    console.log('订单总数:', total)
    
    // 统计汇总数据（用于顶部统计卡片）
    const aggQuery = `
      SELECT 
        COUNT(*) AS totalOrders,
        COALESCE(SUM(amount), 0) AS totalRevenue,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pendingOrders,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completedOrders
      FROM orders
      ${dateCondition}
    `
    const aggResult = await executeQuery(aggQuery) as any[]

    const agg = aggResult[0] || {}
    const totalOrders = Number(agg.totalOrders || 0)
    const totalRevenue = Number(agg.totalRevenue || 0)
    const pendingOrders = Number(agg.pendingOrders || 0)
    const completedOrders = Number(agg.completedOrders || 0)
    const completionRate =
      totalOrders > 0 ? Number(((completedOrders / totalOrders) * 100).toFixed(1)) : 0
    
    // 转换为前端需要的格式
    const formattedOrders = orders.map(order => {
      const amountTRX = parseFloat(order.amount) || 0
      return {
        id: order.id,
        orderNumber: order.order_number,
        chatId: order.chat_id,
        username: order.username || 'N/A',
        nickname: order.username || 'N/A', // 暂时使用username作为nickname
        plan: order.plan || '未指定',
        amount: amountTRX,
        amountSun: Math.floor(amountTRX * 1000000), // TRX转SUN (1 TRX = 1,000,000 SUN)
        status: order.status,
        paymentMethod: order.payment_method,
        type: order.plan || 'energy',
        createdAt: order.created_at,
        updatedAt: order.updated_at
      }
    })
    
    return {
      success: true,
      data: formattedOrders,
      total: total,
      page: page,
      limit: limit,
      stats: {
        totalOrders,
        totalRevenue,
        pendingOrders,
        completionRate,
        // 暂时不做环比统计，先返回 0
        orderGrowth: 0,
        revenueGrowth: 0
      }
    }
  } catch (error) {
    console.error('读取订单数据失败:', error)
    return {
      success: false,
      error: '读取订单数据失败',
      data: [],
      total: 0
    }
  }
})