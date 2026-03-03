/**
 * WordPress授权相关工具函数
 */
/**
 * 从 WordPress获取用户授权的IP列表
 * @param userId WordPress用户ID
 * @returns 授权IP列表(最外4个)
 */
export async function getWordPressUserAuthorizedIPs(userId: number): Promise<string[]> {
  const config = useRuntimeConfig()
  // 优先使用环境变量,fallback到runtimeConfig
  const wpUrl = process.env.WORDPRESS_URL || (config.WORDPRESS_URL as string)
  const username = process.env.WORDPRESS_USERNAME || (config.WORDPRESS_USERNAME as string)
  const appPassword = process.env.WORDPRESS_APP_PASSWORD || (config.WORDPRESS_APP_PASSWORD as string)

  if (!wpUrl || !username || !appPassword) {
    throw createError({ statusCode: 500, statusMessage: 'WordPress 配置缺失' })
  }

  try {
    const auth = Buffer.from(`${username}:${appPassword}`).toString('base64')
    const response = await $fetch(`${wpUrl}/wp-json/wp/v2/users/${userId}?context=edit`, {
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json'
      },
      timeout: 5000,
      retry: 1
    })

    const user = response as any
    
    // 收集所有可能的IP来源
    let allIPs: string[] = []
    
    // 1. 从 user_url 字段获取(支持逗号或换行分隔)
    const websiteField = user.url || ''
    if (websiteField) {
      const ips = websiteField
        .split(/[,\n\r]+/)
        .map((ip: string) => cleanIP(ip))
        .filter((ip: string) => ip.length > 0)
      allIPs.push(...ips)
    }
    
    // 2. 从 meta 字段获取 (WordPress 插件存储的 websites)
    if (user.meta && user.meta.websites) {
      const websites = Array.isArray(user.meta.websites) ? user.meta.websites : [user.meta.websites]
      const ips = websites
        .map((ip: string) => cleanIP(ip))
        .filter((ip: string) => ip.length > 0)
      allIPs.push(...ips)
    }
    
    // 去重并过滤无效IP
    const uniqueIPs = Array.from(new Set(allIPs))
      .filter(ip => isValidIPOrHost(ip))
      .slice(0, 4) // 最外4个IP
    
    return uniqueIPs
  } catch (error: any) {
    const code = error?.code || error?.name || ''
    const msg = code === 'ECONNREFUSED' ? 'WordPress 连接被拒绝' : '获取用户授权IP失败'
    throw createError({ statusCode: 502, statusMessage: msg })
  }
}

/**
 * 清理IP地址(移除协议、端口等)
 */
function cleanIP(ip: string): string {
  if (!ip) return ''
  // 移除协议前缀
  let clean = ip.replace(/^https?:\/\//i, '')
  // 移除端口和路径
  clean = clean.replace(/:\d+.*$/, '')
  clean = clean.replace(/\/.*$/, '')
  // 处理IPv6映射
  if (clean.startsWith('::ffff:')) {
    clean = clean.substring(7)
  }
  return clean.trim()
}

/**
 * 验证IP格式是否有效
 */
export function isValidIP(ip: string): boolean {
  // IPv4格式验证
  const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/
  if (ipv4Regex.test(ip)) {
    const parts = ip.split('.')
    return parts.every(part => parseInt(part) >= 0 && parseInt(part) <= 255)
  }
  
  // IPv6格式验证(简单版)
  const ipv6Regex = /^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$/
  return ipv6Regex.test(ip)
}

/**
 * 验证IP或主机名
 */
function isValidIPOrHost(ip: string): boolean {
  // localhost
  if (ip === 'localhost' || ip === '127.0.0.1' || ip === '0.0.0.0') {
    return true
  }
  // IP地址
  return isValidIP(ip)
}

/**
 * 从WordPress REST API获取订单信息
 */
export async function getWordPressOrder(orderNumber: string, productId: number) {
  const config = useRuntimeConfig()
  // 优先使用环境变量,fallback到runtimeConfig
  const wpUrl = process.env.WORDPRESS_URL || (config.WORDPRESS_URL as string)
  const username = process.env.WORDPRESS_USERNAME || (config.WORDPRESS_USERNAME as string)
  const appPassword = process.env.WORDPRESS_APP_PASSWORD || (config.WORDPRESS_APP_PASSWORD as string)

  if (!wpUrl || !username || !appPassword) {
    throw createError({ statusCode: 500, statusMessage: 'WordPress 配置缺失' })
  }

  try {
    const auth = Buffer.from(`${username}:${appPassword}`).toString('base64')
    const response = await $fetch(`${wpUrl}/wp-json/zibll/v1/order/${orderNumber}`, {
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json'
      },
      timeout: 5000,
      retry: 1
    })

    const order = response as any
    // 注意: 子比主题的status字段, 1表示已支付
    if (order.status !== '1' && order.status !== 1) {
      throw new Error('订单未支付')
    }

    if (order.product_id !== productId) {
      throw new Error(`商品ID不匹配，期望${productId}，实际${order.product_id}`)
    }

    return order
  } catch (error: any) {
    const code = error?.code || error?.name || ''
    const msg = code === 'ECONNREFUSED' ? 'WordPress 连接被拒绝' : (error?.message || '订单查询失败')
    throw createError({ statusCode: 502, statusMessage: msg })
  }
}

/**
 * 验证服务器IP是否在用户授权列表中
 */
export async function verifyServerIP(orderNumber: string, serverIp: string): Promise<{
  valid: boolean
  message: string
  authorizedIPs: string[]
  currentCount: number
}> {
  const config = useRuntimeConfig()
  
  // 优先使用环境变量,fallback到runtimeConfig
  const wpUrl = process.env.WORDPRESS_URL || (config.WORDPRESS_URL as string)
  const username = process.env.WORDPRESS_USERNAME || (config.WORDPRESS_USERNAME as string)
  const appPassword = process.env.WORDPRESS_APP_PASSWORD || (config.WORDPRESS_APP_PASSWORD as string)

  if (!wpUrl || !username || !appPassword) {
    return {
      valid: false,
      message: 'WordPress 配置缺失',
      authorizedIPs: [],
      currentCount: 0
    }
  }
  
  try {
    const auth = Buffer.from(`${username}:${appPassword}`).toString('base64')
    const verifyResponse: any = await $fetch(`${wpUrl}/wp-json/zibll/v1/verify-server`, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json'
      },
      body: {
        order_num: orderNumber,
        server_ip: serverIp
      },
      timeout: 5000,
      retry: 1
    })
    
    return {
      valid: true,
      message: 'IP验证通过',
      authorizedIPs: verifyResponse.allowed || [],
      currentCount: verifyResponse.allowed?.length || 0
    }
  } catch (verifyError: any) {
    const code = verifyError?.code || verifyError?.name || ''
    if (code === 'ECONNREFUSED') {
      return {
        valid: false,
        message: 'WordPress 连接被拒绝',
        authorizedIPs: [],
        currentCount: 0
      }
    }
    const errorData = verifyError?.data || {}
    const allowedIPs = errorData.allowed || []
    return {
      valid: false,
      message: `当前服务器IP (${serverIp}) 未在授权列表中`,
      authorizedIPs: allowedIPs,
      currentCount: allowedIPs.length
    }
  }
}

/**
 * 自动获取服务器的公网IP
 * 注意：必须通过实际网络请求获取，不允许使用环境变量配置，以确保授权安全
 */
export async function getServerPublicIP(): Promise<string> {
  const services = [
    { url: 'https://api.ipify.org?format=json', type: 'json' },
    { url: 'https://ipinfo.io/ip', type: 'text' },
    { url: 'https://api.ip.sb/ip', type: 'text' },
    { url: 'https://ifconfig.me/ip', type: 'text' },
    { url: 'https://icanhazip.com', type: 'text' },
    { url: 'https://checkip.amazonaws.com', type: 'text' }
  ]
  
  for (const service of services) {
    try {
      const response = await $fetch(service.url, { 
        timeout: 5000,
        retry: 0
      })
      let ip = ''
      
      if (typeof response === 'string') {
        ip = response.trim()
      } else if (response && typeof response === 'object' && 'ip' in response) {
        ip = (response as any).ip
      }
      
      // 过滤掉私有IP（Docker内网等）
      if (ip && isValidIP(ip) && !isPrivateIP(ip)) {
        console.log('[getServerPublicIP] 从', service.url, '获取到公网IP:', ip)
        return ip
      }
    } catch (error) {
      console.warn('[getServerPublicIP] 从', service.url, '获取IP失败')
      continue
    }
  }
  
  throw new Error('无法获取服务器公网IP')
}

/**
 * 检查是否为私有IP地址
 */
function isPrivateIP(ip: string): boolean {
  const parts = ip.split('.').map(Number)
  if (parts.length !== 4) return false
  
  // 10.0.0.0 - 10.255.255.255
  if (parts[0] === 10) return true
  
  // 172.16.0.0 - 172.31.255.255
  if (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) return true
  
  // 192.168.0.0 - 192.168.255.255
  if (parts[0] === 192 && parts[1] === 168) return true
  
  // 127.0.0.0 - 127.255.255.255 (loopback)
  if (parts[0] === 127) return true
  
  // 169.254.0.0 - 169.254.255.255 (link-local)
  if (parts[0] === 169 && parts[1] === 254) return true
  
  return false
}
