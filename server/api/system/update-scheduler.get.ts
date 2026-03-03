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
  try {
    const configData = await fs.readFile(SCHEDULER_FILE, 'utf-8')
    const config = JSON.parse(configData)
    return { success: true, config }
  } catch (error) {
    return { success: true, config: defaultConfig }
  }
})