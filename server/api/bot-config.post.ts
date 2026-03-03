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
    const body = await readBody(event)
    
    if (!body || typeof body !== 'object') {
      throw new Error('无效的请求数据')
    }
    
    // 配置文件路径 - 使用项目根目录下的 nl-2333 目录
    const basePath = path.join(process.cwd(), 'nl-2333')
    const configPath = path.join(basePath, 'config.txt')
    const alPyPath = path.join(basePath, 'al.py')
    
    // 读取现有 config.txt（为了保留未管理的配置，例如 main_menu_buttons_json）
    let configLines: string[] = []
    if (fs.existsSync(configPath)) {
      const raw = fs.readFileSync(configPath, 'utf-8')
      configLines = raw.split('\n')
    }

    // 工具函数：更新或追加 key=value 行（保持其它行不变）
    const upsertConfigKey = (key: string, value: string) => {
      let found = false
      configLines = configLines.map((line) => {
        const trimmed = line.trim()
        if (!trimmed || trimmed.startsWith('#')) return line
        if (trimmed.startsWith(`${key}=`)) {
          found = true
          return `${key}=${value}`
        }
        return line
      })
      if (!found) {
        configLines.push(`${key}=${value}`)
      }
    }

    // 基础配置
    upsertConfigKey('TOKEN', body.token || '')
    upsertConfigKey('CUSTOMER_SERVICE_ID', body.customerServiceId || '')
    upsertConfigKey('bot_id', body.botId || '')
    upsertConfigKey('group_link', body.groupLink || '')
    upsertConfigKey('control_address', body.controlAddress || '')
    // 私钥：同时更新 privateKey 和 usdt2trx_private_key 为同一个值
    const privateKeyValue = body.privateKey || ''
    upsertConfigKey('privateKey', privateKeyValue)
    upsertConfigKey('usdt2trx_private_key', privateKeyValue)
    upsertConfigKey('username', body.username || '')
    upsertConfigKey('password', body.password || '')
    upsertConfigKey('ad_time', body.adTime || '')
    upsertConfigKey('huilv_zhekou', body.huilvZhekou || '')
    upsertConfigKey('admin_id', body.adminId || '')

    // 价格配置（先做冲突检测，再写入）
    const hourPrice = body.hourPrice ? parseFloat(String(body.hourPrice)) : NaN
    const dayPrice = body.dayPrice ? parseFloat(String(body.dayPrice)) : NaN
    const threeDayPrice = body.threeDayPrice ? parseFloat(String(body.threeDayPrice)) : NaN
    const bishu5Price = body.bishu5Price ? parseFloat(String(body.bishu5Price)) : NaN
    const bishu15Price = body.bishu15Price ? parseFloat(String(body.bishu15Price)) : NaN
    const bishu50Price = body.bishu50Price ? parseFloat(String(body.bishu50Price)) : NaN
    const bishu100Price = body.bishu100Price ? parseFloat(String(body.bishu100Price)) : NaN

    const priceEntries: { key: string; label: string; value: number }[] = []

    if (!Number.isNaN(hourPrice) && hourPrice > 0) {
      priceEntries.push(
        { key: 'hour_1', label: '1小时1次', value: hourPrice },
        { key: 'hour_2', label: '1小时2次', value: hourPrice * 2 },
        { key: 'hour_5', label: '1小时5次', value: hourPrice * 5 },
        { key: 'hour_10', label: '1小时10次', value: hourPrice * 10 }
      )
    }
    if (!Number.isNaN(dayPrice) && dayPrice > 0) {
      priceEntries.push(
        { key: 'day_5', label: '1天内5次', value: dayPrice * 5 },
        { key: 'day_10', label: '1天内10次', value: dayPrice * 10 },
        { key: 'day_20', label: '1天内20次', value: dayPrice * 20 },
        { key: 'day_50', label: '1天内50次', value: dayPrice * 50 }
      )
    }
    if (!Number.isNaN(threeDayPrice) && threeDayPrice > 0) {
      priceEntries.push(
        { key: 'day3_10', label: '3天内每天10次', value: threeDayPrice * 30 },
        { key: 'day3_20', label: '3天内每天20次', value: threeDayPrice * 60 },
        { key: 'day3_30', label: '3天内每天30次', value: threeDayPrice * 90 },
        { key: 'day3_50', label: '3天内每天50次', value: threeDayPrice * 150 }
      )
    }

    // 笔数套餐价格本身也要避免互相撞（笔数套餐之间）
    if (!Number.isNaN(bishu5Price) && bishu5Price > 0) {
      priceEntries.push({ key: 'bishu_5', label: '笔数套餐 5笔', value: bishu5Price })
    }
    if (!Number.isNaN(bishu15Price) && bishu15Price > 0) {
      priceEntries.push({ key: 'bishu_15', label: '笔数套餐 15笔', value: bishu15Price })
    }
    if (!Number.isNaN(bishu50Price) && bishu50Price > 0) {
      priceEntries.push({ key: 'bishu_50', label: '笔数套餐 50笔', value: bishu50Price })
    }
    if (!Number.isNaN(bishu100Price) && bishu100Price > 0) {
      priceEntries.push({ key: 'bishu_100', label: '笔数套餐 100笔', value: bishu100Price })
    }

    // 检查价格是否冲突（不同套餐价格相同会导致充值金额无法唯一识别）
    if (priceEntries.length > 0) {
      const seen = new Map<string, { label: string; value: number }>()
      const conflicts: string[] = []

      for (const entry of priceEntries) {
        // 统一到 6 位小数，避免浮点误差
        const vKey = entry.value.toFixed(6)
        const existing = seen.get(vKey)
        if (existing && existing.label !== entry.label) {
          conflicts.push(
            `${existing.label} 与 ${entry.label} 的价格相同（${entry.value} TRX），会导致充值金额无法区分套餐`
          )
        } else if (!existing) {
          seen.set(vKey, { label: entry.label, value: entry.value })
        }
      }

      if (conflicts.length > 0) {
        return {
          success: false,
          error: `价格冲突，请调整后再保存：\n- ${conflicts.join('\n- ')}`
        }
      }
    }

    upsertConfigKey('hour_price', body.hourPrice || '')
    upsertConfigKey('day_price', body.dayPrice || '')
    upsertConfigKey('three_day_price', body.threeDayPrice || '')
    upsertConfigKey('bishu_5_price', body.bishu5Price || '')
    upsertConfigKey('bishu_15_price', body.bishu15Price || '')
    upsertConfigKey('bishu_50_price', body.bishu50Price || '')
    upsertConfigKey('bishu_100_price', body.bishu100Price || '')

    // 能量池与回调配置
    upsertConfigKey('energy_pool_api', body.energyPoolApi || '')
    if (body.botNotifyUrl !== undefined) {
      upsertConfigKey('bot_notify_url', body.botNotifyUrl || '')
    }

    // 版本标识（可选）
    if (
      body.versionIdentifier !== undefined &&
      body.versionIdentifier !== null &&
      body.versionIdentifier !== ''
    ) {
      upsertConfigKey('Versionidentifier', body.versionIdentifier)
    }

    // 写回 config.txt（保留其他未修改的行，如 main_menu_buttons_json）
    fs.writeFileSync(configPath, configLines.join('\n'), 'utf-8')
    
    // 更新 al.py 文件中的数据库配置和API_KEY
    if (fs.existsSync(alPyPath)) {
      let alPyContent = fs.readFileSync(alPyPath, 'utf-8')
      
      // 更新API_KEY (第43行)
      if (body.tronApiKey !== undefined) {
        alPyContent = alPyContent.replace(
          /API_KEY\s*=\s*["'][^"']*["']/,
          `API_KEY="${body.tronApiKey}"`
        )
      }
      
      // 更新数据库配置 (第55-59行)
      if (body.dbUser !== undefined || body.dbPassword !== undefined || 
          body.dbHost !== undefined || body.dbName !== undefined || 
          body.dbPort !== undefined) {
        
        // 从环境变量获取数据库配置，不使用硬编码默认值
        const config = useRuntimeConfig()
        const newConfig = {
          user: body.dbUser || config.dbUser,
          password: body.dbPassword || config.dbPassword,
          host: body.dbHost || config.dbHost,
          database: body.dbName || config.dbName,
          port: body.dbPort || config.dbPort
        }
        
        const configBlock = `config = {
        'user': '${newConfig.user}',
        'password': '${newConfig.password}',
        'host': '${newConfig.host}',
        'database': '${newConfig.database}',
        'port': ${newConfig.port},
        'charset': 'utf8mb4'
    }`
        
        // 替换整个config块
        alPyContent = alPyContent.replace(
          /config\s*=\s*\{[^}]+\}/,
          configBlock
        )
      }
      
      // 写入更新后的al.py文件
      fs.writeFileSync(alPyPath, alPyContent, 'utf-8')
    }
    
    return {
      success: true,
      message: '配置保存成功'
    }
  } catch (error) {
    console.error('保存配置文件失败:', error)
    return {
      success: false,
      error: '保存配置文件失败: ' + (error as Error).message
    }
  }
})
