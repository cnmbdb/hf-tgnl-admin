import fs from 'fs'
import path from 'path'

export default defineEventHandler(async () => {
  try {
    const basePath = path.join(process.cwd(), 'nl-2333')
    const configPath = path.join(basePath, 'config.txt')

    if (!fs.existsSync(configPath)) {
      return {
        success: false,
        error: '未找到 config.txt 配置文件'
      }
    }

    const raw = fs.readFileSync(configPath, 'utf-8')
    const cfg: Record<string, string> = {}
    for (const lineRaw of raw.split(/\r?\n/)) {
      const line = lineRaw.trim()
      if (!line || line.startsWith('#')) continue
      const idx = line.indexOf('=')
      if (idx <= 0) continue
      const k = line.slice(0, idx).trim()
      const v = line.slice(idx + 1).trim()
      if (k) cfg[k] = v
    }

    const energyPoolApi = (cfg['energy_pool_api'] || '').replace(/\/+$/, '')
    const username = cfg['username'] || ''
    const password = cfg['password'] || ''

    if (!energyPoolApi || !username || !password) {
      return {
        success: false,
        error: 'config.txt 中缺少 energy_pool_api / username / password 配置'
      }
    }

    // 按能量池实际实现：使用 username/password 作为 query 参数鉴权
    const url = `${energyPoolApi}/v1/get_api_user_info?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`

    const resp = await fetch(url, { method: 'GET' })

    if (!resp.ok) {
      const text = await resp.text().catch(() => '')
      return {
        success: false,
        error: `请求能量池 API 失败: HTTP ${resp.status}`,
        details: text.slice(0, 500)
      }
    }

    const data = await resp.json().catch(() => ({} as any))

    // 兼容能量池当前实现：返回中文字段「当前余额(TRX)」
    let balanceTrx: number | null = null
    if (typeof (data as any)['当前余额(TRX)'] === 'number') {
      balanceTrx = (data as any)['当前余额(TRX)']
    } else if (typeof (data as any).balance_trx === 'number') {
      balanceTrx = (data as any).balance_trx
    } else if (typeof (data as any).balance === 'number') {
      balanceTrx = (data as any).balance
    }

    return {
      success: true,
      data: {
        apiUsername: username,
        raw: data,
        balanceTrx
      }
    }
  } catch (error: any) {
    console.error('读取能量池账户信息失败:', error)
    return {
      success: false,
      error: error?.message || '读取能量池账户信息失败'
    }
  }
})

