import { exec } from 'child_process'
import { promisify } from 'util'
import { requireAdmin } from '../utils/auth'

const execAsync = promisify(exec)

export default defineEventHandler(async (event) => {
  // 验证管理员权限
  const user = await requireAdmin(event)
  if (!user) {
    return {
      success: false,
      error: '需要管理员权限'
    }
  }
  
  try {
    console.log('开始重启 bot 容器...')
    
    // 检查 tgnl-admin-bot 容器是否存在
    try {
      const { stdout: containerCheck } = await execAsync('docker ps -a --filter "name=tgnl-admin-bot" --format "{{.Names}}"')
      if (!containerCheck.trim()) {
        return {
          success: false,
          error: '未找到 tgnl-admin-bot 容器'
        }
      }
      console.log('找到 bot 容器:', containerCheck.trim())
    } catch (error: any) {
      return {
        success: false,
        error: 'Docker 命令执行失败: ' + error.message
      }
    }
    
    // 重启 bot 容器
    try {
      console.log('正在重启 tgnl-admin-bot 容器...')
      await execAsync('docker restart tgnl-admin-bot')
      console.log('bot 容器重启命令已执行')
    } catch (error: any) {
      return {
        success: false,
        error: '重启容器失败: ' + error.message
      }
    }
    
    // 等待容器启动
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // 检查容器状态
    try {
      const { stdout: status } = await execAsync('docker ps --filter "name=tgnl-admin-bot" --format "{{.Status}}"')
      const isRunning = status.toLowerCase().includes('up')
      
      if (isRunning) {
        // 获取容器详细信息
        const { stdout: inspect } = await execAsync('docker inspect tgnl-admin-bot --format "{{.State.StartedAt}}"')
        
        return {
          success: true,
          message: 'bot 容器重启成功',
          container: 'tgnl-admin-bot',
          status: status.trim(),
          startedAt: inspect.trim()
        }
      } else {
        // 获取容器日志
        const { stdout: logs } = await execAsync('docker logs tgnl-admin-bot --tail 20 2>&1')
        return {
          success: false,
          error: 'bot 容器启动失败',
          logs: logs
        }
      }
    } catch (error: any) {
      return {
        success: false,
        error: '检查容器状态失败: ' + error.message
      }
    }
    
  } catch (error: any) {
    console.error('重启 bot 容器时发生错误:', error)
    return {
      success: false,
      error: error.message || '重启 bot 容器失败'
    }
  }
})
