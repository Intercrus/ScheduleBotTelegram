from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.search_callback import search_callback

search_button = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Расписание на неделю",
                             callback_data=search_callback.new(action_name="schedule_for_week")),
    ],
    [
        InlineKeyboardButton(text="Расписание на определенный день",
                             callback_data=search_callback.new(action_name="schedule_for_spec_day")),
    ],
    [
        InlineKeyboardButton(text="Расписание преподавателя",
                             callback_data="action:schedule_for_teacher")
    ],
    [
        InlineKeyboardButton(text="Расписание группы",
                             callback_data="action:schedule_for_group")
    ],
])
