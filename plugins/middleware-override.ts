export default defineNuxtPlugin((nuxtApp) => {
  const orig = nuxtApp.addRouteMiddleware
  nuxtApp.addRouteMiddleware = (name: any, middleware: any, opts: any = {}) => {
    if (name === 'manifest-route-rule') {
      const exists = Array.isArray((nuxtApp as any).middleware) && (nuxtApp as any).middleware.some((mw: any) => {
        const n = typeof mw === 'string' ? mw : (mw?.name || mw?.key || '')
        return n === 'manifest-route-rule'
      })
      if (exists) {
        return orig.call(nuxtApp, name, middleware, { ...opts, override: true })
      }
    }
    return orig.call(nuxtApp, name, middleware, opts)
  }
})
