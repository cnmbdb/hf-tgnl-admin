import fs from 'fs'
import path from 'path'
import { requireAdmin } from '../utils/auth'

export default defineEventHandler(async (event) => {
  const user = await requireAdmin(event)
  if (!user) {
    return {
      success: false,
      error: '需要管理员权限'
    }
  }

  try {
    const basePath = path.join(process.cwd(), 'nl-2333')
    const configPath = path.join(basePath, 'config.txt')

    if (!fs.existsSync(configPath)) {
      return {
        success: false,
        error: '配置文件不存在'
      }
    }

    // 读取 config.txt
    const configContent = fs.readFileSync(configPath, 'utf-8')
    let menuJsonStr = ''
    
    configContent.split('\n').forEach(line => {
      const trimmedLine = line.trim()
      if (trimmedLine && !trimmedLine.startsWith('#') && trimmedLine.startsWith('main_menu_buttons_json=')) {
        menuJsonStr = trimmedLine.split('=', 2)[1]?.trim() || ''
      }
    })

    // 解析 JSON
    let layout: any[] = []
    if (menuJsonStr) {
      try {
        layout = JSON.parse(menuJsonStr)
      } catch (e) {
        console.error('解析键盘布局 JSON 失败:', e)
      }
    }

    // 转换为前端需要的格式（扁平化，保持顺序）
    const buttons: Array<{ key: string; label: string; chain_id: number; rowIndex: number; colIndex: number }> = []
    layout.forEach((row, rowIndex) => {
      row.forEach((btn: any, colIndex: number) => {
        if (btn && typeof btn === 'object' && btn.key && btn.label) {
          buttons.push({
            key: btn.key,
            label: btn.label,
            chain_id: btn.chain_id || parseInt(btn.key) || 0, // 默认使用 key 对应的序号，如果没有 chain_id
            rowIndex,
            colIndex
          })
        }
      })
    })

    return {
      success: true,
      data: {
        layout, // 原始布局（按行组织）
        buttons // 扁平化列表（用于前端展示）
      }
    }
  } catch (error) {
    console.error('读取键盘布局失败:', error)
    return {
      success: false,
      error: '读取键盘布局失败: ' + (error as Error).message
    }
  }
})
