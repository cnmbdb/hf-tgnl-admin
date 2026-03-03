import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs'
import path from 'path'

const execAsync = promisify(exec)

export default defineEventHandler(async (event) => {
  try {
    // 验证请求方法
    if (event.node.req.method !== 'POST') {
      throw createError({
        statusCode: 405,
        statusMessage: 'Method Not Allowed'
      })
    }

    // 获取请求体
    const body = await readBody(event)
    
    // 验证管理员权限（这里可以根据实际需求添加更严格的验证）
    if (!body.adminToken) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Unauthorized: Admin token required'
      })
    }

    // 检查机器人进程是否运行
    const botPath = path.join(process.cwd(), 'nl-2333')
    const configPath = path.join(botPath, 'config.txt')
    
    if (!fs.existsSync(configPath)) {
      throw createError({
        statusCode: 404,
        statusMessage: 'Bot configuration file not found'
      })
    }

    try {
      // 方法1: 通过文件系统触发热重载（修改配置文件的修改时间）
      const now = new Date()
      fs.utimesSync(configPath, now, now)
      
      // 方法2: 如果机器人支持信号重载，可以发送信号
      // 这里我们尝试找到机器人进程并发送重载信号
      try {
        const { stdout } = await execAsync('pgrep -f "python.*al.py"')
        const pids = stdout.trim().split('\n').filter(pid => pid)
        
        if (pids.length > 0) {
          // 发送USR1信号触发重载（如果机器人支持的话）
          for (const pid of pids) {
            try {
              await execAsync(`kill -USR1 ${pid}`)
            } catch (e) {
              // 忽略信号发送失败，因为不是所有进程都支持这个信号
            }
          }
        }
      } catch (e) {
        // 如果找不到进程或发送信号失败，不影响主要功能
        console.log('Could not send reload signal to bot process:', e)
      }

      // 方法3: 创建一个重载标记文件，让机器人检测到后自动重载
      const reloadFlagPath = path.join(botPath, '.reload_flag')
      fs.writeFileSync(reloadFlagPath, new Date().toISOString())

      return {
        success: true,
        message: '配置重载请求已发送',
        timestamp: new Date().toISOString(),
        methods: [
          'Updated config file modification time',
          'Created reload flag file',
          'Attempted to send reload signal to bot process'
        ]
      }

    } catch (error) {
      console.error('Error during bot reload:', error)
      throw createError({
        statusCode: 500,
        statusMessage: `Failed to reload bot configuration: ${error.message}`
      })
    }

  } catch (error) {
    console.error('Bot reload API error:', error)
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: 'Internal server error during bot reload'
    })
  }
})