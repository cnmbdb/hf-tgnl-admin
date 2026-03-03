import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app/**/*.{vue,js,ts}',
    './nuxt.config.{js,ts}',
  ],
  theme: {
    extend: {
      colors: {
        /**
         * primary 颜色用于 @nuxt/ui，确保
         * - bg-primary-*
         * - text-primary-*
         * - ring-primary-*
         * - outline-primary
         * 等工具类都可以正常生成，避免 dev 模式下的报错。
         * 这里使用的是 Tailwind 默认的 emerald 调色板。
         */
        primary: {
          50: '#ecfdf3',
          100: '#dcfce7',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          900: '#14532d',
          950: '#052e16',
          DEFAULT: '#22c55e',
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [],
}

export default config

