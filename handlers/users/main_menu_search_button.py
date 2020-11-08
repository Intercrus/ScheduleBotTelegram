import retrying
import re
from datetime import date, datetime, timedelta
from aiogram.types import Message, CallbackQuery
from googleapiclient.errors import HttpError

from loader import dp, bot
from keyboards.inline.search_button_inline import *
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from utils.data_util import get_data_from_google, find_timetable_by_teacher, find_timetable_by_group
from utils.db_api import quick_commands as commands
from utils.misc import rate_limit


@rate_limit(limit=5)
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

    try:
        data = await get_data_from_google(data_today)
        timetable = await find_timetable_by_group(data, group_name)
        reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
        time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                        "11:30 - 12:50", "13:20 - 14:40",
                        "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
        reformat_timetable = timetable.split("\n")
        div_info_lesson = []

        for i in reformat_timetable:

            try:
                name_teacher = re.search(
                    r"...................\s[А-Я][А-Я][,]*[А-Я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[\s]*[А-Я]*[А-Я]*",
                    i).group(0)
                name_teacher_format = re.search(r"...................\s[А-Я][А-Я]", name_teacher).group(0)
                lesson = re.search(r"[0-9].[А-Я].................\s", i).group(0)
                cabinet = re.search(r"\s\s(\d\d|[А-Я][А-Я])", i).group(0)
                number_of_lesson = re.search(r"[0-9]", i).group(0)

                div_info_lesson.append(
                    f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👤{name_teacher_format.lstrip()}\n")
            except AttributeError:
                div_info_lesson.append(timetable)
                break

        new_line_n = "\n"
        await message.answer(f"📅 {reformat_data.title()}\n\n"
                             f"{f'{new_line_n}'.join(div_info_lesson)}")
    except HttpError:
        name_day = data_today.strftime("%A")
        format_data = data_today.strftime("%d.%m.%y")

        if name_day == "Sunday":
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Выходной день")
        else:
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Нет данных")

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

        await message.answer(f"{data[0][0]}\n----------------\n{msg}")

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
    data_today = date.today()

    try:
        data = await get_data_from_google(data_today)
        timetable = await find_timetable_by_group(data, message.text)
        reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
        time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                        "11:30 - 12:50", "13:20 - 14:40",
                        "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
        reformat_timetable = timetable.split("\n")
        div_info_lesson = []

        for i in reformat_timetable:

            try:
                name_teacher = re.search(
                    r"...................\s[А-Я][А-Я][,]*[А-Я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[а-я]*[\s]*[А-Я]*[А-Я]*",
                    i).group(0)
                name_teacher_format = re.search(r"...................\s[А-Я][А-Я]", name_teacher).group(0)
                lesson = re.search(r"[0-9].[А-Я].................\s", i).group(0)
                cabinet = re.search(r"\s\s(\d\d|[А-Я][А-Я])", i).group(0)
                number_of_lesson = re.search(r"[0-9]", i).group(0)

                div_info_lesson.append(
                    f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👤{name_teacher_format.lstrip()}\n")
            except AttributeError:
                div_info_lesson.append(timetable)
                break

        new_line_n = "\n"
        await message.answer(f"📅 {reformat_data.title()}\n\n"
                             f"{f'{new_line_n}'.join(div_info_lesson)}")
    except HttpError:
        name_day = data_today.strftime("%A")
        format_data = data_today.strftime("%d.%m.%y")

        if name_day == "Sunday":
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Выходной день")
        else:
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Нет данных")

    await state.finish()
