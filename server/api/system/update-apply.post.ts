import { promises as fs } from 'fs'
import { join } from 'path'
import { exec, spawn } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

// 获取文件权限
async function getFilePermissions(filePath: string): Promise<string> {
  try {
    const { stdout } = await execAsync(`stat -f "%Mp%Lp" "${filePath}"`)
    return stdout.trim()
  } catch {
    return '644' // 默认权限
  }
}

// 设置文件权限
async function setFilePermissions(filePath: string, permissions: string): Promise<void> {
  try {
    await execAsync(`chmod ${permissions} "${filePath}"`)
  } catch (error) {
    console.warn(`设置文件权限失败: ${filePath}`, error)
  }
}

// 递归获取目录下所有文件的权限
async function getDirectoryPermissions(dirPath: string): Promise<Record<string, string>> {
  const permissions: Record<string, string> = {}
  
  async function traverse(currentPath: string, relativePath: string = '') {
    try {
      const items = await fs.readdir(currentPath)
      
      for (const item of items) {
        const fullPath = join(currentPath, item)
        const relativeItemPath = relativePath ? join(relativePath, item) : item
        
        try {
          const stat = await fs.stat(fullPath)
          permissions[relativeItemPath] = await getFilePermissions(fullPath)
          
          if (stat.isDirectory()) {
            await traverse(fullPath, relativeItemPath)
          }
        } catch (error) {
          console.warn(`获取权限失败: ${fullPath}`, error)
        }
      }
    } catch (error) {
      console.warn(`读取目录失败: ${currentPath}`, error)
    }
  }
  
  await traverse(dirPath)
  return permissions
}

// 停止当前运行的服务
async function stopCurrentServices(): Promise<{ stopped: string[], errors: string[] }> {
  const stopped: string[] = []
  const errors: string[] = []
  
  try {
    // 停止 npm run dev (Node.js 前端服务)
    try {
      await execAsync(`pkill -f "npm run dev"`)
      stopped.push('npm run dev')
    } catch (error) {
      // 可能进程不存在，不算错误
      console.log('npm run dev 进程可能已停止')
    }
    
    try {
      await execAsync(`pkill -f "node.*nuxt"`)
      stopped.push('nuxt dev server')
    } catch (error) {
      console.log('nuxt dev server 进程可能已停止')
    }
    
    // 停止 Python 机器人服务 (al.py)
    try {
      await execAsync(`pkill -f "python.*al.py"`)
      stopped.push('python al.py')
    } catch (error) {
      console.log('python al.py 进程可能已停止')
    }
    
    try {
      await execAsync(`pkill -f "python3.*al.py"`)
      stopped.push('python3 al.py')
    } catch (error) {
      console.log('python3 al.py 进程可能已停止')
    }
    
    // 等待进程完全停止
    await new Promise(resolve => setTimeout(resolve, 2000))
    
  } catch (error: any) {
    errors.push(`停止服务时出错: ${error.message}`)
  }
  
  return { stopped, errors }
}

// 启动服务的函数
async function startServices(projectRoot: string): Promise<{ started: string[], errors: string[] }> {
  const started: string[] = []
  const errors: string[] = []
  
  try {
    // 启动前端服务 (npm run dev)
    const frontendProcess = spawn('npm', ['run', 'dev'], {
      cwd: projectRoot,
      detached: true,
      stdio: 'ignore'
    })
    
    frontendProcess.unref()
    started.push('前端服务 (npm run dev)')
    
    // 等待2秒让前端服务启动
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 启动Python机器人服务
    const botProcess = spawn('python3', ['al.py'], {
      cwd: join(projectRoot, 'nl-2333'),
      detached: true,
      stdio: 'ignore'
    })
    
    botProcess.unref()
    started.push('机器人服务 (python3 al.py)')
    
  } catch (error: any) {
    errors.push(`启动服务失败: ${error.message}`)
  }
  
  return { started, errors }
}

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    const { sessionId } = body || {}
    
    if (!sessionId) {
      throw createError({
        statusCode: 400,
        statusMessage: '缺少会话ID'
      })
    }
    
    const projectRoot = process.cwd()
    const updateDir = join(projectRoot, '更新文件')
    const appliedFiles: string[] = []
    const skippedFiles: string[] = []
    const errors: string[] = []
    
    try {
      console.log('开始应用更新流程...')
      
      // 第1步：停止当前服务
      console.log('步骤1: 停止当前服务...')
      const { stopped, errors: stopErrors } = await stopCurrentServices()
      errors.push(...stopErrors)
      console.log('已停止服务:', stopped)
      
      // 第2步：记录当前版本的所有文件权限
      console.log('步骤2: 记录当前版本文件权限...')
      const currentPermissions = await getDirectoryPermissions(projectRoot)
      
      // 保存权限信息到备份目录
      const permissionsFile = join(projectRoot, 'data', 'file-permissions.json')
      await fs.writeFile(permissionsFile, JSON.stringify(currentPermissions, null, 2))
      console.log('文件权限已记录到:', permissionsFile)
      
      // 第3步：查找更新文件目录中的非zip文件夹
      console.log('步骤3: 查找更新文件...')
      const updateItems = await fs.readdir(updateDir)
      const nonZipItems = updateItems.filter(item => !item.endsWith('.zip'))
      
      if (nonZipItems.length === 0) {
        throw new Error('更新目录中没有找到非zip文件')
      }
      
      // 假设第一个非zip项目是更新文件夹
      const updateSourceDir = join(updateDir, nonZipItems[0])
      const updateStat = await fs.stat(updateSourceDir)
      
      if (!updateStat.isDirectory()) {
        throw new Error('找到的更新项目不是目录')
      }
      
      console.log('找到更新源目录:', updateSourceDir)
      
      // 第4步：获取更新文件的内容并应用权限
      console.log('步骤4: 应用更新文件...')
      const updateContents = await fs.readdir(updateSourceDir)
      
      for (const item of updateContents) {
        const sourcePath = join(updateSourceDir, item)
        const targetPath = join(projectRoot, item)
        
        try {
          const sourceStat = await fs.stat(sourcePath)
          
          if (sourceStat.isDirectory()) {
            // 处理目录：先删除旧目录，再移动新目录
            try {
              await fs.access(targetPath)
              await fs.rm(targetPath, { recursive: true, force: true })
            } catch {
              // 目标目录不存在，忽略
            }
            
            // 移动目录
            await execAsync(`mv "${sourcePath}" "${targetPath}"`)
            appliedFiles.push(item)
            
            // 递归应用权限
            const itemPermissions = await getDirectoryPermissions(targetPath)
            for (const [relativePath, _] of Object.entries(itemPermissions)) {
              const fullPath = join(targetPath, relativePath)
              const originalPermission = currentPermissions[join(item, relativePath)] || currentPermissions[relativePath] || '644'
              await setFilePermissions(fullPath, originalPermission)
            }
            
          } else {
            // 处理文件：移动并应用权限
            await execAsync(`mv "${sourcePath}" "${targetPath}"`)
            appliedFiles.push(item)
            
            // 应用原始权限
            const originalPermission = currentPermissions[item] || '644'
            await setFilePermissions(targetPath, originalPermission)
          }
          
        } catch (error: any) {
          errors.push(`处理 ${item} 失败: ${error.message}`)
          skippedFiles.push(item)
        }
      }
      
      // 完成第4步，标记为完成
      await $fetch('/api/system/update-state', {
        method: 'POST',
        body: {
          action: 'complete-step',
          sessionId
        }
      })
      
      console.log('步骤4完成，8秒后自动启动第5步...')
      
      // 第5步：8秒后自动重启服务
      setTimeout(async () => {
        try {
          console.log('步骤5: 重启服务...')
          
          let retryCount = 0
          const maxRetries = 3
          let success = false
          
          while (retryCount < maxRetries && !success) {
            try {
              const { started, errors: startErrors } = await startServices(projectRoot)
              
              if (startErrors.length === 0) {
                success = true
                console.log('服务启动成功:', started)
                
                // 完成第5步
                await $fetch('/api/system/update-state', {
                  method: 'POST',
                  body: {
                    action: 'complete-step',
                    sessionId
                  }
                })
                
              } else {
                throw new Error(startErrors.join(', '))
              }
              
            } catch (error: any) {
              retryCount++
              console.error(`第${retryCount}次启动失败:`, error.message)
              
              if (retryCount >= maxRetries) {
                console.log('达到最大重试次数，开始重新构建...')
                
                try {
                  // 处理可能的权限问题
                  await execAsync(`chmod -R 755 ${projectRoot}`)
                  await execAsync(`chmod 644 ${projectRoot}/package.json`)
                  
                  // 重新安装依赖
                  await execAsync('npm install', { cwd: projectRoot })
                  
                  // 重新构建
                  await execAsync('npm run build', { cwd: projectRoot })
                  
                  // 再次尝试启动
                  const { started, errors: finalErrors } = await startServices(projectRoot)
                  
                  if (finalErrors.length === 0) {
                    console.log('重新构建后启动成功:', started)
                    success = true
                    
                    // 完成第5步
                    await $fetch('/api/system/update-state', {
                      method: 'POST',
                      body: {
                        action: 'complete-step',
                        sessionId
                      }
                    })
                  }
                  
                } catch (buildError: any) {
                  console.error('重新构建失败:', buildError.message)
                }
              } else {
                // 等待2秒后重试
                await new Promise(resolve => setTimeout(resolve, 2000))
              }
            }
          }
          
        } catch (error: any) {
          console.error('第5步执行失败:', error.message)
        }
      }, 8000)
      
      // 创建应用更新信息文件
      const applyInfo = {
        timestamp: new Date().toISOString(),
        sessionId,
        appliedFiles,
        skippedFiles,
        errors,
        stoppedServices: stopped,
        updateSourceDir
      }
      
      await fs.writeFile(
        join(projectRoot, 'data', 'last-update.json'),
        JSON.stringify(applyInfo, null, 2)
      )
      
      const hasErrors = errors.length > 0
      const success = appliedFiles.length > 0
      
      return {
        success,
        message: success ? '更新应用成功，8秒后自动重启服务' : '更新应用时出现错误',
        data: {
          appliedFiles,
          skippedFiles,
          errors,
          stoppedServices: stopped,
          totalFiles: updateContents?.length || 0,
          successCount: appliedFiles.length,
          sessionId,
          autoRestartIn: 8
        }
      }
      
    } catch (error: any) {
      console.error('应用更新失败:', error)
      
      // 更新状态管理 - 记录错误
      try {
        await $fetch('/api/system/update-state', {
          method: 'POST',
          body: {
            action: 'update',
            sessionId,
            error: `应用更新失败: ${error.message}`
          }
        })
      } catch (updateError) {
        console.warn('更新状态失败:', updateError)
      }
      
      throw createError({
        statusCode: 500,
        statusMessage: `应用更新失败: ${error.message}`
      })
    }
    
  } catch (error: any) {
    console.error('应用更新失败:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      statusMessage: error.statusMessage || '应用更新失败: ' + (error?.message || '未知错误')
    })
  }
})