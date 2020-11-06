from datetime import date
from aiogram.types import Message, CallbackQuery
from loader import dp, bot
from keyboards.inline.search_button_inline import *
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from utils.data_util import get_data_from_google, find_timetable_by_teacher


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
async def specific_teachers_schedule(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer('Укажите фамилию преподавателя')
    await StatesOfBot.search_by_teacher_state.set()


@dp.message_handler(state=StatesOfBot.search_by_teacher_state)
async def search_timetable_by_teacher(message: Message, state: FSMContext):
    data_today = date.today()
    data = await get_data_from_google(data_today)
    timetable = await find_timetable_by_teacher(data, message.text)

    msg = ''

    if not timetable:
        await message.answer('Ничего не найдено')
    else:
        for item in timetable:
            msg += ' '.join(item) + '\n'

        await message.answer(msg)
    
    await state.finish()


@dp.callback_query_handler(text_contains="schedule_for_group")  # Not finished
async def specific_group_day(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
