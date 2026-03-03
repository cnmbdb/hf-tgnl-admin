import { promises as fs } from 'fs'
import { join } from 'path'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { sessionId, extractPath, backupPath } = body || {}
    
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
    
    if (!backupPath) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少备份路径'
      })
    }

    const projectRoot = process.cwd()
    const appliedFiles: string[] = []
    const skippedFiles: string[] = []
    const errors: string[] = []
    const logs: string[] = []

    // 步骤1: 停止当前服务
    logs.push('开始停止当前服务...')
    try {
      // 停止Web开发服务器 (npm run dev)
      try {
        await execAsync('pkill -f "npm run dev"')
        logs.push('✓ Web开发服务器已停止')
      } catch (error) {
        logs.push('⚠ Web开发服务器可能已经停止或未运行')
      }

      // 停止Python机器人服务 (al.py)
      try {
        await execAsync('pkill -f "python3 al.py"')
        logs.push('✓ Python机器人服务已停止')
      } catch (error) {
        logs.push('⚠ Python机器人服务可能已经停止或未运行')
      }

      // 等待服务完全停止
      await new Promise(resolve => setTimeout(resolve, 2000))
      logs.push('✓ 服务停止完成')
    } catch (error: any) {
      errors.push(`停止服务失败: ${error.message}`)
      logs.push(`✗ 停止服务失败: ${error.message}`)
    }

    // 步骤2: 记录当前版本的所有文件权限
    logs.push('开始记录当前版本文件权限...')
    const permissionsMap: Record<string, string> = {}
    try {
      // 获取项目根目录下所有文件的权限
      const { stdout } = await execAsync(`find "${projectRoot}" -type f -exec stat -f "%N:%Mp%Lp" {} \\;`)
      const permissionLines = stdout.trim().split('\n')
      
      for (const line of permissionLines) {
        if (line.includes(':')) {
          const [filePath, permissions] = line.split(':')
          const relativePath = filePath.replace(projectRoot + '/', '')
          permissionsMap[relativePath] = permissions
        }
      }
      
      // 保存权限信息到文件
      await fs.writeFile(
        join(projectRoot, 'data', 'file-permissions-backup.json'),
        JSON.stringify(permissionsMap, null, 2)
      )
      
      logs.push(`✓ 已记录 ${Object.keys(permissionsMap).length} 个文件的权限`)
    } catch (error: any) {
      errors.push(`记录文件权限失败: ${error.message}`)
      logs.push(`✗ 记录文件权限失败: ${error.message}`)
    }

    // 步骤3: 处理新文件权限并剪切到上层目录
    logs.push('开始处理新文件权限和移动文件...')
    try {
      // 验证路径是否存在
      await fs.access(extractPath)
      
      // 获取解压目录中的所有文件（排除zip文件）
      const extractedItems = await fs.readdir(extractPath)
      const updateItems = extractedItems.filter(item => !item.endsWith('.zip'))
      
      if (updateItems.length === 0) {
        throw new Error('解压目录中没有找到更新文件')
      }

      // 找到非zip的文件夹（应该是nl-admin-vx.x.x格式）
      const updateFolder = updateItems.find(item => {
        const itemPath = join(extractPath, item)
        try {
          const stat = require('fs').statSync(itemPath)
          return stat.isDirectory()
        } catch {
          return false
        }
      })

      if (!updateFolder) {
        throw new Error('未找到更新文件夹')
      }

      const updateFolderPath = join(extractPath, updateFolder)
      logs.push(`✓ 找到更新文件夹: ${updateFolder}`)

      // 获取更新文件夹内的所有文件
      const updateFolderItems = await fs.readdir(updateFolderPath)
      
      // 为新文件设置权限（对应原版本的文件权限）
      for (const item of updateFolderItems) {
        const sourcePath = join(updateFolderPath, item)
        const targetPath = join(projectRoot, item)
        
        try {
          const sourceStat = await fs.stat(sourcePath)
          
          if (sourceStat.isDirectory()) {
            // 处理目录：递归复制并设置权限
            try {
              // 如果目标目录存在，先删除
              try {
                await fs.access(targetPath)
                await fs.rm(targetPath, { recursive: true, force: true })
              } catch {
                // 目标目录不存在，忽略
              }
              
              // 复制新目录
              await execAsync(`cp -r "${sourcePath}" "${targetPath}"`)
              
              // 递归设置目录内文件权限
              await setDirectoryPermissions(sourcePath, targetPath, permissionsMap, projectRoot)
              
              appliedFiles.push(item)
              logs.push(`✓ 已复制目录: ${item}`)
              
            } catch (error: any) {
              errors.push(`复制目录 ${item} 失败: ${error.message}`)
              skippedFiles.push(item)
              logs.push(`✗ 复制目录 ${item} 失败: ${error.message}`)
            }
            
          } else {
            // 处理文件：直接覆盖并设置权限
            try {
              await fs.copyFile(sourcePath, targetPath)
              
              // 设置文件权限
              const relativePath = item
              if (permissionsMap[relativePath]) {
                await execAsync(`chmod ${permissionsMap[relativePath]} "${targetPath}"`)
              }
              
              appliedFiles.push(item)
              logs.push(`✓ 已复制文件: ${item}`)
              
            } catch (error: any) {
              errors.push(`复制文件 ${item} 失败: ${error.message}`)
              skippedFiles.push(item)
              logs.push(`✗ 复制文件 ${item} 失败: ${error.message}`)
            }
          }
          
        } catch (error: any) {
          errors.push(`处理 ${item} 失败: ${error.message}`)
          skippedFiles.push(item)
          logs.push(`✗ 处理 ${item} 失败: ${error.message}`)
        }
      }
      
    } catch (error: any) {
      errors.push(`处理新文件失败: ${error.message}`)
      logs.push(`✗ 处理新文件失败: ${error.message}`)
    }

    // 检查是否有关键文件更新失败
    const criticalFiles = ['package.json', 'nuxt.config.ts', 'server/']
    const failedCriticalFiles = criticalFiles.filter(file => 
      skippedFiles.some(skipped => skipped.includes(file))
    )
    
    if (failedCriticalFiles.length > 0) {
      errors.push(`关键文件更新失败: ${failedCriticalFiles.join(', ')}`)
      logs.push(`✗ 关键文件更新失败: ${failedCriticalFiles.join(', ')}`)
    }

    // 更新package.json后，需要重新安装依赖
    let needsNpmInstall = false
    if (appliedFiles.includes('package.json') || appliedFiles.includes('package-lock.json')) {
      needsNpmInstall = true
      logs.push('✓ 检测到package.json更新，将重新安装依赖')
    }

    // 创建应用更新信息文件
    const applyInfo = {
      timestamp: new Date().toISOString(),
      sessionId,
      appliedFiles,
      skippedFiles,
      errors,
      logs,
      needsNpmInstall,
      extractPath,
      backupPath,
      autoRestart: true
    }
    
    await fs.writeFile(
      join(projectRoot, 'data', 'last-update.json'),
      JSON.stringify(applyInfo, null, 2)
    )

    const hasErrors = errors.length > 0
    const success = appliedFiles.length > 0 && !hasErrors

    // 步骤4: 8秒后自动重启服务
    if (success) {
      logs.push('✓ 文件更新完成，8秒后将自动重启服务...')
      
      // 异步执行重启逻辑，不阻塞当前响应
      setTimeout(async () => {
        await restartServices(projectRoot, needsNpmInstall, sessionId)
      }, 8000)
    }

    // 更新状态管理
    try {
      await $fetch('/api/system/update-state', {
        method: 'POST',
        body: {
          action: 'update',
          sessionId,
          error: hasErrors ? `应用更新时出现错误: ${errors.join(', ')}` : undefined
        }
      })
    } catch (error) {
      console.warn('更新状态失败:', error)
    }

    return {
      success,
      message: success ? '自动更新流程已启动，8秒后将自动重启服务' : '更新应用时出现错误',
      data: {
        appliedFiles,
        skippedFiles,
        errors,
        logs,
        needsNpmInstall,
        totalFiles: appliedFiles.length + skippedFiles.length,
        successCount: appliedFiles.length,
        sessionId,
        autoRestart: success
      }
    }

  } catch (error: any) {
    console.error('自动更新失败:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || '自动更新失败: ' + (error?.message || '未知错误')
    })
  }
})

// 递归设置目录权限的辅助函数
async function setDirectoryPermissions(
  sourceDir: string, 
  targetDir: string, 
  permissionsMap: Record<string, string>, 
  projectRoot: string
) {
  try {
    const items = await fs.readdir(sourceDir)
    
    for (const item of items) {
      const sourcePath = join(sourceDir, item)
      const targetPath = join(targetDir, item)
      const stat = await fs.stat(sourcePath)
      
      if (stat.isDirectory()) {
        await setDirectoryPermissions(sourcePath, targetPath, permissionsMap, projectRoot)
      } else {
        // 设置文件权限
        const relativePath = targetPath.replace(projectRoot + '/', '')
        if (permissionsMap[relativePath]) {
          await execAsync(`chmod ${permissionsMap[relativePath]} "${targetPath}"`)
        }
      }
    }
  } catch (error) {
    console.warn('设置目录权限失败:', error)
  }
}

// 重启服务的辅助函数
async function restartServices(projectRoot: string, needsNpmInstall: boolean, sessionId: string) {
  const logs: string[] = []
  const errors: string[] = []
  
  try {
    logs.push('开始重启服务流程...')
    
    // 如果需要重新安装依赖
    if (needsNpmInstall) {
      logs.push('正在重新安装依赖...')
      try {
        await execAsync('npm install', { cwd: projectRoot })
        logs.push('✓ 依赖安装完成')
      } catch (error: any) {
        errors.push(`依赖安装失败: ${error.message}`)
        logs.push(`✗ 依赖安装失败: ${error.message}`)
      }
    }

    // 启动前端服务（最多重试3次）
    let frontendStarted = false
    for (let i = 0; i < 3; i++) {
      try {
        logs.push(`尝试启动前端服务 (第${i + 1}次)...`)
        
        // 启动前端开发服务器
        exec('npm run dev', { cwd: projectRoot })
        
        // 等待3秒检查服务是否启动成功
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        // 检查服务是否正在运行
        try {
          await execAsync('pgrep -f "npm run dev"')
          frontendStarted = true
          logs.push('✓ 前端服务启动成功')
          break
        } catch {
          logs.push(`✗ 前端服务启动失败 (第${i + 1}次)`)
        }
        
      } catch (error: any) {
        logs.push(`✗ 前端服务启动失败 (第${i + 1}次): ${error.message}`)
      }
    }

    // 如果3次重试都失败，尝试重新构建
    if (!frontendStarted) {
      logs.push('前端服务3次启动失败，开始重新构建...')
      try {
        // 清理缓存和构建文件
        await execAsync('rm -rf .nuxt .output node_modules/.cache', { cwd: projectRoot })
        logs.push('✓ 清理缓存完成')
        
        // 重新安装依赖
        await execAsync('npm install', { cwd: projectRoot })
        logs.push('✓ 重新安装依赖完成')
        
        // 处理可能的权限问题
        await execAsync(`chmod -R 755 "${projectRoot}/node_modules"`, { cwd: projectRoot })
        await execAsync(`chmod -R 755 "${projectRoot}/.nuxt"`, { cwd: projectRoot })
        logs.push('✓ 权限问题已修复')
        
        // 重新启动前端服务
        exec('npm run dev', { cwd: projectRoot })
        await new Promise(resolve => setTimeout(resolve, 5000))
        
        // 检查服务是否启动成功
        try {
          await execAsync('pgrep -f "npm run dev"')
          frontendStarted = true
          logs.push('✓ 重新构建后前端服务启动成功')
        } catch {
          errors.push('重新构建后前端服务仍然启动失败')
          logs.push('✗ 重新构建后前端服务仍然启动失败')
        }
        
      } catch (error: any) {
        errors.push(`重新构建失败: ${error.message}`)
        logs.push(`✗ 重新构建失败: ${error.message}`)
      }
    }

    // 启动Python机器人服务
    try {
      logs.push('正在启动Python机器人服务...')
      
      // 切换到nl-2333目录并启动机器人
      exec('cd nl-2333 && python3 al.py', { cwd: projectRoot })
      
      // 等待2秒检查服务是否启动成功
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      try {
        await execAsync('pgrep -f "python3 al.py"')
        logs.push('✓ Python机器人服务启动成功')
      } catch {
        logs.push('⚠ Python机器人服务可能启动失败，请手动检查')
      }
      
    } catch (error: any) {
      errors.push(`Python机器人服务启动失败: ${error.message}`)
      logs.push(`✗ Python机器人服务启动失败: ${error.message}`)
    }

    // 保存重启日志
    const restartInfo = {
      timestamp: new Date().toISOString(),
      sessionId,
      logs,
      errors,
      frontendStarted,
      needsNpmInstall
    }
    
    await fs.writeFile(
      join(projectRoot, 'data', 'restart-log.json'),
      JSON.stringify(restartInfo, null, 2)
    )

    logs.push('✓ 服务重启流程完成')
    
  } catch (error: any) {
    errors.push(`重启服务失败: ${error.message}`)
    logs.push(`✗ 重启服务失败: ${error.message}`)
  }
}