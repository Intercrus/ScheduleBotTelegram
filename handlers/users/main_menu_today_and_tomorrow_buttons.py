import datetime
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


@dp.message_handler(text="Сегодня")
async def schedule_today(message: Message):
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group

    URL = "https://koopteh.onego.ru/student/lessons/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "accept": "*/*"
    }

    mas_of_link, mas_of_number, a_container, mas_of_data, dict_of_schedule = [], [], [], [], {}
    data_today = datetime.date.today()

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
            dict_of_schedule[mas_of_number[i]] = mas_of_link[i]

        # pprint(dict_of_schedule)

    def parse():
        html = get_html(URL)
        if html.status_code == 200:
            get_content(html.text)
        else:
            print("Error")

    parse()

    del dict_of_schedule["Расписание сессии"]

    spreadsheets_id = ""

    for key in dict_of_schedule:
        if int(data_today.day) == int(key):
            spreadsheets_id = dict_of_schedule[key][39:83]

    CREDENTIALS_FILE = "/home/alien/PycharmProjects/ScheduleBotTelegram/data/CDED12.json"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build("sheets", "v4", http=httpAuth)

    data_today_reformat = data_today.strftime("%d.%m.%Y")

    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheets_id,
        range="A1:N24",
        majorDimension="COLUMNS"
    ).execute()
    # pprint(values)  # Main data from google sheets
    # Parsing is finished, need to get the values

    for key in values:  # Removing unneeded keys
        mas_of_data = values[key]

    data_of_values_today = mas_of_data[0][0]

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


@dp.message_handler(text="Завтра")
async def schedule_tomorrow(message: Message):
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group

    URL = "https://koopteh.onego.ru/student/lessons/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "accept": "*/*"
    }

    mas_of_link, mas_of_number, a_container, mas_of_data, dict_of_schedule = [], [], [], [], {}
    data_today = datetime.date.today()

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
            dict_of_schedule[mas_of_number[i]] = mas_of_link[i]

        # pprint(dict_of_schedule)

    def parse():
        html = get_html(URL)
        if html.status_code == 200:
            get_content(html.text)
        else:
            print("Error")

    parse()

    del dict_of_schedule["Расписание сессии"]

    spreadsheets_id = ""

    tomorrow_day = data_today.day + 1

    for key in dict_of_schedule:
        if int(tomorrow_day) == int(key):
            spreadsheets_id = dict_of_schedule[key][39:83]

    CREDENTIALS_FILE = "/home/alien/PycharmProjects/ScheduleBotTelegram/data/CDED12.json"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build("sheets", "v4", http=httpAuth)

    data_today_reformat = data_today.strftime("%d.%m.%Y")

    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheets_id,
        range="A1:N24",
        majorDimension="COLUMNS"
    ).execute()
    # pprint(values)  # Main data from google sheets
    # Parsing is finished, need to get the values

    for key in values:  # Removing unneeded keys
        mas_of_data = values[key]

    data_of_values_today = mas_of_data[0][0]

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
