---
title: Introdução
description: Introdução detalhada ao projeto TelegramPress (TGNL Admin)
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

# Introdução

**TelegramPress (TGNL Admin)** é um sistema de aluguel de energia Tron (TRX) e entrega automática baseado no Telegram Bot e Painel de Administração Web. Ele integra gerenciamento de pool de energia, monitoramento automático e compra de autoatendimento do usuário, visando fornecer serviços convenientes de aquisição de energia para usuários do ecossistema Tron.

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> Visualização

<div class="screenshot-grid">
  <div class="screenshot-card">
    <img src="/images/preview-1.png" alt="Painel" class="screenshot-img" />
    <div class="screenshot-caption">Painel - Monitoramento de Negócios em Tempo Real</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-2.png" alt="Gerenciamento de Bot" class="screenshot-img" />
    <div class="screenshot-caption">Gerenciamento de Bot - Configuração Visual</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-3.png" alt="Teclado Personalizado" class="screenshot-img" />
    <div class="screenshot-caption">Teclado Personalizado - Interação Flexível</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-4.png" alt="Configurações do Sistema" class="screenshot-img" />
    <div class="screenshot-caption">Configurações do Sistema - Parâmetros Globais</div>
  </div>
</div>

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg> Recursos Principais

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg> Bot Inteligente
- **Negociação Automatizada**: Resposta automática 24/7 aos pedidos dos usuários, entrega instantânea de energia.
- **Respostas Personalizadas**: Suporte a respostas por palavras-chave personalizadas, mensagens de boas-vindas e guias de operação.
- **Distribuição Multinível**: Mecanismo de reembolso de convite integrado para promover o crescimento de usuários.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> Painel de Administração Poderoso
- **Painel Visual**: Exibição em tempo real de métricas importantes como volume de pedidos, faturamento e novos usuários.
- **Agendamento Multi-Pool**: Suporte para adicionar várias APIs de pool de energia, balanceamento de carga inteligente para garantir fornecimento estável.
- **Perfil de Usuário**: Registros detalhados de comportamento do usuário, suportando banimentos, ajustes de saldo, etc.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> Segurança e Estabilidade
- **Armazenamento Local de Chave Privada**: As chaves privadas de pagamento são criptografadas e armazenadas apenas no servidor local para garantir a segurança dos fundos.
- **Containerização Docker**: Isolamento de serviços, implantação simples e forte escalabilidade.
- **Alertas Automáticos**: Notificar automaticamente os administradores sobre anomalias do sistema ou energia insuficiente.

## Visão Geral da Arquitetura

O projeto consiste nos seguintes componentes principais:

- **Serviço de Bot (Python)**: Lida com mensagens do Telegram, interações do usuário, processamento de pedidos e interações na cadeia.
- **Serviço Web (Nuxt/Node.js)**: Fornece API de administração e páginas de frontend.
- **Banco de Dados (MySQL/Redis)**: Armazena dados do usuário, registros de pedidos e filas de cache.
- **Nginx**: Atua como um servidor proxy reverso lidando com solicitações HTTP.

## Casos de Uso

- **Provedores de Aluguel de Energia**: Construa sua própria plataforma de aluguel de energia e venda energia automaticamente via TG Bot.
- **Desenvolvedores Tron**: Integre a funcionalidade de aluguel de energia em seus próprios aplicativos.
- **Gerentes de Comunidade**: Forneça benefícios de aluguel de energia de baixo custo aos membros da comunidade.

::: tip Nota
A versão de código aberto deste projeto é apenas para fins de aprendizado e pesquisa. Cumpra as licenças de código aberto relevantes para uso comercial.
:::