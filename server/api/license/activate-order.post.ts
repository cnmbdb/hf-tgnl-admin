import { executeQuery } from '../../utils/database'
import { getWordPressOrder, getWordPressUserAuthorizedIPs, getServerPublicIP, verifyServerIP } from '../../utils/wordpress-auth'

export default defineEventHandler(async (event) => {
  console.log('[激活订单] 开始处理激活请求')
  
  // 获取当前服务器的公网IP
  let serverIp: string
  try {
    serverIp = await getServerPublicIP()
  } catch (error) {
    throw createError({
      statusCode: 500,
      statusMessage: '无法获取服务器公网IP，请检查网络连接'
    })
  }
  
  console.log('[激活订单] 当前服务器IP:', serverIp)

  try {
    const body = await readBody(event)
    const { orderNumber } = body

    if (!orderNumber) {
      throw createError({
        statusCode: 400,
        statusMessage: '订单号不能为空'
      })
    }

    // 检查订单号是否已经存在于数据库
    const existingLicense = await executeQuery(
      'SELECT * FROM licenses WHERE order_number = ?',
      [orderNumber]
    ) as any[]

    // 如果已存在,检查状态
    if (existingLicense.length > 0) {
      const license = existingLicense[0]
      
      // 如果状态是 active，直接返回成功
      if (license.status === 'active') {
        console.log('[激活] 订单已激活且状态正常')
        return {
          success: true,
          message: '订单已激活',
          license: {
            id: license.order_id,
            orderNumber: orderNumber,
            edition: getEditionFromProduct(license.license_type),
            expiryDate: license.expiry_date,
            activatedAt: license.activated_at
          }
        }
      }
      
      // 如果状态是 inactive 或 expired，允许重新激活
      console.log('[激活] 订单存在但状态为', license.status, '，尝试重新激活')
      
      // 验证IP授权（复用下面的逻辑）
      const config = useRuntimeConfig()
      const productId = parseInt(process.env.WORDPRESS_PRODUCT_ID || config.WORDPRESS_PRODUCT_ID as string || '2061')
      
      let orderInfo: any
      try {
        orderInfo = await getWordPressOrder(orderNumber, productId)
      } catch (e: any) {
        // 如果WordPress查询失败，使用已存储的订单信息直接重新激活
        console.log('[激活] WordPress查询失败，使用已存储信息重新激活')
        await executeQuery(
          'UPDATE licenses SET status = "active", activated_at = NOW() WHERE order_number = ?',
          [orderNumber]
        )
        await executeQuery(
          'INSERT INTO license_history (order_number, action, server_ip, details, created_at) VALUES (?, "activate", ?, ?, NOW())',
          [orderNumber, serverIp, '重新激活授权（使用已存储信息）']
        )
        return {
          success: true,
          message: '授权重新激活成功',
          license: {
            id: license.order_id,
            orderNumber: orderNumber,
            edition: getEditionFromProduct(license.license_type),
            expiryDate: license.expiry_date,
            activatedAt: new Date().toISOString()
          }
        }
      }
      
      // 获取用户授权IP列表
      const userId = orderInfo.user_id
      let authorizedIPs: string[] = []
      if (userId) {
        try {
          authorizedIPs = await getWordPressUserAuthorizedIPs(userId)
        } catch {}
      }
      
      // 验证IP授权
      if (authorizedIPs.length > 0 && !authorizedIPs.includes(serverIp)) {
        if (authorizedIPs.length >= 4) {
          throw createError({
            statusCode: 403,
            statusMessage: `授权失败：已达到最大IP数量(4个)。当前服务器IP (${serverIp}) 未在授权列表中。`
          })
        } else {
          throw createError({
            statusCode: 403,
            statusMessage: `授权失败：当前服务器IP (${serverIp}) 未在授权列表中。请在WordPress用户资料中添加此IP。`
          })
        }
      }
      
      // 重新激活
      await executeQuery(
        'UPDATE licenses SET status = "active", activated_at = NOW() WHERE order_number = ?',
        [orderNumber]
      )
      await executeQuery(
        'INSERT INTO license_history (order_number, action, server_ip, details, created_at) VALUES (?, "activate", ?, ?, NOW())',
        [orderNumber, serverIp, '重新激活授权']
      )
      
      return {
        success: true,
        message: '授权重新激活成功',
        license: {
          id: license.order_id,
          orderNumber: orderNumber,
          edition: getEditionFromProduct(license.license_type),
          expiryDate: license.expiry_date,
          activatedAt: new Date().toISOString()
        }
      }
    }

    const config = useRuntimeConfig()
    const productId = parseInt(process.env.WORDPRESS_PRODUCT_ID || config.WORDPRESS_PRODUCT_ID as string || '2061')

    console.log('[激活] 正在查询订单:', orderNumber)
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
          status: '1',
          pay_price: 0
        }
      } else {
        throw e
      }
    }

    if (!orderInfo) {
      throw createError({
        statusCode: 400,
        statusMessage: '订单不存在或验证失败'
      })
    }

    console.log('[激活] 订单验证成功:', orderInfo)

    // 获取用户设置的授权IP列表
    const userId = orderInfo.user_id
    let authorizedIPs: string[] = []
    if (userId) {
      authorizedIPs = await getWordPressUserAuthorizedIPs(userId)
    }

    // 验证IP授权
    console.log('[激活] 开始验证IP授权')
    console.log(`[激活] 当前服务器IP: ${serverIp}`)
    console.log(`[激活] 用户授权IP列表: ${authorizedIPs.join(', ') || '无'}`)
    console.log(`[激活] 当前IP数量: ${authorizedIPs.length}/4`)

    // 检查IP是否在授权列表中
    if (!authorizedIPs.includes(serverIp)) {
      if (authorizedIPs.length >= 4) {
        throw createError({
          statusCode: 403,
          statusMessage: `授权失败：已达到最大IP数量(4个)。当前服务器IP (${serverIp}) 未在授权列表中。已授权IP: ${authorizedIPs.join(', ')}`
        })
      } else {
        throw createError({
          statusCode: 403,
          statusMessage: `授权失败：当前服务器IP (${serverIp}) 未在授权列表中。请在WordPress用户资料的"网站"字段中添加此IP。当前已授权IP (${authorizedIPs.length}/4): ${authorizedIPs.join(', ') || '无'}`
        })
      }
    }

    console.log('[激活] IP验证通过')

    // 验证通过后继续处理

    // 计算授权时长和到期日期
    const productName = orderInfo.product_name || ''
    const duration = getProductDuration(productName)
    const payTime = orderInfo.pay_time || new Date().toISOString()
    const expiryDate = calculateExpiryDate(payTime, duration)
    const edition = getEditionFromProduct(productName)

    // 保存授权记录到数据库(使用现有表结构)
    await executeQuery(
      `INSERT INTO licenses (
        order_number, 
        order_id, 
        email, 
        customer_name, 
        product_info,
        license_type,
        expiry_date, 
        activated_at,
        status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')`,
      [
        orderNumber,
        orderInfo.order_id,
        orderInfo.user_email,
        orderInfo.user_name,
        JSON.stringify({
          product_name: orderInfo.product_name,
          edition: edition,
          duration_days: duration,
          price: orderInfo.pay_price
        }),
        duration >= 365 ? 'yearly' : 'monthly',
        expiryDate,
        payTime
      ]
    )

    // 记录授权历史
    await executeQuery(
      `INSERT INTO license_history (
        order_number,
        action,
        server_ip,
        details,
        created_at
      ) VALUES (?, 'activate', ?, ?, NOW())`,
      [
        orderNumber,
        serverIp,
        `使用WordPress订单 #${orderInfo.order_id} 激活授权`
      ]
    )

    return {
      success: true,
      message: '授权激活成功',
      license: {
        id: orderInfo.order_id,
        orderNumber: orderNumber,
        edition: edition,
        expiryDate: expiryDate,
        activatedAt: new Date().toISOString()
      }
    }
  } catch (error: any) {
    console.error('订单激活失败:', error)
    const statusMessage = error?.statusMessage || error?.message || '未知错误'
    throw createError({
      statusCode: 500,
      statusMessage: '激活失败: ' + statusMessage
    })
  }
})

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
