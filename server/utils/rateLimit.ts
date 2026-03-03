type Bucket = {
  timestamps: number[]
}

const buckets = new Map<string, Bucket>()
const failures = new Map<string, { count: number; windowStart: number }>()
const blocks = new Map<string, number>() // ip -> unblockAt

export function checkRateLimit(ip: string, key: string, limit: number, windowMs: number): boolean {
  const now = Date.now()
  const id = `${ip}:${key}`
  const bucket = buckets.get(id) || { timestamps: [] }
  // 清理窗口外的请求
  bucket.timestamps = bucket.timestamps.filter(t => now - t <= windowMs)
  if (bucket.timestamps.length >= limit) {
    buckets.set(id, bucket)
    return false
  }
  bucket.timestamps.push(now)
  buckets.set(id, bucket)
  return true
}

export function recordFailure(ip: string, windowMs: number): { blocked: boolean; remaining: number } {
  const now = Date.now()
  const rec = failures.get(ip) || { count: 0, windowStart: now }
  if (now - rec.windowStart > windowMs) {
    rec.count = 0
    rec.windowStart = now
  }
  rec.count += 1
  failures.set(ip, rec)
  const threshold = 5
  if (rec.count >= threshold) {
    // 封禁 15 分钟
    blocks.set(ip, now + 15 * 60 * 1000)
    rec.count = 0
    failures.set(ip, rec)
    return { blocked: true, remaining: 0 }
  }
  return { blocked: false, remaining: threshold - rec.count }
}

export function clearFailures(ip: string) {
  failures.delete(ip)
}

export function isBlocked(ip: string): boolean {
  const until = blocks.get(ip)
  if (!until) return false
  const now = Date.now()
  if (now >= until) {
    blocks.delete(ip)
    return false
  }
  return true
}

export function getClientIp(event: any): string {
  const xff = getRequestHeader(event, 'x-forwarded-for') || ''
  const ip = (xff.split(',')[0] || '').trim()
  if (ip) return ip
  const remote = (event.node?.req?.socket?.remoteAddress || '').trim()
  return remote || 'unknown'
}

export function shouldRequireCaptcha(ip: string, windowMs: number): boolean {
  const rec = failures.get(ip)
  if (!rec) return false
  const now = Date.now()
  if (now - rec.windowStart > windowMs) return false
  return rec.count > 0
}
