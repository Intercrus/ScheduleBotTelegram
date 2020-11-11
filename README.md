# ScheduleBotTelegram
> Бот для Telegram, который отправляет расписание пар Петрозаводского кооперативного техникума.
> Бот написан на Python, с использованием библиотеки aiogram и базы данных PostgreSQL.
> Данного бота можно добавить к себе в телеграм, перейдя по ссылке: @PKTK_schedule_bot

## Начало
1. Клонируйте репозиторий.
2. В /ScheduleBotTelegram/ добавьте файл .env (рядом с app.py и loader.py) (путь к .env: /ScheduleBotTelegram/.env)
3. Настройте .env:
```
BOT_TOKEN= 123123asdbahsbdhb # Токен вашего бота
ADMIN_ID= 6736732864 # Ваш ID в Telegram
ip= 17.01.20.10 # Ваш IP
PG_USER= postgres # Ваш пользователь в PostgreSQL
PG_PASSWORD=passwd # Ваш пароль от пользователя postgresql
DATABASE=gino # Ваша база данных в PostgreSQL
```





