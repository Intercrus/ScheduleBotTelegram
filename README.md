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
3. Network & Security → Security Groups → Edit Inbound Rules- туда добавьте ssh с вашим ip; также добавьте PostgreSQL с любым ip
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
> ```/home/ubuntu``` - директория на сервере, куда будут скопированы файлы бота
> После копирования выглядеть будет так: ```/home/ubuntu/ScheduleBotTelegram```
6. Измените пути к файлам name_groups.txt и key.json вот так:
```
file_name_group = open("/src/data/name_groups.txt")
```
> То же самое и для ключа. То есть вместо ```/home/ubuntu/PycharmProjects/ScheduleBotTelegram/``` мы пишем ```/src/```
7. в .env измените строчку:
```
ip: db
```
8. Установите docker-compose на инстанс:
```
sudo apt-get update
sudo apt-get install docker docker-compose
```
9. Находясь в ```/home/ubuntu/ScheduleBotTelegram``` (путь к ```/ScheduleBotTelegram```) напишите команду:
```
sudo docker-compose up
```
> После этого бот должен запуститься. Если этого не произошло,то смотрите логи и исправляйте обычные файлы или файл .env.
> После изменений файлов контейнер можно пересобрать: ```sudo docker-compose up --build```
10. Чтобы увидеть базу данных, в которую летят юзеры, нужно через PostgreSQL создать сервер, в котором указывается ip инстанса Amazon. Паролем является тот пароль, который указан в .env

> Ctrl + Z - оставить бота включенным. После этого можно будет выходить с сервера и бот будет работать на фоне.
> Остановить бота: ```sudo docker-compose stop```. 
> Если не получается установить бота на сервер после выполнения вышеперечисленных действий пишите мне [@scytheofdeath](http://telegram.me/scytheofdeath)

## Структура репозитория
```
.
├── data                            
│   ├── __init__.py
│   └── key.json
│   └── config.py
│   └── name_groups.txt
│
├── filters                             
│   └── __init__.py
│
├── handlers
│   ├── channels
│   │   └── __init__.py
│   └── errors
│   │   ├── __init__.py
│   │   └── error_handler.py
│   └── groups
│   │   └── __init__.py 
│   └── users
│   │   ├── __init__.py
│   │   └── help.py
│   │   └── main_menu_search_button.py
│   │   └── main_menu_setup_button.py
│   │   └── main_menu_today_and_tomorrow_buttons.py
│   │   └── search_groups.py
│   │   └── start.py
│   └── __init__.py
│
├── keyboards
│   ├── default
│   │   ├── __init__.py
│   │   └── main_menu.py
│   └── inline
│   │   ├── __init__.py
│   │   └── cancel_button_callback.py
│   │   └── cancel_button_inline.py
│   │   └── search_button_inline.py
│   │   └── search_callback.py
│   │   └── setup_button_inline.py
│   │   └── setup_callback.py
│   └── __init__.py
│    
├── middlewares
│   ├── __init__.py
│   └── throttling.py
│    
├── states   
│   ├── __init__.py
│   └── botStates.py
│    
├── utils
│   ├── db_api
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   └── __init__.py
│   │   └── db_gino.py
│   │   └── quick_commands.py
│   └── misc
│   │   ├── __init__.py
│   │   └── logging.py
│   │   └── parsing.py
│   │   └── throttling.py
│   └── redis
│   │   ├── __init__.py
│   │   └── consts.py
│   └── __init__.py
│   └── data_util.py
│   └── notify_admins.py
│   └── scheduler.py
│   └── set_bot_commands.py
│    
├── .env                     
├── .gitignore
├── app.py
├── docker-compose.yml
├── Dockerfile
├── loader.py                    
├── README.md               
└── requirements.txt
```








