---
title: Введение
description: Подробное введение в проект TelegramPress (TGNL Admin)
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

# Введение

**TelegramPress (TGNL Admin)** — это система аренды энергии Tron (TRX) и автоматической доставки на основе Telegram-бота и веб-панели администратора. Она объединяет управление пулом энергии, автоматический мониторинг и самообслуживание пользователей, стремясь предоставить удобные услуги по приобретению энергии для пользователей экосистемы Tron.

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg> Предпросмотр

<div class="screenshot-grid">
  <div class="screenshot-card">
    <img src="/images/preview-1.png" alt="Панель управления" class="screenshot-img" />
    <div class="screenshot-caption">Панель управления — Мониторинг бизнеса в реальном времени</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-2.png" alt="Управление ботом" class="screenshot-img" />
    <div class="screenshot-caption">Управление ботом — Визуальная конфигурация</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-3.png" alt="Пользовательская клавиатура" class="screenshot-img" />
    <div class="screenshot-caption">Пользовательская клавиатура — Гибкое взаимодействие</div>
  </div>
  <div class="screenshot-card">
    <img src="/images/preview-4.png" alt="Настройки системы" class="screenshot-img" />
    <div class="screenshot-caption">Настройки системы — Глобальные параметры</div>
  </div>
</div>

## <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg> Основные функции

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg> Умный бот
- **Автоматическая торговля**: Круглосуточный автоматический ответ на заказы пользователей, мгновенная доставка энергии.
- **Пользовательские ответы**: Поддержка ответов по ключевым словам, приветственных сообщений и руководств по эксплуатации.
- **Многоуровневая дистрибуция**: Встроенный механизм вознаграждения за приглашения для стимулирования роста пользователей.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> Мощная панель администратора
- **Визуальная панель**: Отображение в реальном времени ключевых показателей, таких как объем заказов, оборот и новые пользователи.
- **Планирование мульти-пула**: Поддержка добавления нескольких API пулов энергии, умная балансировка нагрузки для обеспечения стабильных поставок.
- **Профилирование пользователей**: Подробные записи поведения пользователей, поддержка банов, корректировки баланса и т.д.

### <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg> Безопасность и стабильность
- **Локальное хранение закрытых ключей**: Закрытые ключи выплат зашифрованы и хранятся только на локальном сервере для обеспечения безопасности средств.
- **Контейнеризация Docker**: Изоляция сервисов, простое развертывание и высокая масштабируемость.
- **Автоматические оповещения**: Автоматическое уведомление администраторов о системных аномалиях или нехватке энергии.

## Обзор архитектуры

Проект состоит из следующих основных компонентов:

- **Сервис бота (Python)**: Обрабатывает сообщения Telegram, взаимодействия с пользователями, обработку заказов и взаимодействия в цепочке.
- **Веб-сервис (Nuxt/Node.js)**: Предоставляет API администратора и интерфейсные страницы.
- **База данных (MySQL/Redis)**: Хранит данные пользователей, записи заказов и очереди кеша.
- **Nginx**: Действует как обратный прокси-сервер, обрабатывающий HTTP-запросы.

## Сценарии использования

- **Поставщики аренды энергии**: Создайте собственную платформу аренды энергии и продавайте энергию автоматически через TG-бота.
- **Разработчики Tron**: Интегрируйте функцию аренды энергии в свои собственные приложения.
- **Менеджеры сообществ**: Предоставляйте недорогие льготы по аренде энергии членам сообщества.

::: tip Примечание
Версия с открытым исходным кодом этого проекта предназначена только для учебных и исследовательских целей. Пожалуйста, соблюдайте соответствующие лицензии с открытым исходным кодом для коммерческого использования.
:::