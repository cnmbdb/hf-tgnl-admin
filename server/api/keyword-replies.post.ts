import { writeFileSync } from 'fs'
import { join } from 'path'
import { requireAdmin } from '../utils/auth'

export default defineEventHandler(async (event) => {
  // 验证管理员权限
  const user = await requireAdmin(event)
  if (!user) {
    return {
      success: false,
      error: '需要管理员权限'
    }
  }
  try {
    const body = await readBody(event)
    const { keywordReplies } = body
    
    if (!keywordReplies) {
      return {
        success: false,
        error: '缺少关键词回复数据'
      }
    }
    
    // 验证数据结构
    if (!keywordReplies.commands || !keywordReplies.buttons) {
      return {
        success: false,
        error: '关键词回复数据结构不正确'
      }
    }
    
    const keywordRepliesPath = join(process.cwd(), 'nl-2333', 'keyword_replies.json')
    
    // 保存到文件
    writeFileSync(keywordRepliesPath, JSON.stringify(keywordReplies, null, 2), 'utf-8')
    
    return {
      success: true,
      message: '关键词回复保存成功'
    }
  } catch (error) {
    console.error('保存关键词回复失败:', error)
    return {
      success: false,
      error: '保存关键词回复失败'
    }
  }
})