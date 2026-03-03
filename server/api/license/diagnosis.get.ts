import { executeQuery } from '../../utils/database'
import { getServerPublicIP, verifyServerIP } from '../../utils/wordpress-auth'

/**
 * 授权诊断API - 检查授权失效原因
 */
export default defineEventHandler(async (event) => {
  try {
    const diagnosis: any = {
      timestamp: new Date().toISOString(),
      serverIp: '',
      licenseStatus: 'unknown',
      issues: [],
      recommendations: []
    }

    // 1. 获取服务器IP
    try {
      diagnosis.serverIp = await getServerPublicIP()
    } catch (error: any) {
      diagnosis.issues.push({
        type: 'server_ip',
        severity: 'high',
        message: '无法获取服务器公网IP',
        details: error.message
      })
      diagnosis.recommendations.push('请检查服务器网络连接，确保可以访问公网IP查询服务')
    }

    // 2. 查询当前授权状态
    const licenses = await executeQuery(
      'SELECT * FROM licenses ORDER BY activated_at DESC LIMIT 1',
      []
    ) as any[]

    if (licenses.length === 0) {
      diagnosis.licenseStatus = 'not_found'
      diagnosis.issues.push({
        type: 'no_license',
        severity: 'high',
        message: '未找到任何授权记录'
      })
      diagnosis.recommendations.push('请使用订单号激活授权')
      return diagnosis
    }

    const license = licenses[0]
    diagnosis.licenseStatus = license.status
    diagnosis.license = {
      orderNumber: license.order_number,
      status: license.status,
      activatedAt: license.activated_at,
      expiryDate: license.expiry_date
    }

    // 3. 检查授权是否过期
    if (license.expiry_date) {
      const expiryDate = new Date(license.expiry_date)
      const now = new Date()
      if (expiryDate < now) {
        diagnosis.issues.push({
          type: 'expired',
          severity: 'high',
          message: '授权已过期',
          details: `过期时间: ${expiryDate.toISOString()}`
        })
        diagnosis.recommendations.push('授权已过期，请联系管理员续费')
      } else {
        const daysLeft = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
        diagnosis.license.daysLeft = daysLeft
      }
    }

    // 4. 如果授权状态不是 active，查询历史记录找出原因
    if (license.status !== 'active') {
      const history = await executeQuery(
        'SELECT * FROM license_history WHERE order_number = ? ORDER BY created_at DESC LIMIT 10',
        [license.order_number]
      ) as any[]

      diagnosis.history = history.map((h: any) => ({
        action: h.action,
        serverIp: h.server_ip,
        details: h.details,
        createdAt: h.created_at
      }))

      // 分析最近的历史记录
      if (history.length > 0) {
        const lastAction = history[0]
        if (lastAction.action === 'deactivate') {
          diagnosis.issues.push({
            type: 'deactivated',
            severity: 'high',
            message: '授权已被停用',
            details: lastAction.details,
            timestamp: lastAction.created_at
          })

          if (lastAction.details === '无法获取服务器IP') {
            diagnosis.recommendations.push('无法获取服务器IP，请检查服务器网络连接')
          } else if (lastAction.details === '每日校验未通过') {
            diagnosis.issues.push({
              type: 'ip_verification_failed',
              severity: 'high',
              message: 'IP验证失败',
              details: `服务器IP (${lastAction.server_ip}) 未在WordPress授权列表中`
            })
            diagnosis.recommendations.push(`请在WordPress用户资料中添加服务器IP: ${diagnosis.serverIp || lastAction.server_ip}`)
          }
        } else if (lastAction.action === 'expire') {
          diagnosis.issues.push({
            type: 'expired',
            severity: 'high',
            message: '授权已过期',
            timestamp: lastAction.created_at
          })
        }
      }
    }

    // 5. 如果授权是 active，验证IP是否在授权列表中
    if (license.status === 'active' && diagnosis.serverIp) {
      try {
        const verifyResult = await verifyServerIP(license.order_number, diagnosis.serverIp)
        diagnosis.ipVerification = {
          valid: verifyResult.valid,
          authorizedIPs: verifyResult.authorizedIPs,
          currentCount: verifyResult.currentCount,
          message: verifyResult.message
        }

        if (!verifyResult.valid) {
          diagnosis.issues.push({
            type: 'ip_not_authorized',
            severity: 'high',
            message: '当前服务器IP未在授权列表中',
            details: `当前IP: ${diagnosis.serverIp}, 已授权IP: ${verifyResult.authorizedIPs.join(', ') || '无'}`
          })
          diagnosis.recommendations.push(`请在WordPress用户资料中添加服务器IP: ${diagnosis.serverIp}`)
        }
      } catch (error: any) {
        diagnosis.issues.push({
          type: 'ip_verification_error',
          severity: 'medium',
          message: 'IP验证过程出错',
          details: error.message
        })
      }
    }

    // 6. 检查WordPress配置
    const config = useRuntimeConfig()
    const wpUrl = process.env.WORDPRESS_URL || (config.WORDPRESS_URL as string)
    const username = process.env.WORDPRESS_USERNAME || (config.WORDPRESS_USERNAME as string)
    const appPassword = process.env.WORDPRESS_APP_PASSWORD || (config.WORDPRESS_APP_PASSWORD as string)

    if (!wpUrl || !username || !appPassword) {
      diagnosis.issues.push({
        type: 'wordpress_config_missing',
        severity: 'high',
        message: 'WordPress配置缺失'
      })
      diagnosis.recommendations.push('请配置 WORDPRESS_URL, WORDPRESS_USERNAME, WORDPRESS_APP_PASSWORD 环境变量')
    }

    return diagnosis
  } catch (error: any) {
    console.error('授权诊断失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: '授权诊断失败: ' + error.message
    })
  }
})
