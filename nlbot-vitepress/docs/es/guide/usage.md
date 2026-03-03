---
title: Manual de Uso
description: Cómo usar varias funciones de TelegramPress
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

Este manual le guiará sobre cómo usar el panel de administración como administrador y cómo los usuarios interactúan con el bot de Telegram.

## Comandos del Bot (Lado del Usuario)

Comandos comunes para usuarios que interactúan con el bot de Telegram:

- `/start` - Iniciar el bot, ver menú principal
- `Comprar Energía` - Haga clic en el botón del menú, seleccione la duración y el monto
- `Verificar Pedido` - Consultar estado de pedidos de alquiler recientes
- `Centro de Usuario` - Ver saldo, enlace de referencia, etc.
- `Contactar Soporte` - Obtener información de contacto de servicio al cliente

## Panel de Administración (Lado del Administrador)

Después de acceder a la dirección del panel de administración e iniciar sesión, puede ver los siguientes módulos:

### 1. Panel de Control
Vea datos generales del sistema, incluido el recuento de pedidos de hoy, la facturación total, nuevos usuarios, etc.

### 2. Gestión de Pedidos
- **Pedidos de Energía**: Vea registros de alquiler de energía de todos los usuarios, soporte de filtrado por estado (Éxito, Fallido, En Progreso).
- **Compensar Pedido**: Para pedidos fallidos, intente compensar o reembolsar manualmente.

### 3. Gestión de Usuarios
- Vea la lista de todos los usuarios que han usado el bot.
- Modifique el saldo del usuario (Recarga/Deducción).
- Prohibir usuarios infractores.

### 4. Gestión de Bot
- **Reiniciar Bot**: Haga clic en este botón para aplicar los cambios después de modificar la configuración.
- **Mensaje Push**: Transmita mensajes a todos los usuarios o usuarios específicos.

### 5. Integración de Grupo de Energía
- Crear Cuenta de Grupo de Energía: Generar Clave API para llamadas externas.
- Integrar Grupo de Terceros: Configurar información de API de grupo de energía upstream.

## Preguntas Frecuentes (FAQ)

### P: ¿Qué pasa si el bot no responde?
R: 
1. Verifique si los contenedores Docker se están ejecutando normalmente (`docker compose ps`).
2. Verifique los registros del contenedor `bot` (`docker compose logs -f bot`) en busca de errores.
3. Confirme si el Token es correcto y si la red del servidor puede conectarse a la API de Telegram.

### P: ¿Energía no recibida?
R:
1. Verifique si la dirección de pago tiene suficiente TRX para las tarifas de transacción (si es necesario).
2. Verifique si el grupo de energía tiene suficiente energía inactiva.
3. Vea los mensajes de error en los detalles del pedido en el panel de administración.

::: tip Consejo de Mantenimiento
Realice copias de seguridad periódicas de la base de datos (`nl-admin.sql` o directorio `/var/lib/mysql`) para evitar la pérdida de datos.
:::