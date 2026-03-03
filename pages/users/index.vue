<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-3">
          <div class="w-8 h-8 bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-users" class="w-5 h-5 text-[#00dc82]" />
          </div>
          用户管理
        </h1>
        <p class="mt-1 text-sm text-[#9ca3af]">管理TG机器人用户</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-users" class="w-5 h-5 text-blue-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-[#9ca3af]">总用户数</p>
            <p class="text-xl font-semibold text-white">{{ totalUsers }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-check-circle" class="w-5 h-5 text-green-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-[#9ca3af]">活跃用户</p>
            <p class="text-xl font-semibold text-white">{{ activeUsers }}</p>
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-yellow-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-yellow-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-[#9ca3af]">今日新增</p>
            <p class="text-xl font-semibold text-white">{{ newUsersToday }}</p>
          </div>
        </div>
      </div>

      <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
        <div class="flex items-center">
          <div class="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
            <UIcon name="i-heroicons-star" class="w-5 h-5 text-purple-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-[#9ca3af]">VIP用户</p>
            <p class="text-xl font-semibold text-white">{{ vipUsers }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <UInput
            v-model="searchQuery"
            :placeholder="activeTab === 'system' ? '搜索用户名或邮箱...' : '搜索用户名或 Telegram ID...'"
            icon="i-heroicons-magnifying-glass"
            class="w-full"
          />
        </div>
        <div class="flex gap-2">
          <USelect
            v-model="statusFilter"
            :options="statusOptions"
            placeholder="状态"
            class="w-32"
          />
          <USelect
            v-if="activeTab === 'system'"
            v-model="roleFilter"
            :options="roleOptions"
            placeholder="角色"
            class="w-32"
          />
          <UButton 
            v-if="activeTab === 'telegram'"
            @click="showImportModal = true"
            color="primary" 
            size="sm"
            class="bg-[#00dc82] hover:bg-[#00dc82]/80"
          >
            <UIcon name="i-heroicons-arrow-up-tray" class="w-4 h-4 mr-2" />
            导入用户
          </UButton>
          <UButton variant="outline" @click="resetFilters" size="sm">
            重置
          </UButton>
        </div>
      </div>
    </div>

    <!-- 导入用户模态框 -->
    <UModal v-model="showImportModal" :ui="{ width: 'sm:max-w-2xl' }">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-white">导入 Telegram 用户</h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="showImportModal = false" />
          </div>
        </template>

        <div class="space-y-4">
          <!-- 文件上传区域 -->
          <div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6">
            <div class="text-center">
              <UIcon name="i-heroicons-cloud-arrow-up" class="mx-auto h-12 w-12 text-gray-400" />
              <div class="mt-4">
                <label for="file-upload" class="cursor-pointer">
                  <span class="mt-2 block text-sm font-medium text-white">
                    点击上传文件或拖拽文件到此处
                  </span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    accept=".json,.csv"
                    class="sr-only"
                    @change="handleFileUpload"
                  />
                </label>
                <p class="mt-2 text-xs text-gray-500">支持 JSON 和 CSV 格式</p>
              </div>
            </div>
          </div>

          <!-- 文件信息 -->
          <div v-if="selectedFile" class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <UIcon name="i-heroicons-document-text" class="h-5 w-5 text-gray-400 mr-2" />
                <span class="text-sm text-white">{{ selectedFile.name }}</span>
              </div>
              <UButton color="gray" variant="ghost" size="xs" @click="selectedFile = null">
                <UIcon name="i-heroicons-x-mark" class="h-4 w-4" />
              </UButton>
            </div>
          </div>

          <!-- 数据预览 -->
          <div v-if="previewData.length > 0" class="space-y-2">
            <h4 class="text-sm font-medium text-white">数据预览 (前5条)</h4>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 max-h-40 overflow-y-auto">
              <pre class="text-xs text-gray-600 dark:text-gray-300">{{ JSON.stringify(previewData.slice(0, 5), null, 2) }}</pre>
            </div>
          </div>

          <!-- 导入选项 -->
          <div class="space-y-3">
            <UCheckbox v-model="importOptions.updateExisting" label="更新已存在的用户" />
            <UCheckbox v-model="importOptions.validateData" label="验证数据格式" />
          </div>

          <!-- 导入结果 -->
          <div v-if="importResult" class="space-y-2">
            <div :class="importResult.success ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
              {{ importResult.message }}
            </div>
            <div v-if="importResult.data" class="text-xs text-gray-500">
              成功: {{ importResult.data.imported }}, 跳过: {{ importResult.data.skipped }}, 错误: {{ importResult.data.errors?.length || 0 }}
            </div>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton color="gray" variant="outline" @click="showImportModal = false">
              取消
            </UButton>
            <UButton 
              color="primary" 
              :loading="importing"
              :disabled="!selectedFile || previewData.length === 0"
              @click="importUsers"
              class="bg-[#00dc82] hover:bg-[#00dc82]/80"
            >
              {{ importing ? '导入中...' : '开始导入' }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>

    <!-- 系统用户新建/编辑模态框 -->
    <UModal v-model="showUserModal" :ui="{ width: 'sm:max-w-md' }">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-white">
              {{ editingUser ? '编辑系统用户' : '新建系统用户' }}
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="closeUserModal" />
          </div>
        </template>

        <form @submit.prevent="saveUser" class="space-y-4">
          <UFormGroup label="用户名" name="username" required>
             <UInput 
               v-model="userForm.username" 
               placeholder="请输入用户名"
               required
             />
          </UFormGroup>

          <UFormGroup label="密码" name="password" :required="!editingUser">
            <UInput 
              v-model="userForm.password" 
              type="password"
              :placeholder="editingUser ? '留空则不修改密码' : '请输入密码'"
            />
          </UFormGroup>

          <UFormGroup label="确认密码" name="confirmPassword" :required="!editingUser && !!userForm.password">
            <UInput 
              v-model="userForm.confirmPassword" 
              type="password"
              placeholder="请再次输入密码"
            />
          </UFormGroup>

          <UFormGroup label="角色" name="role" required>
            <USelect 
              v-model="userForm.role" 
              :options="[
                { label: '管理员', value: 'admin' },
                { label: '普通用户', value: 'user' }
              ]"
              placeholder="请选择角色"
            />
          </UFormGroup>

          <UFormGroup label="状态" name="status" required>
            <USelect 
              v-model="userForm.status" 
              :options="[
                { label: '活跃', value: 'active' },
                { label: '非活跃', value: 'inactive' }
              ]"
              placeholder="请选择状态"
            />
          </UFormGroup>

          <div class="flex justify-end gap-3 pt-4">
            <UButton color="gray" variant="outline" @click="closeUserModal">
              取消
            </UButton>
            <UButton 
              type="submit"
              color="primary" 
              :loading="saving"
              class="bg-[#00dc82] hover:bg-[#00dc82]/80"
            >
              {{ saving ? '保存中...' : (editingUser ? '更新' : '创建') }}
            </UButton>
          </div>
         </form>
      </UCard>
    </UModal>

    <!-- Telegram 用户编辑模态框（主要调整余额） -->
    <UModal v-model="showTgUserModal" :ui="{ width: 'sm:max-w-md' }">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-white">
              编辑 Telegram 用户
            </h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="closeTgUserModal" />
          </div>
        </template>

        <div class="space-y-4">
          <UFormGroup label="TGID" name="tgid">
            <UInput v-model="tgUserForm.chatId" disabled />
          </UFormGroup>

          <UFormGroup label="用户名" name="name">
            <UInput v-model="tgUserForm.name" disabled />
          </UFormGroup>

          <UFormGroup label="用户余额 (TRX)" name="balance">
            <UInput
              v-model="tgUserForm.balanceTrx"
              type="number"
              step="0.01"
              min="0"
              placeholder="请输入余额（TRX）"
            />
          </UFormGroup>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton color="gray" variant="outline" @click="closeTgUserModal">
              取消
            </UButton>
            <UButton 
              type="button"
              color="primary" 
              :loading="savingTgUser"
              class="bg-[#00dc82] hover:bg-[#00dc82]/80"
              @click="saveTgUser"
            >
              {{ savingTgUser ? '保存中...' : '保存' }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>

    <!-- 删除确认模态框 -->
    <UModal v-model="showDeleteModal" :ui="{ width: 'sm:max-w-md' }">
      <UCard :ui="{ ring: '', divide: 'divide-y divide-gray-100 dark:divide-gray-800' }">
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-white">确认删除</h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark-20-solid" @click="showDeleteModal = false" />
          </div>
        </template>

        <div class="space-y-4">
          <p class="text-white">
            确定要删除用户 <span class="font-semibold text-[#00dc82]">{{ deletingUser?.username || deletingUser?.name }}</span> 吗？
          </p>
          <p class="text-sm text-[#9ca3af]">
            此操作不可撤销，请谨慎操作。
          </p>
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton color="gray" variant="outline" @click="showDeleteModal = false">
              取消
            </UButton>
            <UButton 
              color="red" 
              :loading="deleting"
              @click="confirmDelete"
            >
              {{ deleting ? '删除中...' : '确认删除' }}
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>

    <!-- 用户列表 -->
    <div class="bg-[#1a1a1b] border border-[#2a2a2b] rounded-lg overflow-hidden">
      <div class="px-4 py-3 border-b border-[#2a2a2b]">
        <h3 class="text-lg font-medium text-white">
          {{ activeTab === 'system' ? '系统用户列表' : 'Telegram 用户列表' }}
        </h3>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-[#0c0c0d]">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">用户</th>
              <th v-if="activeTab === 'telegram'" class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">TGID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">状态</th>
              <th v-if="activeTab === 'system'" class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">角色</th>
              <th v-if="activeTab === 'telegram'" class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">用户余额</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">最后活跃</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-[#9ca3af] uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#2a2a2b]">
            <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-[#2a2a2b]/50 transition-colors">
              <td class="px-4 py-3">
                <div class="flex items-center">
                  <UAvatar
                    :src="user.avatar"
                    :alt="user.name"
                    size="sm"
                    class="mr-3"
                  />
                  <div>
                    <div class="text-sm font-medium text-white">{{ user.name }}</div>
                    <div class="text-sm text-[#9ca3af]">{{ user.email || (user.username ? '@' + user.username : '无用户名') }}</div>
                  </div>
                </div>
              </td>
              <td v-if="activeTab === 'telegram'" class="px-4 py-3">
                <div class="text-sm text-white font-mono">{{ user.telegramId || user.tg_user_id }}</div>
              </td>
              <td class="px-4 py-3">
                <UBadge
                  :color="user.status === 'active' ? 'green' : user.status === 'inactive' ? 'gray' : 'red'"
                  variant="subtle"
                  size="sm"
                >
                  {{ getStatusText(user.status) }}
                </UBadge>
              </td>
              <td v-if="activeTab === 'system'" class="px-4 py-3">
                <UBadge
                  :color="user.role === 'admin' ? 'blue' : user.role === 'moderator' ? 'purple' : 'gray'"
                  variant="subtle"
                  size="sm"
                >
                  {{ getRoleText(user.role) }}
                </UBadge>
              </td>
              <td v-if="activeTab === 'telegram'" class="px-4 py-3">
                <div class="text-sm text-white font-medium">
                  {{ formatBalance(user.balance) }} TRX
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-[#9ca3af]">
                {{ formatDate(user.lastActive) }}
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <UButton variant="ghost" size="sm" @click="editUser(user)">
                    <UIcon name="i-heroicons-pencil" class="w-4 h-4" />
                  </UButton>
                  <UButton variant="ghost" size="sm" color="red" @click="deleteUser(user)">
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
          显示 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalUsers) }} 条，共 {{ totalUsers }} 条
        </div>
        <div class="flex items-center gap-2">
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
            :disabled="currentPage * pageSize >= totalUsers"
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
  title: '用户管理',
  middleware: ['auth', 'license']
})

// 响应式数据
const activeTab = ref('telegram')
const searchQuery = ref('')
const statusFilter = ref('')
const roleFilter = ref('')
const currentPage = ref(1)
const pageSize = 10

// 用户数据
const users = ref<any[]>([])
const totalUsers = ref(0)
const activeUsers = ref(0)
const newUsersToday = ref(0)
const onlineUsers = ref(0)
const loading = ref(false)

// AJ1 像素头像配置
const appBase = (useRuntimeConfig() as any).app?.baseURL || '/'
const basePref = appBase.endsWith('/') ? appBase : appBase + '/'
const aj1Avatars = [
  '/avatars/aj1-pixel-1.svg',
  '/avatars/aj1-pixel-2.svg',
  '/avatars/aj1-pixel-3.svg',
  '/avatars/aj1-pixel-4.svg',
  '/avatars/aj1-pixel-5.svg'
]

const getAvatarForUser = (user: any) => {
  // 尽量使用数值型ID生成稳定头像下标
  let seed =
    Number(user.tg_user_id || user.telegramId || user.id) ||
    0

  // 若没有数值ID，则用用户名字符编码求和
  if (!seed) {
    const name =
      (user.username ||
        user.name ||
        user.email ||
        'user') as string
    seed = Array.from(name).reduce(
      (acc, ch) => acc + ch.charCodeAt(0),
      0
    )
  }

  const index =
    Math.abs(seed) % aj1Avatars.length
  return (
    basePref + aj1Avatars[index].replace(/^\//, '')
  )
}

// 系统用户管理
const showUserModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref<any>(null)
const deletingUser = ref<any>(null)
const saving = ref(false)
const deleting = ref(false)

// Telegram 用户编辑
const showTgUserModal = ref(false)
const editingTgUser = ref<any>(null)
const savingTgUser = ref(false)
const tgUserForm = ref({
  chatId: '',
  name: '',
  balanceTrx: 0
})

// 用户表单数据
const userForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'user',
  status: 'active'
})



// 导入功能数据
const showImportModal = ref(false)
const selectedFile = ref<File | null>(null)
const previewData = ref<any[]>([])
const importing = ref(false)
const importResult = ref<any>(null)
const importOptions = ref({
  updateExisting: false,
  validateData: true
})

const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '活跃', value: 'active' },
  { label: '非活跃', value: 'inactive' },
  { label: '已禁用', value: 'disabled' }
]

const roleOptions = [
  { label: '全部角色', value: '' },
  { label: '管理员', value: 'admin' },
  { label: '普通用户', value: 'user' }
]

// API数据获取
const fetchUsers = async () => {
  loading.value = true
  try {
    if (activeTab.value === 'system') {
      const query: any = {
        page: currentPage.value,
        limit: pageSize
      }
      
      if (searchQuery.value) {
        query.search = searchQuery.value
      }
      
      if (statusFilter.value) {
        query.status = statusFilter.value
      }
      
      if (roleFilter.value) {
        query.role = roleFilter.value
      }
      
      const response: any = await $fetch('/api/system-users', { query })
      
      if (response.success && response.data) {
        users.value = response.data.users.map((user: any) => ({
          ...user,
          name: user.username,
          avatar: getAvatarForUser(user),
          lastActive: user.last_login ? new Date(user.last_login) : null
        }))
        totalUsers.value = response.data.pagination.total
        
        // 更新统计数据
        if (response.data.stats) {
          activeUsers.value = response.data.stats.active_count || 0
          newUsersToday.value = response.data.stats.total_users || 0
          onlineUsers.value = response.data.stats.admin_count || 0
        }
      }
    } else {
      const query: any = {
        page: currentPage.value,
        limit: pageSize
      }
      
      if (searchQuery.value) {
        query.search = searchQuery.value
      }
      
      if (statusFilter.value) {
        query.status = statusFilter.value
      }
      
      const response: any = await $fetch('/api/tg-users', { query })
      
      if (response.success && response.data) {
        users.value = response.data.users.map((user: any) => ({
          ...user,
          name:
            `${user.first_name || ''} ${user.last_name || ''}`.trim() ||
            user.username ||
            '未知用户',
          telegramId: user.tg_user_id,
          avatar: getAvatarForUser(user),
          lastActive: new Date(user.last_activity || user.created_at)
        }))
        totalUsers.value = response.data.pagination.total
        
        // 更新统计数据
        if (response.data.stats) {
          activeUsers.value = response.data.stats.active_count || 0
          newUsersToday.value = response.data.stats.today_new_users || 0
          onlineUsers.value = response.data.stats.active_count || 0
        }
      }
    }
  } catch (error) {
    console.error('获取用户数据失败:', error)
    // 显示错误信息给用户
    if (process.client) {
      alert('获取用户数据失败，请检查网络连接或刷新页面重试')
    }
  } finally {
    loading.value = false
  }
}

// 计算属性
const filteredUsers = computed(() => {
  let filtered = users.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.name.toLowerCase().includes(query) ||
      user.email?.toLowerCase().includes(query) ||
      user.telegramId?.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(user => user.status === statusFilter.value)
  }

  if (roleFilter.value && activeTab.value === 'system') {
    filtered = filtered.filter(user => user.role === roleFilter.value)
  }

  return filtered
})

// 方法
const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  roleFilter.value = ''
  currentPage.value = 1
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '活跃',
    inactive: '非活跃',
    disabled: '已禁用'
  }
  return statusMap[status] || status
}

const getRoleText = (role: string) => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    moderator: '版主',
    user: '普通用户'
  }
  return roleMap[role] || role
}

const formatDate = (date: Date | null | undefined) => {
  if (!date || isNaN(new Date(date).getTime())) {
    return '从未登录'
  }
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

const formatBalance = (balance: number) => {
  if (!balance) return '0.00'
  return (balance / 1000000).toFixed(2)
}

const editUser = (user: any) => {
  if (activeTab.value === 'system') {
    editingUser.value = user
    userForm.value = {
      username: user.username,
      password: '',
      confirmPassword: '',
      role: user.role,
      status: user.status
    }
    showUserModal.value = true
  } else {
    // 编辑 Telegram 用户（主要调整余额）
    editingTgUser.value = user
    tgUserForm.value = {
      chatId: String(user.telegramId || user.tg_user_id || user.chat_id || ''),
      name: user.name || user.username || `TG用户_${user.tg_user_id || user.telegramId || ''}`,
      balanceTrx: user.balance ? user.balance / 1000000 : 0
    }
    showTgUserModal.value = true
  }
}

const deleteUser = (user: any) => {
  deletingUser.value = user
  showDeleteModal.value = true
}

// 系统用户管理方法
const closeUserModal = () => {
  showUserModal.value = false
  editingUser.value = null
  userForm.value = {
    username: '',
    password: '',
    confirmPassword: '',
    role: 'user',
    status: 'active'
  }
}

const closeTgUserModal = () => {
  showTgUserModal.value = false
  editingTgUser.value = null
  tgUserForm.value = {
    chatId: '',
    name: '',
    balanceTrx: 0
  }
}

const saveUser = async () => {
  saving.value = true
  try {
    // 验证密码确认
    if (userForm.value.password && userForm.value.password !== userForm.value.confirmPassword) {
      alert('密码确认不匹配')
      return
    }

    const userData: any = {
       username: userForm.value.username,
       role: userForm.value.role,
       status: userForm.value.status
     }

     // 对于编辑用户，只有在输入了新密码时才添加密码字段
     // 对于新建用户，密码是必填的
     if (userForm.value.password && userForm.value.password.trim() !== '') {
       userData.password = userForm.value.password
     }

     let response: any
     if (editingUser.value) {
       // 更新用户
       response = await $fetch('/api/system-users', {
         method: 'PUT',
         body: {
           id: editingUser.value.id,
           ...userData
         }
       })
     } else {
       // 创建用户
       if (!userForm.value.password || userForm.value.password.trim() === '') {
         alert('创建用户时密码为必填项')
         return
       }
       response = await $fetch('/api/system-users', {
         method: 'POST',
         body: userData
       })
     }

    if (response.success) {
      closeUserModal()
      await fetchUsers()
      alert(editingUser.value ? '用户更新成功' : '用户创建成功')
    } else {
       alert((response).error || '操作失败')
     }
  } catch (error: any) {
    console.error('保存用户失败:', error)
    alert(error.message || '保存用户失败')
  } finally {
    saving.value = false
  }
}

const saveTgUser = async () => {
  if (!tgUserForm.value.chatId) {
    alert('缺少 TGID，无法保存')
    return
  }

  const balanceNumber = Number(tgUserForm.value.balanceTrx)
  if (Number.isNaN(balanceNumber)) {
    alert('请输入有效的余额数字')
    return
  }

  savingTgUser.value = true
  try {
    const newBalance = Math.round(balanceNumber * 1000000)
    const response: any = await $fetch('/api/bot-set-balance', {
      method: 'POST',
      body: {
        chat_id: tgUserForm.value.chatId,
        new_balance: newBalance
      }
    })

    if (response.success) {
      closeTgUserModal()
      await fetchUsers()
      alert('Telegram 用户更新成功')
    } else {
      alert((response as any).error || '更新失败')
    }
  } catch (error: any) {
    console.error('保存 Telegram 用户失败:', error)
    alert(error.message || '保存 Telegram 用户失败')
  } finally {
    savingTgUser.value = false
  }
}

const confirmDelete = async () => {
  if (!deletingUser.value) return
  
  deleting.value = true
  try {
     let response: any
     if (activeTab.value === 'telegram') {
       const chatId = deletingUser.value.telegramId || deletingUser.value.tg_user_id || deletingUser.value.chat_id
       response = await $fetch('/api/tg-users', {
         method: 'DELETE',
         query: { chat_id: chatId }
       })
     } else {
       response = await $fetch('/api/system-users', {
       method: 'DELETE',
       query: { id: deletingUser.value.id }
     })
     }

     if (response.success) {
       showDeleteModal.value = false
       deletingUser.value = null
       await fetchUsers()
       alert('用户删除成功')
     } else {
        alert((response).error || '删除失败')
      }
  } catch (error: any) {
    console.error('删除用户失败:', error)
    alert(error.message || '删除用户失败')
  } finally {
    deleting.value = false
  }
}

// 导入功能方法
const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  selectedFile.value = file
  importResult.value = null
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string
      let data = []
      
      if (file.name.endsWith('.json')) {
        data = JSON.parse(content)
      } else if (file.name.endsWith('.csv')) {
        // 简单的CSV解析
        const lines = content.split('\n')
        const headers = lines[0].split(',').map(h => h.trim())
        
        data = lines.slice(1).filter(line => line.trim()).map(line => {
          const values = line.split(',').map(v => v.trim())
          const obj: any = {}
          headers.forEach((header, index) => {
            obj[header] = values[index] || ''
          })
          return obj
        })
      }
      
      if (Array.isArray(data)) {
        previewData.value = data
      } else {
        previewData.value = [data]
      }
    } catch (error) {
      console.error('文件解析错误:', error)
      previewData.value = []
    }
  }
  
  reader.readAsText(file)
}

const importUsers = async () => {
  if (!selectedFile.value || previewData.value.length === 0) return
  
  importing.value = true
  importResult.value = null
  
  try {
    const response: any = await $fetch('/api/import-users', {
      method: 'POST',
      body: {
        users: previewData.value,
        updateExisting: importOptions.value.updateExisting
      }
    })
    
    importResult.value = response
    
    if (response.success) {
      // 刷新用户列表
      await fetchUsers()
      
      // 3秒后自动关闭模态框
      setTimeout(() => {
        showImportModal.value = false
        selectedFile.value = null
        previewData.value = []
        importResult.value = null
      }, 3000)
    }
  } catch (error: any) {
    importResult.value = {
      success: false,
      message: `导入失败: ${error.message || '未知错误'}`
    }
  } finally {
    importing.value = false
  }
}

// 监听器
watch([activeTab, searchQuery, statusFilter, currentPage], () => {
  fetchUsers()
}, { immediate: false })

watch(activeTab, () => {
  resetFilters()
  fetchUsers()
})

// 初始化
onMounted(() => {
  fetchUsers()
})
</script>