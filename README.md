# ScheduleBotTelegram
> Бот для Telegram, который отправляет расписание пар Петрозаводского кооперативного техникума.
> Бот написан на Python с использованием библиотеки aiogram и базы данных PostgreSQL.

**Проект устарел. Новый бот по ссылке @pkt_schedule_bot. Код будет ** [здесь](https://github.com/Intercrus/pkt-schedule-bot)

## Демо

![demo](https://github.com/Intercrus/ScheduleBotTelegram/blob/master/demo.gif)

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

## Как работает бот и в целом происходит парсинг
1. Бот парсит этот сайт https://koopteh.onego.ru/student/lessons/ и достает оттуда ссылки на гугл таблицы. В зависимости от даты парсится нужная таблица
2. С помощью Google Sheets API парсит таблицу и достает значения
3. При помощи регулярных выражений и циклов отправляет отформатированное расписание

## Структура репозитория
```
.
├── data                                                            
│   ├── __init__.py
│   └── key.json                                           # Ключ-пара от Google Sheets
│   └── config.py                                          # Туда загружаются переменные окружения (токен бота, id админа, postgresql и т.д.)
│   └── name_groups.txt                                    # Названия всех групп
│
├── filters                                                # Фильтры для хендлеров (фильтрация апдейтов)                    
│   └── __init__.py
│
├── handlers                                               # Хендлеры (обработчики апдейтов)
│   ├── channels                                           # Хендлеры для каналов                    
│   │   └── __init__.py
│   └── errors                                             # Хендлеры ошибок
│   │   ├── __init__.py
│   │   └── error_handler.py
│   └── groups                                             # Хендлеры для групп
│   │   └── __init__.py 
│   └── users                                              # Хендлеры для пользователей
│   │   ├── __init__.py
│   │   └── help.py                                        # Команда /help
│   │   └── main_menu_search_button.py                     # Кнопка <Поиск>
│   │   └── main_menu_setup_button.py                      # Кнопка <Настройки>
│   │   └── main_menu_today_and_tomorrow_buttons.py        # Кнопки <Сегодня>, <Завтра>, <Неделя>
│   │   └── search_groups.py                               # "Регистрация" пользователя
│   │   └── start.py                                       # Команда /start
│   └── __init__.py
│                                                          
├── keyboards                                              # Клавиатуры 
│   ├── default                                            # Обычные клавиатуры
│   │   ├── __init__.py
│   │   └── main_menu.py                                   # Клавиатура главного меню с кнопками <Сегодня>, <Завтра>, <Неделя>, <Поиск>, <Настройки>
│   └── inline                                             # Inline-клавиатуры
│   │   ├── __init__.py
│   │   └── cancel_button_callback.py                      # Коллбек кнопки <Отмена>
│   │   └── cancel_button_inline.py                        # Кнопка <Отмена>
│   │   └── search_button_inline.py                        # Кнопка <Поиск>
│   │   └── search_callback.py                             # Коллбек кнопки <Поиск>
│   │   └── setup_button_inline.py                         # Кнопка <Настройки>
│   │   └── setup_callback.py                              # Коллбек кнопки <Настройки>
│   └── __init__.py
│    
├── middlewares                                            # Промежуточные программы, они влияют на то, что попадает в хендлер. 
│   ├── __init__.py
│   └── throttling.py                                      # Защита от флуда
│    
├── states                                                 # Состояния для машины состояний (FSM)
│   ├── __init__.py         
│   └── botStates.py                                       # Машина состояний для "регистрации" и некоторых хендлеров
│    
├── utils                                                  # Вспомогательные модули
│   ├── db_api                                             # Работа с базой данных
│   │   ├── schemas 
│   │   │   ├── __init__.py
│   │   │   └── user.py                                    # Создание таблицы
│   │   └── __init__.py
│   │   └── db_gino.py                                     # База данных gino
│   │   └── quick_commands.py                              # Функции для работы с базой данных (например обновление названия группы для пользователя)
│   └── misc                                
│   │   ├── __init__.py
│   │   └── logging.py                                     # Логирование                                      
│   │   └── throttling.py                                  # Функция rate_limit для троттлинга 
│   └── redis                                              # Константы для работы с redis
│   │   ├── __init__.py                                    
│   │   └── consts.py
│   └── __init__.py
│   └── data_util.py                                       # Парсинг
│   └── notify_admins.py                                   # Сообщения для админов
│   └── scheduler.py                                       # Реализация подписки на расписание
│   └── set_bot_commands.py                                # Список команд бота
│                                                              
├── .env                                                   # Переменные окружения (токен бота, id админа, postgresql и т.д.)
├── .gitignore
├── app.py                                                 # Главный файл. В этом файле запускается работа бота. Через этот файл и запускается сам бот
├── docker-compose.yml                                     # Файл для docker-compose
├── Dockerfile                                             # Файл для docker
├── loader.py                                              # Второй главный файл. В этот файл все импортируется, в нем содержатся главные переменные      
├── README.md               
└── requirements.txt                                       # Зависимости (модули), которые необходимы для работы бота.
```
> Файлы __init__.py нужны для правильного импорта модулей.

[Архитектура этого бота](https://github.com/Latand/aiogram-bot-template)







