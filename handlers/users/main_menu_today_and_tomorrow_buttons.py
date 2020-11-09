from datetime import date, timedelta, datetime
import sys
import re
from pprint import pprint
import apiclient
import httplib2
import requests
import retrying

from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from aiogram.types import Message
from loader import dp
from utils.db_api import quick_commands as commands
from utils.data_util import get_data_from_google, find_timetable_by_group
from utils.misc import rate_limit


@rate_limit(limit=10)
@dp.message_handler(text="Сегодня")
async def schedule_today(message: Message):
    global data, new_line_n
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = date.today()

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


@rate_limit(limit=10)
@dp.message_handler(text="Завтра")
async def schedule_tomorrow(message: Message):
    global data
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = date.today() + timedelta(days=1)

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


@rate_limit(limit=30)
@dp.message_handler(text="Неделя")
async def schedule_for_week(message: Message):
    global data
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group

    for day in range(7):
        data_today = date.today() + timedelta(days=day)

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
                continue
            else:
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Нет данных")
                continue
