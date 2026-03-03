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
    return { success: false, error: '系统为单用户模式，禁止删除' }
  } catch (error: any) {
    return { success: false, error: error.message }
  }
})
