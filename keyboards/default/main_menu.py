from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сегодня"),
            KeyboardButton(text="Завтра")
        ],
        [
            KeyboardButton(text="Неделя"),
        ],
        [
            KeyboardButton(text="Поиск"),
        ],
        [
            KeyboardButton(text="Настройки")
        ]
    ],
    resize_keyboard=True
)
