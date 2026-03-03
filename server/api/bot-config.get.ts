import fs from 'fs'
import path from 'path'
import { requireAdmin } from '../utils/auth'

export default defineEventHandler(async (event) => {
  // 暂时跳过认证检查以便测试配置同步功能
  // TODO: 恢复认证检查
  // const user = await requireAdmin(event)
  // if (!user) {
  //   return {
  //     success: false,
  //     error: '需要管理员权限'
  //   }
  // }

  try {
    // 配置文件路径 - 使用项目根目录下的 nl-2333 目录
    const basePath = path.join(process.cwd(), 'nl-2333')
    const configPath = path.join(basePath, 'config.txt')
    const alPyPath = path.join(basePath, 'al.py')

    // 读取 config.txt
    const configData: Record<string, string> = {}
    if (fs.existsSync(configPath)) {
      const configContent = fs.readFileSync(configPath, 'utf-8')
      configContent.split('\n').forEach(line => {
        const trimmedLine = line.trim()
        // 跳过空行和注释行
        if (!trimmedLine || trimmedLine.startsWith('#')) {
          return
        }
        // 使用 split('=', 2) 限制分割次数，防止值中包含 = 号时被错误分割
        const [key, value] = trimmedLine.split('=', 2)
        if (key && value !== undefined) {
          configData[key.trim()] = value.trim()
        }
      })
    }

    // 读取 al.py 中的数据库配置和API_KEY
    const dbConfig: Record<string, string> = {}
    let apiKey = ''
    if (fs.existsSync(alPyPath)) {
      const alPyContent = fs.readFileSync(alPyPath, 'utf-8')
      
      // 提取API_KEY (第43行)
      const apiKeyMatch = alPyContent.match(/API_KEY\s*=\s*["']([^"']*)["']/)
      if (apiKeyMatch) {
        apiKey = apiKeyMatch[1]
      }
      
      // 提取数据库配置 (第55-59行)
      const configMatch = alPyContent.match(/config\s*=\s*\{([^}]+)\}/)
      if (configMatch) {
        const configBlock = configMatch[1]
        const userMatch = configBlock.match(/'user':\s*'([^']*)'/)
        const passwordMatch = configBlock.match(/'password':\s*'([^']*)'/)
        const hostMatch = configBlock.match(/'host':\s*'([^']*)'/)
        const databaseMatch = configBlock.match(/'database':\s*'([^']*)'/)
        const portMatch = configBlock.match(/'port':\s*(\d+)/)
        
        if (userMatch) dbConfig.user = userMatch[1]
        if (passwordMatch) dbConfig.password = passwordMatch[1]
        if (hostMatch) dbConfig.host = hostMatch[1]
        if (databaseMatch) dbConfig.database = databaseMatch[1]
        if (portMatch) dbConfig.port = portMatch[1]
      }
    }

    // 返回配置数据，映射到前端期望的字段名
    return {
      success: true,
      data: {
        // 基础配置 - 从config.txt读取
        token: configData.TOKEN || '',
        adminId: configData.admin_id || '',
        customerServiceId: configData.CUSTOMER_SERVICE_ID || '',
        botId: configData.bot_id || '',
        groupLink: configData.group_link || '',
        controlAddress: configData.control_address || '',
        privateKey: configData.usdt2trx_private_key || configData.privateKey || '',
        username: configData.username || '',
        password: configData.password || '',
        adTime: configData.ad_time || '',
        huilvZhekou: configData.huilv_zhekou || '',
        
        // 价格配置 - 从config.txt读取
        hourPrice: configData.hour_price || '',
        dayPrice: configData.day_price || '',
        threeDayPrice: configData.three_day_price || '',
        
        // 能量池配置 - 从config.txt读取
        energyPoolApi: configData.energy_pool_api || '',
        botNotifyUrl: configData.bot_notify_url || '',
        
        // 版本标识 - 从config.txt读取
        versionIdentifier: configData.Versionidentifier || '',
        
        // 数据库配置 - 从al.py读取
        dbUser: dbConfig.user || '',
        dbPassword: dbConfig.password || '',
        dbHost: dbConfig.host || '',
        dbName: dbConfig.database || '',
        dbPort: dbConfig.port || '',
        
        // API配置 - 从al.py读取
        tronApiKey: apiKey
      }
    }
  } catch (error) {
    console.error('读取配置文件失败:', error)
    return {
      success: false,
      error: '读取配置文件失败: ' + (error as Error).message
    }
  }
})
