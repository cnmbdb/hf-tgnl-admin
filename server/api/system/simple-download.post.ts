import { promises as fs } from 'fs'
import { join } from 'path'

export default defineEventHandler(async (event) => {
  try {
    // 直接下载最新版本，无需复杂验证
    const githubRepo = 'cnmbdb/hf-tgnl-admin'
    
    // 获取最新版本信息
    const releaseResponse = await fetch(`https://api.github.com/repos/${githubRepo}/releases/latest`, {
      headers: {
        'User-Agent': 'HF-TGNL-Admin-Simple-Downloader',
        'Accept': 'application/vnd.github.v3+json'
      }
    })
    
    if (!releaseResponse.ok) {
      throw new Error(`获取版本信息失败: ${releaseResponse.status}`)
    }
    
    const releaseData = await releaseResponse.json()
    
    // 优先查找上传的资源文件（实际发布的文件）
    const zipAsset = releaseData.assets?.find((asset: any) => 
      asset.name.endsWith('.zip') && asset.name.includes('nl-admin')
    )
    
    const downloadUrl = zipAsset ? zipAsset.browser_download_url : releaseData.zipball_url
    const version = releaseData.tag_name
    
    console.log(`下载文件: ${zipAsset ? zipAsset.name : '源码压缩包'}`)
    
    // 确保下载目录存在
    const downloadDir = join(process.cwd(), '更新文件')
    try {
      await fs.access(downloadDir)
    } catch {
      await fs.mkdir(downloadDir, { recursive: true })
    }
    
    // 下载文件
    const fileName = `${version}-${Date.now()}.zip`
    const filePath = join(downloadDir, fileName)
    
    console.log(`开始下载: ${downloadUrl}`)
    
    const downloadResponse = await fetch(downloadUrl, {
      headers: {
        'User-Agent': 'HF-TGNL-Admin-Simple-Downloader'
      }
    })
    
    if (!downloadResponse.ok) {
      throw new Error(`下载失败: ${downloadResponse.status}`)
    }
    
    // 获取文件内容并保存
    const arrayBuffer = await downloadResponse.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)
    
    await fs.writeFile(filePath, buffer)
    
    console.log(`下载完成: ${filePath}`)
    
    return {
      success: true,
      message: '下载完成',
      data: {
        version,
        filePath,
        fileName,
        fileSize: buffer.length,
        downloadedAt: new Date().toISOString()
      }
    }
    
  } catch (error: any) {
    console.error('下载失败:', error)
    return {
      success: false,
      message: '下载失败: ' + (error?.message || '未知错误')
    }
  }
})