import { addRouteMiddleware } from '#app'

export default defineNuxtPlugin(() => {
  if (process.dev) {
    addRouteMiddleware('manifest-route-rule', () => {}, { global: true, override: true })
  }
})
