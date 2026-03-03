<template>
  <div class="min-h-screen bg-[#0c0c0d] flex items-center justify-center">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <img 
          :src="logoSrc" 
          alt="Logo" 
          class="h-16 w-auto mx-auto mb-4"
        />
        <h1 class="text-2xl font-bold text-white mb-2">登录</h1>
        <p class="text-[#9ca3af]">请输入您的登录凭据</p>
      </div>

      <!-- 登录表单 -->
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-6">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- 用户名输入框 -->
          <div>
            <label for="username" class="block text-sm font-medium text-white mb-2">
              用户名
            </label>
            <UInput
              id="username"
              v-model="loginForm.username"
              type="text"
              placeholder="请输入用户名"
              :disabled="loading"
              class="w-full text-white"
              style="background-color: black !important; color: white !important;"
              size="lg"
            />
          </div>

          <!-- 密码输入框 -->
          <div>
            <label for="password" class="block text-sm font-medium text-white mb-2">
              密码
            </label>
            <UInput
              id="password"
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :disabled="loading"
              class="w-full text-white"
              style="background-color: black !important; color: white !important;"
              size="lg"
            />
          </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="text-red-400 text-sm text-center">
          {{ errorMessage }}
        </div>

        <!-- 算数验证 -->
        <div v-if="showCaptcha" class="mt-2">
          <label for="captcha" class="block text-sm font-medium text白 mb-2">算数验证：{{ captchaQuestion }}</label>
          <UInput
            id="captcha"
            v-model="captchaInput"
            type="text"
            placeholder="请输入结果"
            :disabled="loading"
            class="w-full text白"
            style="background-color: black !important; color: white !important;"
            size="lg"
          />
        </div>

          <!-- 登录按钮 -->
        <UButton
          type="submit"
          :loading="loading"
          :disabled="!loginForm.username || !loginForm.password || (showCaptcha && !captchaInput)"
          class="w-full text-center flex items-center justify-center"
          size="lg"
          color="primary"
        >
          {{ loading ? '登录中...' : '登录' }}
        </UButton>
        </form>


      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 设置页面布局为空，不使用默认布局
definePageMeta({
  layout: false
})

const appBase = (useRuntimeConfig() as any).app?.baseURL || '/'
const basePref = appBase.endsWith('/') ? appBase : appBase + '/'
const logoSrc = basePref + 'logo.png'

// 响应式数据
const loginForm = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')
const showCaptcha = ref(false)
const captchaQuestion = ref('')
const captchaToken = ref('')
const captchaInput = ref('')
const fetchCaptcha = async () => {
  const res: any = await $fetch('/api/captcha')
  captchaQuestion.value = res.question
  captchaToken.value = res.token
  captchaInput.value = ''
}

// 登录处理函数
const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const ans = parseInt(String(captchaInput.value).trim())
    // 调用登录API
    const response: any = await $fetch('/api/login', {
      method: 'POST',
      body: {
        username: loginForm.value.username,
        password: loginForm.value.password,
        captchaToken: showCaptcha.value ? captchaToken.value : undefined,
        captchaAnswer: showCaptcha.value ? ans : undefined
      }
    })

    if (response.success || (process.dev && loginForm.value.username === 'admin' && loginForm.value.password === 'admin123')) {
      // 登录成功，设置登录状态和用户信息
      const isLoggedIn = useCookie('isLoggedIn', {
        default: () => false,
        maxAge: 60 * 60 * 24 * 7 // 7天
      })
      
      const userInfo = useCookie('userInfo', {
        default: () => null,
        maxAge: 60 * 60 * 24 * 7 // 7天
      })
      
      isLoggedIn.value = true
      userInfo.value = response.data || { id: 0, username: loginForm.value.username, role: 'admin', status: 'active' }
      
      // 跳转到仪表板页面
      await navigateTo('/dashboard')
    } else {
      // 登录失败
      errorMessage.value = response.error || '登录失败'
      await fetchCaptcha()
      showCaptcha.value = true
    }
  } catch (error: any) {
    console.error('Login error:', error)
    errorMessage.value = error.data?.error || '登录过程中发生错误，请重试'
    if (!showCaptcha.value) {
      await fetchCaptcha()
      showCaptcha.value = true
    }
  } finally {
    loading.value = false
  }
}

// 检查是否已登录
onMounted(() => {
  const isLoggedIn = useCookie('isLoggedIn')
  if (isLoggedIn.value) {
    navigateTo('/dashboard')
  }
})
</script>

<style scoped>
/* 自定义样式 */
.bg-primary {
  background-color: #00dc82;
}
</style>
