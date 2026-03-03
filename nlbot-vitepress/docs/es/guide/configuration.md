---
title: Configuración
description: Guía detallada de configuración del sistema
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

# Guía de Configuración

La configuración para TelegramPress consta de dos partes principales: Variables de Entorno (`.env`) y Configuración de la Aplicación Bot (`al.py` / `config.txt`).

## Variables de Entorno (.env)

El archivo `.env` controla la configuración básica para los contenedores Docker, como conexiones de base de datos y mapeo de puertos.

```bash
# Configuración de Base de Datos
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=tgnl
MYSQL_USER=tgnl_user
MYSQL_PASSWORD=your_db_password

# Puerto de Servicio Web
PORT=35474

# Otras configuraciones del sistema...
```

::: warning Advertencia de Seguridad
Por favor, cambie la contraseña predeterminada de la base de datos para evitar ataques de fuerza bruta.
:::

## Configuración del Bot

La configuración lógica central para el bot generalmente se encuentra en la parte superior de `nl-2333/al.py` o en un archivo de configuración en el mismo directorio.

### Parámetros Clave

| Parámetro | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `api_key` | Clave API del Grupo de Energía | `your_api_key` |
| `privateKey` | Clave Privada de Billetera de Pago | `xxxxxxxx` (Mantener en secreto) |
| `control_address` | Dirección de Billetera de Recepción | `TRX_Address...` |
| `username` | Nombre de Usuario de API | `HFTGID` |
| `CUSTOMER_SERVICE_ID` | Enlace/ID de TG de Servicio al Cliente | `https://t.me/service` |

### Configuración de Precios

Puede establecer precios unitarios para el alquiler de energía de diferentes duraciones:

- `hour_price`: Precio unitario de 1 hora
- `day_price`: Precio unitario de 1 día
- `three_day_price`: Precio unitario de 3 días
- `yucun_price`: Precio unitario de pre-depósito

## Configuración del Panel de Administración

Después de iniciar sesión en el Panel de Administración Web, también puede realizar la configuración dinámica:

1. **Gestión de Bot**: Establecer Token, ID de Administrador.
2. **Configuración de Grupo de Energía**: Agregue y administre nodos de grupo de energía conectados.
3. **Gestión de Productos**: Liste o elimine paquetes de alquiler de energía.

::: tip Nota
Después de modificar `.env` o configuraciones a nivel de código, generalmente necesita reiniciar los contenedores para aplicar los cambios:
`docker compose restart`
:::