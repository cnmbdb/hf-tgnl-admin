---
title: Manual de Uso
description: Como usar vários recursos do TelegramPress
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

# Manual de Uso

Este manual irá guiá-lo sobre como usar o painel de administração como administrador e como os usuários interagem com o bot do Telegram.

## Comandos do Bot (Lado do Usuário)

Comandos comuns para usuários interagindo com o bot do Telegram:

- `/start` - Iniciar o bot, ver menu principal
- `Comprar Energia` - Clique no botão do menu, selecione a duração e o valor
- `Verificar Pedido` - Consultar status de pedidos de aluguel recentes
- `Central do Usuário` - Ver saldo, link de referência, etc.
- `Contatar Suporte` - Obter informações de contato do atendimento ao cliente

## Painel de Administração (Lado do Administrador)

Depois de acessar o endereço do painel de administração e fazer login, você pode ver os seguintes módulos:

### 1. Painel
Visualize os dados gerais do sistema, incluindo a contagem de pedidos de hoje, faturamento total, novos usuários, etc.

### 2. Gerenciamento de Pedidos
- **Pedidos de Energia**: Visualize registros de aluguel de energia de todos os usuários, suporte a filtragem por status (Sucesso, Falha, Em Progresso).
- **Compensar Pedido**: Para pedidos com falha, tente compensar ou reembolsar manualmente.

### 3. Gerenciamento de Usuários
- Visualize a lista de todos os usuários que usaram o bot.
- Modifique o saldo do usuário (Recarga/Dedução).
- Banir usuários infratores.

### 4. Gerenciamento de Bot
- **Reiniciar Bot**: Clique neste botão para aplicar as alterações após modificar a configuração.
- **Enviar Mensagem**: Transmita mensagens para todos os usuários ou usuários específicos.

### 5. Integração do Pool de Energia
- Criar Conta do Pool de Energia: Gerar Chave de API para chamadas externas.
- Integrar Pool de Terceiros: Configurar informações de API de pool de energia upstream.

## Perguntas Frequentes (FAQ)

### P: E se o bot não responder?
R: 
1. Verifique se os contêineres Docker estão funcionando normalmente (`docker compose ps`).
2. Verifique os logs do contêiner `bot` (`docker compose logs -f bot`) em busca de erros.
3. Confirme se o Token está correto e se a rede do servidor pode se conectar à API do Telegram.

### P: Energia não recebida?
R:
1. Verifique se o endereço de pagamento tem TRX suficiente para taxas de transação (se necessário).
2. Verifique se o pool de energia tem energia ociosa suficiente.
3. Visualize mensagens de erro nos detalhes do pedido no painel de administração.

::: tip Conselho de Manutenção
Faça backup regularmente do banco de dados (`nl-admin.sql` ou diretório `/var/lib/mysql`) para evitar perda de dados.
:::