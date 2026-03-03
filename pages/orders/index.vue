<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <div class="w-8 h-8 bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-shopping-bag" class="w-5 h-5 text-[#00dc82]" />
          </div>
          订单管理
        </h1>
        <p class="mt-1 text-sm text-[#9ca3af]">管理所有能量出租订单记录</p>
      </div>
      <div class="flex gap-2">
        <USelect
          v-model="selectedTimeRange"
          :options="timeRangeOptions"
          class="w-32"
        />
        <UButton variant="outline" size="sm" @click="refreshOrders">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
          刷新
        </UButton>
        <UButton color="primary" size="sm" class="bg-[#00dc82] hover:bg-[#00dc82]/80">
          <UIcon name="i-heroicons-arrow-down-tray" class="w-4 h-4 mr-2" />
          导出订单
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
            <p class="text-sm text-[#9ca3af]">总能量出租额</p>
            <p class="text-2xl font-bold text-white">{{ formatNumber(stats.totalRevenue) }} 能量</p>
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
            <p class="text-2xl font-bold text-white">{{ stats.completionRate }}%</p>
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

    <!-- 订单列表 -->
    <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg">
      <div class="p-4 border-b border-[#2a2a2b]">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white">订单列表</h2>
          <div class="flex gap-2 items-center">
            <UButton
              v-if="selectedOrderIds.length > 0"
              color="red"
              size="sm"
              variant="solid"
              @click="handleBatchDelete"
            >
              <UIcon name="i-heroicons-trash" class="w-4 h-4 mr-1" />
              批量删除 ({{ selectedOrderIds.length }})
            </UButton>
            <UInput
              v-model="searchQuery"
              placeholder="搜索订单号、用户..."
              class="w-64"
              icon="i-heroicons-magnifying-glass"
            />
            <USelect
              v-model="statusFilter"
              :options="statusOptions"
              class="w-32"
            />
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-[#0c0c0d]">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider w-10">
                <input
                  type="checkbox"
                  class="rounded border-[#4b5563] bg-transparent"
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">订单号</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">用户</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">能量数量</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">金额</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">状态</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">创建时间</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#2a2a2b]">
            <tr v-for="order in filteredOrders" :key="order.id" class="hover:bg-[#2a2a2b]/50">
              <td class="px-4 py-3">
                <input
                  type="checkbox"
                  class="rounded border-[#4b5563] bg-transparent"
                  :value="order.id"
                  v-model="selectedOrderIds"
                />
              </td>
              <td class="px-4 py-3">
                <div class="text-sm font-medium text-white">{{ order.orderNumber }}</div>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center" v-if="order.chatId && order.chatId !== 0">
                  <div class="w-8 h-8 bg-[#2a2a2b] rounded-full flex items-center justify-center mr-3">
                    <span class="text-xs font-medium text-white">{{ order.nickname?.charAt(0) || 'U' }}</span>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-white">{{ order.nickname || '未设置' }}</div>
                    <div class="text-sm text-[#9ca3af]">@{{ order.username }}</div>
                  </div>
                </div>
                <div class="text-sm text-[#9ca3af]" v-else>匿名用户</div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm text-white">{{ getOrderTypeLabel(order) }}</div>
                <div class="text-sm text-[#9ca3af]" v-if="order.chatId && order.chatId !== 0">Chat ID: {{ order.chatId }}</div>
                <div class="text-sm text-[#9ca3af]" v-else>直接转账订单</div>
              </td>
              <td class="px-4 py-3">
                <div class="text-sm font-medium text-white">{{ order.amount.toFixed(2) }} TRX</div>
                <div class="text-sm text-[#9ca3af]">{{ formatNumber(order.amountSun) }} SUN</div>
              </td>
              <td class="px-4 py-3">
                <UBadge
                  :color="(getStatusColor(order.status))"
                  variant="subtle"
                  size="sm"
                >
                  {{ getStatusLabel(order.status) }}
                </UBadge>
              </td>
              <td class="px-4 py-3 text-sm text-[#9ca3af]">{{ formatDate(order.createdAt) }}</td>
              <td class="px-4 py-3">
                <div class="flex gap-2">
                  <UButton variant="ghost" size="xs" @click="viewOrder(order)">
                    <UIcon name="i-heroicons-eye" class="w-4 h-4" />
                  </UButton>
                  <UButton 
                    variant="ghost" 
                    size="xs" 
                    color="red"
                    @click="handleSingleDelete(order)"
                  >
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                  </UButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="px-4 py-3 border-t border-[#2a2a2b] flex items-center justify-between">
        <div class="text-sm text-[#9ca3af]">
          显示 {{ (currentPage - 1) * pageSize + 1 }} 到 {{ Math.min(currentPage * pageSize, totalOrders) }} 条，共 {{ totalOrders }} 条
        </div>
        <div class="flex gap-2">
          <UButton 
            variant="outline" 
            size="sm" 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            上一页
          </UButton>
          <UButton 
            variant="outline" 
            size="sm" 
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            下一页
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 页面元数据
definePageMeta({
  title: '订单管理',
  middleware: ['auth', 'license']
})

// 响应式数据
const searchQuery = ref('')
const statusFilter = ref('all')
const selectedTimeRange = ref('7d')
const currentPage = ref(1)
const pageSize = ref(10)

// 选中状态
const selectedOrderIds = ref<number[]>([])

// 时间范围选项
const timeRangeOptions = [
  { label: '今天', value: '1d' },
  { label: '7天', value: '7d' },
  { label: '30天', value: '30d' },
  { label: '90天', value: '90d' }
]

// 状态选项
const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '待付款', value: 'pending' },
  { label: '已付款', value: 'paid' },
  { label: '处理中', value: 'processing' },
  { label: '已发货', value: 'shipped' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

// 定义订单类型
interface Order {
  id: number
  orderNumber: string
  chatId: number
  username: string
  nickname: string
  paymentMethod: string
  plan: string
  amount: number
  amountSun: number
  status: string
  createdAt: string
  updatedAt: string
  type: string
}

// 响应式数据
const orders = ref<Order[]>([])
const loading = ref(false)

// 统计数据（由后端聚合提供）
const apiStats = ref({
  totalOrders: 0,
  totalRevenue: 0,
  pendingOrders: 0,
  completionRate: 0,
  orderGrowth: 0,
  revenueGrowth: 0
})

const stats = computed(() => apiStats.value)

// 获取订单数据
const fetchOrders = async () => {
  loading.value = true
  try {
    const response: any = await $fetch('/api/orders')
    console.log('订单API响应:', response)
    if (response && response.success && response.data) {
      orders.value = response.data
      // 使用后端统计数据
      if (response.stats) {
        apiStats.value = {
          totalOrders: response.stats.totalOrders || 0,
          totalRevenue: response.stats.totalRevenue || 0,
          pendingOrders: response.stats.pendingOrders || 0,
          completionRate: response.stats.completionRate || 0,
          orderGrowth: response.stats.orderGrowth || 0,
          revenueGrowth: response.stats.revenueGrowth || 0
        }
      }
      console.log('订单数据加载成功:', orders.value.length, '条')
    } else {
      console.error('订单数据加载失败:', response?.error || '未知错误')
      // 如果是未授权错误,可能需要重新登录
      if (response?.error === '未授权访问') {
        console.warn('需要登录才能查看订单')
      }
    }
  } catch (error) {
    console.error('获取订单数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchOrders()
})

// 计算属性
const filteredOrders = computed(() => {
  let filtered = orders.value

  if (searchQuery.value) {
    filtered = filtered.filter(order => 
      order.orderNumber.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      order.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      order.nickname.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      String(order.chatId).includes(searchQuery.value)
    )
  }

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(order => order.status === statusFilter.value)
  }

  return filtered
})

const totalOrders = computed(() => filteredOrders.value.length)
const totalPages = computed(() => Math.ceil(totalOrders.value / pageSize.value))

const isAllSelected = computed(() => {
  const currentIds = filteredOrders.value.map((o) => o.id)
  return currentIds.length > 0 && currentIds.every((id) => selectedOrderIds.value.includes(id))
})

// 方法
const formatNumber = (num: number) => {
  return new Intl.NumberFormat('zh-CN').format(num)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusColor = (status: string): 'orange' | 'blue' | 'purple' | 'cyan' | 'green' | 'red' | 'gray' => {
  const colors: Record<string, 'orange' | 'blue' | 'purple' | 'cyan' | 'green' | 'red' | 'gray'> = {
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

// 根据支付方式区分订单业务类型文案
const getOrderTypeLabel = (order: Order) => {
  if (order.paymentMethod === 'recharge') {
    return '充值余额'
  }
  return '能量出租'
}

const refreshOrders = () => {
  fetchOrders()
}

const toggleSelectAll = (event: Event) => {
  const checked = (event.target as HTMLInputElement).checked
  if (!checked) {
    selectedOrderIds.value = []
    return
  }
  const currentIds = filteredOrders.value.map((o) => o.id)
  selectedOrderIds.value = Array.from(new Set([...selectedOrderIds.value, ...currentIds]))
}

const deleteOrders = async (ids: number[]) => {
  if (!ids.length) return
  if (!confirm(`确定要删除选中的 ${ids.length} 个订单吗？此操作不可恢复！`)) {
    return
  }
  try {
    const response: any = await $fetch('/api/orders', {
      method: 'DELETE',
      body: { ids }
    })
    if (response && response.success) {
      await fetchOrders()
      selectedOrderIds.value = []
      alert('订单删除成功')
    } else {
      alert((response && response.error) || '删除失败')
    }
  } catch (error: any) {
    console.error('删除订单失败:', error)
    alert(error?.message || '删除订单失败')
  }
}

const handleSingleDelete = (order: Order) => {
  deleteOrders([order.id])
}

const handleBatchDelete = () => {
  deleteOrders(selectedOrderIds.value)
}

const viewOrder = (order: any) => {
  console.log('查看订单:', order)
}

const processOrder = (order: any) => {
  order.status = 'processing'
  console.log('处理订单:', order)
}

const cancelOrder = (order: any) => {
  order.status = 'cancelled'
  console.log('取消订单:', order)
}
</script>