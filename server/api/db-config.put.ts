import fs from 'fs'
import path from 'path'
import { requireAdmin } from '../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    await requireAdmin(event)

    const body = await readBody(event)
    
    // 验证请求体
    if (!body || typeof body !== 'object') {
      throw createError({
        statusCode: 400,
        statusMessage: '请求体格式错误'
      })
    }

    const envPath = path.join(process.cwd(), '.env')
  
  if (!fs.existsSync(envPath)) {
    throw createError({
      statusCode: 404,
      statusMessage: '.env 文件不存在'
    })
  }

    // 读取当前环境变量文件
    const envContent = fs.readFileSync(envPath, 'utf-8')
    const envLines = envContent.split('\n')
    
    // 创建新的环境变量映射
    const envMap = new Map<string, string>()
    const comments = new Map<string, string>() // 保存注释
    
    // 解析现有内容
    envLines.forEach(line => {
      const trimmedLine = line.trim()
      if (trimmedLine.startsWith('#')) {
        // 保存注释行
        const nextLineIndex = envLines.indexOf(line) + 1
        if (nextLineIndex < envLines.length) {
          const nextLine = envLines[nextLineIndex].trim()
          if (nextLine && !nextLine.startsWith('#')) {
            const [key] = nextLine.split('=', 2)
            if (key) {
              comments.set(key.trim(), line)
            }
          }
        }
      } else if (trimmedLine && trimmedLine.includes('=')) {
        const [key, value] = trimmedLine.split('=', 2)
        if (key && value !== undefined) {
          envMap.set(key.trim(), value.trim())
        }
      }
    })

    // 更新配置值（统一使用 DB_* 配置）
    const updateMapping = {
      dbHost: 'DB_HOST',
      dbPort: 'DB_PORT', 
      dbName: 'DB_NAME',
      dbUser: 'DB_USER',
      dbPassword: 'DB_PASSWORD'
    }

    // 应用更新
    Object.entries(updateMapping).forEach(([bodyKey, envKey]) => {
      if (body[bodyKey] !== undefined && body[bodyKey] !== null) {
        envMap.set(envKey, String(body[bodyKey]))
      }
    })

    // 重新构建环境变量文件内容
    const newEnvLines: string[] = []
    
    // 按照特定顺序重新组织配置
    const sections = [
      {
        title: '# 数据库配置（统一配置，所有功能共用）',
        keys: ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
      }
    ]

    // 先添加其他非数据库配置
    envLines.forEach(line => {
      const trimmedLine = line.trim()
      if (trimmedLine && !trimmedLine.startsWith('#')) {
        const [key] = trimmedLine.split('=', 2)
        if (key) {
          const keyName = key.trim()
          // 如果不是数据库相关配置，保留原样
          if (!keyName.includes('DB_')) {
            newEnvLines.push(line)
          }
        }
      } else if (trimmedLine.startsWith('#') && !trimmedLine.includes('数据库配置')) {
        // 保留非数据库相关的注释
        newEnvLines.push(line)
      }
    })

    // 添加空行分隔
    if (newEnvLines.length > 0) {
      newEnvLines.push('')
    }

    // 添加数据库配置部分
    sections.forEach((section, index) => {
      if (index > 0) {
        newEnvLines.push('')
      }
      newEnvLines.push(section.title)
      section.keys.forEach(key => {
        if (envMap.has(key)) {
          newEnvLines.push(`${key}=${envMap.get(key)}`)
        }
      })
    })

    // 写入文件
    fs.writeFileSync(envPath, newEnvLines.join('\n'), 'utf-8')

    // 同步更新到 nl-2333/config.txt 文件
    const configPath = path.join(process.cwd(), 'nl-2333', 'config.txt')
    if (fs.existsSync(configPath)) {
      try {
        const configContent = fs.readFileSync(configPath, 'utf-8')
        let updatedConfig = configContent

        // 更新 config.txt 中的数据库配置（统一使用 DB_* 配置）
        if (envMap.has('DB_HOST')) {
          updatedConfig = updatedConfig.replace(/host=.*/g, `host=${envMap.get('DB_HOST')}`)
        }
        if (envMap.has('DB_USER')) {
          updatedConfig = updatedConfig.replace(/user=.*/g, `user=${envMap.get('DB_USER')}`)
        }
        if (envMap.has('DB_PASSWORD')) {
          updatedConfig = updatedConfig.replace(/password=.*/g, `password=${envMap.get('DB_PASSWORD')}`)
        }
        if (envMap.has('DB_NAME')) {
          updatedConfig = updatedConfig.replace(/database=.*/g, `database=${envMap.get('DB_NAME')}`)
        }
        if (envMap.has('DB_PORT')) {
          updatedConfig = updatedConfig.replace(/port=.*/g, `port=${envMap.get('DB_PORT')}`)
        }

        fs.writeFileSync(configPath, updatedConfig, 'utf-8')
      } catch (configError) {
        console.warn('更新 config.txt 失败:', configError)
      }
    }

    return {
      success: true,
      message: '数据库配置更新成功',
      data: {
        updated: Object.keys(updateMapping).filter(key => body[key] !== undefined)
      }
    }

  } catch (error: any) {
    console.error('更新数据库配置失败:', error)
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: '更新数据库配置失败: ' + error.message
    })
  }
})