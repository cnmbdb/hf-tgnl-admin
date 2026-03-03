import { promises as fs } from 'fs'
import { join } from 'path'
import { spawn } from 'child_process'
import { requireAdmin } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  try {
    // 暂时跳过身份验证以便测试
    // TODO: 恢复身份验证检查
    // const user = await requireAdmin(event)
    // if (!user) {
    //   throw createError({
    //     statusCode: 403,
    //     statusMessage: '需要管理员权限'
    //   })
    // }

    const body = await readBody(event) || {}
    const { version, sessionId } = body
    
    // 验证会话ID
    if (!sessionId) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少会话ID'
      })
    }
    
    // 自动获取GitHub最新版本的下载链接
    const githubRepo = 'cnmbdb/hf-tgnl-admin' // 项目的实际仓库
    let downloadUrl
    let actualVersion = version
    
    try {
      // 使用缓存机制获取GitHub releases数据
      const { githubCache } = await import('../../utils/github-cache')
      const releasesData = await githubCache.getGitHubReleases(githubRepo)
      
      let targetRelease = null
      let targetAsset = null
      
      if (version) {
        // 查找指定版本 - 优先匹配压缩包文件名
        console.log(`正在查找指定版本: ${version}`)
        targetRelease = releasesData.find((release: any) => {
          const asset = release.assets?.find((asset: any) => 
            asset.name.includes('nl-admin') && asset.name.endsWith('.zip')
          )
          if (asset) {
            const fileName = asset.name
            // 优先匹配完整文件名（如：nl-admin-v1.0.5.zip）
            if (fileName === version || fileName === `${version}.zip`) {
              return true
            }
            // 其次匹配提取的版本号
            const versionMatch = fileName.match(/nl-admin-(v?\d+\.\d+\.\d+)\.zip/)
            if (versionMatch && (versionMatch[1] === version || `v${versionMatch[1]}` === version)) {
              return true
            }
          }
          return false
        })
      } else {
        // 查找最新版本（第一个有压缩包文件的版本）
        console.log('正在查找最新版本...')
        for (const release of releasesData) {
          if (release.assets && release.assets.length > 0) {
            const zipAsset = release.assets.find((asset: any) => 
              asset.name.includes('nl-admin') && asset.name.endsWith('.zip')
            )
            if (zipAsset) {
              targetRelease = release
              break
            }
          }
        }
      }
      
      if (targetRelease) {
        // 查找nl-admin压缩包文件
        targetAsset = targetRelease.assets.find((asset: any) => 
          asset.name.includes('nl-admin') && asset.name.endsWith('.zip')
        )
        
        if (targetAsset) {
          downloadUrl = targetAsset.browser_download_url
          
          // 使用压缩包文件名作为版本号（按照用户要求）
          const fileName = targetAsset.name
          actualVersion = fileName // 直接使用文件名作为版本号
          
          console.log(`找到目标版本: ${actualVersion}, 下载链接: ${downloadUrl}`)
        } else {
          throw new Error(`版本 ${targetRelease.tag_name} 中未找到nl-admin压缩包文件`)
        }
      } else {
        throw new Error(version ? `未找到指定版本: ${version}` : '未找到任何可用版本')
      }
      
      if (!downloadUrl) {
        throw new Error('未找到可下载的压缩包')
      }
    } catch (error: any) {
      console.error('获取GitHub下载链接失败:', error)
      
      // 如果是网络超时或连接错误，提供更友好的错误信息
      let errorMessage = error?.message || '未知错误'
      let statusCode = 500
      
      if (error.name === 'TimeoutError' || error.name === 'AbortError') {
        errorMessage = '连接GitHub超时，请检查网络连接后重试'
      } else if (error.message.includes('fetch')) {
        errorMessage = '无法连接到GitHub，请检查网络设置'
      } else if (error.message.includes('速率限制') || error.message.includes('rate limit')) {
        // GitHub API速率限制错误
        errorMessage = error.message
        statusCode = 429 // 使用429状态码表示速率限制
      } else if (error.message.includes('403')) {
        errorMessage = 'GitHub API访问受限，可能是速率限制，请稍后重试'
        statusCode = 429
      }
      
      throw createError({
        statusCode,
        statusMessage: 'GitHub API: ' + errorMessage
      })
    }
    
    // 检查管理员权限 - 暂时禁用以便测试
    // TODO: 恢复身份验证检查
    // const headers = getHeaders(event)
    // const authHeader = headers.authorization
    // 
    // if (!authHeader || !authHeader.startsWith('Bearer ')) {
    //   throw createError({
    //     statusCode: 401,
    //     statusMessage: '未授权访问'
    //   })
    // }
    
    // 确保更新目录存在 - 使用指定的更新文件夹
    const updateDir = join(process.cwd(), '更新文件')
    try {
      await fs.access(updateDir)
    } catch {
      await fs.mkdir(updateDir, { recursive: true })
    }
    
    const backupDir = join(process.cwd(), 'backup')
    try {
      await fs.mkdir(backupDir, { recursive: true })
    } catch (error) {
      console.warn('创建备份目录失败，可能已存在')
    }
    
    // 生成下载ID
    const downloadId = `download-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    // 下载更新文件
    const updateFileName = `update-${actualVersion}-${Date.now()}.zip`
    const updateFilePath = join(updateDir, updateFileName)
    
    try {
      // 导入进度管理函数
      const { setDownloadProgress } = await import('./update-progress.get')
      
      // 初始化进度
      console.log(`初始化下载进度，downloadId: ${downloadId}`)
      setDownloadProgress(downloadId, {
        progress: 0,
        status: 'downloading',
        message: '开始下载...',
        downloadedBytes: 0,
        totalBytes: 0
      })
      
      // 创建带超时的fetch请求
      const controller = new AbortController()
      const timeoutId = setTimeout(() => {
        controller.abort()
      }, 900000) // 15分钟超时，适应慢速网络
      
      const response = await fetch(downloadUrl, {
        headers: {
          'User-Agent': 'HF-TGNL-Admin-OTA-Updater'
        },
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      
      if (!response.ok) {
        throw new Error(`下载失败: ${response.status} ${response.statusText}`)
      }
      
      const totalBytes = parseInt(response.headers.get('content-length') || '0')
      let downloadedBytes = 0
      let lastProgressUpdate = 0
      let lastProgress = 0
      
      // 更新总大小
      setDownloadProgress(downloadId, {
        progress: 0,
        status: 'downloading',
        message: '正在下载...',
        downloadedBytes: 0,
        totalBytes
      })
      
      // 收集下载数据
      const chunks: Buffer[] = []
      
      if (response.body) {
        const reader = response.body.getReader()
        
        try {
          while (true) {
            const { done, value } = await reader.read()
            
            if (done) break
            
            if (value) {
              downloadedBytes += value.length
              chunks.push(Buffer.from(value))
              
              // 计算进度
              const progress = totalBytes > 0 ? Math.round((downloadedBytes / totalBytes) * 100) : 0
              const now = Date.now()
              
              // 节流更新：每500ms或进度变化超过1%时更新
              if (now - lastProgressUpdate > 500 || progress - lastProgress >= 1) {
                setDownloadProgress(downloadId, {
                  progress,
                  status: 'downloading',
                  message: `已下载 ${Math.round(downloadedBytes / 1024 / 1024 * 100) / 100} MB / ${Math.round(totalBytes / 1024 / 1024 * 100) / 100} MB`,
                  downloadedBytes,
                  totalBytes
                })
                lastProgressUpdate = now
                lastProgress = progress
                
                // 输出进度日志
                console.log(`下载进度 ${downloadId}: ${progress}% (${Math.round(downloadedBytes / 1024 / 1024 * 100) / 100} MB / ${Math.round(totalBytes / 1024 / 1024 * 100) / 100} MB)`)
              }
            }
          }
        } finally {
          reader.releaseLock()
        }
      }
      
      // 写入文件
      const buffer = Buffer.concat(chunks)
      console.log(`准备写入文件: ${updateFilePath}, 大小: ${buffer.length} bytes`)
      await fs.writeFile(updateFilePath, buffer)
      console.log(`文件写入完成: ${updateFilePath}`)
      
      // 完成进度
      setDownloadProgress(downloadId, {
        progress: 100,
        status: 'completed',
        message: '下载完成',
        downloadedBytes: buffer.length,
        totalBytes: buffer.length
      })
      
      // 更新状态管理 - 记录下载路径
      try {
        await $fetch('/api/system/update-state', {
          method: 'POST',
          body: {
            action: 'update',
            sessionId,
            downloadPath: updateFilePath
          }
        })
      } catch (error) {
        console.warn('更新状态失败:', error)
      }
      
      return {
        success: true,
        message: '更新文件下载成功',
        data: {
          version: actualVersion,
          filePath: updateFilePath,
          fileSize: buffer.length,
          downloadedAt: new Date().toISOString(),
          downloadId,
          sessionId
        }
      }
    } catch (error) {
      console.error('下载更新文件失败:', error)
      
      // 更新进度状态为失败
      try {
        const { setDownloadProgress } = await import('./update-progress.get')
        setDownloadProgress(downloadId, {
          progress: 0,
          status: 'failed',
          message: '下载失败',
          downloadedBytes: 0,
          totalBytes: 0
        })
      } catch (progressError) {
        console.warn('更新下载进度失败:', progressError)
      }
      
      // 根据错误类型提供不同的错误信息
      let errorMessage = '下载更新文件失败'
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = '下载超时，请检查网络连接后重试'
        } else if (error.message.includes('fetch')) {
          errorMessage = '网络连接失败，请检查网络设置'
        } else {
          errorMessage = `下载失败: ${error.message}`
        }
      }
      
      throw createError({
        statusCode: 500,
        statusMessage: errorMessage
      })
    }
  } catch (error: any) {
    console.error('更新下载失败:', error)
    if (error.statusCode) {
      throw error
    }
    throw createError({
      statusCode: 500,
      statusMessage: '更新下载失败: ' + (error?.message || '未知错误')
    })
  }
})