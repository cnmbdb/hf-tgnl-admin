#!/usr/bin/env node

/**
 * 获取本机公网IP地址
 */

const services = [
  { url: 'https://api.ipify.org?format=json', type: 'json' },
  { url: 'https://ipinfo.io/ip', type: 'text' },
  { url: 'https://api.ip.sb/ip', type: 'text' },
  { url: 'https://ifconfig.me/ip', type: 'text' },
  { url: 'https://icanhazip.com', type: 'text' },
  { url: 'https://checkip.amazonaws.com', type: 'text' }
]

async function getPublicIP() {
  for (const service of services) {
    try {
      const response = await fetch(service.url, { 
        signal: AbortSignal.timeout(5000)
      })
      
      let ip = ''
      if (service.type === 'json') {
        const data = await response.json()
        ip = data.ip || ''
      } else {
        ip = (await response.text()).trim()
      }
      
      if (ip && /^(\d{1,3}\.){3}\d{1,3}$/.test(ip)) {
        return ip
      }
    } catch (error) {
      console.warn(`从 ${service.url} 获取IP失败:`, error.message)
      continue
    }
  }
  
  throw new Error('无法获取公网IP')
}

getPublicIP()
  .then(ip => {
    console.log('本机公网IP:', ip)
    process.exit(0)
  })
  .catch(error => {
    console.error('错误:', error.message)
    process.exit(1)
  })
