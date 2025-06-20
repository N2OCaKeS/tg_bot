# BombTeam Telegram Bot

Мощный SMS-бомбер для Telegram, развёртываемый в Docker-контейнере.

## Быстрый старт

1. **Склонируйте репозиторий:**

```sh
git clone 
cd tg_bot
```

2. **Создайте файл окружения**

Скопируйте `example.env` в `.env` и заполните переменные:

```env
API_TOKEN=ваш_токен_бота
CHANNEL_ID=77223345455
CHANNEL_LINK=https://t.me/your_channel
SECURE_PHONES=79001234567,79007654321
```

- `API_TOKEN` — токен Telegram-бота
- `CHANNEL_ID` — id канала (например, `77223345455`)
- `CHANNEL_LINK` — ссылка на канал
- `SECURE_PHONES` — список телефонов через запятую, которые защищены от бота

1. **Постройте и запустите контейнер:**

```sh
docker build -t bombteam .
docker run --env-file .env bombteam
```

## Использование

- После запуска бот будет работать в Telegram.
- Для работы требуется подписка на канал, указанный в переменных окружения.
- Все настройки производятся через переменные окружения.

## Зависимости

- Python 3.12
- aiogram
- aiohttp
- sqlite3
- fake_useragent

## Примечания

- База данных создаётся автоматически в контейнере (`BombTeam.db`).
- Для обновления кода — пересоберите контейнер.

---

**Внимание!** Используйте только в легальных целях и с согласия владельцев номеров.
