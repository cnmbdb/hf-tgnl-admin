<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <div class="w-8 h-8 bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-chat-bubble-left-right" class="w-5 h-5 text-[#00dc82]" />
          </div>
          关键词回复管理
        </h1>
        <p class="mt-1 text-sm text-[#9ca3af]">管理机器人的关键词回复模块，支持文案、图片、内联按钮组合</p>
      </div>
      <div class="flex gap-2">
        <UButton variant="outline" size="sm" @click="loadKeywordReplies">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
          刷新
        </UButton>
        <UBadge v-if="hasUnsavedChanges" color="orange" variant="subtle" class="px-3 py-1">
          <UIcon name="i-heroicons-clock" class="w-3 h-3 mr-1" />
          自动保存中...
        </UBadge>
        <UBadge v-else color="green" variant="subtle" class="px-3 py-1">
          <UIcon name="i-heroicons-check" class="w-3 h-3 mr-1" />
          已保存
        </UBadge>
      </div>
    </div>

    <!-- 分类标签 -->
    <div class="flex gap-4 border-b border-[#2a2a2b]">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
          activeTab === tab.key
            ? 'text-[#00dc82] border-[#00dc82]'
            : 'text-[#9ca3af] border-transparent hover:text-white hover:border-[#4a4a4b]'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 命令回复模块 -->
    <div v-if="activeTab === 'commands'" class="space-y-6">
      <!-- 添加命令按钮 -->
      <div class="flex justify-end mb-4">
        <UButton color="primary" size="sm" @click="showAddCommandModal = true">
          <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-2" />
          添加命令
        </UButton>
      </div>
      
      <div v-for="(command, commandKey) in keywordReplies.commands" :key="commandKey" class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white flex items-center gap-2 cursor-pointer" @click="toggleGroupCollapse(`commands_${commandKey}`)">
            <UIcon 
              :name="isGroupCollapsed(`commands_${commandKey}`) ? 'i-heroicons-chevron-right' : 'i-heroicons-chevron-down'" 
              class="w-5 h-5 text-[#9ca3af] transition-transform"
            />
            <UIcon name="i-heroicons-command-line" class="w-5 h-5 text-[#00dc82]" />
            {{ commandKey }} 命令回复
          </h3>
          <div class="flex gap-2">
            <UButton variant="outline" size="xs" @click.stop="addModule(commandKey, 'commands')">
              <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-1" />
              添加模块
            </UButton>
            <UButton variant="outline" size="xs" color="red" @click.stop="removeCommand(commandKey)">
              <UIcon name="i-heroicons-trash" class="w-4 h-4 mr-1" />
              删除命令
            </UButton>
          </div>
        </div>
        
        <div v-show="!isGroupCollapsed(`commands_${commandKey}`)" class="space-y-4">
          <div
            v-for="(module, moduleIndex) in command"
            :key="module.id"
            class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2 flex-1 cursor-pointer" @click="toggleModuleCollapse(`commands_${commandKey}_${moduleIndex}`)">
                <UIcon 
                  :name="isModuleCollapsed(`commands_${commandKey}_${moduleIndex}`) ? 'i-heroicons-chevron-right' : 'i-heroicons-chevron-down'" 
                  class="w-4 h-4 text-[#9ca3af] transition-transform"
                />
                <UBadge :color="(getModuleTypeColor(module.type))" variant="subtle" size="sm">
                  {{ getModuleTypeLabel(module.type) }}
                </UBadge>
                <span class="text-xs text-[#9ca3af]">顺序: {{ module.order }}</span>
              </div>
              <div class="flex gap-1" @click.stop>
                <UButton variant="ghost" size="xs" @click="moveModule(commandKey, 'commands', moduleIndex, -1)" :disabled="moduleIndex === 0">
                  <UIcon name="i-heroicons-arrow-up" class="w-3 h-3" />
                </UButton>
                <UButton variant="ghost" size="xs" @click="moveModule(commandKey, 'commands', moduleIndex, 1)" :disabled="moduleIndex === command.length - 1">
                  <UIcon name="i-heroicons-arrow-down" class="w-3 h-3" />
                </UButton>
                <UButton variant="ghost" size="xs" color="red" @click="removeModule(commandKey, 'commands', moduleIndex)">
                  <UIcon name="i-heroicons-trash" class="w-3 h-3" />
                </UButton>
              </div>
            </div>
            
            <!-- 模块内容编辑 -->
            <div v-show="!isModuleCollapsed(`commands_${commandKey}_${moduleIndex}`)" class="space-y-3">
              <!-- 图片路径 -->
              <div v-if="module.type.includes('image')">
                <label class="block text-sm font-medium text-white mb-2">图片文件名</label>
                <UInput
                  :model-value="module.image"
                  @update:model-value="updateModuleField(commandKey, 'commands', moduleIndex, 'image', $event)"
                  placeholder="例如: photo.jpg"
                />
              </div>
              
              <!-- 文案内容 -->
              <div v-if="module.type.includes('text') || module.type === 'text'">
                <label class="block text-sm font-medium text-white mb-2">文案内容</label>
                <UTextarea
                   :model-value="module.content"
                   @update:model-value="updateModuleField(commandKey, 'commands', moduleIndex, 'content', $event)"
                   placeholder="输入回复文案..."
                   :rows="3"
                 />
              </div>
              
              <!-- 内联按钮 -->
              <div v-if="module.type.includes('buttons')">
                <label class="block text-sm font-medium text-white mb-2">内联按钮配置</label>
                
                <!-- 按钮预览区域 -->
                <div class="mb-4 p-3 bg-[#2a2a2b] rounded-lg border border-[#3a3a3b]">
                  <div class="text-xs text-gray-400 mb-2">按钮预览（实际机器人布局）</div>
                  <div class="space-y-2">
                    <div v-for="(row, rowIndex) in module.buttons || []" :key="rowIndex" class="flex gap-2">
                      <button
                        v-for="(button, buttonIndex) in row"
                        :key="buttonIndex"
                        @click="editButton(commandKey, 'commands', moduleIndex, rowIndex, buttonIndex)"
                        class="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded cursor-pointer transition-colors"
                        :class="row.length === 1 ? 'flex-1' : 'flex-1'"
                      >
                        {{ button.text || '未设置' }}
                      </button>
                    </div>
                  </div>
                </div>

                <!-- 按钮编辑区域 -->
                <div class="space-y-3">
                  <div v-for="(row, rowIndex) in module.buttons || []" :key="rowIndex" class="border border-[#3a3a3b] rounded-lg p-3">
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-sm text-gray-400">第 {{ rowIndex + 1 }} 行按钮</span>
                      <div class="flex gap-1">
                        <UButton 
                          v-if="rowIndex > 0"
                          variant="ghost" 
                          size="xs" 
                          @click="moveButtonRow(commandKey, 'commands', moduleIndex, rowIndex, -1)"
                        >
                          <UIcon name="i-heroicons-arrow-up" class="w-3 h-3" />
                        </UButton>
                        <UButton 
                           v-if="module.buttons && rowIndex < module.buttons.length - 1"
                           variant="ghost" 
                           size="xs" 
                           @click="moveButtonRow(commandKey, 'commands', moduleIndex, rowIndex, 1)"
                         >
                          <UIcon name="i-heroicons-arrow-down" class="w-3 h-3" />
                        </UButton>
                        <UButton 
                          v-if="row.length < 2"
                          variant="ghost" 
                          size="xs" 
                          color="green"
                          @click="addButtonToRow(commandKey, 'commands', moduleIndex, rowIndex)"
                        >
                          <UIcon name="i-heroicons-plus" class="w-3 h-3" />
                        </UButton>
                        <UButton 
                          variant="ghost" 
                          size="xs" 
                          color="red" 
                          @click="removeButtonRow(commandKey, 'commands', moduleIndex, rowIndex)"
                        >
                          <UIcon name="i-heroicons-trash" class="w-3 h-3" />
                        </UButton>
                      </div>
                    </div>
                    
                    <div class="space-y-2">
                      <div v-for="(button, buttonIndex) in row" :key="buttonIndex" class="flex gap-2 items-center">
                        <div class="flex-1 grid grid-cols-2 gap-2">
                          <UInput
                            :model-value="button.text"
                            @update:model-value="updateButtonText(commandKey, 'commands', moduleIndex, rowIndex, buttonIndex, $event)"
                            placeholder="按钮文字"
                            size="sm"
                          />
                          <UInput
                            :model-value="button.callback_data || button.url"
                            @update:model-value="updateButtonAction(commandKey, 'commands', moduleIndex, rowIndex, buttonIndex, $event)"
                            placeholder="callback_data 或 url"
                            size="sm"
                          />
                        </div>
                        <UButton 
                          v-if="row.length > 1"
                          variant="ghost" 
                          size="xs" 
                          color="red"
                          @click="removeButton(commandKey, 'commands', moduleIndex, rowIndex, buttonIndex)"
                        >
                          <UIcon name="i-heroicons-x-mark" class="w-3 h-3" />
                        </UButton>
                      </div>
                    </div>
                  </div>
                  
                  <UButton variant="outline" size="xs" @click="addButtonRow(commandKey, 'commands', moduleIndex)">
                    <UIcon name="i-heroicons-plus" class="w-3 h-3 mr-1" />
                    添加按钮行
                  </UButton>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 按钮回复模块 -->
    <div v-if="activeTab === 'buttons'" class="space-y-6">
      <!-- 添加按钮回复按钮 -->
      <div class="flex justify-end mb-4">
        <UButton color="primary" size="sm" @click="showAddButtonModal = true">
          <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-2" />
          添加按钮回复
        </UButton>
      </div>
      
      <div v-for="(button, buttonKey) in keywordReplies.buttons" :key="buttonKey" class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white flex items-center gap-2 cursor-pointer" @click="toggleGroupCollapse(`buttons_${buttonKey}`)">
            <UIcon 
              :name="isGroupCollapsed(`buttons_${buttonKey}`) ? 'i-heroicons-chevron-right' : 'i-heroicons-chevron-down'" 
              class="w-5 h-5 text-[#9ca3af] transition-transform"
            />
            <UIcon name="i-heroicons-cursor-arrow-rays" class="w-5 h-5 text-[#00dc82]" />
            "{{ buttonKey }}" 按钮回复
          </h3>
          <div class="flex gap-2">
            <UButton variant="outline" size="xs" @click.stop="addModule(buttonKey, 'buttons')">
              <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-1" />
              添加模块
            </UButton>
            <UButton variant="outline" size="xs" color="red" @click.stop="removeButtonReply(buttonKey)">
              <UIcon name="i-heroicons-trash" class="w-4 h-4 mr-1" />
              删除
            </UButton>
          </div>
        </div>
        
        <div v-show="!isGroupCollapsed(`buttons_${buttonKey}`)" class="space-y-4">
          <div
            v-for="(module, moduleIndex) in button"
            :key="module.id"
            class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2 flex-1 cursor-pointer" @click="toggleModuleCollapse(`buttons_${buttonKey}_${moduleIndex}`)">
                <UIcon 
                  :name="isModuleCollapsed(`buttons_${buttonKey}_${moduleIndex}`) ? 'i-heroicons-chevron-right' : 'i-heroicons-chevron-down'" 
                  class="w-4 h-4 text-[#9ca3af] transition-transform"
                />
                <UBadge :color="(getModuleTypeColor(module.type))" variant="subtle" size="sm">
                  {{ getModuleTypeLabel(module.type) }}
                </UBadge>
                <span class="text-xs text-[#9ca3af]">顺序: {{ module.order }}</span>
              </div>
              <div class="flex gap-1" @click.stop>
                <UButton variant="ghost" size="xs" @click="moveModule(buttonKey, 'buttons', moduleIndex, -1)" :disabled="moduleIndex === 0">
                  <UIcon name="i-heroicons-arrow-up" class="w-3 h-3" />
                </UButton>
                <UButton variant="ghost" size="xs" @click="moveModule(buttonKey, 'buttons', moduleIndex, 1)" :disabled="moduleIndex === button.length - 1">
                  <UIcon name="i-heroicons-arrow-down" class="w-3 h-3" />
                </UButton>
                <UButton variant="ghost" size="xs" color="red" @click="removeModule(buttonKey, 'buttons', moduleIndex)">
                  <UIcon name="i-heroicons-trash" class="w-3 h-3" />
                </UButton>
              </div>
            </div>
            
            <!-- 模块内容编辑 -->
            <div v-show="!isModuleCollapsed(`buttons_${buttonKey}_${moduleIndex}`)" class="space-y-3">
              <!-- 图片路径 -->
              <div v-if="module.type.includes('image')">
                <label class="block text-sm font-medium text-white mb-2">图片文件名</label>
                <UInput
                  :model-value="module.image"
                  @update:model-value="updateModuleField(buttonKey, 'buttons', moduleIndex, 'image', $event)"
                  placeholder="例如: photo.jpg"
                />
              </div>
              
              <!-- 文案内容 -->
              <div v-if="module.type.includes('text') || module.type === 'text'">
                <label class="block text-sm font-medium text-white mb-2">文案内容</label>
                <UTextarea
                   :model-value="module.content"
                   @update:model-value="updateModuleField(buttonKey, 'buttons', moduleIndex, 'content', $event)"
                   placeholder="输入回复文案..."
                   :rows="3"
                 />
              </div>
              
              <!-- 内联按钮 -->
              <div v-if="module.type.includes('buttons')">
                <label class="block text-sm font-medium text-white mb-3">内联按钮配置</label>
                
                <!-- 按钮预览区域 -->
                <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4 mb-4">
                  <div class="text-xs text-[#9ca3af] mb-2">按钮预览（真实布局）</div>
                  <div class="space-y-2">
                    <div v-for="(row, rowIndex) in module.buttons" :key="rowIndex" class="flex gap-2">
                      <div
                        v-for="(button, buttonIndex) in row"
                        :key="buttonIndex"
                        class="flex-1 bg-[#2a2a2b] hover:bg-[#3a3a3b] border border-[#4a4a4b] rounded-lg px-3 py-2 text-center text-sm text-white cursor-pointer transition-colors"
                        @click="editButton(buttonKey, 'buttons', moduleIndex, rowIndex, buttonIndex)"
                      >
                        {{ button.text || '未设置' }}
                      </div>
                    </div>
                  </div>
                  <div class="flex gap-2 mt-3">
                    <UButton variant="outline" size="xs" @click="addButtonRow(buttonKey, 'buttons', moduleIndex)">
                      <UIcon name="i-heroicons-plus" class="w-3 h-3 mr-1" />
                      添加行
                    </UButton>
                    <UButton variant="outline" size="xs" @click="addButtonToLastRow(buttonKey, 'buttons', moduleIndex)" v-if="module.buttons.length > 0">
                      <UIcon name="i-heroicons-plus" class="w-3 h-3 mr-1" />
                      添加到最后一行
                    </UButton>
                  </div>
                </div>
                
                <!-- 按钮编辑区域 -->
                <div class="space-y-3">
                  <div v-for="(row, rowIndex) in module.buttons" :key="rowIndex" class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-3">
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-medium text-[#9ca3af]">第 {{ rowIndex + 1 }} 行 ({{ row.length }} 个按钮)</span>
                      <div class="flex gap-1">
                        <UButton variant="ghost" size="xs" @click="moveButtonRow(buttonKey, 'buttons', moduleIndex, rowIndex, -1)" :disabled="rowIndex === 0">
                          <UIcon name="i-heroicons-arrow-up" class="w-3 h-3" />
                        </UButton>
                        <UButton variant="ghost" size="xs" @click="moveButtonRow(buttonKey, 'buttons', moduleIndex, rowIndex, 1)" :disabled="rowIndex === module.buttons.length - 1">
                          <UIcon name="i-heroicons-arrow-down" class="w-3 h-3" />
                        </UButton>
                        <UButton variant="ghost" size="xs" color="red" @click="removeButtonRow(buttonKey, 'buttons', moduleIndex, rowIndex)">
                          <UIcon name="i-heroicons-trash" class="w-3 h-3" />
                        </UButton>
                      </div>
                    </div>
                    <div class="grid gap-2" :class="row.length === 1 ? 'grid-cols-1' : 'grid-cols-2'">
                      <div v-for="(button, buttonIndex) in row" :key="buttonIndex" class="space-y-2">
                        <div class="text-xs text-[#9ca3af]">按钮 {{ buttonIndex + 1 }}</div>
                        <UInput
                          :model-value="button.text"
                          @update:model-value="updateButtonText(buttonKey, 'buttons', moduleIndex, rowIndex, buttonIndex, $event)"
                          placeholder="按钮文字"
                          size="sm"
                        />
                        <UInput
                          :model-value="button.callback_data || button.url"
                          @update:model-value="updateButtonAction(buttonKey, 'buttons', moduleIndex, rowIndex, buttonIndex, $event)"
                          placeholder="callback_data 或 url"
                          size="sm"
                        />
                        <UButton variant="ghost" size="xs" color="red" @click="removeButton(buttonKey, 'buttons', moduleIndex, rowIndex, buttonIndex)" v-if="row.length > 1">
                          <UIcon name="i-heroicons-trash" class="w-3 h-3 mr-1" />
                          删除此按钮
                        </UButton>
                      </div>
                    </div>
                    <UButton variant="outline" size="xs" @click="addButtonToRow(buttonKey, 'buttons', moduleIndex, rowIndex)" class="mt-2" v-if="row.length < 2">
                      <UIcon name="i-heroicons-plus" class="w-3 h-3 mr-1" />
                      添加按钮到此行
                    </UButton>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加新模块的模态框 -->
    <UModal v-model="showAddModuleModal">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-white mb-4">添加新模块</h3>
        <div class="space-y-4">
          <USelect
            v-model="newModuleType"
            label="模块类型"
            :options="moduleTypeOptions"
          />
          <div class="flex justify-end gap-2">
            <UButton variant="outline" @click="showAddModuleModal = false">取消</UButton>
            <UButton color="primary" @click="confirmAddModule">添加</UButton>
          </div>
        </div>
      </div>
    </UModal>

    <!-- 添加新命令的模态框 -->
    <UModal v-model="showAddCommandModal">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-white mb-4">添加新命令</h3>
        <div class="space-y-4">
          <UInput
            v-model="newCommandName"
            label="命令名称"
            placeholder="例如: /help 或 查询余额"
            :rules="[value => !!value || '请输入命令名称']"
          />
          <div class="text-sm text-gray-400">
            <p>提示：</p>
            <ul class="list-disc list-inside mt-1 space-y-1">
              <li>命令可以以 / 开头（如 /help）</li>
              <li>也可以是普通文本（如 查询余额）</li>
              <li>如果命令已存在，将无法添加</li>
            </ul>
          </div>
          <div class="flex justify-end gap-2">
            <UButton variant="outline" @click="showAddCommandModal = false; newCommandName = ''">取消</UButton>
            <UButton color="primary" @click="confirmAddCommand">添加</UButton>
          </div>
        </div>
      </div>
    </UModal>

    <!-- 添加新按钮回复的模态框 -->
    <UModal v-model="showAddButtonModal">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-white mb-4">添加新按钮回复</h3>
        <div class="space-y-4">
          <UInput
            v-model="newButtonText"
            label="按钮文字"
            placeholder="例如: 🌟购买会员 或 查询余额"
            :rules="[value => !!value || '请输入按钮文字']"
          />
          <div class="text-sm text-gray-400">
            <p>提示：</p>
            <ul class="list-disc list-inside mt-1 space-y-1">
              <li>按钮文字应与机器人键盘上的按钮文字完全一致</li>
              <li>如果按钮已存在，将无法添加</li>
            </ul>
          </div>
          <div class="flex justify-end gap-2">
            <UButton variant="outline" @click="showAddButtonModal = false; newButtonText = ''">取消</UButton>
            <UButton color="primary" @click="confirmAddButtonReply">添加</UButton>
          </div>
        </div>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
// 页面元数据
definePageMeta({
  title: '关键词回复',
  middleware: ['auth', 'license']
})

// 类型定义
interface ModuleButton {
  text: string
  callback_data?: string
  url?: string
}

interface Module {
  id: string
  type: string
  content: string
  order: number
  image?: string
  buttons?: ModuleButton[][]
}

interface KeywordReplies {
  commands: Record<string, Module[]>
  buttons: Record<string, Module[]>
}

// 响应式数据
const activeTab = ref('commands')
const hasUnsavedChanges = ref(false)
const showAddModuleModal = ref(false)
const showAddCommandModal = ref(false)
const showAddButtonModal = ref(false)
const newModuleType = ref('text')
const newCommandName = ref('')
const newButtonText = ref('')
const pendingModuleKey = ref('')
const pendingModuleCategory = ref('')
// 模块折叠状态：使用字符串key来标识每个模块，格式: "category_key_moduleIndex"
const collapsedModules = ref<Set<string>>(new Set())
// 分组折叠状态：使用字符串key来标识每个关键词组，格式: "category_key"
const collapsedGroups = ref<Set<string>>(new Set())

// 分类标签
const tabs = computed(() => [
  { key: 'commands', label: `命令回复 (${Object.keys(keywordReplies.value.commands || {}).length}个)` },
  { key: 'buttons', label: `按钮回复 (${Object.keys(keywordReplies.value.buttons || {}).length}个)` }
])

// 模块类型选项
const moduleTypeOptions = [
  { label: '文案回复', value: 'text' },
  { label: '图片回复', value: 'image' },
  { label: '文案+内联按钮', value: 'text_buttons' },
  { label: '图片+文案+内联按钮', value: 'image_text_buttons' }
]

// 关键词回复数据
const keywordReplies = ref<KeywordReplies>({
  commands: {},
  buttons: {}
})

// 自动保存定时器
let autoSaveTimer: NodeJS.Timeout | null = null

// 加载关键词回复数据
const loadKeywordReplies = async () => {
  try {
    const response = await $fetch('/api/keyword-replies')
    if (response.success) {
      keywordReplies.value = response.data
    }
  } catch (error) {
    console.error('加载关键词回复失败:', error)
  }
}

// 保存关键词回复数据
const saveKeywordReplies = async () => {
  try {
    const response = await $fetch('/api/keyword-replies', {
      method: 'POST',
      body: {
        keywordReplies: keywordReplies.value
      }
    })
    if (response.success) {
      hasUnsavedChanges.value = false
      // 保存成功后重新加载数据，确保显示最新内容
      await loadKeywordReplies()
    } else {
      throw new Error(response.error || '保存失败')
    }
  } catch (error) {
    console.error('保存关键词回复失败:', error)
    throw error
  }
}

// 标记有未保存的更改
const markAsChanged = () => {
  hasUnsavedChanges.value = true
  
  // 清除之前的定时器
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
  
  // 3秒后自动保存
  autoSaveTimer = setTimeout(() => {
    saveKeywordReplies()
  }, 3000)
}

// 获取模块类型标签
const getModuleTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    text: '文案',
    image: '图片',
    text_buttons: '文案+按钮',
    image_text_buttons: '图片+文案+按钮'
  }
  return labels[type] || type
}

// 获取模块类型颜色
const getModuleTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    text: 'blue',
    image: 'green',
    text_buttons: 'purple',
    image_text_buttons: 'orange'
  }
  return colors[type] || 'gray'
}

// 添加命令
const confirmAddCommand = () => {
  const commandName = newCommandName.value.trim()
  if (!commandName) {
    return
  }
  
  // 检查命令是否已存在
  if (keywordReplies.value.commands[commandName]) {
    alert('该命令已存在，请使用其他名称')
    return
  }
  
  // 创建新命令，默认添加一个文本模块
  keywordReplies.value.commands[commandName] = [
    {
      id: `command_${Date.now()}`,
      type: 'text',
      content: '请输入回复内容',
      order: 1
    }
  ]
  
  markAsChanged()
  showAddCommandModal.value = false
  newCommandName.value = ''
}

// 删除命令
const removeCommand = (commandKey: string) => {
  if (confirm(`确定要删除命令 "${commandKey}" 吗？此操作不可恢复。`)) {
    delete keywordReplies.value.commands[commandKey]
    markAsChanged()
  }
}

// 添加按钮回复
const confirmAddButtonReply = () => {
  const buttonText = newButtonText.value.trim()
  if (!buttonText) {
    return
  }
  
  // 检查按钮是否已存在
  if (keywordReplies.value.buttons[buttonText]) {
    alert('该按钮回复已存在，请使用其他名称')
    return
  }
  
  // 创建新按钮回复，默认添加一个文本模块
  keywordReplies.value.buttons[buttonText] = [
    {
      id: `button_${Date.now()}`,
      type: 'text',
      content: '请输入回复内容',
      order: 1
    }
  ]
  
  markAsChanged()
  showAddButtonModal.value = false
  newButtonText.value = ''
}

// 删除按钮回复
const removeButtonReply = (buttonKey: string) => {
  if (confirm(`确定要删除按钮回复 "${buttonKey}" 吗？此操作不可恢复。`)) {
    delete keywordReplies.value.buttons[buttonKey]
    markAsChanged()
  }
}

// 添加模块
const addModule = (key: string, category: string) => {
  pendingModuleKey.value = key
  pendingModuleCategory.value = category
  showAddModuleModal.value = true
}

// 确认添加模块
const confirmAddModule = () => {
  const category = pendingModuleCategory.value as keyof KeywordReplies
  const key = pendingModuleKey.value
  
  if (!keywordReplies.value[category][key]) {
    keywordReplies.value[category][key] = []
  }
  
  const newModule: Module = {
    id: `module_${Date.now()}`,
    type: newModuleType.value,
    content: '',
    order: keywordReplies.value[category][key].length + 1
  }
  
  if (newModuleType.value.includes('image')) {
    newModule.image = ''
  }
  
  if (newModuleType.value.includes('buttons')) {
    newModule.buttons = [[{ text: '', callback_data: '' }]]
  }
  
  keywordReplies.value[category][key].push(newModule)
  markAsChanged()
  showAddModuleModal.value = false
}

// 移除模块
const removeModule = (key: string, category: string, index: number) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  categoryData[key].splice(index, 1)
  
  // 重新排序
  categoryData[key].forEach((module, i) => {
    module.order = i + 1
  })
  
  markAsChanged()
}

// 移动模块
const moveModule = (key: string, category: string, index: number, direction: number) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const modules = categoryData[key]
  const newIndex = index + direction
  
  if (newIndex >= 0 && newIndex < modules.length) {
    // 交换位置
    [modules[index], modules[newIndex]] = [modules[newIndex], modules[index]]
    
    // 重新排序
    modules.forEach((module, i) => {
      module.order = i + 1
    })
    
    markAsChanged()
  }
}

// 更新模块字段
const updateModuleField = (key: string, category: string, index: number, field: string, value: any) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][index]
  ;(module)[field] = value
  markAsChanged()
}

// 更新按钮文字
const updateButtonText = (key: string, category: string, moduleIndex: number, rowIndex: number, buttonIndex: number, text: string) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][moduleIndex]
  if (module.buttons && module.buttons[rowIndex] && module.buttons[rowIndex][buttonIndex]) {
    module.buttons[rowIndex][buttonIndex].text = text
    markAsChanged()
  }
}

// 更新按钮动作
const updateButtonAction = (key: string, category: string, moduleIndex: number, rowIndex: number, buttonIndex: number, action: string) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][moduleIndex]
  if (module.buttons && module.buttons[rowIndex] && module.buttons[rowIndex][buttonIndex]) {
    const button = module.buttons[rowIndex][buttonIndex]
    
    // 判断是URL还是callback_data
    if (action.startsWith('http')) {
      button.url = action
      delete button.callback_data
    } else {
      button.callback_data = action
      delete button.url
    }
    
    markAsChanged()
  }
}

// 添加按钮行
const addButtonRow = (key: string, category: string, moduleIndex: number) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][moduleIndex]
  if (module.buttons) {
    module.buttons.push([{ text: '', callback_data: '' }])
    markAsChanged()
  }
}

// 移除按钮行
const removeButtonRow = (key: string, category: string, moduleIndex: number, rowIndex: number) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][moduleIndex]
  if (module.buttons) {
    module.buttons.splice(rowIndex, 1)
    markAsChanged()
  }
}

// 添加按钮到最后一行
const addButtonToLastRow = (key: string, category: string, moduleIndex: number) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][moduleIndex]
  if (module.buttons && module.buttons.length > 0) {
    const lastRowIndex = module.buttons.length - 1
    const lastRow = module.buttons[lastRowIndex]
    if (lastRow.length < 2) {
      lastRow.push({ text: '', callback_data: '' })
      markAsChanged()
    }
  }
}

// 添加按钮到指定行
const addButtonToRow = (key: string, category: string, moduleIndex: number, rowIndex: number) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][moduleIndex]
  if (module.buttons && module.buttons[rowIndex] && module.buttons[rowIndex].length < 2) {
    module.buttons[rowIndex].push({ text: '', callback_data: '' })
    markAsChanged()
  }
}

// 移除单个按钮
const removeButton = (key: string, category: string, moduleIndex: number, rowIndex: number, buttonIndex: number) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][moduleIndex]
  if (module.buttons && module.buttons[rowIndex] && module.buttons[rowIndex].length > 1) {
    module.buttons[rowIndex].splice(buttonIndex, 1)
    markAsChanged()
  }
}

// 移动按钮行
const moveButtonRow = (key: string, category: string, moduleIndex: number, rowIndex: number, direction: number) => {
  const categoryData = keywordReplies.value[category as keyof KeywordReplies]
  const module = categoryData[key][moduleIndex]
  if (module.buttons) {
    const newIndex = rowIndex + direction
    if (newIndex >= 0 && newIndex < module.buttons.length) {
      [module.buttons[rowIndex], module.buttons[newIndex]] = [module.buttons[newIndex], module.buttons[rowIndex]]
      markAsChanged()
    }
  }
}

// 编辑按钮（点击预览按钮时的处理）
const editButton = (key: string, category: string, moduleIndex: number, rowIndex: number, buttonIndex: number) => {
  // 这里可以添加更多的编辑逻辑，比如聚焦到对应的输入框
  console.log('编辑按钮:', { key, category, moduleIndex, rowIndex, buttonIndex })
}

// 切换模块折叠状态
const toggleModuleCollapse = (moduleKey: string) => {
  if (collapsedModules.value.has(moduleKey)) {
    collapsedModules.value.delete(moduleKey)
  } else {
    collapsedModules.value.add(moduleKey)
  }
}

// 检查模块是否折叠
const isModuleCollapsed = (moduleKey: string) => {
  return collapsedModules.value.has(moduleKey)
}

// 切换分组折叠状态
const toggleGroupCollapse = (groupKey: string) => {
  if (collapsedGroups.value.has(groupKey)) {
    collapsedGroups.value.delete(groupKey)
  } else {
    collapsedGroups.value.add(groupKey)
  }
}

// 检查分组是否折叠
const isGroupCollapsed = (groupKey: string) => {
  return collapsedGroups.value.has(groupKey)
}

// 页面加载时获取数据
onMounted(() => {
  loadKeywordReplies()
})

// 页面卸载时清除定时器
onUnmounted(() => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
})
</script>