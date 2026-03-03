import fs from 'fs'
import path from 'path'
import { requireAdmin } from '../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    await requireAdmin(event)

    const envPath = path.join(process.cwd(), '.env')
  
  if (!fs.existsSync(envPath)) {
    throw createError({
      statusCode: 404,
      statusMessage: '.env 文件不存在'
    })
  }

    const envContent = fs.readFileSync(envPath, 'utf-8')
    const envLines = envContent.split('\n')
    
    // 解析环境变量（统一使用 DB_* 配置）
    const config = {
      dbHost: '',
      dbPort: '',
      dbName: '',
      dbUser: '',
      dbPassword: ''
    }

    envLines.forEach(line => {
      const trimmedLine = line.trim()
      if (trimmedLine && !trimmedLine.startsWith('#')) {
        const [key, value] = trimmedLine.split('=', 2)
        if (key && value) {
          switch (key.trim()) {
            case 'DB_HOST':
              config.dbHost = value.trim()
              break
            case 'DB_PORT':
              config.dbPort = value.trim()
              break
            case 'DB_NAME':
              config.dbName = value.trim()
              break
            case 'DB_USER':
              config.dbUser = value.trim()
              break
            case 'DB_PASSWORD':
              config.dbPassword = value.trim()
              break
          }
        }
      }
    })

    return {
      success: true,
      data: config
    }

  } catch (error: any) {
    console.error('读取数据库配置失败:', error)
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: '读取数据库配置失败: ' + error.message
    })
  }
})