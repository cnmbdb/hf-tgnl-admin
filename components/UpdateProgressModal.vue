<template>
  <UModal v-model="isOpen" :ui="{ width: 'sm:max-w-2xl' }" :prevent-close="isProcessing">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-white">系统更新</h3>
          <UButton 
            v-if="!isProcessing && !hasError" 
            color="gray" 
            variant="ghost" 
            icon="i-heroicons-x-mark-20-solid" 
            @click="closeModal"
          />
        </div>
      </template>

      <div class="space-y-6">
        <!-- 更新步骤列表 -->
        <div class="space-y-4">
          <div 
            v-for="(step, index) in steps" 
            :key="step.id"
            class="flex items-center p-4 rounded-lg border transition-all duration-300"
            :class="getStepClasses(step, index)"
          >
            <!-- 步骤图标 -->
            <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mr-4">
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center"
                :class="getStepIconClasses(step)"
              >
                <UIcon 
                  v-if="step.status === 'completed'" 
                  name="i-heroicons-check" 
                  class="w-5 h-5 text-white" 
                />
                <UIcon 
                  v-else-if="step.status === 'error'" 
                  name="i-heroicons-x-mark" 
                  class="w-5 h-5 text-white" 
                />
                <UIcon 
                  v-else-if="step.status === 'in_progress'" 
                  name="i-heroicons-arrow-path" 
                  class="w-5 h-5 text-white animate-spin" 
                />
                <span v-else class="text-sm font-medium text-gray-400">{{ index + 1 }}</span>
              </div>
            </div>

            <!-- 步骤内容 -->
            <div class="flex-1">
              <div class="flex items-center justify-between">
                <h4 class="font-medium" :class="getStepTitleClasses(step)">
                  {{ step.title }}
                </h4>
                <UBadge 
                  :color="getStepBadgeColor(step)" 
                  variant="subtle" 
                  size="xs"
                >
                  {{ getStepStatusText(step) }}
                </UBadge>
              </div>
              <p class="text-sm text-gray-400 mt-1">{{ step.description }}</p>
              
              <!-- 进度条 -->
              <div v-if="step.status === 'in_progress' && (step.progress !== undefined && step.progress !== null)" class="mt-3">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-xs text-gray-400">进度</span>
                  <span class="text-xs text-gray-300 font-medium">{{ step.progress || 0 }}%</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    class="bg-gradient-to-r from-green-500 to-green-400 h-2 rounded-full transition-all duration-500 ease-out"
                    :style="{ width: `${step.progress || 0}%` }"
                  ></div>
                </div>
              </div>
              
              <!-- 处理中状态指示 -->
              <div v-if="step.status === 'in_progress' && (step.progress === undefined || step.progress === null)" class="mt-3">
                <div class="flex items-center text-xs text-blue-400">
                  <UIcon name="i-heroicons-arrow-path" class="w-3 h-3 mr-1 animate-spin" />
                  正在处理...
                </div>
              </div>
              
              <!-- 错误信息 -->
              <div v-if="step.status === 'error' && step.error" class="mt-3 p-3 bg-red-900/20 border border-red-800 rounded-lg">
                <div class="text-sm text-red-400">{{ step.error }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 当前步骤详细信息 -->
        <div v-if="currentStep" class="p-4 bg-gray-800 rounded-lg">
          <div class="flex items-center mb-3">
            <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-blue-400 mr-2" />
            <span class="font-medium text-white">当前步骤</span>
          </div>
          <div class="text-sm text-gray-300">{{ currentStep.title }}</div>
          <div class="text-xs text-gray-400 mt-1">{{ currentStep.description }}</div>
          
          <!-- 实时日志 -->
          <div v-if="currentStep.logs && currentStep.logs.length > 0" class="mt-3">
            <div class="text-xs text-gray-400 mb-2">实时日志:</div>
            <div class="bg-black rounded p-2 max-h-32 overflow-y-auto">
              <div 
                v-for="(log, index) in currentStep.logs" 
                :key="index"
                class="text-xs font-mono"
                :class="log.type === 'error' ? 'text-red-400' : log.type === 'warning' ? 'text-yellow-400' : 'text-green-400'"
              >
                [{{ formatTime(log.timestamp) }}] {{ log.message }}
              </div>
            </div>
          </div>
        </div>

        <!-- 全局错误信息 -->
        <div v-if="hasError && errorMessage" class="p-4 bg-red-900/20 border border-red-800 rounded-lg">
          <div class="flex items-center mb-2">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-red-400 mr-2" />
            <span class="font-medium text-red-400">更新失败</span>
          </div>
          <div class="text-sm text-red-300">{{ errorMessage }}</div>
        </div>

        <!-- 成功信息 -->
        <div v-if="isCompleted" class="p-4 bg-green-900/20 border border-green-800 rounded-lg">
          <div class="flex items-center mb-2">
            <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-green-400 mr-2" />
            <span class="font-medium text-green-400">更新完成</span>
          </div>
          <div class="text-sm text-green-300">系统已成功更新到最新版本</div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-between items-center">
          <div class="text-sm text-gray-400">
            <span v-if="sessionId">会话ID: {{ sessionId }}</span>
          </div>
          
          <div class="flex space-x-3">
            <!-- 取消按钮 -->
            <UButton 
              v-if="!isCompleted && !isProcessing"
              variant="outline" 
              color="gray"
              @click="cancelUpdate"
            >
              取消更新
            </UButton>
            
            <!-- 重试按钮 -->
            <UButton 
              v-if="shouldShowRetry && canRetry"
              color="orange"
              @click="retryStep"
            >
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
              重试
            </UButton>
            
            <!-- 下一步按钮 -->
            <UButton 
              v-if="canProceed && !isCompleted"
              :color="currentStep?.status === 'error' ? 'orange' : 'green'"
              @click="nextStep"
              :loading="isProcessing"
            >
              <UIcon 
                :name="currentStep?.status === 'error' ? 'i-heroicons-arrow-path' : 'i-heroicons-arrow-right'" 
                class="w-4 h-4 mr-2" 
              />
              {{ getNextStepText() }}
            </UButton>
            
            <!-- 完成按钮 -->
            <UButton 
              v-if="isCompleted"
              color="green"
              @click="finishUpdate"
            >
              <UIcon name="i-heroicons-check" class="w-4 h-4 mr-2" />
              完成
            </UButton>
            
            <!-- 关闭按钮 -->
            <UButton 
              v-if="!isProcessing && !hasError && !canProceed"
              variant="outline"
              @click="closeModal"
            >
              关闭
            </UButton>
          </div>
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  steps: {
    type: Array,
    default: () => []
  },
  currentStepId: {
    type: String,
    default: ''
  },
  sessionId: {
    type: String,
    default: ''
  },
  errorMessage: {
    type: String,
    default: ''
  },
  canRetry: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'next-step', 'retry-step', 'cancel-update', 'finish-update'])

// 计算属性
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const currentStep = computed(() => {
  return props.steps.find(step => step.id === props.currentStepId)
})

const currentStepIndex = computed(() => {
  return props.steps.findIndex(step => step.id === props.currentStepId)
})

const isProcessing = computed(() => {
  return currentStep.value?.status === 'in_progress'
})

const hasError = computed(() => {
  return props.steps.some(step => step.status === 'error') || !!props.errorMessage
})

const isCompleted = computed(() => {
  return props.steps.every(step => step.status === 'completed')
})

const canProceed = computed(() => {
  if (isProcessing.value || isCompleted.value) return false
  
  // 检查当前步骤是否已完成
  if (currentStep.value?.status === 'completed') {
    // 检查是否还有下一步
    const nextStepIndex = currentStepIndex.value + 1
    return nextStepIndex < props.steps.length
  }
  
  // 检查当前步骤是否可以开始
  if (currentStep.value?.status === 'pending') {
    // 检查前面的步骤是否都已完成
    const prevSteps = props.steps.slice(0, currentStepIndex.value)
    return prevSteps.every(step => step.status === 'completed')
  }
  
  // 如果当前步骤有错误，也可以显示下一步按钮（作为重试）
  if (currentStep.value?.status === 'error') {
    return true
  }
  
  return false
})

// 新增：判断是否应该显示重试按钮
const shouldShowRetry = computed(() => {
  // 只有在有全局错误且不是当前步骤错误时才显示重试按钮
  return hasError.value && !!props.errorMessage && currentStep.value?.status !== 'error'
})

// 方法
const getStepClasses = (step, index) => {
  const baseClasses = 'transition-all duration-300'
  
  if (step.status === 'completed') {
    return `${baseClasses} bg-green-900/20 border-green-800`
  } else if (step.status === 'error') {
    return `${baseClasses} bg-red-900/20 border-red-800`
  } else if (step.status === 'in_progress') {
    return `${baseClasses} bg-blue-900/20 border-blue-800`
  } else if (step.id === props.currentStepId) {
    return `${baseClasses} bg-gray-800 border-gray-600`
  } else {
    return `${baseClasses} bg-gray-900 border-gray-700`
  }
}

const getStepIconClasses = (step) => {
  if (step.status === 'completed') {
    return 'bg-green-600'
  } else if (step.status === 'error') {
    return 'bg-red-600'
  } else if (step.status === 'in_progress') {
    return 'bg-blue-600'
  } else {
    return 'bg-gray-600'
  }
}

const getStepTitleClasses = (step) => {
  if (step.status === 'completed') {
    return 'text-green-400'
  } else if (step.status === 'error') {
    return 'text-red-400'
  } else if (step.status === 'in_progress') {
    return 'text-blue-400'
  } else {
    return 'text-white'
  }
}

const getStepBadgeColor = (step) => {
  switch (step.status) {
    case 'completed': return 'green'
    case 'error': return 'red'
    case 'in_progress': return 'blue'
    default: return 'gray'
  }
}

const getStepStatusText = (step) => {
  switch (step.status) {
    case 'completed': return '已完成'
    case 'error': return '失败'
    case 'in_progress': return '进行中'
    default: return '等待中'
  }
}

const getNextStepText = () => {
  if (!currentStep.value) return '开始'
  
  if (currentStep.value.status === 'pending') {
    return `开始${currentStep.value.title}`
  } else if (currentStep.value.status === 'completed') {
    const nextStepIndex = currentStepIndex.value + 1
    if (nextStepIndex < props.steps.length) {
      return `下一步: ${props.steps[nextStepIndex].title}`
    }
  } else if (currentStep.value.status === 'error') {
    return `重试${currentStep.value.title}`
  }
  
  return '下一步'
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

// 事件处理
const nextStep = () => {
  emit('next-step')
}

const retryStep = () => {
  emit('retry-step')
}

const cancelUpdate = () => {
  emit('cancel-update')
}

const finishUpdate = () => {
  emit('finish-update')
}

const closeModal = () => {
  isOpen.value = false
}
</script>