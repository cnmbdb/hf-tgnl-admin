import { promises as fs } from 'fs'
import path from 'path'

const HISTORY_FILE = path.join(process.cwd(), 'data', 'update-history.json')

export default defineEventHandler(async (event) => {
  try {
    const historyData = await fs.readFile(HISTORY_FILE, 'utf-8')
    const history = JSON.parse(historyData)
    
    const query = getQuery(event)
    const limit = parseInt(query.limit as string) || 50
    const offset = parseInt(query.offset as string) || 0
    
    const paginatedHistory = history.slice(offset, offset + limit)
    
    return {
      success: true,
      data: paginatedHistory,
      total: history.length,
      limit,
      offset
    }
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      return {
        success: true,
        data: [],
        total: 0,
        limit: 50,
        offset: 0
      }
    }
    
    console.error('获取更新历史失败:', error)
    return {
      success: false,
      message: error.message || '获取更新历史失败'
    }
  }
})