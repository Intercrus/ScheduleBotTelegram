from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.cancel_button_callback import cancel_callback


cancel_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Отмена",
                             callback_data=cancel_callback.new(action_name="come_back")),
    ]
])
