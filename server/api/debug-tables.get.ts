import { defineEventHandler } from 'h3'
import { executeQuery } from '../utils/database'

export default defineEventHandler(async (event) => {
  try {
    // 查询所有表
    const tables = await executeQuery('SHOW TABLES')
    
    // 查询每个表的结构
    const tableStructures: any = {}
    
    for (const tableRow of tables as any[]) {
      const tableName = Object.values(tableRow)[0] as string
      const structure = await executeQuery(`DESCRIBE ${tableName}`)
      tableStructures[tableName] = structure
    }
    
    return {
      success: true,
      tables: tableStructures
    }
  } catch (error: any) {
    return {
      success: false,
      error: error.message
    }
  }
})
