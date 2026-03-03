import fs from 'node:fs'
import path from 'node:path'

const envPath = path.join(process.cwd(), '.env')
try {
  const content = fs.readFileSync(envPath, 'utf-8')
  for (const line of content.split(/\r?\n/)) {
    const s = line.trim()
    if (!s || s.startsWith('#') || !s.includes('=')) continue
    const [k, v] = s.split('=', 2)
    process.env[k] = v
  }
} catch {}

const { default: start } = await import('../.output/server/index.mjs')
if (typeof start === 'function') await start()
