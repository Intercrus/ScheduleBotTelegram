from datetime import date, timedelta
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


@dp.message_handler(text="Сегодня")
async def schedule_today(message: Message):
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = date.today()
    data = await get_data_from_google(data_today)
    timetable = await find_timetable_by_group(data, group_name)

    await message.answer(data[0][0])
    await message.answer(timetable)


@dp.message_handler(text="Завтра")
async def schedule_tomorrow(message: Message):
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = date.today() + timedelta(days=1)

    data = await get_data_from_google(data_today)
    timetable = await find_timetable_by_group(data, group_name)

    await message.answer(data[0][0])
    await message.answer(timetable)


@retrying.retry(
    stop_max_attempt_number=5,
    retry_on_exception=lambda ex: True,  # Для любого исключения
    wait_exponential_multiplier=500,
    wait_exponential_max=8000)
# @dp.message_handler(text="Неделя")
# async def schedule_for_week(message: Message):
#     user = await commands.select_user(id=message.from_user.id)
#     group_name = user.name_group
#
#     for day in range(7):
#         data_today = date.today() + timedelta(days=day)
#
#         data = await get_data_from_google(data_today)
#         timetable = await find_timetable_by_group(data, group_name)
#
#         await message.answer(data[0][0])
#         await message.answer(timetable)
