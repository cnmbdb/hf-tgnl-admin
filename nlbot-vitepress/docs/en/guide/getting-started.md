---
title: Quick Start
description: Installation and deployment guide for TelegramPress
layout: doc
sidebar: true
aside: true
outline: [2, 3]
editLink: true
lastUpdated: true
head:
  - - meta
    - name: keywords
      content: install, deploy, docker, setup
---

# Quick Start

This guide will help you quickly deploy the TelegramPress system on your server. We recommend using Docker Compose for deployment, as it is the simplest and most stable method.

## Prerequisites

Before starting, please ensure your server meets the following requirements:

- **OS**: Any Linux distribution (Ubuntu 20.04+ / Debian 10+ recommended)
- **Dependencies**:
  - [Docker](https://docs.docker.com/get-docker/)
  - [Docker Compose](https://docs.docker.com/compose/install/)
- **Hardware**: Recommended 2 cores, 4G RAM or higher
- **Network**: Server must be able to access Telegram API and Tron nodes

## Deployment Steps

### 1. Prepare Server & Install Panel (Optional)

If you prefer a graphical interface, you can install the Baota (aaPanel) panel.
If you are familiar with the command line, you can operate directly in the terminal.

### 2. Get Source Code

Upload the project source code to your server, or clone the repository directly (assuming you have Git):

<a href="https://github.com/cnmbdb/hf-tgnl-admin" target="_blank" class="vp-button-green">
  <svg height="20" viewBox="0 0 16 16" version="1.1" width="20" aria-hidden="true" style="margin-right: 8px; fill: currentColor;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
  Download Source
</a>

```bash
# Create directory
mkdir -p /www/wwwroot/tgnl-admin
cd /www/wwwroot/tgnl-admin

# Upload source files to this directory and unzip
# Ensure the directory structure contains docker-compose.yml
```

### 3. File Permissions

To ensure services in Docker containers can read/write files properly, setting permissions is recommended:

```bash
# Set directory permissions
chmod -R 777 .
```

### 4. Configure Environment Variables

Copy the example configuration file and modify it:

```bash
# Copy env file
cp .env.example .env

# Edit config file
vim .env
```

You need to modify key information in the `.env` file (such as database password, port, etc.). Also, check `nl-2333/config.txt` (if exists) or relevant Bot configuration files.

### 5. Start Services

Use Docker Compose to build and start all services:

```bash
docker compose up -d --build
```

This command will automatically download dependencies, build images, and start the admin panel, database, and bot services.

::: info Waiting for Startup
The first build may take a few minutes, please be patient.
:::

### 6. Verify Deployment

Check container status:

```bash
docker compose ps
```

If all containers are in `Up` state, the startup is successful.

Access the Admin Panel:
- Open browser and visit: `http://ServerIP:35474` (Port defaults to 35474, or the port you set in `.env`)

## Initial Setup

1. **Login to Admin Panel**
   - Default Username: `admin`
   - Default Password: `admin123`
   
2. **Authorization Activation**
   - Go to Admin Panel -> Authorization
   - Enter activation code (for open source or test versions, there might be specific activation methods, or just use it directly)

3. **Configure Bot**
   - Go to Admin Panel -> Bot Management
   - Enter Bot Token (Get from [@BotFather](https://t.me/BotFather))
   - Enter Admin TG ID
   - Click Save and Restart Bot

::: tip Congratulations
Your TelegramPress system has been successfully deployed and is running!
:::
