import { executeQuery } from '../utils/database'
import { requireAdmin } from '../utils/auth'

export default defineEventHandler(async (event) => {
  // 仅管理员可删
  const user = await requireAdmin(event)
  if (!user) {
    return { success: false, error: '需要管理员权限' }
  }

  try {
    const query = getQuery(event)
    const chatIdRaw = (query.chat_id ?? query.tg_user_id ?? query.chatId) as any
    const chatId = Number(chatIdRaw)

    if (!chatId || Number.isNaN(chatId) || chatId <= 0) {
      return { success: false, error: 'chat_id 参数无效' }
    }

    // Telegram 用户数据目前分散在多张表里（以 chat_id 关联）
    // 删除策略：删除该 chat_id 的所有记录（用户再次与机器人交互会重新写入）
    const resTransactions: any = await executeQuery('DELETE FROM transactions WHERE chat_id = ?', [chatId])
    const resOrders: any = await executeQuery('DELETE FROM orders WHERE chat_id = ?', [chatId])
    const resBishu: any = await executeQuery('DELETE FROM bishu_packages WHERE chat_id = ?', [chatId])

    // 同时删除 tg_users 表中的用户主记录，这样前端列表不会再显示这个用户
    const resTgUser: any = await executeQuery('DELETE FROM tg_users WHERE tg_user_id = ?', [chatId])

    return {
      success: true,
      message: 'Telegram 用户删除成功',
      data: {
        chat_id: chatId,
        deleted: {
          transactions: resTransactions?.affectedRows ?? 0,
          orders: resOrders?.affectedRows ?? 0,
          bishu_packages: resBishu?.affectedRows ?? 0,
          tg_users: resTgUser?.affectedRows ?? 0
        }
      }
    }
  } catch (error: any) {
    console.error('Error deleting TG user:', error)
    return { success: false, error: error.message }
  }
})

