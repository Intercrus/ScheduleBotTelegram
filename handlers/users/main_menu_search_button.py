from aiogram.types import Message, CallbackQuery
from loader import dp, bot
from keyboards.inline.search_button_inline import *


@dp.message_handler(text="Поиск")
async def search_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно найти",
                         reply_markup=search_button)


@dp.callback_query_handler(text_contains="schedule_for_spec_day")  # Not finished
async def schedule_for_a_specific_day(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)


@dp.callback_query_handler(text_contains="schedule_for_teacher")  # Not finished
async def specific_teachers_schedule(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)


@dp.callback_query_handler(text_contains="schedule_for_group")  # Not finished
async def specific_group_day(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
