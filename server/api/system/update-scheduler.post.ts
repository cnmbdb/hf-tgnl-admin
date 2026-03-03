import { promises as fs } from 'fs'
import path from 'path'

const SCHEDULER_FILE = path.join(process.cwd(), 'data', 'update-scheduler.json')

interface SchedulerConfig {
  enabled: boolean
  interval: number
  lastCheck: string
  autoDownload: boolean
  autoApply: boolean
}

const defaultConfig: SchedulerConfig = {
  enabled: true,
  interval: 24,
  lastCheck: new Date().toISOString(),
  autoDownload: false,
  autoApply: false
}

export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  
  if (method === 'GET') {
    try {
      const configData = await fs.readFile(SCHEDULER_FILE, 'utf-8')
      const config = JSON.parse(configData)
      return { success: true, config }
    } catch (error) {
      return { success: true, config: defaultConfig }
    }
  }
  
  if (method === 'POST') {
    try {
      const body = await readBody(event)
      const { action, config } = body
      
      const dataDir = path.dirname(SCHEDULER_FILE)
      await fs.mkdir(dataDir, { recursive: true })
      
      if (action === 'start') {
        const newConfig = { ...defaultConfig, ...config, enabled: true }
        await fs.writeFile(SCHEDULER_FILE, JSON.stringify(newConfig, null, 2))
        return { success: true, message: '定时检测已启动', config: newConfig }
      }
      
      if (action === 'stop') {
        const currentConfig = await getCurrentConfig()
        const newConfig = { ...currentConfig, enabled: false }
        await fs.writeFile(SCHEDULER_FILE, JSON.stringify(newConfig, null, 2))
        return { success: true, message: '定时检测已停止', config: newConfig }
      }
      
      if (action === 'update') {
        const currentConfig = await getCurrentConfig()
        const newConfig = { ...currentConfig, ...config }
        await fs.writeFile(SCHEDULER_FILE, JSON.stringify(newConfig, null, 2))
        return { success: true, message: '配置已更新', config: newConfig }
      }
      
      return { success: false, message: '未知操作' }
    } catch (error: any) {
      console.error('定时检测配置失败:', error)
      return { success: false, message: error.message || '操作失败' }
    }
  }
  
  return { success: false, message: '不支持的请求方法' }
})

async function getCurrentConfig(): Promise<SchedulerConfig> {
  try {
    const configData = await fs.readFile(SCHEDULER_FILE, 'utf-8')
    return JSON.parse(configData)
  } catch (error) {
    return defaultConfig
  }
}