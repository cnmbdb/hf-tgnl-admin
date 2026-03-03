<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <div class="w-8 h-8 bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-key" class="w-5 h-5 text-[#00dc82]" />
          </div>
          授权管理
        </h1>
        <p class="mt-1 text-sm text-[#9ca3af]">管理许可证授权和服务器IP绑定</p>
      </div>
      <UButton 
        @click="refreshLicenseInfo"
        :loading="loading"
        variant="outline"
      >
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 mr-2" />
        刷新状态
      </UButton>
    </div>

    <!-- 当前授权状态卡片 -->
    <div v-if="licenseInfo" class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg">
      <div class="px-4 py-3 border-b border-[#2a2a2b]">
        <h3 class="text-lg font-medium text-white flex items-center gap-2">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5 text-green-400" />
          当前授权状态
        </h3>
      </div>
      
      <div class="p-6 space-y-6">
        <!-- 授权概况 -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-xs text-[#9ca3af] mb-1">订单号</p>
                <p class="text-lg font-bold text-white truncate" :class="!licenseInfo.isActive ? 'text-gray-500' : ''">
                  {{ licenseInfo.orderNumber || '未知' }}
                </p>
              </div>
              <UIcon name="i-heroicons-shopping-cart" class="w-8 h-8 text-blue-400 opacity-50 flex-shrink-0 ml-2" />
            </div>
          </div>
          
          <div class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs text-[#9ca3af] mb-1">授权状态</p>
                <p class="text-lg font-bold" :class="licenseInfo.isActive ? 'text-green-400' : 'text-red-400'">
                  {{ licenseInfo.isActive ? '已激活' : '未激活' }}
                </p>
              </div>
              <UIcon 
                :name="licenseInfo.isActive ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" 
                class="w-8 h-8 opacity-50"
                :class="licenseInfo.isActive ? 'text-green-400' : 'text-red-400'"
              />
            </div>
          </div>
          
          <div class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-xs text-[#9ca3af] mb-1">服务器IP</p>
                <p class="text-lg font-bold text-white truncate">{{ licenseInfo.serverIp || 'localhost' }}</p>
              </div>
              <UIcon name="i-heroicons-server" class="w-8 h-8 text-purple-400 opacity-50 flex-shrink-0 ml-2" />
            </div>
          </div>
          
          <div class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs text-[#9ca3af] mb-1">授权IP数</p>
                <p class="text-lg font-bold text-white">{{ licenseInfo.authorizedIps?.length || 0 }}</p>
              </div>
              <UIcon name="i-heroicons-globe-alt" class="w-8 h-8 text-yellow-400 opacity-50" />
            </div>
          </div>
        </div>

        <!-- 已授权IP列表 -->
        <div v-if="licenseInfo.authorizedIps && licenseInfo.authorizedIps.length > 0">
          <h4 class="text-sm font-medium text-white mb-3">已授权IP地址</h4>
          <div class="space-y-2">
            <div 
              v-for="(ip, index) in licenseInfo.authorizedIps" 
              :key="index"
              class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-md p-3 flex items-center justify-between"
            >
              <div class="flex items-center gap-3">
                <UIcon name="i-heroicons-globe-alt" class="w-5 h-5 text-[#00dc82]" />
                <div>
                  <p class="text-white font-mono">{{ ip }}</p>
                  <p v-if="ip === licenseInfo.serverIp" class="text-xs text-[#00dc82] mt-0.5">当前服务器</p>
                </div>
              </div>
              <UBadge color="green" variant="subtle">已授权</UBadge>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- WordPress订单激活 -->
    <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg">
      <div class="px-4 py-3 border-b border-[#2a2a2b] flex items-center justify-between">
        <h3 class="text-lg font-medium text-white flex items-center gap-2">
          <UIcon name="i-heroicons-shopping-cart" class="w-5 h-5 text-[#00dc82]" />
          {{ licenseInfo?.isActive ? '更换授权' : 'WordPress订单激活' }}
        </h3>
        <a href="https://hfz.pw/shop/2101.html" target="_blank" class="text-sm text-[#00dc82] hover:text-[#00dc82]/80 flex items-center gap-1">
          前往商城
          <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-4 h-4" />
        </a>
      </div>
      
      <div class="p-6 space-y-4">
        <!-- 已激活状态 - 只显示取消授权按钮 -->
        <!-- 已授权 - 只显示取消按钮 -->
        <div v-if="licenseInfo?.isActive">
          <div class="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mb-4">
            <div class="flex items-start gap-3">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
              <div>
                <h4 class="text-sm font-medium text-yellow-500 mb-1">警告</h4>
                <p class="text-sm text-yellow-500/80">
                  当前订单已激活授权，如需更换其他订单，请先取消当前授权。
                  取消授权后，当前授权记录将被永久删除，不可恢复！
                </p>
              </div>
            </div>
          </div>
          
          <UButton 
            @click="deactivateLicense" 
            :loading="deactivating"
            color="red" 
            size="lg"
            class="w-full"
          >
            <UIcon name="i-heroicons-trash" class="w-5 h-5 mr-2" />
            取消授权
          </UButton>
        </div>        <!-- 未激活状态 - 显示激活表单 -->
        <template v-else>
          <!-- 提示信息 -->
          <div class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-lg p-4">
            <div class="flex items-start gap-3">
              <UIcon name="i-heroicons-information-circle" class="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
              <div class="text-sm text-[#9ca3af]">
                <p class="mb-2">在 <a href="https://hfz.pw/shop/2101.html" target="_blank" class="text-[#00dc82] hover:text-[#00dc82]/80">HFZ商城</a> 购买授权后，使用订单号即可激活</p>
                <p>订单号可在确认邮件或商城订单页面找到</p>
              </div>
            </div>
          </div>

          <!-- 订单号输入 -->
          <div>
            <label class="block text-white font-medium mb-2">WordPress订单号</label>
            <UInput 
              v-model="orderNumber" 
              placeholder="请输入订单号，例如：202501010001234"
              size="lg"
              class="w-full"
              :disabled="validating || activating"
            />
          </div>

        <!-- 验证结果 -->
        <div v-if="orderValidation?.message" 
          class="p-4 rounded-lg border"
          :class="orderValidation?.valid ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'">
          <div class="flex items-start gap-3">
            <UIcon 
              :name="orderValidation?.valid ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" 
              class="w-5 h-5 mt-0.5 flex-shrink-0"
              :class="orderValidation?.valid ? 'text-green-400' : 'text-red-400'"
            />
            <div class="flex-1">
              <div class="font-medium mb-1" :class="orderValidation?.valid ? 'text-green-400' : 'text-red-400'">
                {{ orderValidation?.valid ? '订单验证成功' : '订单验证失败' }}
              </div>
              <div class="text-sm text-[#9ca3af]">{{ orderValidation?.message }}</div>
              
              <!-- IP验证信息 -->
              <div v-if="orderValidation?.ipVerification" class="mt-4 space-y-3">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-[#9ca3af]">当前服务器IP：</span>
                  <span class="font-mono text-white">{{ orderValidation.ipVerification.currentServerIP }}</span>
                </div>
                
                <div class="flex items-center justify-between text-sm">
                  <span class="text-[#9ca3af]">授权IP数量：</span>
                  <span class="font-medium" :class="orderValidation.ipVerification.currentCount >= 4 ? 'text-yellow-400' : 'text-white'">
                    {{ orderValidation.ipVerification.currentCount }} / {{ orderValidation.ipVerification.maxCount }}
                  </span>
                </div>
                
                <!-- 已授权IP列表（除当前IP外做打码处理） -->
                <div v-if="orderValidation.ipVerification.authorizedIPs && orderValidation.ipVerification.authorizedIPs.length > 0">
                  <p class="text-xs text-[#9ca3af] mb-2">已授权IP列表：</p>
                  <div class="space-y-2">
                    <div 
                      v-for="(ip, index) in orderValidation.ipVerification.authorizedIPs" 
                      :key="index"
                      class="flex items-center justify-between bg-[#0c0c0d] border border-[#2a2a2b] rounded px-3 py-2"
                    >
                      <span class="font-mono text-sm text-white">
                        {{ maskIp(ip, orderValidation.ipVerification.currentServerIP) }}
                      </span>
                      <UBadge 
                        :color="ip === orderValidation.ipVerification.currentServerIP ? 'green' : 'gray'" 
                        variant="subtle" 
                        size="xs"
                      >
                        {{ ip === orderValidation.ipVerification.currentServerIP ? '当前IP' : '已授权' }}
                      </UBadge>
                    </div>
                  </div>
                </div>
                
                <!-- IP验证状态提示 -->
                <div 
                  class="p-3 rounded-lg border"
                  :class="orderValidation.ipVerification.canActivate ? 'bg-green-500/10 border-green-500/30' : 'bg-yellow-500/10 border-yellow-500/30'"
                >
                  <div class="flex items-start gap-2">
                    <UIcon 
                      :name="orderValidation.ipVerification.canActivate ? 'i-heroicons-check-circle' : 'i-heroicons-exclamation-triangle'" 
                      class="w-5 h-5 mt-0.5 flex-shrink-0"
                      :class="orderValidation.ipVerification.canActivate ? 'text-green-400' : 'text-yellow-400'"
                    />
                    <div class="text-sm" :class="orderValidation.ipVerification.canActivate ? 'text-green-400' : 'text-yellow-400'">
                      {{ orderValidation.ipVerification.message }}
                    </div>
                  </div>
                </div>
                
                <!-- 添加IP指引 -->
                <div v-if="!orderValidation.ipVerification.canActivate" class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                  <div class="flex items-start gap-2">
                    <UIcon name="i-heroicons-light-bulb" class="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                    <div class="text-sm text-blue-400">
                      <p class="font-medium mb-1">如何添加授权IP？</p>
                      <ol class="list-decimal list-inside space-y-1 text-xs text-blue-400/80">
                        <li>登录您的 <a href="https://hfz.pw/user" target="_blank" class="underline">WordPress网站账号</a></li>
                        <li>进入个人资料页面</li>
                        <li>在"网站"字段中填入 <code class="bg-black/30 px-1 rounded">{{ orderValidation.ipVerification.currentServerIP }}</code></li>
                        <li>多个IP用逗号分隔，最多4个</li>
                        <li>保存后返回此页面点击"立即激活"</li>
                      </ol>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 授权详情 -->
              <div v-if="orderValidation?.valid && orderValidation?.license" class="mt-4 space-y-4">
                <!-- 授权信息 -->
                <div class="grid grid-cols-3 gap-4">
                  <div class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-md p-3 text-center">
                    <p class="text-lg font-bold text-white">{{ orderValidation?.license?.edition || 'N/A' }}</p>
                    <p class="text-xs text-[#9ca3af] mt-1">授权版本</p>
                  </div>
                  <div class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-md p-3 text-center">
                    <p class="text-lg font-bold text-white">{{ orderValidation?.license?.customerEmail || 'N/A' }}</p>
                    <p class="text-xs text-[#9ca3af] mt-1">客户邮箱</p>
                  </div>
                  <div class="bg-[#0c0c0d] border border-[#2a2a2b] rounded-md p-3 text-center">
                    <p class="text-lg font-bold text-white">{{ orderValidation?.license?.orderNumber }}</p>
                    <p class="text-xs text-[#9ca3af] mt-1">订单号</p>
                  </div>
                </div>
                
                <!-- 激活状态 -->
                <div v-if="orderValidation?.activated" class="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                  <div class="flex items-center gap-2 text-green-400">
                    <UIcon name="i-heroicons-check-circle" class="w-5 h-5" />
                    <span class="font-medium">授权激活成功</span>
                  </div>
                  <p class="text-sm text-[#9ca3af] mt-2">
                    授权已成功激活，当前服务器IP已自动绑定到此订单
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

          <!-- 操作按钮 -->
          <div class="flex gap-3">
            <UButton 
              @click="validateOrder" 
              :loading="validating" 
              :disabled="!orderNumber || activating"
              variant="outline"
              size="lg"
              class="flex-1"
            >
              <UIcon name="i-heroicons-shield-check" class="w-5 h-5 mr-2" />
              验证订单
            </UButton>
            <UButton 
              @click="activateWithOrder" 
              :loading="activating" 
              :disabled="!orderValidation?.valid || !orderValidation?.ipVerification?.canActivate || validating"
              size="lg"
              class="flex-1 bg-[#00dc82] hover:bg-[#00dc82]/80"
            >
              <UIcon name="i-heroicons-sparkles" class="w-5 h-5 mr-2" />
              {{ orderValidation?.needReactivate ? '重新激活' : (orderValidation?.activated ? '已激活' : '立即激活') }}
            </UButton>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 页面元数据
definePageMeta({
  title: '授权管理',
  description: '管理许可证授权和服务器IP绑定',
  middleware: 'auth'
})

// Toast 通知
const toast = useToast()

// 响应式数据
const orderNumber = ref('')
const orderValidation = ref(null)
const licenseInfo = ref(null)

// 加载状态
const loading = ref(false)
const validating = ref(false)
const activating = ref(false)
const deactivating = ref(false)

// IP 打码：当前服务器IP原样显示，其它IP打码隐藏中间两段
const maskIp = (ip, currentIp) => {
  if (!ip) return ''
  if (currentIp && ip === currentIp) return ip
  const parts = ip.split('.')
  if (parts.length !== 4) return ip
  return `${parts[0]}.***.***.${parts[3]}`
}

// 获取当前授权信息
const fetchLicenseInfo = async () => {
  loading.value = true
  try {
    const data = await $fetch('/api/license/info')
    licenseInfo.value = data
  } catch (error) {
    console.error('Failed to fetch license info:', error)
    // 授权信息获取失败不影响页面显示
    licenseInfo.value = {
      isActive: false,
      orderNumber: null,
      serverIp: null,
      authorizedIps: []
    }
  } finally {
    loading.value = false
  }
}

// 刷新授权信息
const refreshLicenseInfo = async () => {
  await fetchLicenseInfo()
  toast.add({
    title: '刷新成功',
    description: '授权信息已更新',
    icon: 'i-heroicons-check-circle',
    color: 'green'
  })
}

// WordPress订单验证
const validateOrder = async () => {
  if (!orderNumber.value) return
  
  validating.value = true
  orderValidation.value = null
  
  try {
    const data = await $fetch('/api/license/validate-order', {
      method: 'POST',
      body: {
        orderNumber: orderNumber.value
      }
    })
    
    // 保留API返回的激活状态
    orderValidation.value = {
      ...data,
      // 如果API返回已激活，保留该状态
      activated: data.activated || false
    }
    
    if (data?.valid) {
      toast.add({
        title: '验证成功',
        description: '订单有效，请点击"立即激活"按钮完成授权',
        icon: 'i-heroicons-check-circle',
        color: 'green'
      })
    } else {
      toast.add({
        title: '验证失败',
        description: data?.message || '订单验证失败',
        icon: 'i-heroicons-x-circle',
        color: 'red'
      })
    }
  } catch (error) {
    console.error('Validate order error:', error)
    orderValidation.value = {
      valid: false,
      message: error.data?.message || error.message || '验证过程出错'
    }
    toast.add({
      title: '验证失败',
      description: error.data?.message || error.message || '无法验证订单',
      icon: 'i-heroicons-x-circle',
      color: 'red'
    })
  } finally {
    validating.value = false
  }
}

// WordPress订单激活
const activateWithOrder = async () => {
  if (!orderNumber.value || !orderValidation.value?.valid) return
  
  activating.value = true
  try {
    const data = await $fetch('/api/license/activate-order', {
      method: 'POST',
      body: {
        orderNumber: orderNumber.value
      }
    })
    
    if (data?.success) {
      toast.add({
        title: '激活成功',
        description: '授权已成功激活，当前服务器IP已自动绑定',
        icon: 'i-heroicons-check-circle',
        color: 'green'
      })
      
      // 更新验证结果显示激活状态
      orderValidation.value = {
        ...orderValidation.value,
        activated: true,
        license: {
          ...orderValidation.value.license,
          ...data.license
        }
      }
      
      // 刷新授权信息
      await fetchLicenseInfo()
      
      // 3秒后重置表单
      setTimeout(() => {
        orderNumber.value = ''
        orderValidation.value = null
      }, 3000)
    }
  } catch (error) {
    console.error('Activate order error:', error)
    toast.add({
      title: '激活失败',
      description: error.data?.message || error.message || '无法激活授权',
      icon: 'i-heroicons-x-circle',
      color: 'red'
    })
  } finally {
    activating.value = false
  }
}

// 取消授权
const deactivateLicense = async () => {
  if (!confirm('确定要取消授权吗？此操作将删除当前授权记录，不可恢复！')) {
    return
  }
  
  deactivating.value = true
  try {
    const data = await $fetch('/api/license/deactivate', {
      method: 'POST',
      body: {
        orderNumber: licenseInfo.value.orderNumber
      }
    })
    
    if (data?.success) {
      toast.add({
        title: '取消成功',
        description: '授权已取消，您可以重新激活其他订单',
        icon: 'i-heroicons-check-circle',
        color: 'green'
      })
      
      // 刷新授权信息以显示未激活状态
      await fetchLicenseInfo()
    }
  } catch (error) {
    console.error('Deactivate license error:', error)
    toast.add({
      title: '取消失败',
      description: error.data?.message || error.message || '无法取消授权',
      icon: 'i-heroicons-x-circle',
      color: 'red'
    })
  } finally {
    deactivating.value = false
  }
}

// 页面加载时获取授权信息
onMounted(() => {
  fetchLicenseInfo()
})
</script>
