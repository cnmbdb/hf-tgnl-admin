import fs from 'fs'
import path from 'path'
import { getServerPublicIP } from '../utils/wordpress-auth'

/**
 * 首次部署辅助：自动把 nl-2333/config.txt 里的 bot_notify_url 从 localhost 替换成服务器公网 IP。
 *
 * 触发条件（默认开启）：
 * - bot_notify_url 存在且 host 是 localhost/127.0.0.1/0.0.0.0
 *
 * 可关闭：
 * - BOT_NOTIFY_URL_AUTO_IP=false
 */
export default async () => {
  try {
    const enabled = (process.env.BOT_NOTIFY_URL_AUTO_IP ?? 'true') === 'true'
    if (!enabled) return

    const basePath = path.join(process.cwd(), 'nl-2333')
    const configPath = path.join(basePath, 'config.txt')
    if (!fs.existsSync(configPath)) return

    const raw = fs.readFileSync(configPath, 'utf-8')
    const lines = raw.split(/\r?\n/)
    const idx = lines.findIndex((l) => l.trim().startsWith('bot_notify_url='))
    if (idx < 0) return

    const currentLine = lines[idx]
    const currentValue = currentLine.split('=', 2)[1]?.trim() || ''
    if (!currentValue) return

    // 仅处理 URL 里 host 为本机的情况
    const isLocalHost = (host: string) =>
      host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0'

    let urlObj: URL | null = null
    try {
      urlObj = new URL(currentValue)
    } catch {
      urlObj = null
    }

    if (urlObj) {
      if (!isLocalHost(urlObj.hostname)) return
      const ip = await getServerPublicIP()
      urlObj.hostname = ip
      const next = urlObj.toString()
      if (next !== currentValue) {
        lines[idx] = `bot_notify_url=${next}`
        fs.writeFileSync(configPath, lines.join('\n'))
        console.log('[bot_notify_url] 已自动替换 localhost -> 公网IP:', next)
      }
      return
    }

    // 非标准 URL：做简单替换（兜底）
    if (!/(localhost|127\.0\.0\.1|0\.0\.0\.0)/.test(currentValue)) return
    const ip = await getServerPublicIP()
    const next = currentValue
      .replace('127.0.0.1', ip)
      .replace('0.0.0.0', ip)
      .replace('localhost', ip)
    if (next !== currentValue) {
      lines[idx] = `bot_notify_url=${next}`
      fs.writeFileSync(configPath, lines.join('\n'))
      console.log('[bot_notify_url] 已自动替换 localhost -> 公网IP:', next)
    }
  } catch (e: any) {
    // 获取公网 IP 失败 / 文件不可写：不影响主流程
    console.warn('[bot_notify_url] 自动填充失败(忽略):', e?.message || e)
  }
}

