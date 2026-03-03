import DefaultTheme from 'vitepress/theme'
import './custom.css'
import { h } from 'vue'
import TelegramButton from './components/TelegramButton.vue'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'sidebar-nav-after': () => h(TelegramButton)
    })
  }
}

