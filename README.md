# ScheduleBotTelegram
> Бот для Telegram, который отправляет расписание пар Петрозаводского кооперативного техникума.
> Бот написан на Python с использованием библиотеки aiogram и базы данных PostgreSQL.
> Данного бота можно добавить к себе в телеграм, перейдя по ссылке: [@PKTK_schedule_bot](http://telegram.me/PKTK_schedule_bot)

## Демо

![demo](https://github.com/Intercrus/ScheduleBotTelegram/blob/master/Peek%202020-11-12%2001-01.gif)

## Начало работы

1. Клонируйте репозиторий
2. В ```/ScheduleBotTelegram/``` добавьте файл .env (рядом с app.py и loader.py) (путь к .env: ```/ScheduleBotTelegram/.env```)
3. Настройте .env:
```
BOT_TOKEN= 123123asdbahsbdhb # Токен вашего бота
ADMIN_ID= 6736732864 # Ваш ID в Telegram
ip= 17.01.20.10 # Ваш IP
PG_USER= postgres # Ваш пользователь в PostgreSQL
PG_PASSWORD=passwd # Ваш пароль от пользователя postgresql
DATABASE=gino # Ваша база данных в PostgreSQL
```
4. В ```/ScheduleBotTelegram/data/``` добавьте ключ-пару от гугл таблиц в формате .json. Как получить эту ключ-пару объяснено в этом видео: https://www.youtube.com/watch?v=Bf8KHZtcxnA&t=232s (путь к key.json: ```/ScheduleBotTelegram/data/key.json```)
5. Измените пути к name_groups.txt и key.json в зависимости от вашей операционной системы и названия ваших директорий. Например в файле ```/ScheduleBotTelegram/handlers/users/start.py``` изменить путь в этой строке: 
```
file_name_group = open("/home/alien/PycharmProjects/ScheduleBotTelegram/data/name_groups.txt")
```
6. Скачать PostgreSQL и зайти в pgAdmin. Там создать сервер с такими настройками (если вы используете Windows, то host отличается):

![](https://github.com/Intercrus/ScheduleBotTelegram/blob/master/Screenshot%20from%202020-11-12%2000-50-39.png)

7. Установить модули, которые использует бот. Они находятся в ```/ScheduleBotTelegram/requirements.txt```
8. Запустить app.py

> После выполнения вышеперечисленных действий бот должен начать работать. Если что-то не получилось пишите мне: [@scytheofdeath](http://telegram.me/scytheofdeath)

## Установка на сервер

> Я буду рассматривать установку на примере Amazon AWS EC2 с использованием docker.

1. Создайте аккаунт на aws.amazon
2. Создайте instance (я рассматриваю instance ubuntu)
3. Network & Security => Security Groups => Edit Inbound Rules- туда добавьте ssh с вашим ip; также добавьте PostgreSQL с любым ip
4. Подключитесь к серверу с помощью команды:
```
ssh -i /путь к вашему ключу от инстанса Amazon/ ubuntu@ip инстанса
```
> Если не получилось подключиться (выдает ошибку Permission Denied) попробуйте изменить права:
```
chmod 600 /путь к ключу/
```
> Если и это не помогло, то гугл в помощь.
5. Загрузите файлы бота на сервер:
```
scp -i /путь к ключу/ -r /путь к ScheduleBotTelegram (эту директорию будем копировать на сервер)/ ubuntu@ip инстанса:/home/ubuntu 
```
> /home/ubuntu - директория на сервере, куда будут скопированы файлы бота
> После копирования выглядеть будет так: ```/home/ubuntu/ScheduleBotTelegram```
6. Измените пути к файлам name_groups.txt и key.json вот так:
```
file_name_group = open("/src/data/name_groups.txt")
```
> То же самое и для ключа. То есть вместо ```/home/ubuntu/PycharmProjects/ScheduleBotTelegram/``` мы пишем ```/src/```








