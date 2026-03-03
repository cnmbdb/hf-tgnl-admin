import { promises as fs } from 'fs'
import { join } from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { sessionId } = body || {}
    
    if (!sessionId) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少会话ID'
      })
    }
    
    const projectRoot = process.cwd()
    const backupDir = join(projectRoot, '备份文件')
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0] + '_' + 
                     new Date().toISOString().replace(/[:.]/g, '-').split('T')[1].split('.')[0]
    const backupPath = join(backupDir, `backup-${timestamp}`)
    
    try {
      // 确保备份目录存在
      try {
        await fs.access(backupDir)
      } catch {
        await fs.mkdir(backupDir, { recursive: true })
      }
      
      // 创建具体的备份目录
      await fs.mkdir(backupPath, { recursive: true })
      
      // 备份整个项目文件夹，但排除一些不必要的目录
      const excludeItems = [
        '.nuxt',
        '.output',
        'node_modules',
        '.git',
        '备份文件',
        '更新文件',
        'logs',
        '*.log'
      ]
      
      // 构建排除参数
      const excludeArgs = excludeItems.map(item => `--exclude='${item}'`).join(' ')
      
      // 使用 rsync 备份整个项目文件夹（排除不必要的文件）
      const projectName = projectRoot.split('/').pop() || '10-15-0energy-robot'
      const fullBackupPath = join(backupPath, projectName)
      
      // 使用 rsync 进行高效备份
      await execAsync(`rsync -av ${excludeArgs} "${projectRoot}/" "${fullBackupPath}/"`)
      
      console.log(`项目完整备份完成: ${fullBackupPath}`)
      
      const backedUpItems = 1 // 整个项目作为一个备份项
      const skippedItems = excludeItems
      
      // 创建备份信息文件
      const backupInfo = {
        timestamp: new Date().toISOString(),
        sessionId,
        backedUpItems,
        skippedItems,
        projectRoot,
        backupPath: fullBackupPath,
        backupType: 'full_project',
        excludedItems: excludeItems
      }
      
      await fs.writeFile(
        join(backupPath, 'backup-info.json'),
        JSON.stringify(backupInfo, null, 2)
      )
      
      // 计算备份大小
      let backupSize = 0
      try {
        const { stdout } = await execAsync(`du -sb "${fullBackupPath}" | cut -f1`)
        backupSize = parseInt(stdout.trim())
      } catch (error) {
        console.warn('无法计算备份大小:', error)
      }
      
      // 更新状态管理
      try {
        await $fetch('/api/system/update-state', {
          method: 'POST',
          body: {
            action: 'update',
            sessionId,
            backupPath: fullBackupPath
          }
        })
      } catch (error) {
        console.warn('更新状态失败:', error)
      }
      
      return {
        success: true,
        message: '整个项目备份成功',
        data: {
          backupPath: fullBackupPath,
          backedUpItems,
          skippedItems,
          backupSize: Math.round(backupSize / 1024 / 1024 * 100) / 100, // MB
          timestamp,
          sessionId,
          backupType: 'full_project'
        }
      }
      
    } catch (error: any) {
      console.error('备份失败:', error)
      
      // 清理失败的备份目录
      try {
        await fs.rm(backupPath, { recursive: true, force: true })
      } catch (cleanupError) {
        console.warn('清理失败的备份目录失败:', cleanupError)
      }
      
      // 更新状态管理 - 记录错误
      try {
        await $fetch('/api/system/update-state', {
          method: 'POST',
          body: {
            action: 'update',
            sessionId,
            error: `备份失败: ${error.message}`
          }
        })
      } catch (updateError) {
        console.warn('更新状态失败:', updateError)
      }
      
      throw createError({
        statusCode: 500,
        statusMessage: `备份失败: ${error.message}`
      })
    }
    
  } catch (error: any) {
    console.error('创建备份失败:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || '创建备份失败: ' + (error?.message || '未知错误')
    })
  }
})