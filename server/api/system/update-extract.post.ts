import { promises as fs } from 'fs'
import { join } from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { sessionId, downloadPath } = body || {}
    
    if (!sessionId) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少会话ID'
      })
    }
    
    if (!downloadPath) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少下载文件路径'
      })
    }
    
    // 验证下载文件是否存在
    try {
      await fs.access(downloadPath)
    } catch {
      throw createError({
        statusCode: 404,
        statusMessage: '下载文件不存在'
      })
    }
    
    // 确保解压目录存在
    const extractDir = join(process.cwd(), '更新文件')
    try {
      await fs.access(extractDir)
    } catch {
      await fs.mkdir(extractDir, { recursive: true })
    }
    
    // 清空解压目录（除了下载的zip文件）
    const files = await fs.readdir(extractDir)
    for (const file of files) {
      const filePath = join(extractDir, file)
      const stat = await fs.stat(filePath)
      
      // 跳过下载的zip文件
      if (filePath === downloadPath) {
        continue
      }
      
      if (stat.isDirectory()) {
        await fs.rm(filePath, { recursive: true, force: true })
      } else {
        await fs.unlink(filePath)
      }
    }
    
    try {
      // 使用unzip命令解压文件，增加maxBuffer以处理大文件
      const { stdout, stderr } = await execAsync(`cd "${extractDir}" && unzip -o "${downloadPath}"`, {
        maxBuffer: 1024 * 1024 * 10 // 10MB buffer
      })
      
      if (stderr && !stderr.includes('Archive:')) {
        console.warn('解压警告:', stderr)
      }
      
      // 检查解压后的文件
      const extractedFiles = await fs.readdir(extractDir)
      const extractedCount = extractedFiles.filter(file => file !== downloadPath.split('/').pop()).length
      
      if (extractedCount === 0) {
        throw new Error('解压后没有找到文件')
      }
      
      // 更新状态管理
      try {
        await $fetch('/api/system/update-state', {
          method: 'POST',
          body: {
            action: 'update',
            sessionId,
            extractPath: extractDir
          }
        })
      } catch (error) {
        console.warn('更新状态失败:', error)
      }
      
      return {
        success: true,
        message: '文件解压成功',
        data: {
          extractPath: extractDir,
          extractedFiles: extractedCount,
          sessionId
        }
      }
      
    } catch (error: any) {
      console.error('解压失败:', error)
      
      // 更新状态管理 - 记录错误
      try {
        await $fetch('/api/system/update-state', {
          method: 'POST',
          body: {
            action: 'update',
            sessionId,
            error: `解压失败: ${error.message}`
          }
        })
      } catch (updateError) {
        console.warn('更新状态失败:', updateError)
      }
      
      throw createError({
        statusCode: 500,
        statusMessage: `解压失败: ${error.message}`
      })
    }
    
  } catch (error: any) {
    console.error('解压文件失败:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || '解压文件失败: ' + (error?.message || '未知错误')
    })
  }
})