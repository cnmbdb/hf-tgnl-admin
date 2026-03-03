<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <div class="w-8 h-8 bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-squares-plus" class="w-5 h-5 text-[#00dc82]" />
          </div>
          内联键盘
        </h1>
        <p class="mt-1 text-sm text-[#9ca3af]">管理机器人的内联键盘按钮和回调功能</p>
      </div>
      <div class="flex gap-2">
        <UButton variant="outline" size="sm" @click="refreshInlineKeyboards">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
          刷新
        </UButton>
        <UButton color="primary" size="sm" class="bg-[#00dc82] hover:bg-[#00dc82]/80" @click="showAddModal = true">
          <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-2" />
          创建内联键盘
        </UButton>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">总内联键盘</p>
            <p class="text-2xl font-bold text-white">{{ stats.totalInlineKeyboards }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-squares-plus" class="w-6 h-6 text-blue-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">活跃键盘</p>
            <p class="text-2xl font-bold text-white">{{ stats.activeInlineKeyboards }}</p>
          </div>
          <div class="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-check-circle" class="w-6 h-6 text-green-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">总回调数</p>
            <p class="text-2xl font-bold text-white">{{ stats.totalCallbacks }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-cursor-arrow-ripple" class="w-6 h-6 text-purple-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">今日点击</p>
            <p class="text-2xl font-bold text-white">{{ stats.todayClicks }}</p>
          </div>
          <div class="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-hand-raised" class="w-6 h-6 text-orange-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- 内联键盘列表 -->
    <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg">
      <div class="p-4 border-b border-[#2a2a2b]">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white">内联键盘列表</h2>
          <div class="flex gap-2">
            <UInput
              v-model="searchQuery"
              placeholder="搜索键盘名称..."
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

      <!-- 卡片网格布局 - 一行两个 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div 
          v-for="keyboard in filteredInlineKeyboards" 
          :key="keyboard.id" 
          class="bg-gradient-to-br from-[#1a1a1b] to-[#2a2a2b] border border-[#3a3a3b] rounded-xl p-6 hover:border-blue-400/50 hover:shadow-xl transition-all duration-300 shadow-lg"
        >
          <!-- 卡片头部 -->
          <div class="mb-4">
            <h3 class="text-lg font-semibold text-white mb-2">{{ keyboard.name }}</h3>
            <p class="text-sm text-[#9ca3af] mb-3">{{ keyboard.description }}</p>
            
            <!-- 状态和回调类型 -->
            <div class="flex items-center justify-between mb-3">
              <UBadge
                :color="keyboard.status === 'active' ? 'green' : 'red'"
                variant="subtle"
                size="sm"
              >
                {{ keyboard.status === 'active' ? '活跃' : '禁用' }}
              </UBadge>
              <div class="flex flex-wrap gap-1">
                <UBadge
                  v-for="type in getUniqueButtonTypes(keyboard.buttons)"
                  :key="type"
                  :color="getTypeColor(type)"
                  variant="subtle"
                  size="xs"
                >
                  {{ getTypeLabel(type) }}
                </UBadge>
              </div>
            </div>
          </div>

          <!-- 按钮预览 -->
          <div class="mb-4">
            <h4 class="text-sm font-medium text-[#9ca3af] mb-2">按钮预览</h4>
            <div class="space-y-2 max-h-32 overflow-y-auto">
              <template v-for="(row, rowIndex) in keyboard.buttons" :key="rowIndex">
                <div
                  v-for="(button, buttonIndex) in row"
                  :key="`${rowIndex}-${buttonIndex}`"
                  class="w-full px-3 py-2 bg-gradient-to-r from-[#2a2a2b] to-[#323234] border border-[#3a3a3b] rounded-lg text-xs text-white flex items-center justify-center hover:border-blue-400/50 transition-all duration-200"
                >
                  <span class="font-medium truncate">{{ button.text }}</span>
                </div>
              </template>
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="mb-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-[#9ca3af]">点击次数</span>
              <div class="text-white font-medium">{{ keyboard.clickCount }}</div>
            </div>
            <div>
              <span class="text-[#9ca3af]">创建时间</span>
              <div class="text-white font-medium text-xs">{{ formatDate(keyboard.createdAt) }}</div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-2 pt-4 border-t border-[#3a3a3b]">
            <UButton variant="ghost" size="xs" @click="editInlineKeyboard(keyboard)" class="flex-1">
              <UIcon name="i-heroicons-pencil" class="w-4 h-4 mr-1" />
              编辑
            </UButton>
            <UButton variant="ghost" size="xs" @click="previewInlineKeyboard(keyboard)">
              <UIcon name="i-heroicons-eye" class="w-4 h-4" />
            </UButton>
            <UButton 
              variant="ghost" 
              size="xs" 
              :color="keyboard.status === 'active' ? 'red' : 'green'"
              @click="toggleInlineKeyboardStatus(keyboard)"
            >
              <UIcon 
                :name="keyboard.status === 'active' ? 'i-heroicons-pause' : 'i-heroicons-play'" 
                class="w-4 h-4" 
              />
            </UButton>
            <UButton variant="ghost" size="xs" color="red" @click="deleteInlineKeyboard(keyboard)">
              <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            </UButton>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建内联键盘模态框 -->
    <UModal v-model="showAddModal" :ui="{ width: 'sm:max-w-3xl' }">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-white mb-4">创建内联键盘</h3>
        <div class="space-y-4">
          <UInput
            v-model="newInlineKeyboard.name"
            label="键盘名称"
            placeholder="输入内联键盘名称"
          />
          
          <UTextarea
            v-model="newInlineKeyboard.description"
            label="描述"
            placeholder="输入键盘描述"
          />
          
          <div>
            <label class="block text-sm font-medium text-white mb-2">按钮布局</label>
            <div class="space-y-3">
              <div v-for="(row, rowIndex) in newInlineKeyboard.buttons" :key="rowIndex" class="border border-[#2a2a2b] rounded-lg p-3">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm text-[#9ca3af]">第 {{ rowIndex + 1 }} 行</span>
                  <div class="flex gap-2">
                    <UButton 
                      variant="ghost" 
                      size="xs" 
                      color="green"
                      @click="addButtonToRow(rowIndex)"
                      :disabled="row.length >= 3"
                    >
                      <UIcon name="i-heroicons-plus" class="w-4 h-4" />
                    </UButton>
                    <UButton 
                      variant="ghost" 
                      size="xs" 
                      color="red"
                      @click="removeRow(rowIndex)"
                      :disabled="newInlineKeyboard.buttons.length <= 1"
                    >
                      <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                    </UButton>
                  </div>
                </div>
                <div class="space-y-2">
                  <div v-for="(button, buttonIndex) in row" :key="buttonIndex" class="grid grid-cols-12 gap-2 items-end">
                    <div class="col-span-4">
                      <UInput
                        v-model="button.text"
                        :placeholder="`按钮文本`"
                        size="sm"
                      />
                    </div>
                    <div class="col-span-3">
                      <USelect
                        v-model="button.type"
                        :options="buttonTypeOptions"
                        size="sm"
                      />
                    </div>
                    <div class="col-span-4">
                      <UInput
                        v-model="button.value"
                        :placeholder="getValuePlaceholder(button.type)"
                        size="sm"
                      />
                    </div>
                    <div class="col-span-1">
                      <UButton 
                        variant="ghost" 
                        size="xs" 
                        color="red"
                        @click="removeButtonFromRow(rowIndex, buttonIndex)"
                        :disabled="row.length <= 1"
                      >
                        <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
                      </UButton>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-3 flex gap-2">
              <UButton 
                variant="outline" 
                size="sm" 
                @click="addRow"
                :disabled="newInlineKeyboard.buttons.length >= 6"
              >
                <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-2" />
                添加行
              </UButton>
            </div>
          </div>
          
          <USelect
            v-model="newInlineKeyboard.status"
            label="状态"
            :options="[
              { label: '活跃', value: 'active' },
              { label: '禁用', value: 'inactive' }
            ]"
          />
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <UButton variant="outline" @click="showAddModal = false">取消</UButton>
          <UButton color="primary" @click="createInlineKeyboard">创建</UButton>
        </div>
      </div>
    </UModal>

    <!-- 预览模态框 -->
    <UModal v-model="showPreviewModal">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-white mb-4">内联键盘预览</h3>
        <div v-if="previewInlineKeyboardData" class="space-y-2">
          <div v-for="(row, rowIndex) in previewInlineKeyboardData.buttons" :key="rowIndex" class="flex gap-2">
            <button
              v-for="(button, buttonIndex) in row"
              :key="buttonIndex"
              class="flex-1 px-3 py-2 bg-[#2a2a2b] border border-[#3a3a3b] rounded text-white hover:bg-[#3a3a3b] transition-colors flex items-center justify-center gap-2"
              :class="{
                'border-blue-500': button.type === 'url',
                'border-green-500': button.type === 'callback',
                'border-purple-500': button.type === 'switch_inline'
              }"
            >
              <UIcon 
                v-if="button.type === 'url'" 
                name="i-heroicons-link" 
                class="w-4 h-4 text-blue-400" 
              />
              <UIcon 
                v-else-if="button.type === 'callback'" 
                name="i-heroicons-cursor-arrow-rays" 
                class="w-4 h-4 text-green-400" 
              />
              <UIcon 
                v-else-if="button.type === 'switch_inline'" 
                name="i-heroicons-arrow-path-rounded-square" 
                class="w-4 h-4 text-purple-400" 
              />
              {{ button.text }}
            </button>
          </div>
          <div class="mt-4 text-sm text-[#9ca3af]">
            <p><strong>说明：</strong></p>
            <ul class="list-disc list-inside space-y-1 mt-2">
              <li><span class="text-blue-400">蓝色边框</span>：URL 链接按钮</li>
              <li><span class="text-green-400">绿色边框</span>：回调数据按钮</li>
              <li><span class="text-purple-400">紫色边框</span>：内联查询按钮</li>
            </ul>
          </div>
        </div>
        <div class="flex justify-end mt-6">
          <UButton @click="showPreviewModal = false">关闭</UButton>
        </div>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
// 页面元数据
definePageMeta({
  title: '内联键盘',
  middleware: ['auth', 'license']
})

// 响应式数据
const showAddModal = ref(false)
const showPreviewModal = ref(false)
const searchQuery = ref('')
const statusFilter = ref('all')
const previewInlineKeyboardData = ref<any>(null)

// 统计数据
const stats = ref({
  totalInlineKeyboards: 7,
  activeInlineKeyboards: 7,
  totalCallbacks: 28,
  todayClicks: 342
})

// 新内联键盘表单
const newInlineKeyboard = ref({
  name: '',
  description: '',
  buttons: [
    [{ text: '按钮1', type: 'callback', value: 'callback_data_1' }]
  ],
  status: 'active'
})

// 状态选项
const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '活跃', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

// 按钮类型选项
const buttonTypeOptions = [
  { label: '回调数据', value: 'callback' },
  { label: 'URL链接', value: 'url' },
  { label: '内联查询', value: 'switch_inline' }
]

// 真实机器人内联键盘数据
const inlineKeyboards = ref([
  {
    id: 1,
    name: '能量购买选项',
    description: 'TRX转能量的时长和次数选择',
    buttons: [
      [
        { text: '1小时1次', type: 'callback', value: 'energy_1h_1' },
        { text: '1小时3次', type: 'callback', value: 'energy_1h_3' },
        { text: '1小时5次', type: 'callback', value: 'energy_1h_5' }
      ],
      [
        { text: '1天1次', type: 'callback', value: 'energy_1d_1' },
        { text: '1天3次', type: 'callback', value: 'energy_1d_3' },
        { text: '1天5次', type: 'callback', value: 'energy_1d_5' }
      ],
      [
        { text: '3天1次', type: 'callback', value: 'energy_3d_1' },
        { text: '3天3次', type: 'callback', value: 'energy_3d_3' },
        { text: '3天5次', type: 'callback', value: 'energy_3d_5' }
      ]
    ],
    status: 'active',
    clickCount: 1245,
    createdAt: '2024-01-15T10:30:00Z'
  },
  {
    id: 2,
    name: '地址管理',
    description: '监听地址的绑定和删除操作',
    buttons: [
      [
        { text: '绑定地址', type: 'callback', value: 'bind_address' },
        { text: '删除地址', type: 'callback', value: 'delete_address' }
      ]
    ],
    status: 'active',
    clickCount: 567,
    createdAt: '2024-01-14T16:45:00Z'
  },
  {
    id: 3,
    name: '支付确认',
    description: '订单支付确认和取消操作',
    buttons: [
      [
        { text: '确认支付', type: 'callback', value: 'confirm_payment' },
        { text: '取消订单', type: 'callback', value: 'cancel_order' }
      ]
    ],
    status: 'active',
    clickCount: 892,
    createdAt: '2024-01-13T11:30:00Z'
  },
  {
    id: 4,
    name: '充值金额选择',
    description: '预设充值金额快速选择',
    buttons: [
      [
        { text: '100', type: 'callback', value: 'recharge_100' },
        { text: '200', type: 'callback', value: 'recharge_200' },
        { text: '500', type: 'callback', value: 'recharge_500' }
      ],
      [
        { text: '1000', type: 'callback', value: 'recharge_1000' },
        { text: '2000', type: 'callback', value: 'recharge_2000' },
        { text: '5000', type: 'callback', value: 'recharge_5000' }
      ]
    ],
    status: 'active',
    clickCount: 734,
    createdAt: '2024-01-12T09:15:00Z'
  },
  {
    id: 5,
    name: '支付方式选择',
    description: '多种支付方式选择界面',
    buttons: [
      [
        { text: '银行卡', type: 'callback', value: 'pay_bank' },
        { text: '支付宝', type: 'callback', value: 'pay_alipay' }
      ],
      [
        { text: '微信', type: 'callback', value: 'pay_wechat' },
        { text: '所有', type: 'callback', value: 'pay_all' }
      ]
    ],
    status: 'active',
    clickCount: 456,
    createdAt: '2024-01-11T14:20:00Z'
  },
  {
    id: 6,
    name: '汇率查询',
    description: '实时汇率查询功能',
    buttons: [
      [
        { text: '查询汇率', type: 'callback', value: 'check_rate' }
      ]
    ],
    status: 'active',
    clickCount: 234,
    createdAt: '2024-01-10T16:30:00Z'
  },
  {
    id: 7,
    name: '客服和群组',
    description: '联系客服和加入群组的快捷入口',
    buttons: [
      [
        { text: '联系客服', type: 'url', value: 'https://t.me/customer_service' },
        { text: '加入群组', type: 'url', value: 'https://t.me/energy_group' }
      ]
    ],
    status: 'active',
    clickCount: 123,
    createdAt: '2024-01-09T12:45:00Z'
  },
  {
    id: 8,
    name: '笔数套餐-已有套餐/添加套餐',
    description: '笔数套餐功能入口',
    buttons: [
      [
        { text: '已有套餐', type: 'callback', value: 'bishu_existing' },
        { text: '添加套餐', type: 'callback', value: 'bishu_add' }
      ]
    ],
    status: 'active',
    clickCount: 0,
    createdAt: new Date().toISOString()
  },
  {
    id: 9,
    name: '笔数套餐-套餐选择',
    description: '选择笔数套餐类型',
    buttons: [
      [
        { text: '5笔/15T', type: 'callback', value: 'bishu_pkg_5_15' },
        { text: '15笔/45T', type: 'callback', value: 'bishu_pkg_15_45' }
      ],
      [
        { text: '50笔/150T', type: 'callback', value: 'bishu_pkg_50_150' },
        { text: '100笔/300T', type: 'callback', value: 'bishu_pkg_100_300' }
      ]
    ],
    status: 'active',
    clickCount: 0,
    createdAt: new Date().toISOString()
  },
  {
    id: 10,
    name: '笔数套餐-支付方式选择',
    description: '选择使用余额或立即支付',
    buttons: [
      [
        { text: '使用余额', type: 'callback', value: 'bishu_pay_balance' },
        { text: '立即支付', type: 'callback', value: 'bishu_pay_now' }
      ]
    ],
    status: 'active',
    clickCount: 0,
    createdAt: new Date().toISOString()
  },
  {
    id: 11,
    name: '笔数套餐-地址管理',
    description: '激活/关闭/删除地址操作',
    buttons: [
      [
        { text: '激活', type: 'callback', value: 'bishu_activate' },
        { text: '关闭', type: 'callback', value: 'bishu_close' },
        { text: '删除', type: 'callback', value: 'bishu_delete' }
      ]
    ],
    status: 'active',
    clickCount: 0,
    createdAt: new Date().toISOString()
  }
])

// 计算属性
const filteredInlineKeyboards = computed(() => {
  let filtered = inlineKeyboards.value

  if (searchQuery.value) {
    filtered = filtered.filter(keyboard => 
      keyboard.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      keyboard.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(keyboard => keyboard.status === statusFilter.value)
  }

  return filtered
})

// 方法
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getUniqueButtonTypes = (buttons: any[][]) => {
  const types = new Set<string>()
  buttons.forEach(row => {
    row.forEach(button => {
      types.add(button.type)
    })
  })
  return Array.from(types)
}

const getTypeColor = (type: string) => {
  switch (type) {
    case 'url': return 'blue'
    case 'callback': return 'green'
    case 'switch_inline': return 'purple'
    default: return 'gray'
  }
}

const getTypeLabel = (type: string) => {
  switch (type) {
    case 'url': return 'URL'
    case 'callback': return '回调'
    case 'switch_inline': return '内联'
    default: return type
  }
}

const getValuePlaceholder = (type: string) => {
  switch (type) {
    case 'url': return 'https://example.com'
    case 'callback': return 'callback_data'
    case 'switch_inline': return 'inline_query'
    default: return '值'
  }
}

const refreshInlineKeyboards = () => {
  console.log('刷新内联键盘列表')
}

const addRow = () => {
  newInlineKeyboard.value.buttons.push([{ text: '', type: 'callback', value: '' }])
}

const removeRow = (index: number) => {
  newInlineKeyboard.value.buttons.splice(index, 1)
}

const addButtonToRow = (rowIndex: number) => {
  newInlineKeyboard.value.buttons[rowIndex].push({ text: '', type: 'callback', value: '' })
}

const removeButtonFromRow = (rowIndex: number, buttonIndex: number) => {
  newInlineKeyboard.value.buttons[rowIndex].splice(buttonIndex, 1)
}

const createInlineKeyboard = () => {
  if (!newInlineKeyboard.value.name) {
    return
  }

  // 过滤空按钮
  const filteredButtons = newInlineKeyboard.value.buttons
    .map(row => row.filter(button => button.text.trim() !== ''))
    .filter(row => row.length > 0)

  if (filteredButtons.length === 0) {
    return
  }

  const keyboard = {
    id: Date.now(),
    name: newInlineKeyboard.value.name,
    description: newInlineKeyboard.value.description,
    buttons: filteredButtons,
    status: newInlineKeyboard.value.status,
    clickCount: 0,
    createdAt: new Date().toISOString()
  }

  inlineKeyboards.value.unshift(keyboard)
  
  // 重置表单
  newInlineKeyboard.value = {
    name: '',
    description: '',
    buttons: [
      [{ text: '按钮1', type: 'callback', value: 'callback_data_1' }]
    ],
    status: 'active'
  }
  
  showAddModal.value = false
}

const editInlineKeyboard = (keyboard: any) => {
  console.log('编辑内联键盘:', keyboard)
}

const previewInlineKeyboard = (keyboard: any) => {
  previewInlineKeyboardData.value = keyboard
  showPreviewModal.value = true
}

const toggleInlineKeyboardStatus = (keyboard: any) => {
  keyboard.status = keyboard.status === 'active' ? 'inactive' : 'active'
}

const deleteInlineKeyboard = (keyboard: any) => {
  const index = inlineKeyboards.value.findIndex(k => k.id === keyboard.id)
  if (index > -1) {
    inlineKeyboards.value.splice(index, 1)
  }
}
</script>