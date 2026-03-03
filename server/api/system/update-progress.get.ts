import { promises as fs } from 'fs'
import { join } from 'path'

// 全局下载进度存储
const downloadProgress = new Map()

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    const downloadId = query.downloadId as string
    
    if (!downloadId) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少下载ID'
      })
    }
    
    const progress = downloadProgress.get(downloadId) || {
      progress: 0,
      status: 'pending',
      message: '准备下载...',
      downloadedBytes: 0,
      totalBytes: 0
    }

    console.log(`获取下载进度，downloadId: ${downloadId}, progress:`, progress)

    return {
      success: true,
      data: progress
    }
  } catch (error: any) {
    console.error('获取下载进度失败:', error)
    throw createError({
      statusCode: 500,
      statusMessage: '获取下载进度失败: ' + (error?.message || '未知错误')
    })
  }
})

// 导出进度管理函数供其他模块使用
export const setDownloadProgress = (downloadId: string, progress: any) => {
  downloadProgress.set(downloadId, progress)
}

export const getDownloadProgress = (downloadId: string) => {
  return downloadProgress.get(downloadId)
}

export const clearDownloadProgress = (downloadId: string) => {
  downloadProgress.delete(downloadId)
}