<template>
  <div class="p-6 space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white">机器人命令管理</h1>
        <p class="text-[#9ca3af] mt-1">配置和管理机器人的命令响应</p>
      </div>
      <div class="flex items-center gap-3">
        <UBadge v-if="saveStatus === 'saving'" color="yellow" variant="subtle">
          <UIcon name="i-heroicons-arrow-path" class="w-3 h-3 animate-spin mr-1" />
          保存中...
        </UBadge>
        <UBadge v-else-if="saveStatus === 'saved'" color="green" variant="subtle">
          <UIcon name="i-heroicons-check" class="w-3 h-3 mr-1" />
          已保存
        </UBadge>
        <UBadge v-else-if="saveStatus === 'error'" color="red" variant="subtle">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-3 h-3 mr-1" />
          保存失败
        </UBadge>
        <UButton @click="refreshCommands" variant="outline" size="sm">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
          刷新
        </UButton>
        <UButton @click="addNewCommand" color="primary" size="sm">
          <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-2" />
          添加命令
        </UButton>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">总命令数</p>
            <p class="text-2xl font-bold text-white">{{ commands.length }}</p>
          </div>
          <UIcon name="i-heroicons-command-line" class="w-8 h-8 text-[#00dc82]" />
        </div>
      </div>
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">活跃命令</p>
            <p class="text-2xl font-bold text-white">{{ activeCommandsCount }}</p>
          </div>
          <UIcon name="i-heroicons-play" class="w-8 h-8 text-green-500" />
        </div>
      </div>
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">今日使用</p>
            <p class="text-2xl font-bold text-white">{{ totalUsageToday }}</p>
          </div>
          <UIcon name="i-heroicons-chart-bar" class="w-8 h-8 text-blue-500" />
        </div>
      </div>
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">错误率</p>
            <p class="text-2xl font-bold text-white">{{ errorRate }}%</p>
          </div>
          <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 text-red-500" />
        </div>
      </div>
    </div>



    <!-- 命令配置列表 -->
    <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg">
      <div class="p-4 border-b border-[#2a2a2b]">
        <h2 class="text-lg font-semibold text-white">命令配置</h2>
        <p class="text-sm text-[#9ca3af] mt-1">直接编辑命令信息，修改后将自动保存</p>
      </div>
      
      <div class="p-4 space-y-4">
        <div 
          v-for="(command, index) in commands" 
          :key="command.id"
          class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-4 space-y-4"
        >
          <!-- 命令头部 -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <code class="px-2 py-1 bg-[#1a1a1b] rounded text-[#00dc82] text-sm font-mono">
                /{{ command.name }}
              </code>
              <UBadge
                :color="command.status === 'active' ? 'green' : 'red'"
                variant="subtle"
                size="sm"
              >
                {{ command.status === 'active' ? '活跃' : '禁用' }}
              </UBadge>
            </div>
            <div class="flex items-center gap-2">
              <UButton 
                variant="ghost" 
                size="xs" 
                :color="command.status === 'active' ? 'red' : 'green'"
                @click="toggleCommandStatus(command)"
              >
                <UIcon 
                  :name="command.status === 'active' ? 'i-heroicons-pause' : 'i-heroicons-play'" 
                  class="w-4 h-4" 
                />
                {{ command.status === 'active' ? '禁用' : '启用' }}
              </UButton>
              <UButton variant="ghost" size="xs" color="red" @click="deleteCommand(index)">
                <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                删除
              </UButton>
            </div>
          </div>

          <!-- 可编辑字段 -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-[#9ca3af] mb-2">命令名称</label>
              <UInput
                v-model="command.name"
                placeholder="例如: start, help, info"
                @input="onCommandChange(command)"
                class="w-full"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-[#9ca3af] mb-2">命令描述</label>
              <UInput
                v-model="command.description"
                placeholder="描述这个命令的功能..."
                @input="onCommandChange(command)"
                class="w-full"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-[#9ca3af] mb-2">回复内容</label>
            <UTextarea
              v-model="command.response"
              placeholder="用户使用此命令时的回复内容..."
              @input="onCommandChange(command)"
              :rows="4"
              class="w-full"
            />
          </div>

          <!-- 统计信息 -->
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 pt-2 border-t border-[#2a2a2b]">
            <div>
              <p class="text-xs text-[#9ca3af]">使用次数</p>
              <p class="text-sm font-medium text-white">{{ command.usageCount }}</p>
            </div>
            <div>
              <p class="text-xs text-[#9ca3af]">最后使用</p>
              <p class="text-sm font-medium text-white">{{ formatDate(command.lastUsed) }}</p>
            </div>
            <div>
              <p class="text-xs text-[#9ca3af]">创建时间</p>
              <p class="text-sm font-medium text-white">{{ formatDate(command.createdAt) }}</p>
            </div>
            <div>
              <p class="text-xs text-[#9ca3af]">更新时间</p>
              <p class="text-sm font-medium text-white">{{ formatDate(command.updatedAt) }}</p>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="commands.length === 0" class="text-center py-12">
          <UIcon name="i-heroicons-command-line" class="w-12 h-12 text-[#4a4a4b] mx-auto mb-4" />
          <h3 class="text-lg font-medium text-white mb-2">暂无命令配置</h3>
          <p class="text-[#9ca3af] mb-4">开始添加您的第一个机器人命令</p>
          <UButton @click="addNewCommand" color="primary">
            <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-2" />
            添加命令
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 页面元数据
definePageMeta({
  title: '机器人命令',
  middleware: ['auth', 'license']
})

// 类型定义
interface BotCommand {
  id: number
  name: string
  description: string
  response: string
  status: 'active' | 'inactive'
  usageCount: number
  lastUsed: Date
  createdAt: Date
  updatedAt: Date
}

// 响应式数据
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const saveTimeouts = new Map<number, NodeJS.Timeout>()

// 基于实际机器人功能的命令数据
const commands = ref<BotCommand[]>([
  {
    id: 1,
    name: 'start',
    description: '开始使用机器人',
    response: '欢迎使用USDT转TRX，TRX转能量机器人\n\n🔺进U即兑TRX,进TRX即兑能量,\n24小时全自动返,1U起兑\n❗️注意:请勿使用交易所转账,丢失自负!!\n\n‼️有任何问题,请私聊联系老板',
    status: 'active',
    usageCount: 2847,
    lastUsed: new Date('2024-01-15T10:30:00'),
    createdAt: new Date('2024-01-01T00:00:00'),
    updatedAt: new Date('2024-01-15T10:30:00')
  },
  {
    id: 2,
    name: '查询后台信息',
    description: '查询后台系统信息',
    response: '📊 后台系统信息\n\n正在查询后台配置和状态信息...',
    status: 'active',
    usageCount: 0,
    lastUsed: new Date(),
    createdAt: new Date(),
    updatedAt: new Date()
  }
])

// 计算属性
const activeCommandsCount = computed(() => 
  commands.value.filter(cmd => cmd.status === 'active').length
)

const totalUsageToday = computed(() => 
  commands.value.reduce((total, cmd) => total + cmd.usageCount, 0)
)

const errorRate = computed(() => 1.2)

// 方法
const onCommandChange = (command: BotCommand) => {
  // 清除之前的定时器
  if (saveTimeouts.has(command.id)) {
    clearTimeout(saveTimeouts.get(command.id)!)
    saveTimeouts.delete(command.id)
  }

  // 设置新的定时器，3秒后自动保存
  const timeout = setTimeout(() => {
    saveCommand(command)
    saveTimeouts.delete(command.id)
  }, 3000)

  saveTimeouts.set(command.id, timeout)
  
  // 更新修改时间
  command.updatedAt = new Date()
}

const saveCommand = async (command: BotCommand) => {
  try {
    saveStatus.value = 'saving'
    
    // 调用API保存
    const response = await $fetch('/api/bot-commands', {
      method: 'POST',
      body: { commands: [command] }
    })

    if (response.success) {
      saveStatus.value = 'saved'
      setTimeout(() => {
        if (saveStatus.value === 'saved') {
          saveStatus.value = 'idle'
        }
      }, 2000)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('保存命令失败:', error)
    saveStatus.value = 'error'
    setTimeout(() => {
      saveStatus.value = 'idle'
    }, 3000)
  }
}

const saveAllCommands = async () => {
  try {
    saveStatus.value = 'saving'
    
    const response = await $fetch('/api/bot-commands', {
      method: 'POST',
      body: { commands: commands.value }
    })

    if (response.success) {
      saveStatus.value = 'saved'
      setTimeout(() => {
        if (saveStatus.value === 'saved') {
          saveStatus.value = 'idle'
        }
      }, 2000)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('保存所有命令失败:', error)
    saveStatus.value = 'error'
    setTimeout(() => {
      saveStatus.value = 'idle'
    }, 3000)
  }
}

const addNewCommand = () => {
  const newCommand: BotCommand = {
    id: Date.now(),
    name: '',
    description: '',
    response: '',
    status: 'active',
    usageCount: 0,
    lastUsed: new Date(),
    createdAt: new Date(),
    updatedAt: new Date()
  }
  
  commands.value.unshift(newCommand)
}

const toggleCommandStatus = (command: BotCommand) => {
  command.status = command.status === 'active' ? 'inactive' : 'active'
  command.updatedAt = new Date()
  onCommandChange(command)
}

const deleteCommand = (index: number) => {
  const command = commands.value[index]
  
  // 清除定时器
  if (saveTimeouts.has(command.id)) {
    clearTimeout(saveTimeouts.get(command.id)!)
    saveTimeouts.delete(command.id)
  }
  
  commands.value.splice(index, 1)
  saveAllCommands()
}

const refreshCommands = () => {
  // 这里可以从API重新加载命令数据
  console.log('刷新命令列表')
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// 页面卸载时清理定时器
onUnmounted(() => {
  saveTimeouts.forEach(timeout => clearTimeout(timeout))
  saveTimeouts.clear()
})
</script>