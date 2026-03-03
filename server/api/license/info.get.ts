import { executeQuery } from '../../utils/database'

export default defineEventHandler(async (event) => {
  try {
    const config = useRuntimeConfig()
    
    // 获取客户端真实IP地址
    const headers = getHeaders(event)
    const clientIp = headers['x-forwarded-for']?.split(',')[0].trim() 
      || headers['x-real-ip'] 
      || event.node.req.socket.remoteAddress 
      || 'localhost'
    
    // 标准化IP地址
    const normalizedIp = clientIp === '::1' || clientIp === '127.0.0.1' ? 'localhost' : clientIp

    // 直接从数据库查询激活的授权记录(不依赖环境变量)
    const licenseResult = await executeQuery(
      'SELECT * FROM licenses WHERE status = "active" ORDER BY activated_at DESC LIMIT 1',
      []
    ) as any[]

    if (licenseResult.length === 0) {
      // 没有激活的授权
      return {
        isActive: false,
        orderNumber: '',
        serverIp: normalizedIp,
        authorizedIps: [],
        message: '授权未激活，请使用订单号激活'
      }
    }

    const license = licenseResult[0]
    const orderNumber = license.order_number

    // 只返回当前服务器IP,不显示WordPress中的所有授权IP
    return {
      isActive: true,
      orderNumber: orderNumber,
      orderInfo: {
        orderId: license.order_id,
        customerEmail: license.email,
        customerName: license.customer_name,
        edition: license.license_type,
        activatedAt: license.activated_at,
        expiryDate: license.expiry_date
      },
      serverIp: normalizedIp,
      authorizedIps: [normalizedIp], // 只返回当前服务器IP
      message: '授权已激活'
    }
  } catch (error: any) {
    console.error('获取授权信息失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: '获取授权信息失败: ' + error.message
    })
  }
})
