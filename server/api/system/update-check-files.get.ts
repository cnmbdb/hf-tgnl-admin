import { promises as fs } from 'fs'
import { join } from 'path'

export default defineEventHandler(async (event) => {
  try {
    const updateDir = join(process.cwd(), '更新文件')
    
    // 检查更新目录是否存在
    try {
      await fs.access(updateDir)
    } catch {
      return {
        success: true,
        data: {
          hasDownloadedFiles: false,
          files: []
        }
      }
    }
    
    // 读取目录中的文件
    const files = await fs.readdir(updateDir)
    const zipFiles = files.filter(file => 
      file.endsWith('.zip') && 
      (file.includes('update-nl-admin') || file.includes('nl-admin-') || file.includes('nl-admin'))
    )
    
    const fileDetails = []
    for (const file of zipFiles) {
      const filePath = join(updateDir, file)
      try {
        const stats = await fs.stat(filePath)
        if (stats.size > 0) { // 只包含非空文件
          fileDetails.push({
            name: file,
            path: filePath,
            size: stats.size,
            createdAt: stats.birthtime,
            modifiedAt: stats.mtime
          })
        }
      } catch (error) {
        console.warn(`无法获取文件 ${file} 的信息:`, error)
      }
    }
    
    // 按修改时间排序，最新的在前
    fileDetails.sort((a, b) => new Date(b.modifiedAt).getTime() - new Date(a.modifiedAt).getTime())
    
    return {
      success: true,
      data: {
        hasDownloadedFiles: fileDetails.length > 0,
        files: fileDetails,
        latestFile: fileDetails[0] || null
      }
    }
  } catch (error) {
    console.error('检查下载文件失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: '检查下载文件失败: ' + (error as Error).message
    })
  }
})