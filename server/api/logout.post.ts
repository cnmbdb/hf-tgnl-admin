export default defineEventHandler(async (event) => {
  try {
    // 清除用户信息 cookie
    deleteCookie(event, 'userInfo', {
      path: '/'
    })
    
    return {
      success: true,
      message: '注销成功'
    }
  } catch (error: any) {
    console.error('Error during logout:', error)
    return {
      success: false,
      error: '注销过程中发生错误'
    }
  }
})