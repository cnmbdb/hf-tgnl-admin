import { executeQuery } from '../../utils/database'

export default defineEventHandler(async (event) => {
  console.log('[取消授权] 开始处理取消授权请求')

  try {
    const body = await readBody(event)
    const { orderNumber } = body

    if (!orderNumber) {
      throw createError({
        statusCode: 400,
        statusMessage: '订单号不能为空'
      })
    }

    // 检查授权是否存在
    const existingLicense = await executeQuery(
      'SELECT * FROM licenses WHERE order_number = ?',
      [orderNumber]
    ) as any[]

    if (existingLicense.length === 0) {
      throw createError({
        statusCode: 404,
        statusMessage: '未找到该授权记录'
      })
    }

    // 删除授权记录
    await executeQuery(
      'DELETE FROM licenses WHERE order_number = ?',
      [orderNumber]
    )

    // 记录取消授权历史
    await executeQuery(
      `INSERT INTO license_history (
        order_number,
        action,
        server_ip,
        details,
        created_at
      ) VALUES (?, 'deactivate', ?, ?, NOW())`,
      [
        orderNumber,
        'localhost',
        `取消授权，订单号: ${orderNumber}`
      ]
    )

    console.log(`[取消授权] 订单 ${orderNumber} 已取消授权`)

    return {
      success: true,
      message: '授权已取消'
    }
  } catch (error: any) {
    console.error('取消授权失败:', error)
    
    if (error.statusCode) {
      throw error
    }
    
    throw createError({
      statusCode: 500,
      statusMessage: '取消授权失败: ' + error.message
    })
  }
})
