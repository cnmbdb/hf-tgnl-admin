---
title: Configuration
description: Detailed system configuration guide
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: config, env, settings, parameters
---

# Configuration Guide

Configuration for TelegramPress consists of two main parts: Environment Variables (`.env`) and Bot Application Configuration (`al.py` / `config.txt`).

## Environment Variables (.env)

The `.env` file controls the basic settings for Docker containers, such as database connections and port mapping.

```bash
# Database Config
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=tgnl
MYSQL_USER=tgnl_user
MYSQL_PASSWORD=your_db_password

# Web Service Port
PORT=35474

# Other system configs...
```

::: warning Security Warning
Please change the default database password to prevent brute force attacks.
:::

## Bot Configuration

The core logic configuration for the bot is usually located at the top of `nl-2333/al.py` or in a configuration file in the same directory.

### Key Parameters

| Parameter | Description | Example |
| :--- | :--- | :--- |
| `api_key` | Energy Pool API Key | `your_api_key` |
| `privateKey` | Payout Wallet Private Key | `xxxxxxxx` (Keep secret) |
| `control_address` | Receiving Wallet Address | `TRX_Address...` |
| `username` | API Username | `HFTGID` |
| `CUSTOMER_SERVICE_ID` | Customer Service TG Link/ID | `https://t.me/service` |

### Pricing Configuration

You can set unit prices for energy leasing of different durations:

- `hour_price`: 1-hour unit price
- `day_price`: 1-day unit price
- `three_day_price`: 3-day unit price
- `yucun_price`: Pre-deposit unit price

## Admin Panel Configuration

After logging into the Web Admin Panel, you can also perform dynamic configuration:

1. **Bot Management**: Set Token, Admin ID.
2. **Energy Pool Config**: Add and manage connected energy pool nodes.
3. **Product Management**: List or delist energy leasing packages.

::: tip Note
After modifying `.env` or code-level configurations, you usually need to restart containers to apply changes:
`docker compose restart`
:::
