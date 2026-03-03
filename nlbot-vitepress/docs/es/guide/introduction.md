---
title: Introducción
description: Introducción detallada al proyecto TelegramPress (TGNL Admin)
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

# Introducción

**TelegramPress (TGNL Admin)** es un sistema de alquiler de energía Tron (TRX) y entrega automática basado en Telegram Bot y Panel de Administración Web. Integra gestión de grupo de energía, monitoreo automático y compra de autoservicio del usuario, con el objetivo de proporcionar servicios convenientes de adquisición de energía para los usuarios del ecosistema Tron.

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> Vista Previa

<div class="screenshot-grid">
  <div class="screenshot-card">
    <img src="/images/preview-1.png" alt="Panel de Control" class="screenshot-img" />
    <div class="screenshot-caption">Panel de Control - Monitoreo de Negocios en Tiempo Real</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-2.png" alt="Gestión de Bot" class="screenshot-img" />
    <div class="screenshot-caption">Gestión de Bot - Configuración Visual</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-3.png" alt="Teclado Personalizado" class="screenshot-img" />
    <div class="screenshot-caption">Teclado Personalizado - Interacción Flexible</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-4.png" alt="Configuración del Sistema" class="screenshot-img" />
    <div class="screenshot-caption">Configuración del Sistema - Parámetros Globales</div>
  </div>
</div>

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg> Características Principales

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg> Bot Inteligente
- **Comercio Automatizado**: Respuesta automática 24/7 a los pedidos de los usuarios, entrega instantánea de energía.
- **Respuestas Personalizadas**: Soporte para respuestas de palabras clave personalizadas, mensajes de bienvenida y guías de operación.
- **Distribución Multinivel**: Mecanismo de reembolso de invitación integrado para promover el crecimiento de usuarios.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> Potente Panel de Administración
- **Panel Visual**: Visualización en tiempo real de métricas clave como volumen de pedidos, facturación y nuevos usuarios.
- **Programación Multi-Pool**: Soporte para agregar múltiples API de grupo de energía, equilibrio de carga inteligente para garantizar un suministro estable.
- **Perfil de Usuario**: Registros detallados del comportamiento del usuario, soporte para prohibiciones, ajustes de saldo, etc.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> Seguridad y Estabilidad
- **Almacenamiento Local de Clave Privada**: Las claves privadas de pago están encriptadas y almacenadas solo en el servidor local para garantizar la seguridad de los fondos.
- **Contenedorización Docker**: Aislamiento de servicios, implementación simple y fuerte escalabilidad.
- **Alertas Automáticas**: Notificar automáticamente a los administradores sobre anomalías del sistema o energía insuficiente.

## Descripción General de la Arquitectura

El proyecto consta de los siguientes componentes principales:

- **Servicio de Bot (Python)**: Maneja mensajes de Telegram, interacciones de usuario, procesamiento de pedidos e interacciones en cadena.
- **Servicio Web (Nuxt/Node.js)**: Proporciona API de administración y páginas frontend.
- **Base de Datos (MySQL/Redis)**: Almacena datos de usuario, registros de pedidos y colas de caché.
- **Nginx**: Actúa como un servidor proxy inverso que maneja solicitudes HTTP.

## Casos de Uso

- **Proveedores de Alquiler de Energía**: Construya su propia plataforma de alquiler de energía y venda energía automáticamente a través de TG Bot.
- **Desarrolladores Tron**: Integre la funcionalidad de alquiler de energía en sus propias aplicaciones.
- **Gerentes de Comunidad**: Proporcione beneficios de alquiler de energía de bajo costo a los miembros de la comunidad.

::: tip Nota
La versión de código abierto de este proyecto es solo para fines de aprendizaje e investigación. Cumpla con las licencias de código abierto relevantes para uso comercial.
:::