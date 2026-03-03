export default defineNitroPlugin(() => {
  const originalWarn = console.warn
  console.warn = function (...args: any[]) {
    const msg = args.join(' ')
    if (msg.includes('manifest-route-rule') || msg.includes('middleware already exists')) return
    originalWarn.apply(console, args)
  }
})
