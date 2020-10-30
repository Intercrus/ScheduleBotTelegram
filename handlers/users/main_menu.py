import datetime
import time
import re
from pprint import pprint
import apiclient
import httplib2
import requests
from aiogram.dispatcher.filters import state
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
from utils.db_api import quick_commands as commands


@dp.message_handler(text="Настройки (в разработке)", state=StatesOfBot.search_groups_state)
async def setup_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно настроить",
                         reply_markup=setup_button)


@dp.message_handler(text="Поиск (в разработке)", state=StatesOfBot.search_groups_state)
async def search_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно найти",
                         reply_markup=search_button)


@dp.message_handler(text="Сегодня", state=StatesOfBot.search_groups_state)
async def shedule_today(message: Message, state: FSMContext):
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
    ).execute()
    # pprint(values)  # Main data from google sheets
    # Parsing is finished, need to get the values
    data_group_name = await state.get_data()
    group_name = data_group_name.get("group_name")

    for key in values:  # Removing unneeded keys
        mas_of_data = values[key]

    data_of_values_today = mas_of_data[0][0]

    # Removed the last and first element because it throws an error when iterating over the array
    remove_the_last_item = mas_of_data[-1]
    remove_the_first_item = mas_of_data[0]
    mas_of_data.remove(remove_the_last_item)
    mas_of_data.remove(remove_the_first_item)

    result_group_1 = 0
    result_group_2 = 0
    result_group_3 = 0

    async def find_timetable(data, value):
        for i in range(len(data)):
            try:
                idx = data[i].index(value)
                new_data = []

                for j in range(idx + 1, len(data[i])):
                    if data[i][j] == '':
                        continue
                    elif data[i][j][1] == '.' or not re.search(r'^[0-9]{1}[A-ZА-Я0-9-]+$', data[i][j]):
                        new_data.append(data[i][j])
                    else:
                        break
                await message.answer(data_of_values_today)
                await message.answer('\n'.join(new_data))
            except Exception:
                continue

    await find_timetable(mas_of_data, group_name)


@dp.message_handler(text="Завтра", state=StatesOfBot.search_groups_state)
async def shedule_tomorrow(message: Message, state: FSMContext):
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
        if (int(data_today.day) + 1) == int(key):
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
    ).execute()
    # pprint(values)  # Main data from google sheets
    # Parsing is finished, need to get the values
    data_group_name = await state.get_data()
    group_name = data_group_name.get("group_name")

    for key in values:  # Removing unneeded keys
        mas_of_data = values[key]

    data_of_values_today = mas_of_data[0][0]

    # Removed the last and first element because it throws an error when iterating over the array
    remove_the_last_item = mas_of_data[-1]
    remove_the_first_item = mas_of_data[0]
    mas_of_data.remove(remove_the_last_item)
    mas_of_data.remove(remove_the_first_item)

    result_group_1 = 0
    result_group_2 = 0
    result_group_3 = 0

    async def find_timetable(data, value):
        for i in range(len(data)):
            try:
                idx = data[i].index(value)  # Индекс группы
                new_data = []

                for j in range(idx + 1, len(data[i])):
                    if data[i][j] == '':
                        continue
                    elif data[i][j][1] == '.' or not re.search(r'^[0-9]{1}[A-ZА-Я0-9-]+$', data[i][j]):
                        new_data.append(data[i][j])
                    else:
                        break
                await message.answer(data_of_values_today)
                await message.answer('\n'.join(new_data))
            except Exception:
                continue

    await find_timetable(mas_of_data, group_name)


@dp.callback_query_handler(text_contains="advertisement")
async def get_ad(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer("Подробности @scytheofdeath")


