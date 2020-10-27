import datetime
import logging
import re

import apiclient
import httplib2
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

URL = "https://koopteh.onego.ru/student/lessons/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
    "accept": "*/*"
}
CREDENTIALS_FILE = "data/CDED12.json"


def today():
    return datetime.date.today().day


def get_html(url, params=None):
    request = requests.get(url, headers=HEADERS, params=params)
    return request


def get_content(html):
    mas_of_link = []
    mas_of_number = []
    a_container = []
    dict_of_schedule = {}

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

    return dict_of_schedule


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        return get_content(html.text)
    else:
        print("Error")


def get_schedules_data():
    dict_of_schedule = parse()
    dict_of_schedule.pop("Расписание сессии")

    spreadsheets_id = ""

    for key in dict_of_schedule:
        if today() == int(key):
            spreadsheets_id = dict_of_schedule[key][39:83]

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
    service.spreadsheets()
    logging.info(f"{values=}")
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