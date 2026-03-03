import { promises as fs } from 'fs'
import path from 'path'

export default defineEventHandler(async (event) => {
  try {
    const updateFolderPath = path.join(process.cwd(), '更新文件')
    
    // 检查文件夹是否存在
    try {
      await fs.access(updateFolderPath)
    } catch {
      // 文件夹不存在，创建它
      await fs.mkdir(updateFolderPath, { recursive: true })
      return {
        success: true,
        data: {
          isEmpty: true,
          fileCount: 0,
          files: []
        }
      }
    }
    
    // 读取文件夹内容
    const files = await fs.readdir(updateFolderPath)
    
    // 过滤掉隐藏文件和系统文件
    const validFiles = files.filter(file => 
      !file.startsWith('.') && 
      !file.startsWith('__') &&
      file !== 'Thumbs.db'
    )
    
    const fileDetails = []
    for (const file of validFiles) {
      try {
        const filePath = path.join(updateFolderPath, file)
        const stats = await fs.stat(filePath)
        fileDetails.push({
          name: file,
          size: stats.size,
          isDirectory: stats.isDirectory(),
          modifiedAt: stats.mtime
        })
      } catch (error) {
        console.error(`获取文件信息失败: ${file}`, error)
      }
    }
    
    return {
      success: true,
      data: {
        isEmpty: validFiles.length === 0,
        fileCount: validFiles.length,
        files: fileDetails
      }
    }
  } catch (error: any) {
    console.error('检查更新文件夹失败:', error)
    return {
      success: false,
      message: '检查更新文件夹失败: ' + (error?.message || '未知错误')
    }
  }
})