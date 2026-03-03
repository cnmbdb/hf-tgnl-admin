import { promises as fs } from 'fs'
import { join } from 'path'

interface CacheData {
  data: any
  timestamp: number
  expiresAt: number
}

interface GitHubRelease {
  tag_name: string
  name: string
  body: string
  published_at: string
  tarball_url: string
  html_url: string
  author: {
    login: string
    avatar_url: string
  }
  assets: Array<{
    name: string
    browser_download_url: string
    size: number
  }>
}

class GitHubCache {
  private cacheDir: string
  private cacheFile: string
  private cacheDuration: number // 缓存持续时间（毫秒）

  constructor() {
    this.cacheDir = join(process.cwd(), 'data')
    this.cacheFile = join(this.cacheDir, 'github-releases-cache.json')
    this.cacheDuration = 10 * 60 * 1000 // 10分钟缓存
  }

  // 确保缓存目录存在
  private async ensureCacheDir() {
    try {
      await fs.access(this.cacheDir)
    } catch {
      await fs.mkdir(this.cacheDir, { recursive: true })
    }
  }

  // 获取缓存数据
  async getCache(): Promise<GitHubRelease[] | null> {
    try {
      await this.ensureCacheDir()
      const cacheContent = await fs.readFile(this.cacheFile, 'utf-8')
      const cache: CacheData = JSON.parse(cacheContent)
      
      // 检查缓存是否过期
      if (Date.now() > cache.expiresAt) {
        console.log('GitHub releases缓存已过期')
        return null
      }
      
      console.log('使用GitHub releases缓存数据')
      return cache.data
    } catch (error) {
      console.log('读取GitHub releases缓存失败，将重新获取')
      return null
    }
  }

  // 设置缓存数据
  async setCache(data: GitHubRelease[]) {
    try {
      await this.ensureCacheDir()
      const cache: CacheData = {
        data,
        timestamp: Date.now(),
        expiresAt: Date.now() + this.cacheDuration
      }
      
      await fs.writeFile(this.cacheFile, JSON.stringify(cache, null, 2))
      console.log('GitHub releases数据已缓存')
    } catch (error) {
      console.error('保存GitHub releases缓存失败:', error)
    }
  }

  // 清除缓存
  async clearCache() {
    try {
      await fs.unlink(this.cacheFile)
      console.log('GitHub releases缓存已清除')
    } catch (error) {
      console.log('清除GitHub releases缓存失败或缓存不存在')
    }
  }

  // 获取GitHub releases数据（带缓存）
  async getGitHubReleases(githubRepo: string): Promise<GitHubRelease[]> {
    // 首先尝试从缓存获取
    const cachedData = await this.getCache()
    if (cachedData) {
      return cachedData
    }

    // 缓存不存在或已过期，从GitHub API获取
    console.log('正在从GitHub releases API获取版本信息...')
    const releasesApiUrl = `https://api.github.com/repos/${githubRepo}/releases`
    
    const response = await fetch(releasesApiUrl, {
      headers: {
        'User-Agent': 'HF-TGNL-Admin-Downloader/1.0',
        'Accept': 'application/vnd.github.v3+json',
      },
      // 添加超时设置
      signal: AbortSignal.timeout(15000) // 15秒超时
    })
    
    if (!response.ok) {
      // 检查是否是速率限制错误
      if (response.status === 403) {
        const rateLimitRemaining = response.headers.get('X-RateLimit-Remaining')
        const rateLimitReset = response.headers.get('X-RateLimit-Reset')
        
        if (rateLimitRemaining === '0') {
          const resetTime = rateLimitReset ? new Date(parseInt(rateLimitReset) * 1000) : null
          const resetTimeStr = resetTime ? resetTime.toLocaleString('zh-CN') : '未知'
          throw new Error(`GitHub API速率限制已达上限，请在 ${resetTimeStr} 后重试`)
        }
      }
      
      throw new Error(`GitHub releases API: ${response.status} ${response.statusText}`)
    }
    
    const releasesData = await response.json()
    console.log(`成功获取GitHub releases数据，发现 ${releasesData.length} 个版本`)
    
    // 保存到缓存
    await this.setCache(releasesData)
    
    return releasesData
  }
}

// 导出单例实例
export const githubCache = new GitHubCache()