import { executeQuery } from '../../utils/database'

/**
 * 快速检查授权状态
 */
export default defineEventHandler(async (event) => {
  try {
    // 查询是否有激活的授权
    const licenses = await executeQuery(
      'SELECT * FROM licenses WHERE status = ? LIMIT 1',
      ['active']
    ) as any[]

    if (licenses.length > 0) {
      const license = licenses[0]
      
      // 检查是否过期
      const expiryDate = new Date(license.expiry_date)
      const now = new Date()
      
      if (expiryDate < now) {
        return {
          isActive: false,
          isExpired: true,
          message: '授权已过期'
        }
      }

      return {
        isActive: true,
        isExpired: false,
        orderNumber: license.order_number,
        expiryDate: license.expiry_date,
        message: '授权有效'
      }
    }

    return {
      isActive: false,
      isExpired: false,
      message: '未激活授权'
    }
  } catch (error) {
    console.error('检查授权状态失败:', error)
    return {
      isActive: false,
      isExpired: false,
      message: '授权状态检查失败'
    }
  }
})
