import { getPoolStats } from '../utils/database'

export default defineEventHandler(async (event) => {
  const stats = getPoolStats()
  
  return {
    status: stats ? 'healthy' : 'unhealthy',
    database: stats ? {
      connected: true,
      ...stats
    } : {
      connected: false,
      error: 'Database pool not initialized'
    },
    timestamp: new Date().toISOString()
  }
})
