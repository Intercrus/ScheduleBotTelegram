import datetime
import time
import re
from pprint import pprint
import apiclient
import httplib2
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

from aiogram.dispatcher.filters.builtin import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from keyboards.default import main_menu
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from keyboards.inline.setup_button_inline import setup_button
from keyboards.inline.setup_callback import *
from keyboards.inline.search_button_inline import *
from keyboards.inline.search_callback import *


@dp.message_handler(text="Настройки")
async def setup_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно настроить",
                         reply_markup=setup_button)


@dp.message_handler(text="Поиск")
async def search_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно найти",
                         reply_markup=search_button)


@dp.message_handler(text="Сегодня")
async def shedule_today(message: Message):
    URL = "https://koopteh.onego.ru/student/lessons/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "accept": "*/*"
    }
    mas_of_link = []
    mas_of_number = []
    a_container = []
    dict_of_shedule = {}
    data_today = datetime.date.today()
    mas_of_data = []

    # name_of_group = input()

    def get_html(url, params=None):
        request = requests.get(url, headers=HEADERS, params=params)
        return request

    def get_content(html):
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.find_all('a', href=re.compile("docs.google")):
            mas_of_link.append(link.get('href'))

        for number in soup.find_all('a', href=re.compile("docs.google")):
            a_container.append(number)

        for strong_tag in a_container:
            mas_of_number.append(strong_tag.text)

        count_link = len(mas_of_number)

        for i in range(count_link):
            dict_of_shedule[mas_of_number[i]] = mas_of_link[i]

        # pprint(dict_of_shedule)

    def parse():
        html = get_html(URL)
        if html.status_code == 200:
            get_content(html.text)
        else:
            print("Error")

    parse()

    del dict_of_shedule["Расписание сессии"]

    spreadsheets_id = ""

    for key in dict_of_shedule:
        if int(data_today.day) == int(key):
            spreadsheets_id = dict_of_shedule[key][39:83]

    CREDENTIALS_FILE = "/home/alien/PycharmProjects/ScheduleBotTelegram/handlers/users/CDED12.json"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build("sheets", "v4", http=httpAuth)
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheets_id,
        range="A1:N24",
        majorDimension="COLUMNS"
    ).execute()  # Main data from google sheets
    # Parsing is finished, need to get the values

    # for key in values:  # Removing unneeded keys
    #     mas_of_data = values[key]
    # print(mas_of_data)
    #
    # data_of_values_today = mas_of_data[0][0]

    # Removed the last and first element because it throws an error when iterating over the array
    # remove_the_last_item = mas_of_data[-1]
    # remove_the_first_item = mas_of_data[0]
    # mas_of_data.remove(remove_the_last_item)
    # mas_of_data.remove(remove_the_first_item)

    # joined_mas_of_data = '\n'.join(','.join(map(str, row)) for row in mas_of_data)
    # print(joined_mas_of_data)

    # pattern_group = f"{message.text}"
    #
    # for val in mas_of_data:
    #     if re.match(pattern_group, mas_of_data):
    #         print()

    # for val in mas_of_data:
    #     pass
    #     # print(val[0])
    #     # print(val[8])
    #     # print(val[16])

    exit()


@dp.message_handler(text="Завтра")
async def shedule_tomorrow(message: Message):
    pass


@dp.callback_query_handler(text_contains="advertisement")
async def get_ad(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer("Подробности @scytheofdeath")

# @dp.message_handler(state=StatesOfBot.search_groups_state)
# async def main_menu(message: Message, state: FSMContext):
#     pass
#
#
#     await message.answer(f"setup",
#                      reply_markup=setup_button)
#
#     await StatesOfBot.main_menu_state.set()
