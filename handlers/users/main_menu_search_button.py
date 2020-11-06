import retrying
from datetime import date, datetime, timedelta
from aiogram.types import Message, CallbackQuery
from googleapiclient.errors import HttpError

from loader import dp, bot
from keyboards.inline.search_button_inline import *
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from utils.data_util import get_data_from_google, find_timetable_by_teacher, find_timetable_by_group
from utils.db_api import quick_commands as commands


@dp.message_handler(text="Поиск")
async def search_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно найти",
                         reply_markup=search_button)


@dp.callback_query_handler(text_contains="schedule_for_spec_day")
async def schedule_for_a_specific_day(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer('Укажите дату, на которую нужно найти расписание. '
                              '\nНапример: 2020-11-06 (год-месяц-день)')
    await StatesOfBot.search_by_spec_day.set()


@dp.message_handler(state=StatesOfBot.search_by_spec_day)
async def search_timetable_by_specific_day(message: Message, state: FSMContext):
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = datetime.strptime(message.text, "%Y-%m-%d")
    data = await get_data_from_google(data_today)
    timetable = await find_timetable_by_group(data, group_name)

    await message.answer(data[0][0])
    await message.answer(timetable)

    await state.finish()


@dp.callback_query_handler(text_contains="schedule_for_teacher")
async def specific_teachers_schedule(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer('Укажите фамилию преподавателя и имя преподавателя. \nНапример: Голубник АА')
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


@dp.callback_query_handler(text_contains="schedule_for_group")
async def specific_group_day(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer('Укажите название группы. \nНапример: 2ИС-2')
    await StatesOfBot.search_by_name_group.set()


@dp.message_handler(state=StatesOfBot.search_by_name_group)
async def search_timetable_by_name_group(message: Message, state: FSMContext):
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = date.today()

    data = await get_data_from_google(data_today)
    timetable = await find_timetable_by_group(data, message.text)

    await message.answer(data[0][0])
    await message.answer(timetable)

    await state.finish()
