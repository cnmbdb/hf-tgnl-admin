import { executeQuery } from '../../utils/database'
import { getWordPressOrder, getWordPressUserAuthorizedIPs, getServerPublicIP, verifyServerIP } from '../../utils/wordpress-auth'

/**
 * 从WordPress REST API获取订单信息 (已移至wordpress-auth.ts)
 */
async function _getWordPressOrder(orderNumber: string, productId: number) {
  const config = useRuntimeConfig()
  const wpUrl = config.WORDPRESS_URL as string
  const username = config.WORDPRESS_USERNAME as string
  const appPassword = config.WORDPRESS_APP_PASSWORD as string

  try {
    // 使用子比主题API查询订单
    const auth = Buffer.from(`${username}:${appPassword}`).toString('base64')
    const response = await $fetch(`${wpUrl}/wp-json/zibll/v1/order/${orderNumber}`, {
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json'
      }
    })

    console.log('[WordPress API] 订单查询成功:', response)

    // 验证订单状态和商品ID
    const order = response as any
    if (order.pay_status !== '1') {
      throw new Error('订单未支付')
    }

    if (order.product_id !== productId) {
      throw new Error(`商品ID不匹配，期望${productId}，实际${order.product_id}`)
    }

    return order
  } catch (error: any) {
    console.error('[WordPress API] 订单查询失败:', error)
    throw error
  }
}

/**
 * 从商品名称中获取授权时长
 */
function getProductDuration(productName: string): number {
  if (productName.includes('月')) {
    const match = productName.match(/(\d+)个?月/)
    if (match) {
      return parseInt(match[1]) * 30
    }
  }
  if (productName.includes('年')) {
    const match = productName.match(/(\d+)年/)
    if (match) {
      return parseInt(match[1]) * 365
    }
  }
  return 365 // 默认1年
}

/**
 * 计算到期日期
 */
function calculateExpiryDate(startDate: string, durationDays: number): string {
  const start = new Date(startDate)
  const expiry = new Date(start.getTime() + durationDays * 24 * 60 * 60 * 1000)
  return expiry.toISOString().split('T')[0]
}

/**
 * 从商品名称中获取版本信息
 */
function getEditionFromProduct(productName: string): string {
  if (productName.includes('企业版') || productName.includes('Enterprise')) {
    return '企业版'
  }
  if (productName.includes('专业版') || productName.includes('Professional')) {
    return '专业版'
  }
  if (productName.includes('基础版') || productName.includes('Basic')) {
    return '基础版'
  }
  return '标准版'
}

export default defineEventHandler(async (event) => {
  console.log('[订单验证] 开始处理验证请求')
  
  // 获取当前服务器IP
  let serverIp: string = 'unknown'
  try {
    serverIp = await getServerPublicIP()
  } catch (error) {
    console.warn('[订单验证] 无法获取服务器IP')
  }
  
  try {
    const body = await readBody(event)
    const { orderNumber } = body

    if (!orderNumber) {
      throw createError({
        statusCode: 400,
        statusMessage: '订单号不能为空'
      })
    }

    // 检查订单号是否已经被激活
    const existingLicense = await executeQuery(
      'SELECT * FROM licenses WHERE order_number = ?',
      [orderNumber]
    ) as any[]

    if (existingLicense.length > 0) {
      const license = existingLicense[0]
      let productInfo: any = {}
      try {
        productInfo = typeof license.product_info === 'string' 
          ? JSON.parse(license.product_info) 
          : (license.product_info || {})
      } catch (e) {
        productInfo = {}
      }
      
      // 检查授权状态
      const isActive = license.status === 'active'
      const activatedServerIp = license.server_ip || ''
      
      const ipVerification = {
        currentServerIP: serverIp,
        isAuthorized: serverIp === activatedServerIp || serverIp === 'unknown',
        authorizedIPs: activatedServerIp ? [activatedServerIp] : [],
        currentCount: activatedServerIp ? 1 : 0,
        maxCount: 4,
        // 如果状态是 inactive，允许重新激活
        canActivate: !isActive,
        message: isActive ? '订单已激活' : '订单需要重新激活'
      }
      
      return {
        valid: true,
        message: isActive ? '订单已激活' : '订单需要重新激活',
        activated: isActive,
        needReactivate: !isActive,
        license: {
          orderId: license.order_id,
          orderNumber: license.order_number,
          customerEmail: license.email,
          customerName: license.customer_name,
          edition: productInfo.edition || '标准版',
          duration: productInfo.duration_days || 365,
          expiryDate: license.expiry_date,
          activatedAt: license.activated_at,
          status: license.status
        },
        ipVerification
      }
    }

    // 从WordPress REST API验证订单
    const config = useRuntimeConfig()
    const productId = parseInt(process.env.WORDPRESS_PRODUCT_ID || config.WORDPRESS_PRODUCT_ID as string || '2061')

    let orderInfo: any
    try {
      orderInfo = await getWordPressOrder(orderNumber, productId)
    } catch (e: any) {
      const bypass = (process.env.LICENSE_DEV_BYPASS === 'true') && (process.env.NODE_ENV !== 'production')
      const code = e?.statusCode || 0
      const msg = e?.statusMessage || e?.message || ''
      if (bypass && (msg.includes('连接被拒绝') || code === 502)) {
        const now = new Date().toISOString()
        orderInfo = {
          order_id: 0,
          user_email: 'dev@example.com',
          user_name: 'Dev',
          product_name: '标准版 1年',
          pay_time: now,
          user_id: 0,
          product_id: productId,
          status: '1'
        }
      } else {
        throw e
      }
    }

    if (!orderInfo) {
      return {
        valid: false,
        message: '订单不存在或验证失败'
      }
    }

    // 计算授权信息
    const productName = orderInfo.product_name || ''
    const duration = getProductDuration(productName)
    const payTime = orderInfo.pay_time || new Date().toISOString()
    const expiryDate = calculateExpiryDate(payTime, duration)
    const edition = getEditionFromProduct(productName)

    // 获取用户在WordPress设置的授权IP列表
    const userId = orderInfo.user_id
    let authorizedIPs: string[] = []
    if (userId) {
      try {
        authorizedIPs = await getWordPressUserAuthorizedIPs(userId)
      } catch (error) {
        console.warn('[订单验证] 获取用户授权IP失败')
      }
    }

    // 验证当前服务器IP是否在授权列表中
    let ipVerification = {
      currentServerIP: serverIp,
      isAuthorized: false,
      authorizedIPs: authorizedIPs.length > 0 ? authorizedIPs : [serverIp], // 返回完整授权IP列表
      currentCount: authorizedIPs.length,
      maxCount: 4,
      canActivate: false,
      message: ''
    }

    if (serverIp !== 'unknown') {
      // 检查IP是否在授权列表中
      ipVerification.isAuthorized = authorizedIPs.includes(serverIp)
      
      if (authorizedIPs.length >= 4 && !ipVerification.isAuthorized) {
        ipVerification.canActivate = false
        ipVerification.message = `已达到最大授权数量(4个)，当前服务器IP (${serverIp}) 未在授权列表中`
      } else if (ipVerification.isAuthorized) {
        ipVerification.canActivate = true
        ipVerification.message = `当前服务器IP (${serverIp}) 已在授权列表中，可以激活`
      } else {
        ipVerification.canActivate = false
        ipVerification.message = `当前服务器IP (${serverIp}) 未在授权列表中，请在WordPress用户资料的"网站"字段中添加此IP`
      }
    } else {
      ipVerification.canActivate = false
      ipVerification.message = '无法获取服务器IP，请检查网络连接'
    }

    return {
      valid: true,
      message: '订单验证成功',
      license: {
        orderId: orderInfo.order_id,
        orderNumber: orderNumber,
        customerEmail: orderInfo.user_email,
        customerName: orderInfo.user_name,
        edition: edition,
        duration: duration,
        expiryDate: expiryDate,
        activatedAt: payTime
      },
      ipVerification
    }
  } catch (error: any) {
    console.error('WordPress订单验证失败:', error)
    const statusMessage = error?.statusMessage || error?.message || '未知错误'
    return {
      valid: false,
      message: `验证失败: ${statusMessage}`
    }
  }
})
