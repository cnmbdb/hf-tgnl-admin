import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export default defineEventHandler(async (event) => {
  try {
    // 获取 Docker 容器中的机器人状态
    const botProcesses = await getBotContainerStatus()
    
    return {
      success: true,
      data: {
        processes: botProcesses,
        processCount: botProcesses.length,
        timestamp: new Date().toISOString()
      }
    }
  } catch (error) {
    console.error('获取机器人状态失败:', error)
    return {
      success: false,
      error: '获取机器人状态失败',
      data: {
        processes: [],
        processCount: 0,
        timestamp: new Date().toISOString()
      }
    }
  }
})

async function getBotContainerStatus() {
  try {
    const processes = []
    
    // 检查 tgnl-admin-bot 容器状态
    const { stdout: containerInfo } = await execAsync(
      `docker inspect tgnl-admin-bot --format '{{.State.Status}}|{{.State.StartedAt}}|{{.State.Health.Status}}'`
    ).catch(() => ({ stdout: '' }))
    
    if (!containerInfo.trim()) {
      return processes
    }
    
    const [status, startedAt, healthStatus] = containerInfo.trim().split('|')
    
    if (status === 'running') {
      // 获取容器资源使用情况
      const { stdout: statsOutput } = await execAsync(
        `docker stats tgnl-admin-bot --no-stream --format '{{.CPUPerc}}|{{.MemPerc}}'`
      ).catch(() => ({ stdout: '0%|0%' }))
      
      const [cpuPerc, memPerc] = statsOutput.trim().split('|')
      const cpuUsage = parseFloat(cpuPerc.replace('%', '')) || 0
      const memUsage = parseFloat(memPerc.replace('%', '')) || 0
      
      // 计算运行时间
      const startTime = new Date(startedAt)
      const now = new Date()
      const uptimeSeconds = Math.floor((now.getTime() - startTime.getTime()) / 1000)
      
      processes.push({
        pid: 'docker',
        name: 'Telegram Bot (tgnl-admin-bot)',
        cpuUsage: cpuUsage,
        memUsage: memUsage,
        status: 'running',
        uptime: formatUptime(uptimeSeconds),
        startedAt: startedAt,
        command: 'python3 al.py',
        workingDir: '/app',
        user: 'docker',
        healthStatus: healthStatus || 'none'
      })
    }
    
    return processes
  } catch (error) {
    console.error('获取 Docker 容器状态失败:', error)
    return []
  }
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (days > 0) {
    return `${days}d ${hours}h ${minutes}m`
  } else if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}
