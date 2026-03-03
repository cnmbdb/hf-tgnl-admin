---
title: Configuração
description: Guia detalhado de configuração do sistema
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

# Guia de Configuração

A configuração para TelegramPress consiste em duas partes principais: Variáveis de Ambiente (`.env`) e Configuração do Aplicativo Bot (`al.py` / `config.txt`).

## Variáveis de Ambiente (.env)

O arquivo `.env` controla as configurações básicas para contêineres Docker, como conexões de banco de dados e mapeamento de portas.

```bash
# Configuração do Banco de Dados
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=tgnl
MYSQL_USER=tgnl_user
MYSQL_PASSWORD=your_db_password

# Porta de Serviço Web
PORT=35474

# Outras configurações do sistema...
```

::: warning Aviso de Segurança
Por favor, altere a senha padrão do banco de dados para evitar ataques de força bruta.
:::

## Configuração do Bot

A configuração lógica central para o bot geralmente está localizada no topo de `nl-2333/al.py` ou em um arquivo de configuração no mesmo diretório.

### Parâmetros Principais

| Parâmetro | Descrição | Exemplo |
| :--- | :--- | :--- |
| `api_key` | Chave API do Pool de Energia | `your_api_key` |
| `privateKey` | Chave Privada da Carteira de Pagamento | `xxxxxxxx` (Manter em segredo) |
| `control_address` | Endereço da Carteira de Recebimento | `TRX_Address...` |
| `username` | Nome de Usuário da API | `HFTGID` |
| `CUSTOMER_SERVICE_ID` | Link/ID do TG de Atendimento ao Cliente | `https://t.me/service` |

### Configuração de Preços

Você pode definir preços unitários para aluguel de energia de diferentes durações:

- `hour_price`: Preço unitário de 1 hora
- `day_price`: Preço unitário de 1 dia
- `three_day_price`: Preço unitário de 3 dias
- `yucun_price`: Preço unitário de pré-depósito

## Configuração do Painel de Administração

Depois de fazer login no Painel de Administração Web, você também pode executar a configuração dinâmica:

1. **Gerenciamento de Bot**: Definir Token, ID de Admin.
2. **Configuração do Pool de Energia**: Adicione e gerencie nós de pool de energia conectados.
3. **Gerenciamento de Produtos**: Liste ou remova pacotes de aluguel de energia.

::: tip Nota
Depois de modificar `.env` ou configurações de nível de código, você geralmente precisa reiniciar os contêineres para aplicar as alterações:
`docker compose restart`
:::