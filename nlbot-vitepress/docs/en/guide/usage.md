---
title: Usage Manual
description: How to use various features of TelegramPress
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: usage, manual, bot commands, admin panel
---

# Usage Manual

This manual will guide you on how to use the admin panel as an administrator and how users interact with the Telegram bot.

## Bot Commands (User Side)

Common commands for users interacting with the Telegram bot:

- `/start` - Start the bot, view main menu
- `Buy Energy` - Click menu button, select duration and amount
- `Check Order` - Query status of recent leasing orders
- `User Center` - View balance, referral link, etc.
- `Contact Support` - Get customer service contact info

## Admin Panel (Admin Side)

After accessing the admin panel address and logging in, you can see the following modules:

### 1. Dashboard
View system overview data, including today's order count, total turnover, new users, etc.

### 2. Order Management
- **Energy Orders**: View energy leasing records of all users, support filtering by status (Success, Failed, In Progress).
- **Compensate Order**: For failed orders, manually attempt to compensate or refund.

### 3. User Management
- View list of all users who have used the bot.
- Modify user balance (Recharge/Deduct).
- Ban violating users.

### 4. Bot Management
- **Restart Bot**: Click this button to apply changes after modifying configuration.
- **Push Message**: Broadcast messages to all users or specific users.

### 5. Energy Pool Integration
- Create Energy Pool Account: Generate API Key for external calls.
- Integrate 3rd Party Pool: Configure upstream energy pool API information.

## FAQ

### Q: What if the bot doesn't respond?
A: 
1. Check if Docker containers are running normally (`docker compose ps`).
2. Check `bot` container logs (`docker compose logs -f bot`) for errors.
3. Confirm if Token is correct and if server network can connect to Telegram API.

### Q: Energy not received?
A:
1. Check if the payout address has enough TRX for transaction fees (if needed).
2. Check if the energy pool has enough idle energy.
3. View error messages in order details on the admin panel.

::: tip Maintenance Advice
Regularly backup the database (`nl-admin.sql` or `/var/lib/mysql` directory) to prevent data loss.
:::
