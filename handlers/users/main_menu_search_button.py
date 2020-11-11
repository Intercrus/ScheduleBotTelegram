
import re
from datetime import date, datetime, timedelta
from aiogram.types import Message, CallbackQuery
from googleapiclient.errors import HttpError
from itertools import zip_longest

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
    global data_today
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group

    try:
        data_today = datetime.strptime(message.text, "%Y-%m-%d")
    except ValueError:
        await message.answer("Некорректный ввод даты.\n"
                             "Введите дату в соответствии с образцом.")
        await state.finish()

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
                try:
                    name_teacher = re.search(
                        r"\s([А-Я](.)*\s[А-Я][А-Я][,](.)*\s[А-Я][А-Я]|[А-Я](.)*\s[А-Я][А-Я]\s|\s[А-Я]......\s[А-Я][А-Я]|\s[А-Я].......\s[А-Я][А-Я])",
                        i).group(0)
                    name_teacher_format = re.search(
                        r"[А-Я][а-я](.)*\s[А-Я][А-Я]|[А-Я][а-я](.)*\s[А-Я][А-Я][,][А-Я](.)*\s[А-Я][А-Я]",
                        name_teacher).group(0)
                except AttributeError:
                    name_teacher_format = ""
                lesson = re.search(r"[0-9].[А-Я](.){18}\s|[0-9].[А-Я][А-Я]\s\d\d", i).group(0)

                if name_teacher_format.strip() == "Маликина АВ" or name_teacher_format.strip() == "Ольшина ТА":
                    cabinet = "-"
                else:
                    cabinet = re.search(
                        r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|\d|(\bакт)\s(\bзал)|\s\sдист\s\s)", i).group(0)

                number_of_lesson = re.search(r"[0-9]", i).group(0)

                div_info_lesson.append(
                    f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👤{name_teacher_format.lstrip()}\n")
            except AttributeError:
                div_info_lesson.append(timetable)
                break

        new_line_n = "\n"
        await message.answer(f"📅 {reformat_data.title()}\n\n"
                             f"{f'{new_line_n}'.join(div_info_lesson)}")

        await state.finish()
    except HttpError:
        name_day = data_today.strftime("%A")
        format_data = data_today.strftime("%d.%m.%y")

        if name_day == "Sunday":
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Выходной день")
            await state.finish()
        else:
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Нет данных")
            await state.finish()


@dp.callback_query_handler(text_contains="schedule_for_teacher")
async def specific_teachers_schedule(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer('Укажите фамилию преподавателя и имя преподавателя. \nНапример: Опуховская АА')
    await StatesOfBot.search_by_teacher_state.set()


@dp.message_handler(state=StatesOfBot.search_by_teacher_state)
async def search_timetable_by_teacher(message: Message, state: FSMContext):
    data_today = date.today()

    try:
        data = await get_data_from_google(data_today)
        reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
        time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                        "11:30 - 12:50", "13:20 - 14:40",
                        "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
        timetable = await find_timetable_by_teacher(data, message.text)
        reformat_timetable = sorted(timetable)
        reformat_timetable_2 = [item for sublist in reformat_timetable for item in sublist]

        def concatenation_of_two_strings(elem):
            for x in zip_longest(elem[::2], elem[1::2], fillvalue=''):
                yield '  '.join(x)

        reformat_timetable_3 = list(concatenation_of_two_strings(reformat_timetable_2))
        div_info_lesson = []

        if not timetable:
            await message.answer('Ничего не найдено')
            await state.finish()
        else:
            for i in reformat_timetable_3:
                print(reformat_timetable_3)
                lesson = re.search(r"[0-9].[А-Я](.)*\s", i).group(0)
                if message.text == "Маликина АВ" or message.text == "Ольшина ТА":
                    cabinet = "-"
                else:
                    cabinet = re.search(
                        r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|(\bакт)(\bзал)|дист|\d)", i).group(0)
                number_of_lesson = re.search(r"[0-9]", i).group(0)

                div_info_lesson.append(
                    f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👤{message.text.lstrip()}\n")

            new_line_n = "\n"
            await message.answer(f"📅 {reformat_data.title()}\n\n"
                                 f"{f'{new_line_n}'.join(div_info_lesson)}")
            await state.finish()

    except HttpError:
        name_day = data_today.strftime("%A")
        format_data = data_today.strftime("%d.%m.%y")

        if name_day == "Sunday":
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Выходной день")
            await state.finish()
        else:
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Нет данных")
            await state.finish()

    except IndexError:
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
    global reformat_timetable
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
                try:
                    name_teacher = re.search(
                        r"\s([А-Я](.)*\s[А-Я][А-Я][,](.)*\s[А-Я][А-Я]|[А-Я](.)*\s[А-Я][А-Я]\s|\s[А-Я]......\s[А-Я][А-Я]|\s[А-Я].......\s[А-Я][А-Я])",
                        i).group(0)
                    name_teacher_format = re.search(
                        r"[А-Я][а-я](.)*\s[А-Я][А-Я]|[А-Я][а-я](.)*\s[А-Я][А-Я][,][А-Я](.)*\s[А-Я][А-Я]",
                        name_teacher).group(0)
                except AttributeError:
                    name_teacher_format = ""
                lesson = re.search(r"[0-9].[А-Я](.){18}\s|[0-9].[А-Я][А-Я]\s\d\d", i).group(0)

                if name_teacher_format.strip() == "Маликина АВ" or name_teacher_format.strip() == "Ольшина ТА":
                    cabinet = "-"
                else:
                    cabinet = re.search(
                        r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|\d|(\bакт)\s(\bзал)|\s\sдист\s\s)", i).group(0)

                number_of_lesson = re.search(r"[0-9]", i).group(0)

                div_info_lesson.append(
                    f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👤{name_teacher_format.lstrip()}\n")
            except AttributeError:
                div_info_lesson.append(timetable)
                break

        new_line_n = "\n"
        await message.answer(f"📅 {reformat_data.title()}\n\n"
                             f"{f'{new_line_n}'.join(div_info_lesson)}")
        await state.finish()

    except HttpError:
        name_day = data_today.strftime("%A")
        format_data = data_today.strftime("%d.%m.%y")

        if name_day == "Sunday":
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Выходной день")
            await state.finish()
        else:
            await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Нет данных")
            await state.finish()

    except AttributeError:
        await message.answer("Некорректный ввод группы.\n"
                             "Введите группу в соответствии с образцом.")
        await state.finish()
