---
title: Introduction
description: Detailed introduction to TelegramPress (TGNL Admin) project
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: telegram, bot, tron, energy, leasing, admin
---

# Introduction

**TelegramPress (TGNL Admin)** is a Tron (TRX) energy leasing and automatic delivery system based on Telegram Bot and Web Admin Panel. It integrates energy pool management, automatic monitoring, and user self-service purchasing, aiming to provide convenient energy acquisition services for Tron ecosystem users.

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> Preview

<div class="screenshot-grid">
  <div class="screenshot-card">
    <img src="/images/preview-1.png" alt="Dashboard" class="screenshot-img" />
    <div class="screenshot-caption">Dashboard - Real-time Business Monitoring</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-2.png" alt="Bot Management" class="screenshot-img" />
    <div class="screenshot-caption">Bot Management - Visual Configuration</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-3.png" alt="Custom Keyboard" class="screenshot-img" />
    <div class="screenshot-caption">Custom Keyboard - Flexible Interaction</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-4.png" alt="System Settings" class="screenshot-img" />
    <div class="screenshot-caption">System Settings - Global Parameters</div>
  </div>
</div>

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg> Core Features

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg> Smart Bot
- **Automated Trading**: 24/7 automatic response to user orders, instant energy delivery.
- **Custom Replies**: Support custom keyword replies, welcome messages, and operation guides.
- **Multi-level Distribution**: Built-in invitation rebate mechanism to promote user growth.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> Powerful Admin Panel
- **Visual Dashboard**: Real-time display of key metrics like order volume, turnover, and new users.
- **Multi-Pool Scheduling**: Support adding multiple energy pool APIs, smart load balancing to ensure stable supply.
- **User Profiling**: Detailed user behavior records, supporting bans, balance adjustments, etc.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> Security & Stability
- **Local Private Key Storage**: Payout private keys are encrypted and stored only on the local server to ensure fund security.
- **Docker Containerization**: Service isolation, simple deployment, and strong scalability.
- **Auto Alerts**: Automatically notify administrators of system anomalies or insufficient energy.

## Architecture Overview

The project consists of the following main components:

- **Bot Service (Python)**: Handles Telegram messages, user interactions, order processing, and on-chain interactions.
- **Web Service (Nuxt/Node.js)**: Provides Admin API and frontend pages.
- **Database (MySQL/Redis)**: Stores user data, order records, and cache queues.
- **Nginx**: Acts as a reverse proxy server handling HTTP requests.

## Use Cases

- **Energy Leasing Providers**: Build your own energy leasing platform and sell energy automatically via TG Bot.
- **Tron Developers**: Integrate energy leasing functionality into your own applications.
- **Community Managers**: Provide low-cost energy leasing benefits to community members.

::: tip Note
The open-source version of this project is for learning and research purposes only. Please comply with relevant open-source licenses for commercial use.
:::
