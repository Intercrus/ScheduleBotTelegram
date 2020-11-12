from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

choice_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Студент"),
            KeyboardButton(text="Преподаватель")
        ]
    ],
    resize_keyboard=True
)
