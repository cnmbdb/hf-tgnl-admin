---
title: TGBot-Ultra
description: TGBot-Ultra 文档首页
layout: doc
sidebar: true
aside: true
outline: [2, 3]
lastUpdated: true
---

# TGBot-Ultra

欢迎来到 TGBot-Ultra 文档中心。这是一个功能强大的 Telegram 机器人综合管理系统，支持能量租赁、会员订阅、虚拟商城等多种业务场景。

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg> 文档导航

请选择您需要了解的内容：

<div class="VPFeatures">
  <div class="VPFeature">
    <div class="box">
      <div class="icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
      </div>
      <h2 class="title">项目介绍</h2>
      <p class="details">了解 TGBot-Ultra 的核心功能、技术架构与适用场景。</p>
      <a href="/tgbot-Ultra/introduction" class="link">阅读更多 →</a>
    </div>
  </div>
  <div class="VPFeature">
    <div class="box">
      <div class="icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
      </div>
      <h2 class="title">部署指南</h2>
      <p class="details">快速在您的服务器上安装和部署 TGBot-Ultra 系统。</p>
      <a href="/tgbot-Ultra/getting-started" class="link">开始部署 →</a>
    </div>
  </div>
  <div class="VPFeature">
    <div class="box">
      <div class="icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
      </div>
      <h2 class="title">使用手册</h2>
      <p class="details">后台功能操作说明、机器人配置与日常运维命令。</p>
      <a href="/tgbot-Ultra/usage" class="link">查看手册 →</a>
    </div>
  </div>
</div>

<style>
.VPFeatures {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(224px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.VPFeature {
  border: 1px solid var(--vp-c-bg-soft);
  border-radius: 12px;
  background-color: var(--vp-c-bg-soft);
  transition: border-color 0.25s, background-color 0.25s;
}

.VPFeature:hover {
  border-color: var(--vp-c-brand-1);
}

.VPFeature .box {
  display: flex;
  flex-direction: column;
  padding: 24px;
  height: 100%;
}

.VPFeature .icon {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  border-radius: 6px;
  background-color: var(--vp-c-default-soft);
  width: 48px;
  height: 48px;
  font-size: 24px;
  transition: background-color 0.25s;
}

.VPFeature .title {
  line-height: 24px;
  font-size: 16px;
  font-weight: 600;
}

.VPFeature .details {
  flex-grow: 1;
  padding-top: 8px;
  line-height: 24px;
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-2);
}

.VPFeature .link {
  margin-top: 12px;
  color: var(--vp-c-brand-1);
  font-weight: 500;
  text-decoration: none;
}

.VPFeature .link:hover {
  color: var(--vp-c-brand-2);
  text-decoration: underline;
}
</style>
