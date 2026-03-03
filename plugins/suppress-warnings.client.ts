// 客户端警告过滤插件 - 减少内存泄露
export default defineNuxtPlugin(() => {
  // 保存原始的 console 方法
  const originalWarn = console.warn
  const originalLog = console.log
  
  // 过滤警告信息的关键词列表
  const warningFilters = [
    'middleware already exists',
    'manifest-route-rule',
    'Module type of file',
    'HMR',
    'hot update',
    'vite'
  ]
  
  // 过滤日志信息的关键词列表
  const logFilters = [
    '刷新仪表板',
    '获取机器人状态',
    'HMR',
    'hot update'
  ]
  
  // 覆盖 console.warn
  console.warn = function(...args: any[]) {
    const message = args.join(' ')
    
    // 检查是否匹配任何过滤关键词
    if (warningFilters.some(filter => message.includes(filter))) {
      return
    }
    
    // 其他警告正常输出
    originalWarn.apply(console, args)
  }
  
  // 覆盖 console.log - 减少日志输出
  console.log = function(...args: any[]) {
    const message = args.join(' ')
    
    // 过滤开发调试日志
    if (logFilters.some(filter => message.includes(filter))) {
      return
    }
    
    // 其他日志正常输出
    originalLog.apply(console, args)
  }
})
