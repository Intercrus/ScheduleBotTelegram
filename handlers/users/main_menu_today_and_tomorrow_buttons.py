from datetime import date, timedelta
import re
from pprint import pprint
import apiclient
import httplib2
import requests

from bs4 import BeautifulSoup
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
