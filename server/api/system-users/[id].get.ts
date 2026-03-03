import { } from '../../utils/database'

export default defineEventHandler(async (event) => {
  try {
    const envUser = process.env.DEV_ADMIN_USER || 'admin'
    return { success: true, data: { id: 1, username: envUser, email: '', role: 'admin', status: 'active' } }
  } catch (error: any) {
    return { success: false, error: error.message }
  }
})
