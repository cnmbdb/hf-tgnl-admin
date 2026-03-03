import { executeQuery } from '../utils/database'
import { requireAdmin } from '../utils/auth'

export default defineEventHandler(async (event) => {
  // 仅管理员可以删除订单
  const user = await requireAdmin(event)
  if (!user) {
    return {
      success: false,
      error: '需要管理员权限'
    }
  }

  try {
    const query = getQuery(event)
    let body: any = {}
    try {
      body = await readBody(event)
    } catch {
      body = {}
    }

    // 支持两种传参方式：
    // 1) 单个 id: ?id=1 或 body.id
    // 2) 批量 ids: body.ids = [1,2,3]
    let ids: number[] = []

    if (Array.isArray(body?.ids)) {
      ids = body.ids.map((v: any) => Number(v))
    } else if (body?.id !== undefined) {
      ids = [Number(body.id)]
    } else if (query.id) {
      ids = String(query.id)
        .split(',')
        .map((v) => Number(v))
    }

    ids = ids.filter((id) => !Number.isNaN(id) && id > 0)

    if (!ids.length) {
      return {
        success: false,
        error: '缺少要删除的订单 ID'
      }
    }

    const placeholders = ids.map(() => '?').join(',')
    const result: any = await executeQuery(
      `DELETE FROM orders WHERE id IN (${placeholders})`,
      ids
    )

    return {
      success: true,
      message: '订单删除成功',
      data: {
        ids,
        affectedRows: result?.affectedRows ?? ids.length
      }
    }
  } catch (error: any) {
    console.error('删除订单失败:', error)
    return {
      success: false,
      error: error.message || '删除订单失败'
    }
  }
})

