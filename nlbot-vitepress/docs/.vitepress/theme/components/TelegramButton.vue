<script setup>
import { computed } from 'vue'

// 计算 Telegram 链接，可以根据需要扩展逻辑
const tgLink = 'https://t.me/HFTGID'
</script>

<template>
  <div class="tg-footer-action">
    <a :href="tgLink" target="_blank" class="tg-button">
      <!-- Telegram 图标 SVG -->
      <svg class="tg-icon" viewBox="0 0 24 24" width="24" height="24" xmlns="http://www.w3.org/2000/svg">
        <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 11.944 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" fill="currentColor"/>
      </svg>
      <span>联系Telegram</span>
    </a>
  </div>
</template>

<style scoped>
.tg-footer-action {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  margin-bottom: 16px;
  padding: 0 12px;
}

.tg-button {
  display: inline-flex;
  align-items: center;
  /* 修改：去掉 justify-content: center，改为 flex-start 让内容靠左 */
  justify-content: flex-start;
  gap: 12px; /* 增加图标和文字的间距 */
  /* 修改：统一 padding，让左边间隙固定，右边留白 */
  padding: 8px 24px 8px 8px;
  width: auto;
  min-width: auto;
  max-width: 100%;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  text-decoration: none !important;
  
  /* 默认浅色模式样式：Telegram 蓝背景，白色文字/图标 */
  background-color: #229ED9;
  color: #ffffff !important;
}

.tg-button span {
  flex-grow: 1;
  text-align: left; /* 让文字自然跟随 */
  padding-right: 0; /* 不需要额外的 padding 了 */
}

.tg-button:hover {
  background-color: #1a8cc4;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(34, 158, 217, 0.3);
}

.tg-icon {
  fill: currentColor;
}

/* 深色模式样式：保持 Telegram 蓝背景，黑色文字/图标 */
:global(.dark) .tg-button {
  background-color: #229ED9;
  color: #000000 !important;
}

:global(.dark) .tg-button:hover {
  background-color: #40a7e3; /* 深色模式下 hover 稍微亮一点 */
  box-shadow: 0 4px 12px rgba(34, 158, 217, 0.4);
}
</style>
