<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <div class="w-8 h-8 bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-chart-bar" class="w-5 h-5 text-[#00dc82]" />
          </div>
          数据分析
        </h1>
        <p class="mt-1 text-sm text-[#9ca3af]">分析能量出租业务数据和趋势</p>
      </div>
      <div class="flex gap-2">
        <USelect
          v-model="selectedTimeRange"
          :options="timeRangeOptions"
          class="w-32"
        />
        <UButton variant="outline" size="sm" @click="refreshStats" :loading="loading">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
          刷新
        </UButton>
      </div>
    </div>

    <!-- 订单统计卡片 -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">总订单数</p>
            <p class="text-2xl font-bold text-white">{{ formatNumber(stats.totalOrders) }}</p>
            <div class="flex items-center mt-1">
              <UIcon 
                :name="stats.orderGrowth >= 0 ? 'i-heroicons-arrow-trending-up' : 'i-heroicons-arrow-trending-down'" 
                :class="stats.orderGrowth >= 0 ? 'text-green-400' : 'text-red-400'"
                class="w-4 h-4 mr-1"
              />
              <span :class="stats.orderGrowth >= 0 ? 'text-green-400' : 'text-red-400'" class="text-sm">
                {{ Math.abs(stats.orderGrowth) }}%
              </span>
              <span class="text-[#9ca3af] text-sm ml-1">vs 上期</span>
            </div>
          </div>
          <div class="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-shopping-bag" class="w-6 h-6 text-blue-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">总销售额</p>
            <p class="text-2xl font-bold text-white">¥{{ formatNumber(stats.totalRevenue) }}</p>
            <div class="flex items-center mt-1">
              <UIcon 
                :name="stats.revenueGrowth >= 0 ? 'i-heroicons-arrow-trending-up' : 'i-heroicons-arrow-trending-down'" 
                :class="stats.revenueGrowth >= 0 ? 'text-green-400' : 'text-red-400'"
                class="w-4 h-4 mr-1"
              />
              <span :class="stats.revenueGrowth >= 0 ? 'text-green-400' : 'text-red-400'" class="text-sm">
                {{ Math.abs(stats.revenueGrowth) }}%
              </span>
              <span class="text-[#9ca3af] text-sm ml-1">vs 上期</span>
            </div>
          </div>
          <div class="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-currency-dollar" class="w-6 h-6 text-green-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">待处理订单</p>
            <p class="text-2xl font-bold text-white">{{ formatNumber(stats.pendingOrders) }}</p>
            <div class="flex items-center mt-1">
              <UIcon name="i-heroicons-clock" class="w-4 h-4 mr-1 text-orange-400" />
              <span class="text-orange-400 text-sm">需要处理</span>
            </div>
          </div>
          <div class="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-clock" class="w-6 h-6 text-orange-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">完成率</p>
            <p class="text-2xl font-bold text-white">{{ stats.completionRate.toFixed(1) }}%</p>
            <div class="flex items-center mt-1">
              <UIcon name="i-heroicons-check-circle" class="w-4 h-4 mr-1 text-green-400" />
              <span class="text-green-400 text-sm">已完成</span>
            </div>
          </div>
          <div class="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-chart-pie" class="w-6 h-6 text-purple-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- 订单趋势图 -->
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-white">订单趋势</h2>
          </div>
        <div class="h-64">
          <canvas ref="orderTrendChart"></canvas>
        </div>
      </div>

      <!-- 销售额趋势图 -->
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-white">销售额趋势</h2>
        </div>
        <div class="h-64">
          <canvas ref="revenueTrendChart"></canvas>
        </div>
      </div>
    </div>

    <!-- 订单状态分布 -->
    <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-white">订单状态分布</h2>
      </div>
      <div class="h-64">
        <canvas ref="statusChart"></canvas>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { Chart, registerables } from 'chart.js'

// 注册 Chart.js 组件
Chart.register(...registerables)

// 页面元数据
definePageMeta({
  title: '数据分析',
  middleware: ['auth', 'license']
})

// 响应式数据
const selectedTimeRange = ref('7d')
const loading = ref(false)

// 图表引用
const orderTrendChart = ref<HTMLCanvasElement | null>(null)
const revenueTrendChart = ref<HTMLCanvasElement | null>(null)
const statusChart = ref<HTMLCanvasElement | null>(null)

// 图表实例
let orderChartInstance: Chart | null = null
let revenueChartInstance: Chart | null = null
let statusChartInstance: Chart | null = null

// 时间范围选项
const timeRangeOptions = [
  { label: '今天', value: '1d' },
  { label: '7天', value: '7d' },
  { label: '30天', value: '30d' },
  { label: '90天', value: '90d' }
]

// 统计数据
const stats = ref({
  totalOrders: 0,
  totalRevenue: 0,
  pendingOrders: 0,
  completionRate: 0,
  orderGrowth: 0,
  revenueGrowth: 0
})

// 图表数据
const chartData = ref({
  orderTrend: {
    labels: [] as string[],
    data: [] as number[]
  },
  revenueTrend: {
    labels: [] as string[],
    data: [] as number[]
  },
  statusDistribution: {
    labels: [] as string[],
    data: [] as number[]
  }
})

// 计算时间范围
const getTimeRange = () => {
  const now = new Date()
  let startDate = new Date()
  
  switch (selectedTimeRange.value) {
    case '1d':
      startDate.setDate(now.getDate() - 1)
      break
    case '7d':
      startDate.setDate(now.getDate() - 7)
      break
    case '30d':
      startDate.setDate(now.getDate() - 30)
      break
    case '90d':
      startDate.setDate(now.getDate() - 90)
      break
  }
  
  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: now.toISOString().split('T')[0],
    startDateObj: startDate,
    endDateObj: now
  }
}

// 获取统计数据
const fetchStats = async () => {
  loading.value = true
  try {
    const { startDate, endDate, startDateObj, endDateObj } = getTimeRange()
    
    // 获取当前时间范围的统计数据
    const currentResponse = await $fetch('/api/orders', {
      query: {
        startDate,
        endDate
      }
    })
    
    // 获取上一个时间范围的统计数据（用于计算增长率）
    const daysDiff = Math.floor((endDateObj.getTime() - startDateObj.getTime()) / (1000 * 60 * 60 * 24))
    const prevStartDate = new Date(startDateObj)
    prevStartDate.setDate(prevStartDate.getDate() - daysDiff)
    
    const prevStartDateStr = prevStartDate.toISOString().split('T')[0]
    const prevEndDateStr = startDate
    
    const prevResponse = await $fetch('/api/orders', {
      query: {
        startDate: prevStartDateStr,
        endDate: prevEndDateStr
      }
    })
    
    if (currentResponse.success && prevResponse.success) {
      const currentStats = currentResponse.stats || {}
      const prevStats = prevResponse.stats || {}
      
      // 计算增长率
      const orderGrowth = prevStats.totalOrders > 0 
        ? ((currentStats.totalOrders - prevStats.totalOrders) / prevStats.totalOrders * 100).toFixed(1)
        : currentStats.totalOrders > 0 ? 100 : 0
      
      const revenueGrowth = prevStats.totalRevenue > 0
        ? ((currentStats.totalRevenue - prevStats.totalRevenue) / prevStats.totalRevenue * 100).toFixed(1)
        : currentStats.totalRevenue > 0 ? 100 : 0
      
      stats.value = {
        totalOrders: currentStats.totalOrders || 0,
        totalRevenue: currentStats.totalRevenue || 0,
        pendingOrders: currentStats.pendingOrders || 0,
        completionRate: currentStats.completionRate || 0,
        orderGrowth: parseFloat(orderGrowth as string),
        revenueGrowth: parseFloat(revenueGrowth as string)
      }
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    // 如果API调用失败，尝试使用默认的orders API
    try {
      const response = await $fetch('/api/orders')
      if (response.success && response.stats) {
        stats.value = {
          totalOrders: response.stats.totalOrders || 0,
          totalRevenue: response.stats.totalRevenue || 0,
          pendingOrders: response.stats.pendingOrders || 0,
          completionRate: response.stats.completionRate || 0,
          orderGrowth: response.stats.orderGrowth || 0,
          revenueGrowth: response.stats.revenueGrowth || 0
        }
      }
    } catch (fallbackError) {
      console.error('获取统计数据失败（备用方案）:', fallbackError)
    }
  } finally {
    loading.value = false
  }
  
  // 获取图表数据
  await fetchChartData()
}

// 监听时间范围变化
watch(selectedTimeRange, () => {
  fetchStats()
})

// 页面加载时获取数据
onMounted(async () => {
  await fetchStats()
  // 等待 DOM 渲染完成后再初始化图表
  await nextTick()
  updateCharts()
})

// 方法
const formatNumber = (num: number) => {
  return new Intl.NumberFormat('zh-CN').format(num)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'orange',
    paid: 'blue',
    processing: 'purple',
    shipped: 'cyan',
    completed: 'green',
    cancelled: 'red'
  }
  return colors[status] || 'gray'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待付款',
    paid: '已付款',
    processing: '处理中',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消'
  }
  return labels[status] || status
}

const refreshStats = () => {
  fetchStats()
}

// 获取图表数据
const fetchChartData = async (): Promise<void> => {
  try {
    const { startDate, endDate } = getTimeRange()
    
    // 获取每日订单和销售额数据
    // 使用 limit=10000 确保获取所有订单数据用于统计（API 会忽略 limit >= 1000 的限制）
    const response = await $fetch('/api/orders', {
      query: {
        startDate,
        endDate,
        limit: 10000 // 获取所有数据用于图表统计
      }
    })
    
    if (response.success && response.data) {
      // 按日期分组统计
      const dailyOrders: Record<string, { orders: number, revenue: number }> = {}
      const statusCount: Record<string, number> = {}
      
      response.data.forEach((order: any) => {
        const date = new Date(order.createdAt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
        if (!dailyOrders[date]) {
          dailyOrders[date] = { orders: 0, revenue: 0 }
        }
        dailyOrders[date].orders++
        dailyOrders[date].revenue += parseFloat(order.amount) || 0
        
        // 统计状态分布
        const status = order.status || 'unknown'
        statusCount[status] = (statusCount[status] || 0) + 1
      })
      
      // 转换为图表数据格式
      const dates = Object.keys(dailyOrders).sort()
      chartData.value.orderTrend = {
        labels: dates,
        data: dates.map(date => dailyOrders[date].orders)
      }
      
      chartData.value.revenueTrend = {
        labels: dates,
        data: dates.map(date => dailyOrders[date].revenue)
      }
      
      // 状态分布 - 确保按固定顺序显示
      const statusLabels: Record<string, string> = {
        pending: '待付款',
        paid: '已付款',
        processing: '处理中',
        completed: '已完成',
        cancelled: '已取消',
        unknown: '未知'
      }
      
      // 按固定顺序排列状态，确保图表颜色一致
      const statusOrder = ['pending', 'paid', 'processing', 'completed', 'cancelled', 'unknown']
      const sortedStatusKeys = statusOrder.filter(s => statusCount[s] > 0)
      const otherStatusKeys = Object.keys(statusCount).filter(s => !statusOrder.includes(s))
      
      chartData.value.statusDistribution = {
        labels: [...sortedStatusKeys, ...otherStatusKeys].map(s => statusLabels[s] || s),
        data: [...sortedStatusKeys, ...otherStatusKeys].map(s => statusCount[s] || 0)
      }
      
      console.log('订单状态分布数据:', chartData.value.statusDistribution)
      
      // 等待 DOM 更新后再更新图表
      await nextTick()
      updateCharts()
    }
  } catch (error) {
    console.error('获取图表数据失败:', error)
  }
}

// 更新图表
const updateCharts = () => {
  if (!orderTrendChart.value || !revenueTrendChart.value || !statusChart.value) {
    return
  }
  // 订单趋势图
  if (orderTrendChart.value) {
    if (orderChartInstance) {
      orderChartInstance.destroy()
    }
    orderChartInstance = new Chart(orderTrendChart.value, {
      type: 'line',
      data: {
        labels: chartData.value.orderTrend.labels,
        datasets: [{
          label: '订单数',
          data: chartData.value.orderTrend.data,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#9ca3af'
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#9ca3af'
            },
            grid: {
              color: '#2a2a2b'
            }
          },
          y: {
            ticks: {
              color: '#9ca3af'
            },
            grid: {
              color: '#2a2a2b'
            }
          }
        }
      }
    })
  }
  
  // 销售额趋势图
  if (revenueTrendChart.value) {
    if (revenueChartInstance) {
      revenueChartInstance.destroy()
    }
    revenueChartInstance = new Chart(revenueTrendChart.value, {
      type: 'line',
      data: {
        labels: chartData.value.revenueTrend.labels,
        datasets: [{
          label: '销售额 (¥)',
          data: chartData.value.revenueTrend.data,
          borderColor: '#00dc82',
          backgroundColor: 'rgba(0, 220, 130, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#9ca3af'
            }
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#9ca3af'
            },
            grid: {
              color: '#2a2a2b'
            }
          },
          y: {
            ticks: {
              color: '#9ca3af'
            },
            grid: {
              color: '#2a2a2b'
            }
          }
        }
      }
    })
  }
  
  // 订单状态分布图
  if (statusChart.value) {
    if (statusChartInstance) {
      statusChartInstance.destroy()
    }
    statusChartInstance = new Chart(statusChart.value, {
      type: 'doughnut',
      data: {
        labels: chartData.value.statusDistribution.labels,
        datasets: [{
          data: chartData.value.statusDistribution.data,
          backgroundColor: [
            'rgba(251, 146, 60, 0.8)',  // 待付款 - orange
            'rgba(59, 130, 246, 0.8)',   // 已付款 - blue
            'rgba(168, 85, 247, 0.8)',   // 处理中 - purple
            'rgba(34, 197, 94, 0.8)',    // 已完成 - green
            'rgba(239, 68, 68, 0.8)',    // 已取消 - red
            'rgba(156, 163, 175, 0.8)'   // 未知 - gray
          ],
          borderColor: '#1a1a1b',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: '#9ca3af',
              padding: 15
            }
          }
        }
      }
    })
  }
}

// 组件卸载时清理图表
onUnmounted(() => {
  if (orderChartInstance) {
    orderChartInstance.destroy()
  }
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
  }
  if (statusChartInstance) {
    statusChartInstance.destroy()
  }
})
</script>