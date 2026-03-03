import { defineEventHandler } from 'h3'
import { executeQuery } from '../utils/database'

export default defineEventHandler(async (event) => {
  try {
    const query = `
      INSERT INTO users (username, email, password, role, status, created_at, updated_at) VALUES
      ('admin', 'admin@example.com', '$2b$10$abcdefghijklmnopqrstuv', 'admin', 'active', NOW(), NOW()),
      ('user1', 'user1@example.com', '$2b$10$abcdefghijklmnopqrstuv', 'user', 'active', NOW(), NOW()),
      ('user2', 'user2@example.com', '$2b$10$abcdefghijklmnopqrstuv', 'user', 'active', NOW(), NOW()),
      ('moderator', 'mod@example.com', '$2b$10$abcdefghijklmnopqrstuv', 'moderator', 'active', NOW(), NOW()),
      ('viewer', 'viewer@example.com', '$2b$10$abcdefghijklmnopqrstuv', 'viewer', 'inactive', NOW(), NOW())
    `
    
    await executeQuery(query)
    
    return { success: true, message: '已插入5个测试用户' }
  } catch (error: any) {
    return { success: false, error: error.message }
  }
})
