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


values = {'range': 'g!A1:N24', 'majorDimension': 'COLUMNS', 'values':
    [
        ['27.10.2020 \nВторник', '', '', '', '', '', '', '', '27.10.2020 \nВторник', '', '', '', '', '', '', '',
         '27.10.2020 \nВторник'],
        ['1ГС', '1.Русский язык                                                        Сергеева АА              9',
         '2.Физ-ра                      Ольшина ТА',
         '3.История                                                      Цветкова КС              9', '', '', '', '',
         '2ПС-1', '', '', '', '4.Админ право                                    Раутио АЭ          14',
         '5.Админ право                                    Раутио АЭ          14',
         '6.Гражд право                                    Акрицкая СГ          14', '', '3ПС-1',
         '1.Прав соц об                                     Мартынов СА             25',
         '2.Информатика                              Михайлова ИВ           20',
         '3.Ин.яз.   25/26                                   Бондарь ЛГ,Хафизова АА'],
        ['1А', '', '2.История                                                      Цветкова КС             9',
         '3.Физ-ра                      Ольшина ТА',
         '4.Химия                                                      Богданова НД              9', '', '', '',
         '2ПС-2',
         '', '', '', '4.История                                              Дианова КА          дист',
         '5.Гражд право                                    Акрицкая СГ        дист',
         '6.Админ право                                    Раутио АЭ        дист ',
         '7.Физ-ра                      Маликина АВ         дист', '3ПС-2',
         '1.Информатика  1 гр                             Михайлова ИВ           20',
         '2.Прав соц об                                     Мартынов СА             15',
         '3.Психология                                                      Дианова КА           13',
         '4.Прав соц об                                     Мартынов СА             15'],
        ['1Б', '1.История                                                      Лопарева АВ               10',
         '2.Литература                                                        Зайцева ВВ                10',
         '3.Экономика                                            Воронецкая ЛА         10', '', '', '', '', '2ГС', '',
         '',
         '', '4.Орг деят сл                                                Барышникова АЮ        дист',
         '5.Орг деят сл                                                Барышникова АЮ        дист ', '', '', '3ГС',
         '11:30',
         'Экзамен', '"Менеджмент"', 'Гущина АО', '8'],
        ['1БД', '1.История                                                      Цветкова КС              23',
         '2.Химия                                                      Богданова НД              23',
         '3.Математика                                                    Шидерская ОС               20', '', '', '',
         '',
         '2ТР', '11:30', 'Экзамен', '"Эк-ка отрасли"', 'Кузнецова СИ', 'акт зал', '', '', '3ИС-1', 'Производственная',
         'практика'], ['1В', '1.Физ-ра                      Ольшина ТА',
                       '2.Проект деят                                                        Сергеева АА              12',
                       '3.ОБЖ                                     Чванова НА             12', '', '', '', '', '2ИС-1',
                       '',
                       '', '', '4.Эл мат логики                     Голубник АА            26',
                       '5.Ин.яз.     25/26                                  Берников АП,Хафизова АА   ',
                       '6.Физ-ра                      Маликина АВ        ', '', '3ИС-2', 'Производственная',
                       'практика'],
        ['1ЗМ', '1.История                      Ускова КВ      14', '2.История                      Ускова КВ      14',
         '3.Информатика                                 Васильева СВ           30', '', '', '', '', '2ИС-2', '', '', '',
         '4.Осн алг                     Евграфова УС           28',
         '5.Опер ЭВМ                      Опуховская АА            20',
         '6.Эл мат логики                     Голубник АА            26',
         '7.Опер ЭВМ                      Опуховская АА            20', '3ИС-3', 'Производственная', 'практика'],
        ['1ПС-1', '', '2.Обществоз                                                      Лопарева АВ             21',
         '3.История                      Ускова КВ        21',
         '4.ОБЖ                                     Чванова НА             20', '', '', '', '2ИС-3', '', '', '',
         '4.Ин.яз.   27/29а                                    Берников АП,Хафизова АА   ',
         '5.Эл мат логики                     Голубник АА            27',
         '6.Опер ЭВМ                      Опуховская АА            20',
         '7.Осн алг                     Евграфова УС           28', '3ЗМ',
         '1.Геодезия                                               Силина АА              28',
         '2.Кадастры                                                  Пяжиева ТВ              28',
         '3.Кадастры                                                  Пяжиева ТВ              28'],
        ['1ПС-2', '1.История                                                      Дианова КА             13',
         '2.ОБЖ                                     Чванова НА             13',
         '3.Обществоз                                                      Лопарева АВ             13', '', '', '', '',
         '2ИС-4', '', '', '', '4.Выш мат                     Козлова ЮЕ           23',
         '5.Осн алг                     Евграфова УС           28',
         '6.Осн алг                     Евграфова УС           28',
         '7.Эл мат логики                     Голубник АА            23', '3БД',
         '1.ОКР                                            Воронецкая ЛА              27',
         '2.ОКР                                            Воронецкая ЛА              27',
         '3.Прав обес в ПД                                   Мартынов СА             27'],
        ['1ИС-1', '1.Русский язык                                                        Зайцева ВВ                 14',
         '2.Информатика                                 Васильева СВ           30',
         '3.Химия                                                      Богданова НД              14', '', '', '', '',
         '2ЗМ-1', '', '', '', '4.Стр черт                                               Силина АА              21',
         '5.Физ-ра                      Маликина АВ        ',
         '6.Ист потр коопр                                          Солдатова ТД            21', '', '3Б', '',
         '2.Бух техн                                                  Пашкевич ЕЛ      22',
         '3.Бух техн                                                  Пашкевич ЕЛ      22',
         '4.Физ-ра                      Ольшина ТА'],
        ['1ИС-2', '1.Математика                   Козлова ЮЕ           8',
         '2.География                                     Берников АП      8',
         '3.Русский язык                                                        Зайцева ВВ                 8',
         '', '', '', '', '2ЗМ-2', '', '', '',
         '4.Информатика                                 Васильева СВ           30',
         '5.Ист потр коопр                                          Солдатова ТД            23',
         '6.Стр черт                                               Силина АА              23',
         '', '3ТОП', '',
         '2.Русс яз и КР                         Бахрова МЕ           23',
         '3.Русс яз и КР                         Бахрова МЕ           23'],
        ['1ИС-3', '', '2.Математика                   Козлова ЮЕ           7',
         '3.География                                     Берников АП      7',
         '4.История                                                      Цветкова КС             7', '', '', '',
         '2БД-1',
         '', '', '', '4.Осн бух уч                                                 Пашкевич ЕЛ      22',
         '5.Статистика                             Филатова НА           30',
         '6.ОБР                                          Николаева ЮА         22', '', '4ТОП', '',
         '2.Русс яз и КР                         Бахрова МЕ           23',
         '3.Русс яз и КР                         Бахрова МЕ           23',
         '4.Ин.яз.                                  Бондарь ЛГ        25'],
        ['1ИС-4', '1.ОБЖ                                     Чванова НА             29а',
         '2.История                                                      Дианова КА             29а',
         '3.Математика                   Козлова ЮЕ           29а', '', '', '', '', '2БД-2', '', '', '',
         '4.Осн бух уч                                                 Бжесток ВА     10',
         '5.ОБР                                          Николаева   ЮА       10',
         '6.Статистика                                                  Филатова НА            10', '', '4ИС',
         '1.Инфор техн                            Панфилов АВ              ДО',
         '2.Инфор техн                            Панфилов АВ              ДО',
         '3.Инфор техн                            Панфилов АВ              ДО'],
        ['', '', '', '', '', '', '', '', '2Б', '11:30', 'Экзамен', '"Статистика"', 'Кустова АА']]}
