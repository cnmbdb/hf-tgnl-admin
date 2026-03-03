---
title: Início Rápido
description: Guia de instalação e implantação do TelegramPress
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

# Início Rápido

Este guia o ajudará a implantar rapidamente o sistema TelegramPress em seu servidor. Recomendamos usar o Docker Compose para implantação, pois é o método mais simples e estável.

## Pré-requisitos

Antes de começar, certifique-se de que seu servidor atenda aos seguintes requisitos:

- **SO**: Qualquer distribuição Linux (Ubuntu 20.04+ / Debian 10+ recomendado)
- **Dependências**:
  - [Docker](https://docs.docker.com/get-docker/)
  - [Docker Compose](https://docs.docker.com/compose/install/)
- **Hardware**: Recomendado 2 núcleos, 4 GB de RAM ou superior
- **Rede**: O servidor deve ser capaz de acessar a API do Telegram e nós Tron

## Etapas de Implantação

### 1. Preparar Servidor e Instalar Painel (Opcional)

Se você preferir uma interface gráfica, pode instalar o painel Baota (aaPanel).
Se você estiver familiarizado com a linha de comando, pode operar diretamente no terminal.

### 2. Obter Código Fonte

Carregue o código-fonte do projeto para o seu servidor ou clone o repositório diretamente (supondo que você tenha Git):

<a href="https://github.com/cnmbdb/hf-tgnl-admin" target="_blank" class="vp-button-green">
  <svg height="20" viewBox="0 0 16 16" version="1.1" width="20" aria-hidden="true" style="margin-right: 8px; fill: currentColor;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
  Baixar Fonte
</a>

```bash
# Criar diretório
mkdir -p /www/wwwroot/tgnl-admin
cd /www/wwwroot/tgnl-admin

# Carregue os arquivos de origem para este diretório e descompacte
# Certifique-se de que a estrutura do diretório contenha docker-compose.yml
```

### 3. Permissões de Arquivo

Para garantir que os serviços nos contêineres Docker possam ler/gravar arquivos corretamente, é recomendável definir permissões:

```bash
# Definir permissões de diretório
chmod -R 777 .
```

### 4. Configurar Variáveis de Ambiente

Copie o arquivo de configuração de exemplo e modifique-o:

```bash
# Copiar arquivo env
cp .env.example .env

# Editar arquivo de configuração
vim .env
```

Você precisa modificar as informações principais no arquivo `.env` (como senha do banco de dados, porta, etc.). Além disso, verifique `nl-2333/config.txt` (se existir) ou arquivos de configuração de Bot relevantes.

### 5. Iniciar Serviços

Use o Docker Compose para construir e iniciar todos os serviços:

```bash
docker compose up -d --build
```

Este comando baixará automaticamente as dependências, construirá imagens e iniciará o painel de administração, banco de dados e serviços de bot.

::: info Aguardando Inicialização
A primeira compilação pode levar alguns minutos, por favor, seja paciente.
:::

### 6. Verificar Implantação

Verifique o status do contêiner:

```bash
docker compose ps
```

Se todos os contêineres estiverem no estado `Up`, a inicialização foi bem-sucedida.

Acesse o Painel de Administração:
- Abra o navegador e visite: `http://IPdoServidor:35474` (Porta padrão para 35474, ou a porta que você definiu em `.env`)

## Configuração Inicial

1. **Login no Painel de Administração**
   - Nome de usuário padrão: `admin`
   - Senha padrão: `admin123`
   
2. **Ativação de Autorização**
   - Vá para Painel de Administração -> Autorização
   - Digite o código de ativação (para versões de código aberto ou teste, pode haver métodos de ativação específicos ou apenas use diretamente)

3. **Configurar Bot**
   - Vá para Painel de Administração -> Gerenciamento de Bot
   - Digite o Token do Bot (Obtenha em [@BotFather](https://t.me/BotFather))
   - Digite o ID do Admin TG
   - Clique em Salvar e Reiniciar Bot

::: tip Parabéns
Seu sistema TelegramPress foi implantado com sucesso e está em execução!
:::