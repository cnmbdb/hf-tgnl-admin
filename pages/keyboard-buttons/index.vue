<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <div class="w-8 h-8 bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-rectangle-group" class="w-5 h-5 text-[#00dc82]" />
          </div>
          键盘按钮
        </h1>
        <p class="mt-1 text-sm text-[#9ca3af]">管理机器人的自定义键盘按钮布局</p>
      </div>
      <div class="flex gap-2">
        <UButton variant="outline" size="sm" @click="refreshKeyboards">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
          刷新
        </UButton>
        <UButton color="primary" size="sm" class="bg-[#00dc82] hover:bg-[#00dc82]/80" @click="showAddModal = true">
          <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-2" />
          创建键盘
        </UButton>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">总键盘数</p>
            <p class="text-2xl font-bold text-white">{{ stats.totalKeyboards }}</p>
          </div>
          <div class="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-rectangle-group" class="w-6 h-6 text-blue-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">活跃键盘</p>
            <p class="text-2xl font-bold text-white">{{ stats.activeKeyboards }}</p>
          </div>
          <div class="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-check-circle" class="w-6 h-6 text-green-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">总按钮数</p>
            <p class="text-2xl font-bold text-white">{{ stats.totalButtons }}</p>
          </div>
          <div class="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-squares-2x2" class="w-6 h-6 text-purple-400" />
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-[#9ca3af]">今日使用</p>
            <p class="text-2xl font-bold text-white">{{ stats.todayUsage }}</p>
          </div>
          <div class="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-cursor-arrow-rays" class="w-6 h-6 text-orange-400" />
          </div>
        </div>
      </div>
    </div>

    <!-- 键盘列表 -->
    <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg">
      <div class="p-4 border-b border-[#2a2a2b]">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white">键盘列表</h2>
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

      <!-- 键盘卡片网格布局 - 每个键盘占两列：左侧键盘预览，右侧功能链 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <template v-for="keyboard in filteredKeyboards" :key="keyboard.id">
          <!-- 左侧：键盘卡片 -->
          <div 
            class="bg-gradient-to-br from-[#1a1a1b] to-[#2a2a2b] border border-[#3a3a3b] rounded-xl p-6 hover:border-blue-400/50 hover:shadow-xl transition-all duration-300 group"
          >
            <!-- 卡片头部 -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-white mb-1 group-hover:text-blue-400 transition-colors">
                  {{ keyboard.name }}
                </h3>
                <p class="text-sm text-[#9ca3af] line-clamp-2">{{ keyboard.description }}</p>
              </div>
              <UBadge
                :color="keyboard.status === 'active' ? 'green' : 'red'"
                variant="subtle"
                size="sm"
                class="ml-2"
              >
                {{ keyboard.status === 'active' ? '活跃' : '禁用' }}
              </UBadge>
            </div>

            <!-- 键盘按钮预览 -->
            <div class="mb-4">
              <h4 class="text-sm font-medium text-[#9ca3af] mb-3">按钮布局</h4>
              <div class="space-y-2">
                <div
                  v-for="(row, rowIndex) in keyboard.layout"
                  :key="rowIndex"
                  class="grid grid-cols-2 gap-2 w-full"
                >
                  <button
                    v-for="(button, buttonIndex) in row"
                    :key="`${rowIndex}-${buttonIndex}`"
                    class="w-full px-3 py-2 bg-gradient-to-r from-[#2a2a2b] to-[#323234] border border-[#3a3a3b] rounded-lg text-sm text-white hover:border-blue-400/30 transition-all duration-200 min-h-[40px] text-center block"
                  >
                    {{ button.text }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 统计信息 -->
            <div class="grid grid-cols-2 gap-4 mb-4 p-3 bg-[#0c0c0d]/50 rounded-lg">
              <div class="text-center">
                <div class="text-lg font-semibold text-white">{{ keyboard.buttonCount }}</div>
                <div class="text-xs text-[#9ca3af]">按钮数量</div>
              </div>
              <div class="text-center">
                <div class="text-lg font-semibold text-white">{{ keyboard.usageCount }}</div>
                <div class="text-xs text-[#9ca3af]">使用次数</div>
              </div>
            </div>

            <!-- 创建时间 -->
            <div class="text-xs text-[#9ca3af] mb-4">
              创建于 {{ formatDate(keyboard.createdAt) }}
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-2">
              <UButton variant="soft" size="sm" class="flex-1" @click="editKeyboard(keyboard)">
                <UIcon name="i-heroicons-pencil" class="w-4 h-4 mr-1" />
                编辑
              </UButton>
              <UButton variant="soft" size="sm" @click="previewKeyboard(keyboard)">
                <UIcon name="i-heroicons-eye" class="w-4 h-4" />
              </UButton>
              <UButton 
                variant="soft" 
                size="sm" 
                :color="keyboard.status === 'active' ? 'red' : 'green'"
                @click="toggleKeyboardStatus(keyboard)"
              >
                <UIcon 
                  :name="keyboard.status === 'active' ? 'i-heroicons-pause' : 'i-heroicons-play'" 
                  class="w-4 h-4" 
                />
              </UButton>
              <UButton variant="soft" size="sm" color="red" @click="deleteKeyboard(keyboard)">
                <UIcon name="i-heroicons-trash" class="w-4 h-4" />
              </UButton>
            </div>
          </div>

          <!-- 右侧：功能链配置卡片 -->
          <div class="bg-gradient-to-br from-[#1a1a1b] to-[#2a2a2b] border border-[#3a3a3b] rounded-xl p-6">
            <div class="flex items-start justify-between mb-4">
              <div>
                <h3 class="text-lg font-semibold text-white mb-1">
                  功能链配置
                </h3>
                <p class="text-sm text-[#9ca3af]">
                  与左侧 {{ keyboard.name }} 的 9 个按钮一一对应（1-9）
                </p>
              </div>
            </div>

            <div class="space-y-2">
              <div
                v-for="chain in getButtonChains(keyboard)"
                :key="chain.index"
                class="flex items-center justify-between px-3 py-2 bg-[#0c0c0d]/60 border border-[#3a3a3b] rounded-lg cursor-pointer hover:border-blue-400/50 hover:bg-[#111827] transition-colors"
                @click="openWorkflow(chain)"
              >
                <div class="flex items-center gap-3">
                  <div class="w-6 h-6 rounded-full bg-blue-500/20 border border-blue-400/40 flex items-center justify-center text-xs font-semibold text-blue-300">
                    {{ chain.index }}
                  </div>
                  <div class="flex flex-col">
                    <span class="text-sm text-white">
                      {{ chain.label }}
                    </span>
                    <span v-if="chain.buttonText" class="text-xs text-[#6b7280]">
                      关联按钮: {{ chain.buttonText }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-[#9ca3af]">
                    功能链 {{ chain.index }}
                  </span>
                  <UIcon name="i-heroicons-arrow-right" class="w-4 h-4 text-[#6b7280]" />
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- 创建 / 编辑键盘模态框 -->
    <UModal v-model="showAddModal" :ui="{ width: 'sm:max-w-2xl' }">
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">
            {{ editingKeyboard ? '编辑键盘' : '创建键盘' }}
          </h3>
          <!-- 一键应用默认主键盘配置 -->
          <UButton
            variant="soft"
            size="xs"
            color="primary"
            class="bg-[#00dc82]/10 hover:bg-[#00dc82]/20 text-[#00dc82]"
            @click="applyDefaultKeyboardLayout"
          >
            <UIcon name="i-heroicons-sparkles" class="w-4 h-4 mr-1" />
            选择默认配置
          </UButton>
        </div>
        <div class="space-y-4">
          <UInput
            v-model="newKeyboard.name"
            label="键盘名称"
            placeholder="输入键盘名称"
          />

          <div>
            <label class="block text-sm font-medium text-white mb-2">键盘布局</label>
            <div class="space-y-3">
              <div v-for="(row, rowIndex) in newKeyboard.layout" :key="rowIndex" class="space-y-2">
                <div class="flex gap-2 items-center">
                  <div class="flex-1 flex gap-2">
                    <div v-for="(button, buttonIndex) in row" :key="buttonIndex" class="flex-1">
                      <UInput
                        v-model="button.text"
                        :placeholder="`按钮 ${buttonIndex + 1}`"
                        size="sm"
                      />
                    </div>
                  </div>
                  <UButton 
                    variant="ghost" 
                    size="xs" 
                    color="green"
                    @click="addButtonToRow(rowIndex)"
                    :disabled="row.length >= 4"
                  >
                    <UIcon name="i-heroicons-plus" class="w-4 h-4" />
                  </UButton>
                  <UButton 
                    variant="ghost" 
                    size="xs" 
                    color="red"
                    @click="removeRow(rowIndex)"
                    :disabled="newKeyboard.layout.length <= 1"
                  >
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                  </UButton>
                </div>
                <!-- 功能链选择器（折叠框） -->
                <div class="bg-[#0c0c0d]/50 border border-[#2a2a2b] rounded-lg p-3">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs text-[#9ca3af]">功能链关联</span>
                    <UIcon name="i-heroicons-chevron-down" class="w-4 h-4 text-[#9ca3af]" />
                  </div>
                  <div class="grid grid-cols-3 gap-2">
                    <div
                      v-for="(button, buttonIndex) in row"
                      :key="buttonIndex"
                      class="space-y-1"
                    >
                      <label class="text-xs text-[#9ca3af]">按钮 {{ buttonIndex + 1 }}</label>
                      <USelect
                        v-model="button.chain_id"
                        :options="chainOptions"
                        size="sm"
                        :placeholder="`选择功能链`"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-2 flex gap-2">
              <UButton 
                variant="outline" 
                size="sm" 
                @click="addRow"
                :disabled="newKeyboard.layout.length >= 8"
              >
                <UIcon name="i-heroicons-plus" class="w-4 h-4 mr-2" />
                添加行
              </UButton>
            </div>
          </div>
          
          <USelect
            v-model="newKeyboard.status"
            label="状态"
            :options="[
              { label: '活跃', value: 'active' },
              { label: '禁用', value: 'inactive' }
            ]"
          />
        </div>
        <div class="flex justify-end gap-2 mt-6">
          <UButton variant="outline" @click="showAddModal = false">取消</UButton>
          <UButton color="primary" @click="saveKeyboard">
            {{ editingKeyboard ? '保存' : '创建' }}
          </UButton>
        </div>
      </div>
    </UModal>

    <!-- 预览模态框 -->
    <UModal v-model="showPreviewModal">
      <div class="p-6">
        <h3 class="text-lg font-semibold text-white mb-4">键盘预览</h3>
        <div v-if="previewKeyboardData" class="space-y-2">
          <div v-for="(row, rowIndex) in previewKeyboardData.layout" :key="rowIndex" class="flex gap-2">
            <button
              v-for="(button, buttonIndex) in row"
              :key="buttonIndex"
              class="flex-1 px-3 py-2 bg-[#2a2a2b] border border-[#3a3a3b] rounded text-white hover:bg-[#3a3a3b] transition-colors"
            >
              {{ button.text }}
            </button>
          </div>
        </div>
        <div class="flex justify-end mt-6">
          <UButton @click="showPreviewModal = false">关闭</UButton>
        </div>
      </div>
    </UModal>

<!-- 功能链工作流详情模态框（可视化流程） -->
    <UModal v-model="showWorkflowModal" :ui="{ width: 'sm:max-w-3xl' }">
      <div class="p-6 space-y-6">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-white">
            功能链 {{ currentWorkflow?.index }}：{{ currentWorkflow?.label }}
          </h3>
          <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="closeWorkflowModal" />
        </div>

        <div v-if="currentWorkflow" class="space-y-4">
          <div class="text-xs text-[#9ca3af]">
            以下为该按钮在机器人中的处理流程，按执行顺序从上到下展示（类似 n8n 工作流节点）：
          </div>

          <!-- tree 模式：主线 + 分支链 -->
          <div v-if="currentWorkflow.mode === 'tree'" class="relative">
            <!-- 主线垂直连线 -->
            <div class="absolute left-6 top-0 bottom-0 border-l border-dashed border-[#374151]"></div>

            <div
              v-for="(step, idx) in currentWorkflow.tree.main"
              :key="step.id"
              class="relative pl-12 pb-8 last:pb-0"
            >
              <!-- 主线节点圆点 -->
              <div
                class="absolute left-3 top-2 w-6 h-6 rounded-full border border-blue-400 bg-[#111827] flex items-center justify-center text-xs font-semibold text-blue-300"
              >
                {{ idx + 1 }}
              </div>

              <!-- 主线节点卡片 -->
              <div class="bg-[#111827] border border-[#374151] rounded-lg p-3 shadow-sm">
                <div class="flex items-center justify-between mb-2">
                  <div class="text-sm font-semibold text-white">
                    {{ step.title }}
                  </div>
                  <UBadge color="blue" variant="soft" size="xs">
                    STEP {{ idx + 1 }}
                  </UBadge>
                </div>

                <!-- 一步内，用户 & 机器人对话：每条消息一个横向小胶囊标题 + 文案 -->
                <div class="space-y-3">
                  <div
                    v-for="(msg, mIdx) in step.messages"
                    :key="mIdx"
                    class="text-[11px] leading-relaxed"
                  >
                    <div class="mb-1">
                      <span
                        class="inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-[0.12em]"
                        :class="msg.role === 'user' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/40' : 'bg-sky-500/10 text-sky-300 border border-sky-500/40'"
                      >
                        {{ msg.role === 'user' ? '用户' : '机器人' }}
                      </span>
                    </div>
                    <p class="text-[#d1d5db] whitespace-pre-line">
                      {{ msg.text }}
                    </p>
                  </div>

                  <div
                    v-if="step.buttons && step.buttons.length"
                    class="flex flex-wrap gap-1 pt-1"
                  >
                    <span
                      v-for="btn in step.buttons"
                      :key="btn"
                      class="px-2 py-0.5 rounded-full bg-[#020617]/60 border border-[#1f2937] text-[10px] text-[#e5e7eb]"
                    >
                      {{ btn }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 分支容器 -->
              <div
                v-if="step.branches && step.branches.length"
                class="mt-4 pl-3"
              >
                <div class="text-[11px] text-[#9ca3af] mb-2">
                  内联按钮分支：
                </div>
                <div class="flex gap-4 items-start">
                  <div
                    v-for="branch in step.branches"
                    :key="branch.id"
                    class="relative flex-1"
                  >
                    <!-- 分支竖线 -->
                    <div class="absolute left-4 top-6 bottom-0 border-l border-dashed border-[#374151]"></div>

                    <!-- 分支标签 -->
                    <div class="inline-flex items-center gap-2 mb-3 pl-2">
                      <span
                        class="px-2 py-0.5 rounded-full bg-blue-500/15 text-[11px] text-blue-300 border border-blue-400/40"
                      >
                        {{ branch.label }}
                      </span>
                    </div>

                    <!-- 分支卡片链 -->
                    <div
                      v-for="(bStep, bIdx) in branch.steps"
                      :key="bStep.id"
                      class="relative pl-8 pb-5 last:pb-0"
                    >
                      <!-- 分支节点圆点 -->
                      <div
                        class="absolute left-1 top-2 w-5 h-5 rounded-full border border-indigo-400 bg-[#020617] flex items-center justify-center text-[10px] font-semibold text-indigo-200"
                      >
                        {{ bIdx + 1 }}
                      </div>

                      <div class="bg-[#020617] border border-[#283548] rounded-lg p-3 shadow-sm">
                        <div class="flex items-center justify-between mb-1">
                          <div class="text-xs font-semibold text-white">
                            {{ bStep.title }}
                          </div>
                        </div>

                        <div class="space-y-3">
                          <div
                            v-for="(msg, bmIdx) in bStep.messages"
                            :key="bmIdx"
                            class="text-[11px] leading-relaxed"
                          >
                            <div class="mb-1">
                              <span
                                class="inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold tracking-[0.12em]"
                                :class="msg.role === 'user' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/40' : 'bg-sky-500/10 text-sky-300 border border-sky-500/40'"
                              >
                                {{ msg.role === 'user' ? '用户' : '机器人' }}
                              </span>
                            </div>
                            <p class="text-[#d1d5db] whitespace-pre-line">
                              {{ msg.text }}
                            </p>
                          </div>

                          <div
                            v-if="bStep.buttons && bStep.buttons.length"
                            class="flex flex-wrap gap-1 pt-1"
                          >
                            <span
                              v-for="btn in bStep.buttons"
                              :key="btn"
                              class="px-2 py-0.5 rounded-full bg-[#020617]/60 border border-[#1f2937] text-[10px] text-[#e5e7eb]"
                            >
                              {{ btn }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- linear 模式：旧的纯主线展示 -->
          <div v-else class="relative">
            <!-- 垂直连线 -->
            <div class="absolute left-6 top-0 bottom-0 border-l border-dashed border-[#374151]"></div>

            <div
              v-for="(node, idx) in currentWorkflow.nodes"
              :key="idx"
              class="relative pl-12 pb-6 last:pb-0"
            >
              <!-- 节点圆点 -->
              <div
                class="absolute left-3 top-2 w-6 h-6 rounded-full border border-blue-400 bg-[#111827] flex items-center justify-center text-xs font-semibold text-blue-300"
              >
                {{ idx + 1 }}
              </div>

              <!-- 节点卡片 -->
              <div class="bg-[#111827] border border-[#374151] rounded-lg p-3 shadow-sm">
                <div class="flex items-center justify-between mb-1">
                  <div class="text-sm font-semibold text-white">
                    {{ node.title }}
                  </div>
                  <UBadge color="blue" variant="soft" size="xs">
                    STEP {{ idx + 1 }}
                  </UBadge>
                </div>
                <p class="text-xs text-[#d1d5db] leading-relaxed whitespace-pre-line">
                  {{ node.detail }}
                </p>

                <!-- 内联按钮分支（仅文案） -->
                <div v-if="node.buttons && node.buttons.length" class="mt-3 pt-3 border-t border-[#1f2933] space-y-2">
                  <div class="text-[11px] text-[#9ca3af]">
                    内联按钮说明：
                  </div>
                  <div class="space-y-2">
                    <div
                      v-for="btn in node.buttons"
                      :key="btn.label"
                      class="bg-[#020617]/40 border border-[#1f2937] rounded-md p-2"
                    >
                      <div class="inline-flex items-center gap-2 mb-1">
                        <span
                          class="px-2 py-0.5 rounded-full bg-blue-500/20 text-[11px] text-blue-300 border border-blue-400/40"
                        >
                          {{ btn.label }}
                        </span>
                      </div>
                      <p class="text-[11px] text-[#d1d5db] leading-snug whitespace-pre-line">
                        {{ btn.branch }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
// 页面元数据
definePageMeta({
  title: '键盘按钮',
  middleware: ['auth', 'license']
})

// 响应式数据
const showAddModal = ref(false)
const showPreviewModal = ref(false)
const showWorkflowModal = ref(false)
const searchQuery = ref('')
const statusFilter = ref('all')
const previewKeyboardData = ref<any>(null)
const editingKeyboard = ref<any | null>(null)

// 键盘表单（用于新建和编辑）
const newKeyboard = ref({
  name: '',
  description: '',
  layout: [
    [{ text: '按钮1', action: 'text', chain_id: 1 }]
  ],
  status: 'active'
})

// 一键应用默认主键盘配置
const applyDefaultKeyboardLayout = () => {
  // 深拷贝，避免直接引用常量
  newKeyboard.value.layout = DEFAULT_MAIN_KEYBOARD_LAYOUT.map((row: any[]) =>
    row.map((btn: any) => ({ ...btn }))
  )
  // 如果还没命名，默认命名为主键盘菜单
  if (!newKeyboard.value.name) {
    newKeyboard.value.name = '主键盘菜单'
  }
}

// 状态选项
const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '活跃', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

// 功能链固定标题映射（1-16）
// 1-9：主键盘九大功能
// 10-16：系统级功能链（无需绑定按钮，只用于文档说明）
const CHAIN_TITLES: Record<number, string> = {
  1: '笔数套餐',
  2: '预存扣费',
  3: 'USDT转TRX',
  4: '查交易',
  5: 'TRX转能量',
  6: '已监听地址',
  7: '开始/结束监听',
  8: '我要充值',
  9: '个人中心',
  10: '/start',
  11: '查询后台信息（初始）',
  12: '查询后台信息（已有API）',
  13: '订单能量下发成功',
  14: 'API余额充值成功',
  15: '检测小额金额触发',
  16: '一键克隆机器人'
}

// 功能链选项（用于下拉选择）—— 这里只提供 1-9，避免误把系统级功能链绑定到按钮
const chainOptions = Array.from({ length: 9 }, (_, i) => ({
  label: `${i + 1}. ${CHAIN_TITLES[i + 1]}`,
  value: i + 1
}))

// 默认主键盘布局（9 个按钮 + 对应功能链）
const DEFAULT_MAIN_KEYBOARD_LAYOUT = [
  [
    { text: '📦 笔数套餐', action: 'text', chain_id: 1 }
  ],
  [
    { text: '💰 预存扣费', action: 'text', chain_id: 2 },
    { text: '✅ USDT转TRX', action: 'text', chain_id: 3 }
  ],
  [
    { text: '🔍 查交易', action: 'text', chain_id: 4 },
    { text: '⚡ TRX转能量', action: 'text', chain_id: 5 }
  ],
  [
    { text: '📍 已监听地址', action: 'text', chain_id: 6 },
    { text: '🔔 开始/结束监听', action: 'text', chain_id: 7 }
  ],
  [
    { text: '💳 我要充值', action: 'text', chain_id: 8 },
    { text: '👤 个人中心', action: 'text', chain_id: 9 }
  ]
]

// 真实机器人回复键盘数据
const keyboards = ref([
  {
    id: 1,
    name: '主键盘菜单',
    description: '',
    type: 'reply',
    layout: [
      [
        { text: '📦 笔数套餐', action: 'text' }
      ],
      [
        { text: '💰 预存扣费', action: 'text' },
        { text: '✅ USDT转TRX', action: 'text' }
      ],
      [
        { text: '🔍 查交易', action: 'text' },
        { text: '⚡ TRX转能量', action: 'text' }
      ],
      [
        { text: '📍 已监听地址', action: 'text' },
        { text: '🔔 开始/结束监听', action: 'text' }
      ],
      [
        { text: '💳 我要充值', action: 'text' },
        { text: '👤 个人中心', action: 'text' }
      ]
    ],
    buttonCount: 9,
    status: 'active',
    usageCount: 0,
    createdAt: '2024-01-15T10:30:00Z'
  }
])

// 统计数据（根据当前键盘数据实时计算）
const stats = computed(() => {
  const list = keyboards.value || []
  const totalKeyboards = list.length
  const activeKeyboards = list.filter(k => k.status === 'active').length
  const totalButtons = list.reduce((sum, k) => sum + (k.buttonCount || 0), 0)
  const todayUsage = list.reduce((sum, k) => sum + (k.usageCount || 0), 0)

  return {
    totalKeyboards,
    activeKeyboards,
    totalButtons,
    todayUsage
  }
})

// 将键盘布局扁平化为 1-9 对应的功能链，并在下方追加 10-16 的系统级功能链说明
const getButtonChains = (keyboard: any) => {
  // 收集所有按钮及其 chain_id
  const buttons: Array<{ chain_id: number; text: string }> = []
  ;(keyboard.layout || []).forEach((row: any[]) => {
    row.forEach((btn: any) => {
      if (btn && typeof btn.text === 'string' && btn.text.trim()) {
        buttons.push({
          chain_id: btn.chain_id || 0, // 如果没有 chain_id，默认为 0
          text: btn.text.trim()
        })
      }
    })
  })

  // 生成功能链列表（固定 1-9，标题固定）
  const chains: { index: number; label: string; buttonText?: string; chainId?: number }[] = []
  for (let i = 1; i <= 9; i++) {
    // 查找关联到该功能链的按钮
    const associatedButton = buttons.find(btn => btn.chain_id === i)
    chains.push({
      index: i,
      label: CHAIN_TITLES[i] || `功能链 ${i}`, // 固定标题
      buttonText: associatedButton?.text, // 关联的按钮文案（可选显示）
      chainId: i
    })
  }

  // 追加 10-16 号系统级功能链（不关联具体按钮，只展示说明）
  for (let i = 10; i <= 16; i++) {
    chains.push({
      index: i,
      label: CHAIN_TITLES[i] || `功能链 ${i}`
    })
  }

  return chains
}

// 功能链工作流节点（从机器人逻辑抽象而来）
type WorkflowButtonBranch = { label: string; branch: string }
type WorkflowNode = { title: string; detail: string; buttons?: WorkflowButtonBranch[] }

// tree 模式：主线 + 分支链
type WorkflowRole = 'user' | 'bot'
type WorkflowMessage = {
  role: WorkflowRole
  text: string
  buttons?: string[]
}

type WorkflowBranchStep = {
  id: string
  title: string
  messages: WorkflowMessage[]
  buttons?: string[]
}

type WorkflowBranch = {
  id: string
  label: string
  steps: WorkflowBranchStep[]
}

type WorkflowMainStep = {
  id: string
  title: string
  messages: WorkflowMessage[]
  buttons?: string[]
  branches?: WorkflowBranch[]
}

type WorkflowTree = {
  main: WorkflowMainStep[]
}

type WorkflowDefinition =
  | {
      mode: 'tree'
      tree: WorkflowTree
    }
  | {
      mode: 'linear'
      nodes: WorkflowNode[]
    }

const workflowMap: Record<string, WorkflowDefinition> = {
  // 按钮 1：📦 笔数套餐 —— 使用 tree 模式（主线 + A/B 分支）
  // 兼容：有的地方按钮文字不带图标「笔数套餐」，有的地方带图标「📦 笔数套餐」
  '📦 笔数套餐': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'main-1',
          title: '收到指令 & 展示入口按钮',
          messages: [
            {
              role: 'user',
              text: '用户发送指令「📦 笔数套餐」。'
            },
            {
              role: 'bot',
              text: '机器人进入套餐管理流程，回复一条说明文案，并展示两个入口按钮供用户选择不同业务分支。',
              buttons: ['已有套餐', '添加套餐']
            }
          ],
          buttons: ['已有套餐', '添加套餐'],
          branches: [
            {
              id: 'branch-a',
              label: '已有套餐',
              steps: [
                {
                  id: 'a1',
                  title: 'A1 已有套餐列表',
                  messages: [
                    {
                      role: 'user',
                      text: '用户点击按钮「已有套餐」。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人查询数据库中该用户已配置的笔数套餐地址列表。\n' +
                        '如果存在，按地址 / 套餐类型 / 状态罗列出来，供用户查看当前激活 / 休眠的套餐，后续续费和关闭由其他入口处理。'
                    }
                  ]
                }
              ]
            },
            {
              id: 'branch-b',
              label: '添加套餐',
              steps: [
                {
                  id: 'b1',
                  title: 'B1 展示可选套餐按钮',
                  messages: [
                    {
                      role: 'user',
                      text: '用户点击按钮「添加套餐」。'
                    },
                    {
                      role: 'bot',
                      text: '机器人提示「请选择你要添加的笔数套餐类型」，并展示若干套餐按钮供选择。',
                      buttons: ['5笔 / 15T', '15笔 / 45T', '50笔 / 150T', '100笔 / 300T']
                    }
                  ],
                  buttons: ['5笔 / 15T', '15笔 / 45T', '50笔 / 150T', '100笔 / 300T']
                },
                {
                  id: 'b2',
                  title: 'B2 用户选择套餐',
                  messages: [
                    {
                      role: 'user',
                      text: '用户点击其中一个套餐按钮，例如「15笔 / 45T」。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人记录所选套餐类型（例如【15笔 / 45T】），并提示「请发送要绑定的 Tron 地址（TRC20 / TRX 地址）」。'
                    }
                  ]
                },
                {
                  id: 'b3',
                  title: 'B3 用户输入地址',
                  messages: [
                    {
                      role: 'user',
                      text: '用户发送要绑定的 Tron 地址，例如：TLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人校验地址格式无误后，回复确认文案，并提示「请选择支付方式」。同时展示支付方式按钮。',
                      buttons: ['使用余额', '立即支付']
                    }
                  ],
                  buttons: ['使用余额', '立即支付']
                },
                {
                  id: 'b4',
                  title: 'B4 用户选择支付方式',
                  messages: [
                    {
                      role: 'user',
                      text: '用户点击支付方式按钮（例如「立即支付」或「使用余额」）。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人根据选择的支付方式返回支付指引：\n' +
                        '· 使用余额：检查账户余额是否足够，足够则直接扣减并创建套餐订单；\n' +
                        '· 立即支付：返回收款地址或二维码，等待链上到账。'
                    }
                  ]
                },
                {
                  id: 'b5',
                  title: 'B5 支付完成 & 套餐生效',
                  messages: [
                    {
                      role: 'user',
                      text: '用户完成链上支付，或余额扣费成功，机器人监控到订单状态变为已支付。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人将该地址与所选套餐写入数据库，标记为「激活中」，并回复「套餐已生效」确认文案，提示后续如何查看与管理。'
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  },
  // 不带图标的别名
  '笔数套餐': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'main-1',
          title: '收到指令 & 展示入口按钮',
          messages: [
            {
              role: 'user',
              text: '用户发送指令「📦 笔数套餐」。'
            },
            {
              role: 'bot',
              text: '机器人进入套餐管理流程，回复一条说明文案，并展示两个入口按钮供用户选择不同业务分支。',
              buttons: ['已有套餐', '添加套餐']
            }
          ],
          buttons: ['已有套餐', '添加套餐'],
          branches: [
            {
              id: 'branch-a',
              label: '已有套餐',
              steps: [
                {
                  id: 'a1',
                  title: 'A1 已有套餐列表',
                  messages: [
                    {
                      role: 'user',
                      text: '用户点击按钮「已有套餐」。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人查询数据库中该用户已配置的笔数套餐地址列表。\n' +
                        '如果存在，按地址 / 套餐类型 / 状态罗列出来，供用户查看当前激活 / 休眠的套餐，后续续费和关闭由其他入口处理。'
                    }
                  ]
                }
              ]
            },
            {
              id: 'branch-b',
              label: '添加套餐',
              steps: [
                {
                  id: 'b1',
                  title: 'B1 展示可选套餐按钮',
                  messages: [
                    {
                      role: 'user',
                      text: '用户点击按钮「添加套餐」。'
                    },
                    {
                      role: 'bot',
                      text: '机器人提示「请选择你要添加的笔数套餐类型」，并展示若干套餐按钮供选择。',
                      buttons: ['5笔 / 15T', '15笔 / 45T', '50笔 / 150T', '100笔 / 300T']
                    }
                  ],
                  buttons: ['5笔 / 15T', '15笔 / 45T', '50笔 / 150T', '100笔 / 300T']
                },
                {
                  id: 'b2',
                  title: 'B2 用户选择套餐',
                  messages: [
                    {
                      role: 'user',
                      text: '用户点击其中一个套餐按钮，例如「15笔 / 45T」。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人记录所选套餐类型（例如【15笔 / 45T】），并提示「请发送要绑定的 Tron 地址（TRC20 / TRX 地址）」。'
                    }
                  ]
                },
                {
                  id: 'b3',
                  title: 'B3 用户输入地址',
                  messages: [
                    {
                      role: 'user',
                      text: '用户发送要绑定的 Tron 地址，例如：TLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人校验地址格式无误后，回复确认文案，并提示「请选择支付方式」。同时展示支付方式按钮。',
                      buttons: ['使用余额', '立即支付']
                    }
                  ],
                  buttons: ['使用余额', '立即支付']
                },
                {
                  id: 'b4',
                  title: 'B4 用户选择支付方式',
                  messages: [
                    {
                      role: 'user',
                      text: '用户点击支付方式按钮（例如「立即支付」或「使用余额」）。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人根据选择的支付方式返回支付指引：\n' +
                        '· 使用余额：检查账户余额是否足够，足够则直接扣减并创建套餐订单；\n' +
                        '· 立即支付：返回收款地址或二维码，等待链上到账。'
                    }
                  ]
                },
                {
                  id: 'b5',
                  title: 'B5 支付完成 & 套餐生效',
                  messages: [
                    {
                      role: 'user',
                      text: '用户完成链上支付，或余额扣费成功，机器人监控到订单状态变为已支付。'
                    },
                    {
                      role: 'bot',
                      text:
                        '机器人将该地址与所选套餐写入数据库，标记为「激活中」，并回复「套餐已生效」确认文案，提示后续如何查看与管理。'
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  },

  // 其他按钮（2-9）改为 tree 模式，统一用主线小卡片串起来
  '🛎 预存扣费': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'pre-1',
          title: '收到指令 & 查询余额',
          messages: [
            {
              role: 'user',
              text: '用户点击「🛎 预存扣费」。'
            },
            {
              role: 'bot',
              text:
                '机器人进入预存模式管理流程，通过数据库读取用户余额（transactions 表），判断是否 ≥ 10 TRX。'
            }
          ]
        },
        {
          id: 'pre-2',
          title: '余额充足：展示已配置地址',
          messages: [
            {
              role: 'bot',
              text:
                '当余额充足时，从本地「自动充.txt」中查找该用户已配置的自动充能地址，按地址列表展示，并在每条后面附带「绑定地址 / 删除地址」等操作按钮。'
            }
          ]
        },
        {
          id: 'pre-3',
          title: '地址管理操作',
          messages: [
            {
              role: 'user',
              text:
                '用户通过点击「绑定地址」按钮，或发送「开启地址 地址」/「停用地址 地址」等命令，来管理自动充能地址。'
            },
            {
              role: 'bot',
              text:
                '机器人根据用户操作，在配置中增加、启用、停用或删除对应地址，用于后续自动扣费充能任务。'
            }
          ]
        },
        {
          id: 'pre-4',
          title: '余额不足：提示充值',
          messages: [
            {
              role: 'bot',
              text:
                '若检测到余额 < 10 TRX，则不展示地址列表，而是提示「余额不足，无法开启预存扣费」。\n' +
                '同时给出若干充值金额按钮（50 / 100 / 200 / 500 等），引导用户先完成充值再回来开启预存扣费服务。'
            }
          ]
        }
      ]
    }
  },
  '✅ USDT转TRX': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'usdt-1',
          title: '收到指令 & 进入兑换流程',
          messages: [
            {
              role: 'user',
              text: '用户点击「✅ USDT转TRX」。'
            },
            {
              role: 'bot',
              text: '机器人进入汇率兑换流程，准备计算当前可兑换额度。'
            }
          ]
        },
        {
          id: 'usdt-2',
          title: '计算可兑额度',
          messages: [
            {
              role: 'bot',
              text:
                '机器人调用 gethuilv() 获取当前汇率，并查询控制地址余额，计算当前可兑换的 USDT 数量（保留两位小数）。'
            }
          ]
        },
        {
          id: 'usdt-3',
          title: '发送兑换信息',
          messages: [
            {
              role: 'bot',
              text:
                '机器人将可兑换的 USDT 数量、实时汇率、自动兑换规则等信息整理成一条说明消息发送给用户，\n' +
                '并附上接收 USDT 的 TRC20 地址（支持点击复制或长按复制）。'
            }
          ]
        },
        {
          id: 'usdt-4',
          title: '附加操作入口',
          messages: [
            {
              role: 'bot',
              text:
                '在同一条或后续消息中，机器人附带「加入群组」和「联系客服」两个按钮，方便用户加入社群或遇到问题时联系客服人工处理。'
            }
          ]
        }
      ]
    }
  },
  '⏰ 查交易': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'tx-1',
          title: '收到指令 & 发送使用说明',
          messages: [
            {
              role: 'user',
              text: '用户点击「⏰ 查交易」。'
            },
            {
              role: 'bot',
              text:
                '机器人回复使用说明，引导用户使用「查交易 地址」的命令格式，例如：「查交易 TEfbxrUw...」。'
            }
          ]
        },
        {
          id: 'tx-2',
          title: '解析命令',
          messages: [
            {
              role: 'user',
              text: '用户按提示发送「查交易 + 地址」的消息。'
            },
            {
              role: 'bot',
              text: '机器人从文本中解析出目标地址，并进行基本格式校验。'
            }
          ]
        },
        {
          id: 'tx-3',
          title: '查询链上记录',
          messages: [
            {
              role: 'bot',
              text:
                '机器人调用链上 API 查询该地址的最近交易记录，包括时间、金额、方向（转入 / 转出）等信息。'
            }
          ]
        },
        {
          id: 'tx-4',
          title: '返回结果',
          messages: [
            {
              role: 'bot',
              text:
                '机器人将整理好的交易明细以列表形式发送给用户，方便核对充值到账或历史转账记录；如无记录则返回相应提示。'
            }
          ]
        }
      ]
    }
  },
  '⚡ TRX转能量': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'energy-1',
          title: '收到指令 & 进入能量兑换流程',
          messages: [
            {
              role: 'user',
              text: '用户点击「⚡ TRX转能量」。'
            },
            {
              role: 'bot',
              text: '机器人进入能量兑换流程，准备读取本地配置。'
            }
          ]
        },
        {
          id: 'energy-2',
          title: '读取配置',
          messages: [
            {
              role: 'bot',
              text:
                '机器人读取「能量按钮.txt」等本地配置，判断当前是否配置了固定套餐按钮，还是仅提供联系客服入口。'
            }
          ]
        },
        {
          id: 'energy-3',
          title: '默认模式：展示联系客服入口',
          messages: [
            {
              role: 'bot',
              text:
                '如果没有配置自助套餐按钮，则机器人展示一个「🔋 联系客服」按钮，提示用户通过客服完成 TRX→能量兑换。'
            }
          ]
        },
        {
          id: 'energy-4',
          title: '自助兑换模式（可选）',
          messages: [
            {
              role: 'user',
              text: '当存在固定套餐按钮时，用户点击其中一个套餐按钮。'
            },
            {
              role: 'bot',
              text:
                '机器人按照预设规则从用户余额或指定地址扣除相应 TRX，完成能量发放，并在后台记录本次交易（用于统计和排错）。'
            }
          ]
        }
      ]
    }
  },
  '📢 已监听地址': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'watch-1',
          title: '收到指令 & 读取监听文件',
          messages: [
            {
              role: 'user',
              text: '用户点击「📢 已监听地址」。'
            },
            {
              role: 'bot',
              text:
                '机器人从本地「监听.txt」中读取所有已配置的监听地址记录。'
            }
          ]
        },
        {
          id: 'watch-2',
          title: '过滤当前用户的地址',
          messages: [
            {
              role: 'bot',
              text:
                '机器人按 chat_id 过滤文件中的行，只保留属于当前用户的所有监听地址。'
            }
          ]
        },
        {
          id: 'watch-3',
          title: '展示地址列表或无数据提示',
          messages: [
            {
              role: 'bot',
              text:
                '如果存在监听地址，则逐行展示地址（通常用 Markdown 反引号包裹，方便复制）。\n' +
                '如果没有任何记录，则回复「此账户无监听地址」的提示文案。'
            }
          ]
        }
      ]
    }
  },
  '🔔 开始/结束监听': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'listen-1',
          title: '收到指令 & 发送操作说明',
          messages: [
            {
              role: 'user',
              text: '用户点击「🔔 开始/结束监听」。'
            },
            {
              role: 'bot',
              text:
                '机器人发送操作说明，介绍如何使用「开始监听 地址」和「结束监听 地址」两类命令。'
            }
          ]
        },
        {
          id: 'listen-2',
          title: '开始监听',
          messages: [
            {
              role: 'user',
              text: '用户发送「开始监听 地址」指令。'
            },
            {
              role: 'bot',
              text:
                '机器人校验地址格式无误后，将该地址写入监听配置文件或数据库，后续会监控该地址的链上交易。'
            }
          ]
        },
        {
          id: 'listen-3',
          title: '结束监听',
          messages: [
            {
              role: 'user',
              text: '用户发送「结束监听 地址」指令。'
            },
            {
              role: 'bot',
              text:
                '机器人从监听列表中移除对应地址，并停止对该地址后续新交易的监控。'
            }
          ]
        }
      ]
    }
  },
  '💳 我要充值': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'recharge-1',
          title: '收到指令 & 进入充值流程',
          messages: [
            {
              role: 'user',
              text: '用户点击「💳 我要充值」。'
            },
            {
              role: 'bot',
              text: '机器人进入充值流程，准备发送充值须知。'
            }
          ]
        },
        {
          id: 'recharge-2',
          title: '展示充值说明',
          messages: [
            {
              role: 'bot',
              text:
                '机器人发送充值须知，包括：最小充值金额、仅支持 TRX / TRC20、不要使用交易所直接充值等安全提示。'
            }
          ]
        },
        {
          id: 'recharge-3',
          title: '提供收款地址',
          messages: [
            {
              role: 'bot',
              text:
                '机器人提供项目的收款地址（支持点击复制），用户向该地址转入 TRX 或 TRC20 资产。'
            }
          ]
        },
        {
          id: 'recharge-4',
          title: '监听入账并更新余额',
          messages: [
            {
              role: 'bot',
              text:
                '后台服务或机器人进程监听该收款地址的入账交易，将充值记录写入订单表和余额表，并更新用户账户余额，然后通过消息通知用户充值结果。'
            }
          ]
        }
      ]
    }
  },
  '👤 个人中心': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'me-1',
          title: '收到指令 & 查询账户信息',
          messages: [
            {
              role: 'user',
              text: '用户点击「👤 个人中心」。'
            },
            {
              role: 'bot',
              text:
                '机器人根据 chat_id 查询数据库中的账户信息，准备生成账户概况。'
            }
          ]
        },
        {
          id: 'me-2',
          title: '读取账户信息',
          messages: [
            {
              role: 'bot',
              text:
                '从数据库中读取当前余额、已购买的笔数套餐、预存扣费状态、最近一次交易时间等字段。'
            }
          ]
        },
        {
          id: 'me-3',
          title: '展示账户概况',
          messages: [
            {
              role: 'bot',
              text:
                '机器人将账户摘要信息整理成一条或多条消息发送给用户，作为后续操作（开启套餐、充值、查看记录等）的总入口。'
            }
          ]
        }
      ]
    }
  },

  // 10 `/start`：机器人初始化 & 注册
  '/start': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'start-1',
          title: '收到 /start 指令',
          messages: [
            {
              role: 'user',
              text: '用户在私聊中发送 `/start` 指令，或首次点击机器人对话框。'
            },
            {
              role: 'bot',
              text:
                '机器人通过 handle_start_command 调用前端 API `/api/bot-register-user`，' +
                '以 chat_id / username / 昵称 为参数，在后台创建或更新用户记录。'
            }
          ]
        },
        {
          id: 'start-2',
          title: '发送欢迎语 & 主键盘',
          messages: [
            {
              role: 'bot',
              text:
                '注册成功后，机器人发送欢迎文本，并附带主键盘菜单（当前配置的 1–9 号功能按钮），作为后续所有操作的入口。'
            }
          ]
        }
      ]
    }
  },

  // 11 查询后台信息（初始）：自动创建能量池 API 账号
  '查询后台信息（初始）': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'admin-1',
          title: '收到「查询后台信息」命令',
          messages: [
            {
              role: 'user',
              text: '管理员在与机器人的私聊中发送「查询后台信息」。'
            },
            {
              role: 'bot',
              text:
                '机器人首先校验 chat_id 是否为管理员 ID，不是则提示「无权限」。' +
                '只有管理员才能继续后续步骤。'
            }
          ]
        },
        {
          id: 'admin-2',
          title: '检测能量池 API 账号是否已绑定',
          messages: [
            {
              role: 'bot',
              text:
                '当检测到 config.txt 中 username / password 为空时，机器人调用能量池系统的 `/api/api-users` 接口，' +
                '自动创建一个新的 API 账号，并将用户名和密码写回 config.txt，然后触发 reload_config() 重新加载配置。'
            }
          ]
        },
        {
          id: 'admin-3',
          title: '发送新建账号信息',
          messages: [
            {
              role: 'bot',
              text:
                '账号创建成功后，机器人通过私信把「API 用户名 / 密码 / 能量池地址」发送给管理员，' +
                '并提示该账号已经写入配置文件，无需重启机器人即可生效。'
            }
          ]
        }
      ]
    }
  },

  // 12 查询后台信息（已有API）：查询余额 & 同步配置
  '查询后台信息（已有API）': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'admin2-1',
          title: '查询能量池 API 账户信息',
          messages: [
            {
              role: 'user',
              text: '管理员在已经绑定 API 账号的前提下，再次发送「查询后台信息」。'
            },
            {
              role: 'bot',
              text:
                '机器人使用 username / password 和 bot_username 调用能量池接口 `/v1/get_api_user_info`，' +
                '获取当前 API 余额、日限额、已用额度等信息。'
            }
          ]
        },
        {
          id: 'admin2-2',
          title: '展示后台信息 & 提供充值入口',
          messages: [
            {
              role: 'bot',
              text:
                '机器人将接口返回的信息整理成多行文本回复给管理员，并附带一个「给API账号余额充值」按钮，' +
                '后续点击该按钮会进入 API 余额充值流程。'
            }
          ]
        },
        {
          id: 'admin2-3',
          title: '同步机器人配置到能量池系统',
          messages: [
            {
              role: 'bot',
              text:
                '同时，机器人会读取本地 config.txt（包含 bot_notify_url 等配置），' +
                '并通过 `/api/bots/config` 接口将当前机器人配置同步到能量池系统，' +
                '用于后续回调及展示。'
            }
          ]
        }
      ]
    }
  },

  // 13 订单能量下发成功：能量订单支付成功后的主流程
  '订单能量下发成功': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'order-1',
          title: '检测到订单支付成功',
          messages: [
            {
              role: 'bot',
              text:
                '机器人或能量池后台检测到某笔能量订单支付成功（包括余额支付和 TRX 支付两种），' +
                '准备触发能量下发流程。'
            }
          ]
        },
        {
          id: 'order-2',
          title: '调用能量下发接口',
          messages: [
            {
              role: 'bot',
              text:
                '机器人根据订单类型调用能量池的能量下发接口（例如 energy_tran2），' +
                '将指定数量的能量委托到目标地址，并在本地记录交易哈希和下发结果。'
            }
          ]
        },
        {
          id: 'order-3',
          title: '更新订单状态 & 通知用户/管理员',
          messages: [
            {
              role: 'bot',
              text:
                '能量下发成功后，机器人更新订单状态为「已完成 / 已激活」，' +
                '向用户发送成功提醒（包含套餐信息、目标地址等），并向管理员发送一条简要通知，便于运营侧统计和排错。'
            }
          ]
        }
      ]
    }
  },

  // 14 API 余额充值成功：能量池 API 账户入账通知
  'API余额充值成功': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'api-1',
          title: '检测到 API 充值成功',
          messages: [
            {
              role: 'bot',
              text:
                '当能量池系统检测到某笔 API 余额充值订单支付成功时，会回调机器人或由机器人轮询订单状态，' +
                '确认本次充值金额与订单信息。'
            }
          ]
        },
        {
          id: 'api-2',
          title: '更新 API 余额',
          messages: [
            {
              role: 'bot',
              text:
                '机器人根据回调数据更新本地记录中的 API 余额（或从能量池重新拉取最新余额），' +
                '用于后续展示和风控判断。'
            }
          ]
        },
        {
          id: 'api-3',
          title: '通知管理员充值结果',
          messages: [
            {
              role: 'bot',
              text:
                '机器人向管理员发送「API 余额充值成功」提示，包含充值金额、订单号、当前最新余额等信息，' +
                '便于确认本次充值是否到帐。'
            }
          ]
        }
      ]
    }
  },

  // 15 检测小额金额触发：用于风控 / 监控的小额收款告警
  '检测小额金额触发': {
    mode: 'tree',
    tree: {
      main: [
        {
          id: 'small-1',
          title: '监听链上交易',
          messages: [
            {
              role: 'bot',
              text:
                '机器人在扫描 Tron 区块或处理回调时，检测到一笔金额处于预设“小额阈值范围”内的转账，' +
                '将该交易标记为「小额触发候选」。'
            }
          ]
        },
        {
          id: 'small-2',
          title: '匹配订单或地址标签',
          messages: [
            {
              role: 'bot',
              text:
                '机器人尝试将这笔小额转账与已有订单、监控地址或测试地址进行匹配，' +
                '判断其是否属于测试转账、找零、恶意刷单等场景。'
            }
          ]
        },
        {
          id: 'small-3',
          title: '告警与记录',
          messages: [
            {
              role: 'bot',
              text:
                '当判断为可疑或需要关注的小额交易时，机器人向管理员发送告警消息（包含地址、金额、时间等），' +
                '并在日志中记录，便于后续追踪和调整风控规则。'
            }
          ]
        }
      ]
    }
  },

  // 16 一键克隆机器人：预留功能链（尚未实现）
  '一键克隆机器人': {
    mode: 'linear',
    nodes: [
      {
        title: '预留功能',
        detail:
          '该功能链用于未来的一键克隆 / 复制机器人配置功能，目前仅作为占位符，' +
          '尚未在机器人代码中实现具体逻辑。'
      }
    ]
  }
}

// 兼容：功能链标题有“带图标”和“纯文字”两种写法
// 左侧卡片用的是纯文字（例如「预存扣费」），按钮本身通常带图标（例如「💰 预存扣费」或「🛎 预存扣费」）
workflowMap['预存扣费'] = workflowMap['🛎 预存扣费']
workflowMap['USDT转TRX'] = workflowMap['✅ USDT转TRX']
workflowMap['查交易'] = workflowMap['⏰ 查交易']
workflowMap['TRX转能量'] = workflowMap['⚡ TRX转能量']
workflowMap['已监听地址'] = workflowMap['📢 已监听地址']
workflowMap['开始/结束监听'] = workflowMap['🔔 开始/结束监听']
workflowMap['我要充值'] = workflowMap['💳 我要充值']
workflowMap['个人中心'] = workflowMap['👤 个人中心']

const currentWorkflow = ref<
  | {
      index: number
      label: string
      mode: WorkflowDefinition['mode']
      nodes?: WorkflowNode[]
      tree?: WorkflowTree
    }
  | null
>(null)

const openWorkflow = (chain: { index: number; label: string }) => {
  const def = workflowMap[chain.label]

  if (!def) {
    currentWorkflow.value = {
      index: chain.index,
      label: chain.label,
      mode: 'linear',
      nodes: [
        {
          title: '未配置',
          detail: '该功能链暂未配置详细工作流，请查看机器人代码或联系开发者补充文档。'
        }
      ]
    }
    showWorkflowModal.value = true
    return
  }

  currentWorkflow.value = {
    index: chain.index,
    label: chain.label,
    mode: def.mode,
    nodes: def.mode === 'linear' ? def.nodes : undefined,
    tree: def.mode === 'tree' ? def.tree : undefined
  }
  showWorkflowModal.value = true
}

const closeWorkflowModal = () => {
  showWorkflowModal.value = false
  currentWorkflow.value = null
}

// 计算属性
const filteredKeyboards = computed(() => {
  let filtered = keyboards.value

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

const refreshKeyboards = () => {
  console.log('刷新键盘列表')
}

const addRow = () => {
  newKeyboard.value.layout.push([{ text: '', action: 'text' }])
}

const removeRow = (index: number) => {
  newKeyboard.value.layout.splice(index, 1)
}

const addButtonToRow = (rowIndex: number) => {
  // 计算当前按钮的默认 chain_id（按顺序 1-9）
  let buttonCount = 0
  newKeyboard.value.layout.forEach((row: any[]) => {
    row.forEach(() => buttonCount++)
  })
  const defaultChainId = Math.min(buttonCount + 1, 9) // 最多 9 个按钮
  newKeyboard.value.layout[rowIndex].push({ 
    text: '', 
    action: 'text',
    chain_id: defaultChainId
  })
}

const saveKeyboard = async () => {
  if (!newKeyboard.value.name) {
    return
  }

  // 清理空按钮 / 空行
  const normalizedLayout = newKeyboard.value.layout
    .map(row => row.filter(button => button.text.trim() !== ''))
    .filter(row => row.length > 0)

  const buttonCount = normalizedLayout.reduce((total, row) => total + row.length, 0)

  // 判断是否是主键盘菜单（需要同步到机器人）
  const isMainKeyboard = editingKeyboard.value?.id === 1 || editingKeyboard.value?.name === '主键盘菜单' || newKeyboard.value.name === '主键盘菜单'

  if (editingKeyboard.value) {
    // 编辑模式：更新现有键盘
    editingKeyboard.value.name = newKeyboard.value.name
    editingKeyboard.value.description = newKeyboard.value.description
    editingKeyboard.value.layout = normalizedLayout
    editingKeyboard.value.buttonCount = buttonCount
    editingKeyboard.value.status = newKeyboard.value.status
    // 不改 usageCount / createdAt
  } else {
    // 新建模式
    const keyboard = {
      id: Date.now(),
      name: newKeyboard.value.name,
      description: newKeyboard.value.description,
      type: 'reply',
      layout: normalizedLayout,
      buttonCount,
      status: newKeyboard.value.status,
      usageCount: 0,
      createdAt: new Date().toISOString()
    }
    keyboards.value.unshift(keyboard)
  }

  // 如果是主键盘菜单，同步到机器人配置
  if (isMainKeyboard) {
    try {
      const response: any = await $fetch('/api/keyboard-layout', {
        method: 'PUT',
        body: {
          layout: normalizedLayout
        }
      })
      if (response.success) {
        // 可以显示成功提示
        console.log('键盘布局已同步到机器人配置')
      } else {
        console.error('同步键盘布局失败:', response.error)
      }
    } catch (error) {
      console.error('同步键盘布局失败:', error)
    }
  }

  // 重置表单 & 状态
  newKeyboard.value = {
    name: '',
    description: '',
    layout: [
      [{ text: '按钮1', action: 'text', chain_id: 1 }]
    ],
    status: 'active'
  }
  editingKeyboard.value = null
  showAddModal.value = false
}

const editKeyboard = (keyboard: any) => {
  editingKeyboard.value = keyboard
  // 将当前键盘数据填充到表单
  newKeyboard.value = {
    name: keyboard.name,
    description: keyboard.description,
    layout: (keyboard.layout || []).map((row: any[], rowIndex: number) =>
      row.map((btn: any, btnIndex: number) => ({
        text: btn.text || '',
        action: btn.action || 'text',
        chain_id: btn.chain_id || (rowIndex * 2 + btnIndex + 1) // 如果没有 chain_id，按位置计算默认值
      }))
    ),
    status: keyboard.status || 'active'
  }
  showAddModal.value = true
}

const previewKeyboard = (keyboard: any) => {
  previewKeyboardData.value = keyboard
  showPreviewModal.value = true
}

const toggleKeyboardStatus = (keyboard: any) => {
  keyboard.status = keyboard.status === 'active' ? 'inactive' : 'active'
}

const deleteKeyboard = (keyboard: any) => {
  const index = keyboards.value.findIndex(k => k.id === keyboard.id)
  if (index > -1) {
    keyboards.value.splice(index, 1)
  }
}

// 页面加载时，从机器人配置读取主键盘菜单布局
onMounted(async () => {
  try {
    const response: any = await $fetch('/api/keyboard-layout')
    if (response.success && response.data && response.data.layout) {
      const { layout } = response.data
      // 找到主键盘菜单并更新布局
      const mainKeyboard = keyboards.value.find(k => k.id === 1 || k.name === '主键盘菜单')
      if (mainKeyboard && layout && Array.isArray(layout) && layout.length > 0) {
        // 将配置格式转换为前端格式（包含 chain_id）
        const newLayout = layout.map((row: any[]) =>
          row.map((btn: any) => ({
            text: btn.label || '',
            action: 'text',
            chain_id: btn.chain_id || 0 // 从配置读取 chain_id
          }))
        )
        const buttonCount = newLayout.reduce((total: number, row: any[]) => total + row.length, 0)
        
        // 只有当按钮数量大于0时才更新（避免覆盖为0）
        if (buttonCount > 0) {
          mainKeyboard.layout = newLayout
          mainKeyboard.buttonCount = buttonCount
        } else {
          console.warn('从API读取的键盘布局按钮数量为0，保留默认布局')
        }
      }
    } else {
      console.warn('API返回数据无效，保留默认键盘布局')
    }
  } catch (error) {
    console.error('加载键盘布局失败:', error)
    // API调用失败时，保留默认布局，不做任何修改
  }
})
</script>