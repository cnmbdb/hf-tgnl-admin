import { executeQuery } from '../utils/database'

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    const status = query.status as string || 'all'
    const page = parseInt(query.page as string) || 1
    const limit = parseInt(query.limit as string) || 10
    const offset = (page - 1) * limit

    // 构建查询条件
    let whereClause = '1=1'
    const params: any[] = []

    if (status && status !== 'all') {
      whereClause += ' AND status = ?'
      params.push(status)
    }

    // 查询用户总数
    const countSql = `SELECT COUNT(*) as total FROM tg_users WHERE ${whereClause}`
    const countResult = await executeQuery(countSql, params) as any[]
    const total = countResult[0]?.total || 0

    // 查询用户列表
    const sql = `
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
      FROM tg_users 
      WHERE ${whereClause}
      ORDER BY last_activity DESC, created_at DESC
      LIMIT ? OFFSET ?
    `
    params.push(limit, offset)
    const users = await executeQuery(sql, params) as any[]

    // 查询每个用户的余额（从transactions表）
    const usersWithBalance = await Promise.all(
      users.map(async (user) => {
        const balanceResult = await executeQuery(
          'SELECT amount FROM transactions WHERE chat_id = ? ORDER BY id DESC LIMIT 1',
          [user.tg_user_id]
        ) as any[]
        
        const balance = balanceResult[0]?.amount || 0
        const balanceTRX = (balance / 1000000).toFixed(2) // 转换为TRX

        // 格式化用户名
        const displayUsername = user.username 
          ? `@${user.username}` 
          : (user.first_name || `用户${user.tg_user_id}`)

        // 格式化会员类型
        const membershipMap: Record<string, string> = {
          'free': '免费用户',
          'vip': 'VIP会员',
          'premium': '高级会员'
        }
        const membership = membershipMap[user.membership_type] || '免费用户'

        // 格式化状态
        const statusMap: Record<string, string> = {
          'active': '活跃',
          'inactive': '非活跃',
          'banned': '已禁用'
        }
        const statusLabel = statusMap[user.status] || user.status

        return {
          id: user.id,
          tgUserId: user.tg_user_id,
          username: displayUsername,
          nickname: `${user.first_name || ''} ${user.last_name || ''}`.trim() || displayUsername,
          avatar: `https://avatars.githubusercontent.com/u/${user.id % 5 + 1}?v=4`, // 使用id生成头像
          membership,
          status: statusLabel,
          balance: balanceTRX,
          createdAt: user.created_at ? new Date(user.created_at).toISOString().split('T')[0] : '',
          lastActive: user.last_activity ? new Date(user.last_activity).toISOString().split('T')[0] : ''
        }
      })
    )

    return {
      success: true,
      data: usersWithBalance,
      total,
      page,
      limit
    }
  } catch (error: any) {
    console.error('获取用户列表失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: `获取用户列表失败: ${error.message || '未知错误'}`
    })
  }
})