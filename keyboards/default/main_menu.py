from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сегодня"),
            KeyboardButton(text="Завтра")
        ],
        [
            KeyboardButton(text="Поиск (в разработке)"),
        ],
        [
            KeyboardButton(text="Настройки (в разработке)")
        ]
    ],
    resize_keyboard=True
)