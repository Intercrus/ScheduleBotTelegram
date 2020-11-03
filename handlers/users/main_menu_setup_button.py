from aiogram.types import Message, CallbackQuery
from loader import dp, bot
from keyboards.inline.setup_button_inline import setup_button


@dp.message_handler(text="Настройки")
async def setup_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно настроить",
                         reply_markup=setup_button)


@dp.callback_query_handler(text_contains="sub_on_schedule")  # Not finished
async def subscribe_to_the_schedule(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)


@dp.callback_query_handler(text_contains="advertisement")  # Completed
async def advertising(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer("Подробности @scytheofdeath")


@dp.callback_query_handler(text_contains="reset_setup")  # Not finished
async def reset_settings(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
