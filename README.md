# Business Lead Bot

Telegram-бот для сбора заявок, уведомлений менеджеру и простой автоматизации.

## Возможности
- Сбор заявок (имя, телефон, услуга, комментарий)
- Мгновенные уведомления администратору
- Кнопки выбора услуг
- Статистика заявок (для админа)
- Простая база данных SQLite

## Стек
- Python 3.11+
- aiogram 3.x
- SQLite

## Установка

```bash
git clone https://github.com/gdenikita/business-lead-bot.git
cd business-lead-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Создай `.env`:
```
BOT_TOKEN=токен_от_BotFather
ADMIN_ID=твой_telegram_id
```

Запуск:
```bash
python bot.py
```

## Команды
- `/start` — начать / оставить заявку
- `/stats` — статистика (только для админа)
