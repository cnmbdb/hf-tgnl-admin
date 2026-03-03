import crypto from 'crypto'
import { getClientIp } from '../utils/rateLimit'

export default defineEventHandler((event) => {
  const ip = getClientIp(event)
  const a = Math.floor(Math.random() * 9) + 1
  const b = Math.floor(Math.random() * 9) + 1
  const exp = Date.now() + 5 * 60 * 1000
  const secret = process.env.NUXT_SECRET_KEY || 'nuxt-secret'
  const data = `${a}:${b}:${exp}:${ip}`
  const h = crypto.createHmac('sha256', secret).update(data).digest('hex')
  const token = Buffer.from(JSON.stringify({ a, b, exp, ip, h })).toString('base64')
  return {
    question: `${a} + ${b} = ?`,
    token
  }
})
