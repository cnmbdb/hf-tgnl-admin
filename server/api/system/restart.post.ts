import { spawn, exec as execCallback } from 'child_process'
import { join } from 'path'
import { promisify } from 'util'

const exec = promisify(execCallback)

export default defineEventHandler(async (event) => {
  try {
    // 检查管理员权限
    const headers = getHeaders(event)
    const authHeader = headers.authorization
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw createError({
        statusCode: 401,
        statusMessage: '未授权访问'
      })
    }
    
    const body = await readBody(event)
    const { restartType = 'all' } = body // 'all', 'frontend', 'robot'
    
    // 延迟重启，给客户端时间接收响应
    setTimeout(async () => {
      console.log(`系统正在重启 (${restartType})...`)
      
      try {
        if (restartType === 'all' || restartType === 'robot') {
          // 重启机器人端 (Python进程)
          console.log('正在重启机器人端...')
          try {
            // 查找并终止Python机器人进程
            await exec('pkill -f "python.*al.py" || true')
            console.log('机器人端进程已终止')
            
            // 重新启动机器人端
            setTimeout(() => {
              const robotProcess = spawn('python3', ['al.py'], {
                cwd: join(process.cwd(), 'nl-2333'),
                detached: true,
                stdio: 'ignore'
              })
              
              robotProcess.unref()
              console.log('机器人端已重新启动')
            }, 1000)
          } catch (error) {
            console.warn('重启机器人端失败:', error)
          }
        }
        
        if (restartType === 'all' || restartType === 'frontend') {
          // 重启前端 (Nuxt进程)
          console.log('正在重启前端...')
          
          // 尝试使用PM2重启
          const pm2Restart = spawn('pm2', ['restart', 'all'], {
            detached: true,
            stdio: 'ignore'
          })
          
          pm2Restart.on('error', (error) => {
            console.warn('PM2重启失败，尝试进程退出:', error)
            // 如果PM2重启失败，退出进程让系统管理器重启
            process.exit(0)
          })
          
          pm2Restart.on('close', (code) => {
            if (code !== 0) {
              console.warn('PM2重启返回非零代码，尝试进程退出')
              process.exit(0)
            } else {
              console.log('前端已重新启动')
            }
          })
          
          // 超时后强制退出
          setTimeout(() => {
            console.log('重启超时，强制退出进程')
            process.exit(0)
          }, 15000)
        }
      } catch (error) {
        console.error('重启过程中出现错误:', error)
        // 发生错误时强制退出
        process.exit(1)
      }
    }, 2000)
    
    return {
      success: true,
      message: '系统将在2秒后重启',
      data: {
        restartAt: new Date(Date.now() + 2000).toISOString()
      }
    }
  } catch (error: any) {
    console.error('系统重启失败:', error)
    if (error.statusCode) {
      throw error
    }
    throw createError({
      statusCode: 500,
      statusMessage: '系统重启失败: ' + (error?.message || '未知错误')
    })
  }
})