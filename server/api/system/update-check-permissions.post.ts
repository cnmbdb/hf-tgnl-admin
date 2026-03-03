import { promises as fs } from 'fs'
import { join } from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { sessionId, extractPath } = body || {}
    
    if (!sessionId) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少会话ID'
      })
    }
    
    if (!extractPath) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少解压路径'
      })
    }
    
    // 验证解压目录是否存在
    try {
      await fs.access(extractPath)
    } catch {
      throw createError({
        statusCode: 404,
        statusMessage: '解压目录不存在'
      })
    }
    
    const projectRoot = process.cwd()
    const issues: string[] = []
    const warnings: string[] = []
    
    try {
      // 检查解压后的文件
      const extractedFiles = await fs.readdir(extractPath)
      const updateFiles = extractedFiles.filter(file => !file.endsWith('.zip'))
      
      if (updateFiles.length === 0) {
        throw new Error('解压目录中没有找到更新文件')
      }
      
      // 检查关键文件和目录的权限
      const criticalPaths = [
        'package.json',
        'nuxt.config.ts', 
        'server/',
        'pages/',
        'components/',
        'assets/',
        'public/'
      ]
      
      for (const criticalPath of criticalPaths) {
        const targetPath = join(projectRoot, criticalPath)
        const updatePath = join(extractPath, criticalPath)
        
        // 检查目标文件/目录是否存在
        try {
          const targetStat = await fs.stat(targetPath)
          
          // 检查是否有写权限
          try {
            await fs.access(targetPath, fs.constants.W_OK)
          } catch {
            issues.push(`无法写入 ${criticalPath}：权限不足`)
          }
          
          // 检查更新文件是否存在
          try {
            await fs.stat(updatePath)
          } catch {
            warnings.push(`更新包中缺少 ${criticalPath}`)
          }
          
        } catch {
          warnings.push(`目标路径 ${criticalPath} 不存在`)
        }
      }
      
      // 检查磁盘空间
      try {
        const { stdout } = await execAsync(`df -h "${projectRoot}" | tail -1 | awk '{print $4}'`)
        const availableSpace = stdout.trim()
        
        // 计算更新文件总大小
        let totalSize = 0
        for (const file of updateFiles) {
          const filePath = join(extractPath, file)
          const stat = await fs.stat(filePath)
          if (stat.isFile()) {
            totalSize += stat.size
          } else if (stat.isDirectory()) {
            // 递归计算目录大小
            const { stdout: dirSize } = await execAsync(`du -sb "${filePath}" | cut -f1`)
            totalSize += parseInt(dirSize.trim())
          }
        }
        
        const totalSizeMB = Math.round(totalSize / 1024 / 1024)
        
        if (totalSizeMB > 100) { // 如果更新文件超过100MB，警告磁盘空间
          warnings.push(`更新文件较大 (${totalSizeMB}MB)，请确保有足够磁盘空间`)
        }
        
      } catch (error) {
        warnings.push('无法检查磁盘空间')
      }
      
      // 检查进程权限
      try {
        const processUser = process.getuid ? process.getuid() : 'unknown'
        const { stdout } = await execAsync(`ls -la "${projectRoot}" | head -2 | tail -1 | awk '{print $3}'`)
        const fileOwner = stdout.trim()
        
        if (processUser !== 'unknown' && fileOwner !== 'unknown') {
          // 这里可以添加更详细的权限检查
        }
      } catch (error) {
        warnings.push('无法检查进程权限')
      }
      
      const hasIssues = issues.length > 0
      const canProceed = !hasIssues
      
      // 更新状态管理
      try {
        await $fetch('/api/system/update-state', {
          method: 'POST',
          body: {
            action: 'update',
            sessionId,
            error: hasIssues ? `权限检查失败: ${issues.join(', ')}` : undefined
          }
        })
      } catch (error) {
        console.warn('更新状态失败:', error)
      }
      
      return {
        success: true,
        message: canProceed ? '权限检查通过' : '权限检查发现问题',
        data: {
          canProceed,
          issues,
          warnings,
          updateFiles: updateFiles.length,
          sessionId
        }
      }
      
    } catch (error: any) {
      console.error('权限检查失败:', error)
      
      // 更新状态管理 - 记录错误
      try {
        await $fetch('/api/system/update-state', {
          method: 'POST',
          body: {
            action: 'update',
            sessionId,
            error: `权限检查失败: ${error.message}`
          }
        })
      } catch (updateError) {
        console.warn('更新状态失败:', updateError)
      }
      
      throw createError({
        statusCode: 500,
        statusMessage: `权限检查失败: ${error.message}`
      })
    }
    
  } catch (error: any) {
    console.error('文件权限检查失败:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || '文件权限检查失败: ' + (error?.message || '未知错误')
    })
  }
})