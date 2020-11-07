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
    global data
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = date.today()

    try:
        data = await get_data_from_google(data_today)
        timetable = await find_timetable_by_group(data, group_name)
        reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])

        print(timetable)

        reformat_key = re.search(r"\s...................\s[А-Я][А-Я]", timetable)
        print(reformat_key.group(0))

        await message.answer(f"📅 {reformat_data.title()}\n----------------\n{timetable}")

    except HttpError:
        name_day = data_today.strftime("%A")
        format_data = data_today.strftime("%d.%m.%y")

        if name_day == "Sunday":
            await message.answer(f"{''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Выходной день")
        else:
            await message.answer(f"{''.join(format_data)}, {''.join(name_day)}\n"
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

        await message.answer(f"{data[0][0]}\n----------------\n{timetable}")
    except HttpError:
        name_day = data_today.strftime("%A")
        format_data = data_today.strftime("%d.%m.%y")

        if name_day == "Sunday":
            await message.answer(f"{''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Выходной день")
        else:
            await message.answer(f"{''.join(format_data)}, {''.join(name_day)}\n"
                                 f"Нет данных")


@rate_limit(limit=10)
@dp.message_handler(text="Неделя")
async def schedule_for_week(message: Message):
    global data
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group

    for day in range(7):
        data_today = date.today() + timedelta(days=day)

        try:
            data = await get_data_from_google(data_today)

        except HttpError:
            name_day = data_today.strftime("%A")
            format_data = data_today.strftime("%d.%m.%y")

            if name_day == "Sunday":
                await message.answer(f"{''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Выходной день")
                continue
            else:
                await message.answer(f"{''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Нет данных")
                continue

        timetable = await find_timetable_by_group(data, group_name)

        await message.answer(f"{data[0][0]}\n----------------\n{timetable}")
