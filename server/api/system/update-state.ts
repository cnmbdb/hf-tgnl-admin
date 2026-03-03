import { promises as fs } from 'fs'
import { join } from 'path'

// 更新状态存储文件路径
const UPDATE_STATE_FILE = join(process.cwd(), 'data', 'update-state.json')

// 更新步骤定义
export const UPDATE_STEPS = {
  DOWNLOAD: 1,
  EXTRACT: 2, 
  BACKUP: 3,
  APPLY: 4,
  RESTART: 5
}

export const STEP_NAMES = {
  [UPDATE_STEPS.DOWNLOAD]: '下载更新包',
  [UPDATE_STEPS.EXTRACT]: '解压文件', 
  [UPDATE_STEPS.BACKUP]: '备份当前版本',
  [UPDATE_STEPS.APPLY]: '应用更新',
  [UPDATE_STEPS.RESTART]: '重启系统'
}

export const STEP_DESCRIPTIONS = {
  [UPDATE_STEPS.DOWNLOAD]: '从GitHub下载最新版本',
  [UPDATE_STEPS.EXTRACT]: '解压下载的更新包',
  [UPDATE_STEPS.BACKUP]: '创建当前版本的备份',
  [UPDATE_STEPS.APPLY]: '覆盖旧文件并检查权限',
  [UPDATE_STEPS.RESTART]: '重启前端和机器人端'
}

interface UpdateState {
  sessionId: string
  currentStep: number
  completedSteps: number[]
  version?: string
  downloadPath?: string
  extractPath?: string
  backupPath?: string
  startedAt: string
  lastUpdatedAt: string
  error?: string
  canProceed: boolean
}

// 确保数据目录存在
async function ensureDataDir() {
  const dataDir = join(process.cwd(), 'data')
  try {
    await fs.access(dataDir)
  } catch {
    await fs.mkdir(dataDir, { recursive: true })
  }
}

// 读取更新状态
async function readUpdateState(): Promise<UpdateState | null> {
  try {
    await ensureDataDir()
    const data = await fs.readFile(UPDATE_STATE_FILE, 'utf-8')
    return JSON.parse(data)
  } catch {
    return null
  }
}

// 保存更新状态
async function saveUpdateState(state: UpdateState) {
  await ensureDataDir()
  await fs.writeFile(UPDATE_STATE_FILE, JSON.stringify(state, null, 2))
}

export default defineEventHandler(async (event) => {
  const method = getMethod(event)
  
  try {
    if (method === 'GET') {
      // 获取当前更新状态
      const state = await readUpdateState()
      
      if (!state) {
        return {
          success: true,
          data: {
            hasActiveUpdate: false,
            steps: Object.keys(UPDATE_STEPS).map(key => ({
              id: UPDATE_STEPS[key as keyof typeof UPDATE_STEPS],
              name: STEP_NAMES[UPDATE_STEPS[key as keyof typeof UPDATE_STEPS]],
              description: STEP_DESCRIPTIONS[UPDATE_STEPS[key as keyof typeof UPDATE_STEPS]],
              completed: false,
              current: false
            }))
          }
        }
      }
      
      const steps = Object.keys(UPDATE_STEPS).map(key => {
        const stepId = UPDATE_STEPS[key as keyof typeof UPDATE_STEPS]
        return {
          id: stepId,
          name: STEP_NAMES[stepId],
          description: STEP_DESCRIPTIONS[stepId],
          completed: state.completedSteps.includes(stepId),
          current: state.currentStep === stepId
        }
      })
      
      return {
        success: true,
        data: {
          hasActiveUpdate: true,
          sessionId: state.sessionId,
          currentStep: state.currentStep,
          completedSteps: state.completedSteps,
          version: state.version,
          startedAt: state.startedAt,
          lastUpdatedAt: state.lastUpdatedAt,
          error: state.error,
          canProceed: state.canProceed,
          steps
        }
      }
    }
    
    if (method === 'POST') {
      // 创建新的更新会话或更新状态
      const body = await readBody(event)
      const { action, sessionId, step, version, downloadPath, extractPath, backupPath, error } = body
      
      if (action === 'start') {
        // 开始新的更新会话
        const newSessionId = `update-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        const newState: UpdateState = {
          sessionId: newSessionId,
          currentStep: UPDATE_STEPS.DOWNLOAD,
          completedSteps: [],
          version,
          startedAt: new Date().toISOString(),
          lastUpdatedAt: new Date().toISOString(),
          canProceed: true
        }
        
        await saveUpdateState(newState)
        
        return {
          success: true,
          message: '更新会话已创建',
          data: { sessionId: newSessionId }
        }
      }
      
      if (action === 'update') {
        // 更新状态
        const currentState = await readUpdateState()
        
        if (!currentState || currentState.sessionId !== sessionId) {
          throw createError({
            statusCode: 404,
            statusMessage: '更新会话不存在或已过期'
          })
        }
        
        const updatedState: UpdateState = {
          ...currentState,
          lastUpdatedAt: new Date().toISOString()
        }
        
        if (step !== undefined) {
          updatedState.currentStep = step
        }
        
        if (downloadPath !== undefined) {
          updatedState.downloadPath = downloadPath
        }
        
        if (extractPath !== undefined) {
          updatedState.extractPath = extractPath
        }
        
        if (backupPath !== undefined) {
          updatedState.backupPath = backupPath
        }
        
        if (error !== undefined) {
          updatedState.error = error
          updatedState.canProceed = !error
        }
        
        await saveUpdateState(updatedState)
        
        return {
          success: true,
          message: '状态已更新'
        }
      }
      
      if (action === 'complete-step') {
        // 完成当前步骤
        const currentState = await readUpdateState()
        
        if (!currentState || currentState.sessionId !== sessionId) {
          throw createError({
            statusCode: 404,
            statusMessage: '更新会话不存在或已过期'
          })
        }
        
        const updatedState: UpdateState = {
          ...currentState,
          completedSteps: [...currentState.completedSteps, currentState.currentStep],
          currentStep: currentState.currentStep + 1,
          lastUpdatedAt: new Date().toISOString(),
          canProceed: currentState.currentStep < UPDATE_STEPS.RESTART
        }
        
        await saveUpdateState(updatedState)
        
        return {
          success: true,
          message: '步骤已完成'
        }
      }
      
      if (action === 'clear') {
        // 清除更新状态
        try {
          await fs.unlink(UPDATE_STATE_FILE)
        } catch {
          // 文件不存在，忽略错误
        }
        
        return {
          success: true,
          message: '更新状态已清除'
        }
      }
    }
    
    throw createError({
      statusCode: 405,
      statusMessage: '不支持的请求方法'
    })
    
  } catch (error: any) {
    console.error('更新状态管理失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: '更新状态管理失败: ' + (error?.message || '未知错误')
    })
  }
})