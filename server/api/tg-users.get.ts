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
    console.log('TG用户API调用 (基于tg_users表)')
    const query = getQuery(event)
    const page = Math.max(1, parseInt(query.page as string) || 1)
    const limit = Math.max(1, Math.min(100, parseInt(query.limit as string) || 10)) // 限制在1-100之间
    const search = query.search as string || ''
    const status = query.status as string || ''
    
    const offset = Math.max(0, (page - 1) * limit) // 确保offset >= 0
    
    // 构建WHERE条件（使用参数化查询防止SQL注入）
    let whereConditions: string[] = []
    const params: any[] = []
    
    if (search) {
      whereConditions.push(`(
        CAST(tg.tg_user_id AS CHAR) LIKE ? OR 
        tg.username LIKE ? OR 
        tg.first_name LIKE ? OR 
        tg.last_name LIKE ?
      )`)
      const searchPattern = `%${search}%`
      params.push(searchPattern, searchPattern, searchPattern, searchPattern)
    }
    if (status) {
      whereConditions.push(`tg.status = ?`)
      params.push(status)
    }
    const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : ''
    
    // 获取总用户数
    const countQuery = `
      SELECT COUNT(*) as total 
      FROM tg_users tg
      ${whereClause}
    `
    console.log('Count query:', countQuery, 'Params:', params)
    const countResult = await executeQuery(countQuery, params) as any[]
    const total = countResult[0]?.total || 0
    
    // 获取用户列表 - 先查询用户，再查询余额（避免复杂子查询的参数化问题）
    // 注意：LIMIT和OFFSET必须使用整数，不能使用参数化查询
    const usersQuery = `
      SELECT 
        id,
        tg_user_id,
        username,
        first_name,
        last_name,
        status,
        membership_type,
        last_activity,
        created_at,
        updated_at
      FROM tg_users tg
      ${whereClause}
      ORDER BY last_activity DESC, created_at DESC
      LIMIT ${limit} OFFSET ${offset}
    `
    console.log('Users query:', usersQuery, 'Params:', params)
    const usersResult = await executeQuery(usersQuery, params) as any[]
    
    // 为每个用户查询最新余额
    const usersWithBalance = await Promise.all(
      usersResult.map(async (user) => {
        const balanceResult = await executeQuery(
          'SELECT amount FROM transactions WHERE chat_id = ? ORDER BY id DESC LIMIT 1',
          [user.tg_user_id]
        ) as any[]
        const balance = balanceResult[0]?.amount || 0
        return {
          ...user,
          balance: parseFloat(balance) || 0
        }
      })
    )
    
    // 格式化用户数据
    const users = usersWithBalance.map(user => ({
      id: user.id,
      tg_user_id: user.tg_user_id,
      username: user.username || `TG用户_${user.tg_user_id}`,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      status: user.status || 'active',
      membership_type: user.membership_type || 'free',
      balance: parseFloat(user.balance) || 0,
      last_activity: user.last_activity || user.created_at,
      created_at: user.created_at,
      updated_at: user.updated_at || user.created_at
    }))
    
    // 获取统计数据
    const statsQuery = `
      SELECT 
        COUNT(*) as total_users,
        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count,
        COUNT(CASE WHEN DATE(created_at) = CURDATE() THEN 1 END) as today_new_users,
        COUNT(CASE WHEN membership_type = 'vip' OR membership_type = 'premium' THEN 1 END) as vip_users
      FROM tg_users
    `
    const statsResult = await executeQuery(statsQuery) as any[]
    const stats = statsResult[0]
    
    return {
      success: true,
      data: {
        users,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit)
        },
        stats: stats
      }
    }
  } catch (error: any) {
    console.error('Error fetching TG users from transactions:', error)
    return {
      success: false,
      error: error.message,
      data: {
        users: [],
        pagination: {
          page: 1,
          limit: 10,
          total: 0,
          totalPages: 0
        },
        stats: {
          total_users: 0,
          active_count: 0,
          today_new_users: 0
        }
      }
    }
  }
})