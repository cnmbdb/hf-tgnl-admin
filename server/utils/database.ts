import mysql from 'mysql2/promise'

// 连接池配置
let pool: mysql.Pool | null = null
let poolConfig: mysql.PoolOptions | null = null
let lastReconnectTime = 0
const RECONNECT_COOLDOWN = 5000 // 5秒内不重复重连

// 连接池监控
let activeConnections = 0
let totalQueries = 0
let failedQueries = 0
let slowQueries = 0
const SLOW_QUERY_THRESHOLD = 5000 // 5秒

// 查询超时配置
const QUERY_TIMEOUT = 30000 // 30秒

function getPoolConfig() {
  const config = useRuntimeConfig()
  const loadFromEnvFile = (key: string) => {
    try {
      const fs = require('fs') as typeof import('fs')
      const path = require('path') as typeof import('path')
      const candidates = [
        path.join(process.cwd(), '.env'),
        path.join(process.cwd(), '../.env'),
        path.join(process.cwd(), '../../.env')
      ]
      const found = candidates.find(p => fs.existsSync(p))
      if (!found) return ''
      const content = fs.readFileSync(found, 'utf-8')
      const line = content.split('\n').find((l: string) => l.trim().startsWith(key + '='))
      if (!line) return ''
      return line.split('=', 2)[1]?.trim() || ''
    } catch { return '' }
  }
  
  const host = process.env.DB_HOST || config.dbHost || loadFromEnvFile('DB_HOST') || 'db'
  const user = process.env.DB_USER || config.dbUser || loadFromEnvFile('DB_USER') || 'root'
  const password = process.env.DB_PASSWORD || config.dbPassword || loadFromEnvFile('DB_PASSWORD') || 'root'
  const database = process.env.DB_NAME || config.dbName || loadFromEnvFile('DB_NAME') || 'tgnl'
  const port = Number(process.env.DB_PORT || config.dbPort || loadFromEnvFile('DB_PORT') || 3306)

  return {
    host,
    user,
    password,
    database,
    port,
    charset: 'utf8mb4' as const,
    waitForConnections: true,
    connectionLimit: 20, // 增加连接池大小
    queueLimit: 50, // 限制队列长度，防止无限等待
    enableKeepAlive: true,
    keepAliveInitialDelay: 0,
    // 连接超时（ms）
    connectTimeout: 10000,
    // 最大空闲时间
    maxIdle: 10,
  }
}

function getPool(): mysql.Pool {
  const currentConfig = getPoolConfig()
  const configKey = JSON.stringify(currentConfig)

  // 如果已有连接池但已被关闭，强制丢弃重建（防止 "Pool is closed" 一直复用坏对象）
  if (pool && (pool as any).pool?._closed) {
    try {
      pool.end().catch(() => {})
    } catch {}
    pool = null
  }

  // 如果配置改变或池不存在，重新创建
  if (!pool || JSON.stringify(poolConfig) !== configKey) {
    if (pool) {
      pool.end().catch(() => {})
    }
    poolConfig = currentConfig
    pool = mysql.createPool(currentConfig)
    
    // 监听连接错误
    pool.on('error', (err: any) => {
      console.error('Database pool error:', err)
      if (err.code === 'PROTOCOL_CONNECTION_LOST' || err.code === 'ECONNREFUSED') {
        // 连接丢失，标记需要重连
        pool = null
      }
    })
    
    // 监听连接获取
    pool.on('connection', (connection: any) => {
      activeConnections++
      connection.on('end', () => {
        activeConnections = Math.max(0, activeConnections - 1)
      })
    })
    
    // 定期检查连接池状态和清理
    if (typeof setInterval !== 'undefined') {
      setInterval(() => {
        if (pool) {
          const poolState = (pool as any).pool?._allConnections?.length || 0
          const poolFree = (pool as any).pool?._freeConnections?.length || 0
          const poolQueue = (pool as any).pool?._connectionQueue?.length || 0
          
          // 如果连接池接近满载，记录警告
          if (poolState > 15 || poolQueue > 10) {
            console.warn('Database pool status:', {
              total: poolState,
              free: poolFree,
              queue: poolQueue,
              active: activeConnections
            })
          }
          
          // 如果队列过长，尝试清理并重连
          if (poolQueue > 30) {
            console.error('Database pool queue too long, attempting to reconnect...', {
              queue: poolQueue,
              total: poolState,
              free: poolFree
            })
            reconnectPool().catch(err => {
              console.error('Failed to reconnect pool during cleanup:', err)
            })
          }
        }
      }, 30000) // 每30秒检查一次
    }
  }
  
  return pool
}

async function reconnectPool(): Promise<mysql.Pool> {
  const now = Date.now()
  if (now - lastReconnectTime < RECONNECT_COOLDOWN) {
    // 冷却期内，等待后重试
    await new Promise(resolve => setTimeout(resolve, RECONNECT_COOLDOWN - (now - lastReconnectTime)))
  }
  
  lastReconnectTime = Date.now()
  
  if (pool) {
    try {
      await pool.end()
    } catch (e) {
      // 忽略关闭错误
    }
  }
  
  pool = null
  return getPool()
}

function createTimeoutPromise(timeout: number, message: string): Promise<never> {
  return new Promise((_, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(message))
    }, timeout)
    // 清理定时器（虽然不会执行，但保持代码整洁）
    return () => clearTimeout(timer)
  }) as Promise<never>
}

export async function executeQuery(query: string, params: any[] = [], retries = 3): Promise<any> {
  let lastError: any = null
  const startTime = Date.now()
  totalQueries++
  
  for (let attempt = 0; attempt < retries; attempt++) {
    let timeoutTimer: NodeJS.Timeout | null = null
    
    try {
      const currentPool = getPool()
      
      // 检查连接池状态
      const poolState = (currentPool as any).pool?._allConnections?.length || 0
      const poolQueue = (currentPool as any).pool?._connectionQueue?.length || 0
      
      if (poolQueue > 20) {
        console.warn(`Database pool queue is long: ${poolQueue} queries waiting`)
      }
      
      // 测试连接（带超时）
      try {
        const testTimeout = createTimeoutPromise(5000, 'Connection test timeout')
        await Promise.race([
          currentPool.query('SELECT 1'),
          testTimeout
        ])
      } catch (testError: any) {
        // 连接测试失败，尝试重连
        const isPoolClosed =
          testError?.code === 'POOL_CLOSED' ||
          testError?.message?.includes('Pool is closed')

        if (testError.code === 'PROTOCOL_CONNECTION_LOST' || 
            testError.code === 'ECONNREFUSED' || 
            testError.code === 'ER_BAD_DB_ERROR' ||
            testError.message?.includes('timeout') ||
            isPoolClosed) {
          console.warn(`Database connection test failed (attempt ${attempt + 1}/${retries}), reconnecting...`)
          await reconnectPool()
          continue
        }
        throw testError
      }
      
      // 执行查询（带超时保护）
      const queryTimeout = createTimeoutPromise(
        QUERY_TIMEOUT, 
        `Query timeout after ${QUERY_TIMEOUT}ms: ${query.substring(0, 100)}...`
      )
      const queryPromise = currentPool.execute(query, params)
      const [results] = await Promise.race([queryPromise, queryTimeout]) as any
      
      // 记录慢查询
      const queryTime = Date.now() - startTime
      if (queryTime > SLOW_QUERY_THRESHOLD) {
        slowQueries++
        console.warn(`Slow query detected (${queryTime}ms):`, query.substring(0, 200))
      }
      
      return results
    } catch (error: any) {
      lastError = error
      const errorMessage = error?.message || ''
      const isPoolClosed =
        error?.code === 'POOL_CLOSED' ||
        errorMessage.includes('Pool is closed')
      const errorCode = isPoolClosed ? 'POOL_CLOSED' : error?.code
      
      // 可重试的错误
      const retryableErrors = [
        'POOL_CLOSED',
        'PROTOCOL_CONNECTION_LOST',
        'ECONNREFUSED',
        'ETIMEDOUT',
        'ENOTFOUND',
        'ER_LOCK_WAIT_TIMEOUT'
      ]
      
      // 数据库不存在错误 - 尝试创建数据库
      if (errorCode === 'ER_BAD_DB_ERROR') {
        const config = getPoolConfig()
        console.warn(`Database not found: ${config.database}, attempting to create...`)
        
        try {
          // 连接到 MySQL 服务器（不指定数据库）
          const { database, ...adminConfig } = config
          const adminConnection = await mysql.createConnection({
            ...adminConfig,
            database: undefined // 不指定数据库，连接到 MySQL 服务器
          })
          
          // 创建数据库
          await adminConnection.query(`CREATE DATABASE IF NOT EXISTS \`${database}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci`)
          await adminConnection.end()
          
          // 重新创建连接池
          pool = null
          console.log(`Database ${database} created successfully`)
          
          // 重试查询
          if (attempt < retries - 1) {
            await new Promise(resolve => setTimeout(resolve, 1000))
            continue
          }
        } catch (createError: any) {
          console.error(`Failed to create database:`, createError)
          // 如果创建失败，继续抛出原始错误
          throw error
        }
      }
      
      // 连接池关闭（可能来自并发重连/池重建竞态）：强制丢弃并重连后重试
      if (isPoolClosed && attempt < retries - 1) {
        console.warn(`Database pool closed (attempt ${attempt + 1}/${retries}), reconnecting...`)
        pool = null
        const delay = Math.min(500 * (attempt + 1), 1500)
        await new Promise(resolve => setTimeout(resolve, delay))
        await reconnectPool()
        continue
      }

      // 如果是可重试错误且还有重试次数
      if (retryableErrors.includes(errorCode) && attempt < retries - 1) {
        const delay = Math.min(1000 * Math.pow(2, attempt), 5000) // 指数退避，最多5秒
        console.warn(`Database query failed (attempt ${attempt + 1}/${retries}), retrying in ${delay}ms...`, errorCode)
        await new Promise(resolve => setTimeout(resolve, delay))
        await reconnectPool()
        continue
      }
      
      // 不可重试或重试次数用完
      failedQueries++
      console.error('Database query error:', {
        code: error?.code,
        message: error?.message,
        query: query.substring(0, 100),
        attempt: attempt + 1,
        time: Date.now() - startTime
      })
      throw error
    }
  }
  
  // 所有重试都失败
  failedQueries++
  const error = lastError || new Error('数据库查询失败')
  console.error('Database query failed after all retries:', {
    query: query.substring(0, 100),
    totalTime: Date.now() - startTime
  })
  throw error
}

// 获取连接池统计信息
export function getPoolStats() {
  if (!pool) return null
  
  const poolState = (pool as any).pool?._allConnections?.length || 0
  const poolFree = (pool as any).pool?._freeConnections?.length || 0
  const poolQueue = (pool as any).pool?._connectionQueue?.length || 0
  
  return {
    totalConnections: poolState,
    freeConnections: poolFree,
    activeConnections: activeConnections,
    queuedQueries: poolQueue,
    totalQueries,
    failedQueries,
    slowQueries,
    successRate: totalQueries > 0 ? ((totalQueries - failedQueries) / totalQueries * 100).toFixed(2) + '%' : '0%'
  }
}
