<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-primary flex items-center gap-3">
          <div class="w-8 h-8 bg-card border border-card rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-bolt" class="w-5 h-5 text-[#00dc82]" />
          </div>
          能量出租管理系统
        </h1>
        <p class="mt-1 text-sm text-secondary">监控能量出租机器人状态和交易数据</p>
      </div>
      <div class="flex gap-2">
        <UButton variant="outline" size="sm">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
          刷新数据
        </UButton>
        <UButton color="primary" size="sm" class="bg-[#00dc82] hover:bg-[#00dc82]/80">
          <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4 mr-2" />
          系统设置
        </UButton>
      </div>
    </div>

    <!-- 系统状态概览 -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="bg-card border border-card rounded-lg p-4">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-bolt" class="w-5 h-5 text-green-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-secondary">机器人状态</p>
            <p class="text-xl font-semibold text-green-400">{{ systemStatus.status }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-card border border-card rounded-lg p-4">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-users" class="w-5 h-5 text-blue-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-secondary">活跃用户</p>
            <p class="text-xl font-semibold text-primary">{{ systemStatus.activeUsers }}</p>
          </div>
        </div>
      </div>

      <div class="bg-card border border-card rounded-lg p-4">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-currency-dollar" class="w-5 h-5 text-purple-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-secondary">今日交易</p>
            <p class="text-xl font-semibold text-primary">{{ systemStatus.todayTransactions }}</p>
          </div>
        </div>
      </div>

      <div class="bg-card border border-card rounded-lg p-4">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-yellow-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-bolt" class="w-5 h-5 text-yellow-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-secondary">总能量出租</p>
            <p class="text-xl font-semibold text-primary">{{ formatEnergy(systemStatus.totalEnergyRented) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 能量池下游成本概览（从能量池 API 自动读取） -->
    <div class="bg-card border border-card rounded-lg p-4 mt-4">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-fire" class="w-4 h-4 text-yellow-400" />
          <h3 class="text-sm font-medium text-primary">API 调用成本（TRX）</h3>
        </div>
        <span class="text-xs text-secondary">来自能量池系统 (EP001)</span>
      </div>
      <div class="grid grid-cols-5 gap-2 text-xs">
        <div class="bg-input border border-card rounded-md p-2 text-center">
          <div class="text-secondary">1小时</div>
          <div class="text-primary font-medium mt-1">
            {{ formatPrice(downstreamPricing.cost1HourTrx) }}
          </div>
        </div>
        <div class="bg-input border border-card rounded-md p-2 text-center">
          <div class="text-secondary">1天</div>
          <div class="text-primary font-medium mt-1">
            {{ formatPrice(downstreamPricing.cost1DayTrx) }}
          </div>
        </div>
        <div class="bg-input border border-card rounded-md p-2 text-center">
          <div class="text-secondary">3天</div>
          <div class="text-primary font-medium mt-1">
            {{ formatPrice(downstreamPricing.cost3DayTrx) }}
          </div>
        </div>
        <div class="bg-input border border-card rounded-md p-2 text-center">
          <div class="text-secondary">30天</div>
          <div class="text-primary font-medium mt-1">
            {{ formatPrice(downstreamPricing.cost30DayTrx) }}
          </div>
        </div>
        <div class="bg-input border border-card rounded-md p-2 text-center">
          <div class="text-secondary">笔数</div>
          <div class="text-primary font-medium mt-1">
            {{ formatPrice(downstreamPricing.costBishuTrx) }}
          </div>
        </div>
      </div>
      <p class="mt-2 text-[11px] text-secondary">
        提示：价格来自能量池 API，如需调整，请在能量池后台修改对应套餐成本。
      </p>
    </div>

    <!-- 服务状态监控：仅保留 Telegram 机器人服务卡片 -->
      <div class="bg-card border border-card rounded-lg">
        <div class="px-4 py-3 border-b border-card flex items-center justify-between">
          <h3 class="text-lg font-medium text-primary flex items-center gap-2">
            <UIcon name="i-simple-icons-telegram" class="w-5 h-5 text-blue-400" />
            能量出租机器人
          </h3>
          <UBadge :color="telegramService.status === 'online' ? 'green' : 'red'" variant="subtle">
            {{ telegramService.status === 'online' ? '在线' : '离线' }}
          </UBadge>
        </div>
        
        <div class="p-4 space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-input border border-card rounded-md p-3 text-center">
              <p class="text-2xl font-bold text-primary">{{ telegramService.activeUsers }}</p>
              <p class="text-xs text-secondary">活跃用户</p>
            </div>
            <div class="bg-input border border-card rounded-md p-3 text-center">
              <p class="text-2xl font-bold text-primary">{{ telegramService.energyTransactions }}</p>
              <p class="text-xs text-secondary">能量交易</p>
            </div>
          </div>
          
          <!-- 机器人进程状态 -->
          <div class="bg-input border border-card rounded-md p-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-medium text-primary flex items-center gap-2">
                <UIcon name="i-heroicons-cpu-chip" class="w-4 h-4 text-blue-400" />
                机器人进程状态
                <UBadge v-if="processCount !== undefined" :color="processCount > 0 ? 'green' : 'red'" variant="subtle" size="xs">
                  {{ processCount }} 个进程
                </UBadge>
              </h4>
              <UButton variant="ghost" size="xs" @click="refreshBotStatus">
                <UIcon name="i-heroicons-arrow-path" class="w-3 h-3" />
              </UButton>
            </div>
            
            <div v-if="botProcesses.length > 0" class="space-y-3">
              <div v-for="process in botProcesses" :key="process.pid" class="bg-card border border-card rounded-md p-3">
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center space-x-2">
                    <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span class="text-sm font-medium text-primary">{{ process.name }}</span>
                  </div>
                  <UBadge color="green" variant="subtle" size="xs">运行中</UBadge>
                </div>
                
                <div class="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span class="text-secondary">进程ID:</span>
                    <span class="text-primary ml-1">{{ process.pid }}</span>
                  </div>
                  <div>
                    <span class="text-secondary">运行时间:</span>
                    <span class="text-primary ml-1">{{ process.uptime }}</span>
                  </div>
                  <div>
                    <span class="text-secondary">CPU:</span>
                    <span class="text-primary ml-1">{{ process.cpuUsage }}%</span>
                  </div>
                  <div>
                    <span class="text-secondary">内存:</span>
                    <span class="text-primary ml-1">{{ process.memUsage }}%</span>
                  </div>
                </div>
                
                <div class="mt-2 text-xs">
                  <span class="text-secondary">启动时间:</span>
                  <span class="text-primary ml-1">{{ formatDateTime(process.startedAt) }}</span>
                </div>
              </div>
            </div>
            
            <div v-else class="text-center py-4">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-yellow-400 mx-auto mb-2" />
              <p class="text-sm text-secondary">未检测到机器人进程</p>
            </div>
          </div>
          
          <div class="flex items-center justify-between p-3 bg-input border border-card rounded-md">
            <div class="flex items-center space-x-3">
              <div class="relative">
                <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                <div class="absolute inset-0 w-3 h-3 bg-green-400 rounded-full animate-ping opacity-75"></div>
              </div>
              <span class="text-primary font-medium">已连接</span>
            </div>
            <span class="text-sm text-secondary">最后更新: {{ telegramService.lastUpdate }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 页面元数据
definePageMeta({
  title: '能量出租管理系统',
  description: '监控能量出租机器人状态和交易数据'
})

// 响应式数据
const systemStatus = ref({
  status: '加载中...',
  activeUsers: 0,
  todayTransactions: 0,
  totalEnergyRented: 0
})

const telegramService = ref({
  status: 'online',
  activeUsers: 0,
  energyTransactions: 0,
  lastUpdate: '-'
})

const apiService = ref({
  status: 'normal',
  requestsCount: 0,
  uptime: 0,
  responseTime: 0
})

const database = ref({
  status: 'connected',
  totalUsers: 0,
  totalMessages: 0,
  dbSize: '0GB',
  connections: 0
})

// 能量池下游成本（从能量池系统读取）
const downstreamPricing = ref({
  cost1HourTrx: null,
  cost1DayTrx: null,
  cost3DayTrx: null,
  cost30DayTrx: null,
  costBishuTrx: null
})

// 机器人进程状态
const botProcesses = ref([])
const processCount = ref(0)

const recentActivities = ref([
  {
    id: 1,
    icon: 'i-heroicons-bolt',
    message: '用户完成能量出租交易',
    time: '2分钟前',
    type: 'success',
    status: '成功'
  },
  {
    id: 2,
    icon: 'i-heroicons-user-plus',
    message: '新用户开始使用能量出租服务',
    time: '5分钟前',
    type: 'success',
    status: '成功'
  },
  {
    id: 3,
    icon: 'i-heroicons-currency-dollar',
    message: '大额能量交易完成',
    time: '10分钟前',
    type: 'success',
    status: '完成'
  },
  {
    id: 4,
    icon: 'i-heroicons-arrow-path',
    message: '机器人自动处理能量分配',
    time: '15分钟前',
    type: 'info',
    status: '处理中'
  }
])

// 定时器引用
let refreshTimer = null

// 生命周期钩子
onMounted(() => {
  // 初始化数据
  refreshData()
  
  // 设置定时刷新
  refreshTimer = setInterval(refreshData, 30000) // 每30秒刷新一次
})

// 组件销毁时清理定时器
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})

// 方法
const refreshData = async () => {
  try {
    await fetchDashboardStats()
    await fetchBotStatus()
  } catch (error) {
    // 静默处理错误,避免日志泄露
  }
}

// 仪表盘汇总统计
const fetchDashboardStats = async () => {
  try {
    const response = await $fetch('/api/dashboard')
    if (response.success && response.data) {
      systemStatus.value = response.data.systemStatus
      telegramService.value = response.data.telegramService
      apiService.value = response.data.apiService
      database.value = response.data.database
      if (response.data.downstreamPricing) {
        downstreamPricing.value = {
          cost1HourTrx: response.data.downstreamPricing.cost1HourTrx,
          cost1DayTrx: response.data.downstreamPricing.cost1DayTrx,
          cost3DayTrx: response.data.downstreamPricing.cost3DayTrx,
          cost30DayTrx: response.data.downstreamPricing.cost30DayTrx,
          costBishuTrx: response.data.downstreamPricing.costBishuTrx
        }
      }
    }
  } catch (error) {
    // 连接失败时标记数据库状态
    database.value.status = 'disconnected'
  }
}

// 获取机器人状态
const fetchBotStatus = async () => {
  try {
    const response = await $fetch('/api/bot-status')
    if (response.success) {
      botProcesses.value = response.data.processes
      processCount.value = response.data.processCount || response.data.processes.length
    }
  } catch (error) {
    // 静默处理错误
    botProcesses.value = []
    processCount.value = 0
  }
}

// 刷新机器人状态
const refreshBotStatus = async () => {
  await fetchBotStatus()
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 格式化能量数值
const formatEnergy = (energy) => {
  if (energy >= 100000000) {
    return (energy / 100000000).toFixed(1) + '亿'
  } else if (energy >= 10000) {
    return (energy / 10000).toFixed(1) + '万'
  } else {
    return energy.toString()
  }
}

// 格式化价格（TRX）
const formatPrice = (val) => {
  if (val === null || val === undefined || isNaN(Number(val))) {
    return '-'
  }
  return Number(val).toFixed(2)
}
</script>