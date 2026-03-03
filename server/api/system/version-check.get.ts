export default defineEventHandler(async (event) => {
  try {
    // GitHub仓库信息
    const GITHUB_REPO = 'cnmbdb/hf-tgnl-admin'
    const RELEASES_URL = `https://github.com/${GITHUB_REPO}/releases`
    
    let currentVersion = process.env.APP_VERSION || ''
    if (!currentVersion) {
      try {
        const fs = await import('fs')
        const path = await import('path')
        const envPathCandidates = [
          path.default.join(process.cwd(), '.env'),
          path.default.join(process.cwd(), '../.env'),
          path.default.join(process.cwd(), '../../.env')
        ]
        const envPath = envPathCandidates.find(p => fs.existsSync(p))
        if (envPath) {
          const content = fs.readFileSync(envPath, 'utf-8')
          const line = content.split('\n').find(l => l.trim().startsWith('APP_VERSION=')) || ''
          currentVersion = line ? line.split('=', 2)[1].trim() : ''
        }
      } catch {}
    }
    if (!currentVersion) {
      try {
        const fs = await import('fs')
        const path = await import('path')
        const packageJsonPath = path.default.resolve(process.cwd(), 'package.json')
        const packageJsonContent = await fs.promises.readFile(packageJsonPath, 'utf-8')
        const packageJson = JSON.parse(packageJsonContent)
        currentVersion = packageJson.version || '1.0.4'
      } catch {
        currentVersion = '1.0.4'
      }
    }
    
    // 从GitHub releases API获取最新版本
    let hasUpdate = false
    let updateInfo = null
    let latestVersion = currentVersion

    try {
      // 获取GitHub releases数据
      const response = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/releases/latest`, {
        headers: {
          'Accept': 'application/vnd.github+json',
          'User-Agent': 'tgnl-admin'
        }
      })
      
      if (response.ok) {
        const release = await response.json()
        
        // 从tag_name或name中提取版本号（支持多种格式）
        // 格式1: nl.adminv1.0.7 -> 1.0.7
        // 格式2: v1.0.7 -> 1.0.7  
        // 格式3: 1.0.7 -> 1.0.7
        let versionStr = release.tag_name
        const versionMatch = versionStr.match(/(\d+\.\d+\.\d+)/)
        if (versionMatch) {
          latestVersion = versionMatch[1]
        } else {
          latestVersion = versionStr.replace(/^v/, '')
        }
        
        console.log('GitHub最新版本:', latestVersion, '当前版本:', currentVersion)
        
        // 比较版本号
        if (compareVersions(latestVersion, currentVersion) > 0) {
          hasUpdate = true
          updateInfo = {
            version: latestVersion,
            name: release.name || `Release ${latestVersion}`,
            description: release.body || '无详细描述',
            publishedAt: release.published_at,
            downloadUrl: RELEASES_URL, // 直接跳转到releases页面
            htmlUrl: release.html_url,
            changelog: release.body || '请访问GitHub查看详细更新日志'
          }
        }
      }
    } catch (error) {
      console.error('获取GitHub版本信息失败:', error)
    }

    return {
      success: true,
      data: {
        currentVersion,
        latestVersion,
        hasUpdate,
        updateInfo,
        releasesUrl: RELEASES_URL, // 添加releases页面链接
        lastChecked: new Date().toISOString(),
        source: 'github-releases'
      }
    }

  } catch (error) {
    console.error('版本检查失败:', error)
    
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
      data: {
        currentVersion: '1.0.4',
        latestVersion: '1.0.4',
        hasUpdate: false,
        updateInfo: null,
        releasesUrl: 'https://github.com/cnmbdb/hf-tgnl-admin/releases',
        lastChecked: new Date().toISOString(),
        source: 'fallback'
      }
    }
  }
})

// 比较版本号
function compareVersions(version1: string, version2: string): number {
  const v1Parts = version1.split('.').map(Number)
  const v2Parts = version2.split('.').map(Number)
  
  for (let i = 0; i < Math.max(v1Parts.length, v2Parts.length); i++) {
    const v1Part = v1Parts[i] || 0
    const v2Part = v2Parts[i] || 0
    
    if (v1Part > v2Part) return 1
    if (v1Part < v2Part) return -1
  }
  
  return 0
}
