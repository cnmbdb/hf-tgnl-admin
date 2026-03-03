import fs from 'fs'
import path from 'path'
import { requireAdmin } from '../utils/auth'

// 功能链编号 1-9 与机器人内部 key 的映射（用于写回 config.txt）
const CHAIN_KEY_MAP: Record<number, string> = {
  1: 'bishu',
  2: 'yucun',
  3: 'usdt2trx',
  4: 'check_tx',
  5: 'trx2energy',
  6: 'monitored_addresses',
  7: 'toggle_monitor',
  8: 'recharge',
  9: 'profile'
}

export default defineEventHandler(async (event) => {
  const user = await requireAdmin(event)
  if (!user) {
    return {
      success: false,
      error: '需要管理员权限'
    }
  }

  try {
    const body = await readBody(event)
    const { layout } = body // layout 是前端传来的按钮布局数组，格式：[[{text, action, chain_id}], ...]

    if (!layout || !Array.isArray(layout)) {
      return {
        success: false,
        error: '无效的布局数据'
      }
    }

    // 将前端布局转换为配置格式
    // 前端格式：[[{text: '📦 笔数套餐', action: 'text', chain_id: 1}], ...]
    // 配置格式：[[{key: 'bishu', label: '📦 笔数套餐', chain_id: 1}], ...]
    const configLayout: any[] = []

    layout.forEach((row: any[]) => {
      const configRow: any[] = []
      row.forEach((btn: any) => {
        if (btn && btn.text) {
          const chainId = btn.chain_id && btn.chain_id >= 1 && btn.chain_id <= 9 
            ? parseInt(btn.chain_id) 
            : 0

          if (!chainId) {
            return
          }

          const key = CHAIN_KEY_MAP[chainId]
          if (!key) {
            return
          }

          configRow.push({
            key,
            label: btn.text.trim(),
            chain_id: chainId
          })
        }
      })
      if (configRow.length > 0) {
        configLayout.push(configRow)
      }
    })

    // 生成 JSON 字符串
    const menuJsonStr = JSON.stringify(configLayout)

    // 读取并更新 config.txt
    const basePath = path.join(process.cwd(), 'nl-2333')
    const configPath = path.join(basePath, 'config.txt')

    if (!fs.existsSync(configPath)) {
      return {
        success: false,
        error: '配置文件不存在'
      }
    }

    // 读取现有配置
    const configContent = fs.readFileSync(configPath, 'utf-8')
    const lines = configContent.split('\n')
    
    // 查找并更新 main_menu_buttons_json 行
    let found = false
    const updatedLines = lines.map(line => {
      const trimmedLine = line.trim()
      if (trimmedLine.startsWith('main_menu_buttons_json=')) {
        found = true
        return `main_menu_buttons_json=${menuJsonStr}`
      }
      return line
    })

    // 如果没有找到，在文件末尾添加
    if (!found) {
      updatedLines.push('')
      updatedLines.push('# 主键盘菜单配置（JSON格式，9个按钮的布局，按行组织）')
      updatedLines.push('# key 固定不变（用于代码逻辑），label 可修改（显示文案）')
      updatedLines.push(`main_menu_buttons_json=${menuJsonStr}`)
    }

    // 写回文件
    fs.writeFileSync(configPath, updatedLines.join('\n'), 'utf-8')

    return {
      success: true,
      message: '键盘布局已同步到机器人配置',
      data: {
        layout: configLayout
      }
    }
  } catch (error) {
    console.error('保存键盘布局失败:', error)
    return {
      success: false,
      error: '保存键盘布局失败: ' + (error as Error).message
    }
  }
})
