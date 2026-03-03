import { promises as fs } from 'fs'
import path from 'path'

export default defineEventHandler(async (event) => {
  try {
    const projectRoot = process.cwd()
    const updateFolder = path.join(projectRoot, '更新文件')
    const backupFolder = path.join(projectRoot, '备份文件')
    
    // 检查解压状态（第2步）
    let extractStatus = 'pending'
    try {
      const updateFiles = await fs.readdir(updateFolder)
      
      // 如果有 __MACOSX 文件夹，说明已解压完成
      if (updateFiles.includes('__MACOSX')) {
        extractStatus = 'completed'
      }
      // 如果有 .zip 文件，说明可以解压
      else if (updateFiles.some(file => file.endsWith('.zip'))) {
        extractStatus = 'ready'
      }
      // 否则等待中
      else {
        extractStatus = 'pending'
      }
    } catch (error) {
      extractStatus = 'pending'
    }
    
    // 检查备份状态（第3步）
    let backupStatus = 'pending'
    try {
      const backupFiles = await fs.readdir(backupFolder)
      
      // 过滤掉系统文件（.DS_Store等）
      const actualBackupFiles = backupFiles.filter(file => 
        !file.startsWith('.') && 
        file !== 'Thumbs.db' && 
        file !== 'desktop.ini'
      )
      
      // 如果备份文件夹有实际内容，说明已备份完成
      if (actualBackupFiles.length > 0) {
        backupStatus = 'completed'
      }
      // 如果备份文件夹为空（只有系统文件），说明可以备份
      else {
        backupStatus = 'ready'
      }
    } catch (error) {
      // 如果文件夹不存在，创建它并设为可备份
      try {
        await fs.mkdir(backupFolder, { recursive: true })
        backupStatus = 'ready'
      } catch (createError) {
        backupStatus = 'pending'
      }
    }
    
    return {
      success: true,
      data: {
        step2: {
          status: extractStatus,
          description: extractStatus === 'completed' ? '解压完成' : 
                      extractStatus === 'ready' ? '可以解压' : '等待中'
        },
        step3: {
          status: backupStatus,
          description: backupStatus === 'completed' ? '备份完成' : 
                      backupStatus === 'ready' ? '可以备份' : '等待中'
        }
      }
    }
  } catch (error) {
    console.error('检查文件夹状态失败:', error)
    return {
      success: false,
      error: '检查文件夹状态失败',
      data: {
        step2: { status: 'pending', description: '等待中' },
        step3: { status: 'pending', description: '等待中' }
      }
    }
  }
})