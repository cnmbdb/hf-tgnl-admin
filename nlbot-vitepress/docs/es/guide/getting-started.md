---
title: Inicio Rápido
description: Guía de instalación y despliegue para TelegramPress
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

# Inicio Rápido

Esta guía le ayudará a desplegar rápidamente el sistema TelegramPress en su servidor. Recomendamos utilizar Docker Compose para el despliegue, ya que es el método más simple y estable.

## Prerrequisitos

Antes de comenzar, asegúrese de que su servidor cumpla con los siguientes requisitos:

- **SO**: Cualquier distribución de Linux (se recomienda Ubuntu 20.04+ / Debian 10+)
- **Dependencias**:
  - [Docker](https://docs.docker.com/get-docker/)
  - [Docker Compose](https://docs.docker.com/compose/install/)
- **Hardware**: Recomendado 2 núcleos, 4 GB de RAM o superior
- **Red**: El servidor debe poder acceder a la API de Telegram y a los nodos Tron

## Pasos de Despliegue

### 1. Preparar Servidor e Instalar Panel (Opcional)

Si prefiere una interfaz gráfica, puede instalar el panel Baota (aaPanel).
Si está familiarizado con la línea de comandos, puede operar directamente en la terminal.

### 2. Obtener Código Fuente

Suba el código fuente del proyecto a su servidor, o clone el repositorio directamente (suponiendo que tenga Git):

<a href="https://github.com/cnmbdb/hf-tgnl-admin" target="_blank" class="vp-button-green">
  <svg height="20" viewBox="0 0 16 16" version="1.1" width="20" aria-hidden="true" style="margin-right: 8px; fill: currentColor;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
  Descargar Fuente
</a>

```bash
# Crear directorio
mkdir -p /www/wwwroot/tgnl-admin
cd /www/wwwroot/tgnl-admin

# Suba los archivos fuente a este directorio y descomprima
# Asegúrese de que la estructura del directorio contenga docker-compose.yml
```

### 3. Permisos de Archivo

Para asegurar que los servicios en contenedores Docker puedan leer/escribir archivos correctamente, se recomienda establecer permisos:

```bash
# Establecer permisos de directorio
chmod -R 777 .
```

### 4. Configurar Variables de Entorno

Copie el archivo de configuración de ejemplo y modifíquelo:

```bash
# Copiar archivo env
cp .env.example .env

# Editar archivo de configuración
vim .env
```

Necesita modificar la información clave en el archivo `.env` (como contraseña de base de datos, puerto, etc.). Además, verifique `nl-2333/config.txt` (si existe) o archivos de configuración de Bot relevantes.

### 5. Iniciar Servicios

Use Docker Compose para construir e iniciar todos los servicios:

```bash
docker compose up -d --build
```

Este comando descargará automáticamente las dependencias, construirá imágenes e iniciará el panel de administración, la base de datos y los servicios de bot.

::: info Esperando Inicio
La primera compilación puede tardar unos minutos, por favor tenga paciencia.
:::

### 6. Verificar Despliegue

Verifique el estado del contenedor:

```bash
docker compose ps
```

Si todos los contenedores están en estado `Up`, el inicio fue exitoso.

Acceder al Panel de Administración:
- Abra el navegador y visite: `http://IPdelServidor:35474` (Puerto por defecto 35474, o el puerto que configuró en `.env`)

## Configuración Inicial

1. **Iniciar Sesión en Panel de Administración**
   - Nombre de usuario predeterminado: `admin`
   - Contraseña predeterminada: `admin123`
   
2. **Activación de Autorización**
   - Vaya a Panel de Administración -> Autorización
   - Ingrese el código de activación (para versiones de código abierto o de prueba, puede haber métodos de activación específicos, o simplemente úselo directamente)

3. **Configurar Bot**
   - Vaya a Panel de Administración -> Gestión de Bot
   - Ingrese el Token del Bot (Obtenga de [@BotFather](https://t.me/BotFather))
   - Ingrese el ID de Admin TG
   - Haga clic en Guardar y Reiniciar Bot

::: tip Felicidades
¡Su sistema TelegramPress ha sido desplegado exitosamente y está funcionando!
:::