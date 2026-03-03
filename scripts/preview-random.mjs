import net from 'node:net'
import { spawn } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'

function randomPort(min = 20000, max = 50000) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function randomToken() {
  return 'adm-' + Math.random().toString(36).slice(2, 8)
}

function checkPort(port) {
  return new Promise((resolve) => {
    const server = net.createServer()
    server.once('error', () => resolve(false))
    server.once('listening', () => {
      server.close(() => resolve(true))
    })
    server.listen(port, '0.0.0.0')
  })
}

async function pickAvailablePort() {
  for (let i = 0; i < 10; i++) {
    const p = randomPort()
    // eslint-disable-next-line no-await-in-loop
    const ok = await checkPort(p)
    if (ok) return p
  }
  return 3000
}

const writeOnly = process.env.WRITE_ENV_ONLY === '1'
// Docker 构建 / 生产环境禁止随机改写 .env（否则会把 baseURL/PORT 写成随机值，导致部署后路径漂移）
const disableRandomEnv = process.env.DISABLE_RANDOM_ENV === '1' || process.env.NO_RANDOM_ENV === '1'

// prebuild 场景只需要“不要改写”，直接退出即可
if (disableRandomEnv && writeOnly) {
  console.log('Random env is disabled (DISABLE_RANDOM_ENV=1). Keeping existing .env PORT/APP_BASE_PATH.')
  process.exit(0)
}
const port = await pickAvailablePort()
const token = randomToken()
process.env.PORT = String(port)
process.env.APP_BASE_PATH = `/${token}`
console.log(`${writeOnly ? 'Writing env with' : 'Building with'} base /${token} and ${writeOnly ? '' : 'starting on '}port ${port}`)

const envPath = path.join(process.cwd(), '.env')
let envContent = ''
try { envContent = fs.readFileSync(envPath, 'utf-8') } catch {}
const lines = envContent ? envContent.split(/\r?\n/) : []
const setKV = (k, v) => {
  const idx = lines.findIndex(l => l.trim().startsWith(k + '='))
  const val = `${k}=${v}`
  if (idx >= 0) lines[idx] = val
  else lines.push(val)
}
const getKV = (k) => {
  const idx = lines.findIndex(l => l.trim().startsWith(k + '='))
  if (idx < 0) return ''
  const s = lines[idx]
  return s.substring(s.indexOf('=') + 1).trim()
}
const bumpPatch = (v) => {
  const raw = String(v || '0.0.0').replace(/^v/i, '')
  const parts = raw.split('.')
  while (parts.length < 3) parts.push('0')
  const maj = parseInt(parts[0] || '0', 10)
  const min = parseInt(parts[1] || '0', 10)
  const pat = parseInt(parts[2] || '0', 10) + 1
  return `${maj}.${min}.${pat}`
}
setKV('APP_BASE_PATH', `/${token}`)
setKV('PORT', String(port))
const currentVer = process.env.APP_VERSION || getKV('APP_VERSION') || '2.7.8'
const nextVer = bumpPatch(currentVer)
setKV('APP_VERSION', nextVer)
fs.writeFileSync(envPath, lines.join('\n'))

if (writeOnly) {
  console.log(`Updated .env -> APP_BASE_PATH=/${token}, PORT=${port}, APP_VERSION=${nextVer}`)
  process.exit(0)
}

await new Promise((resolve, reject) => {
  const child = spawn('npm', ['run', 'build'], {
    stdio: 'inherit',
  env: { ...process.env, APP_BASE_PATH: `/${token}` }
})
  child.on('exit', (code) => {
    if (code === 0) resolve()
    else reject(new Error(`Build failed with code ${code}`))
  })
})

const childServer = spawn('node', ['.output/server/index.mjs'], {
  stdio: 'inherit',
  env: { ...process.env, PORT: String(port), APP_BASE_PATH: `/${token}`, APP_VERSION: nextVer }
})
childServer.on('exit', (code) => {
  process.exit(code ?? 0)
})
