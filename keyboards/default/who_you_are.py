from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

who_you_are = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Студент")
        ],
        [
            KeyboardButton(text="Преподаватель")
        ]
    ],
    resize_keyboard=True
)


