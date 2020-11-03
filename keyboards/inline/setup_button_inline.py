from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.setup_callback import setup_callback

setup_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Подписаться на расписание",
                             callback_data=setup_callback.new(action_name="sub_on_schedule")),
    ],
    [
        InlineKeyboardButton(text="Место для рекламы",
                             callback_data="action:advertisement")
    ],
    [
        InlineKeyboardButton(text="Сбросить настройки",
                             callback_data="action:reset_setup")
    ],
])
