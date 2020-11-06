import re
from pprint import pprint
import apiclient
import httplib2
import requests

from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials


# Получает данные из google-таблиц
async def get_data_from_google(target_date):
    URL = "https://koopteh.onego.ru/student/lessons/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "accept": "*/*"
    }

    mas_of_link, mas_of_number, a_container, mas_of_data, dict_of_schedule = [], [], [], [], {}

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
        if int(target_date.day) == int(key):
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

    data_today_reformat = target_date.strftime("%d.%m.%Y")

    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheets_id,
        range="A1:N24",
        majorDimension="COLUMNS"
    ).execute()
    # pprint(values)  # Main data from google sheets
    # Parsing is finished, need to get the values

    for key in values:  # Removing unneeded keys
        mas_of_data = values[key]

    return mas_of_data


# Находит расписание по имени группы
async def find_timetable_by_group(data, value):
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
            return '\n'.join(new_data)
        except Exception:
            continue


# Находит расписание по имени препода
async def find_timetable_by_teacher(data, value):
    global lesson, cabinet
    out_data = []
    for item in data:
        for i in range(len(item)):
            if item[i].find(value) > -1:
                new_data = item[i].split('  ')
                result = []

                for elem in new_data:
                    if elem.strip():
                        result.append(elem)

                if len(result) == 3:

                    if result[1].find(value) > -1:
                        out_data.append([result[0], result[-1]])

                    else:
                        cabinet = ''
                        if -1 < result[2].find(value) <= 5:  # result[2].find(value) > -1 and result[2].find(value) <= 5
                            cabinet = result[1].split('/')[0]
                        if result[2].find(value) > -1 and result[2].find(value) >= 5:
                            cabinet = result[1].split('/')[1]

                        out_data.append([result[0], cabinet])

                if len(result) == 2:
                    if result[1].find(',') > -1:
                        pattern = re.findall(r'[0-9]*/[0-9]*$', result[0])[0]
                        cabs = pattern.split('/')
                        new_str = result[0].replace(pattern, '')

                        src = new_str.split('/')
                        if -1 < result[1].find(value) <= 5:  # result[1].find(value) > -1 and result[1].find(value) <= 5
                            lesson = src[0]
                            cabinet = cabs[0]
                        if result[1].find(value) > -1 and result[1].find(value) >= 5:
                            lesson = src[1]
                            cabinet = cabs[1]

                        out_data.append([lesson, cabinet])  # global
                    else:
                        out_data.append([result[0]])

                if len(result) == 1:
                    cabinet = item[i + 1]
                    lesson = item[i - 3] + item[i - 2] + item[i - 1]
                    out_data.append([lesson, cabinet])

    return out_data
