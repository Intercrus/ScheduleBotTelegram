import os
from datetime import datetime, date
import asyncio
import re
from itertools import zip_longest

import aioschedule
import requests
from googleapiclient.errors import HttpError

from utils.db_api import quick_commands as commands
from utils.data_util import get_data_from_google, find_timetable_by_group, find_timetable_by_teacher


async def send_notification():
    global item
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    date_today = date.today()
    users = await commands.select_all_users_for_notification(current_time)

    if not users:
        pass
    else:
        try:
            data = await get_data_from_google(date_today)

            for item in users:
                if item.name_group != 'None':
                    timetable = await find_timetable_by_group(data, item.name_group)
                    reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
                    time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                                    "11:30 - 12:50", "13:20 - 14:40",
                                    "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
                    reformat_timetable = timetable.split("\n")
                    div_info_lesson = []

                    for i in reformat_timetable:

                        try:
                            try:
                                name_teacher = re.search(
                                    r"\s([А-Я](.)*\s[А-Я][А-Я][,](.)*\s[А-Я][А-Я]|[А-Я](.)*\s[А-Я][А-Я]\s|\s[А-Я]......\s[А-Я][А-Я]|\s[А-Я].......\s[А-Я][А-Я])",
                                    i).group(0)
                                name_teacher_format = re.search(
                                    r"[А-Я][а-я](.)*\s[А-Я][А-Я]|[А-Я][а-я](.)*\s[А-Я][А-Я][,][А-Я](.)*\s[А-Я][А-Я]",
                                    name_teacher).group(0)
                            except AttributeError:
                                name_teacher_format = ""
                            lesson = re.search(r"[0-9].[А-Я](.){18}\s|[0-9].[А-Я][А-Я]\s\d\d", i).group(0)

                            if name_teacher_format.strip() == "Маликина АВ" or name_teacher_format.strip() == "Ольшина ТА":
                                cabinet = "-"
                            else:
                                cabinet = re.search(
                                    r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|\d|(\bакт)\s(\bзал)|\s\sдист\s\s)",
                                    i).group(
                                    0)

                            number_of_lesson = re.search(r"[0-9]", i).group(0)

                            div_info_lesson.append(
                                f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👤{name_teacher_format.lstrip()}\n")

                        except AttributeError:
                            div_info_lesson.append(timetable)
                            break

                    new_line_n = "\n"
                    msg = (f"📅 {reformat_data.title()}\n\n {f'{new_line_n}'.join(div_info_lesson)}")
                    url = 'https://api.telegram.org/bot' + \
                          str(os.getenv("BOT_TOKEN")) + '/sendMessage?chat_id=' + \
                          str(item.id) + '&text=' + msg
                    requests.get(url=url)

                else:
                    reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
                    time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                                    "11:30 - 12:50", "13:20 - 14:40",
                                    "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
                    timetable = await find_timetable_by_teacher(data, item.teacher)
                    reformat_timetable = sorted(timetable)
                    teacher_name = str(item.teacher)
                    teacher_id = item.id
                    group_names, div_info_lesson = [], []

                    for item in reformat_timetable:
                        group_names.append(item.pop(-1))

                    reformat_timetable_2 = [item for sublist in reformat_timetable for item in sublist]

                    def concatenation_of_two_strings(elem):
                        for x in zip_longest(elem[::2], elem[1::2], fillvalue=''):
                            yield '  '.join(x)

                    reformat_timetable_3 = list(concatenation_of_two_strings(reformat_timetable_2))

                    count_group = -1
                    if not timetable:
                        name_day = date_today.strftime("%A")
                        format_data = date_today.strftime("%d.%m.%y")
                        msg = (f"📅 {''.join(format_data)}\nНа сегодня пар нет")
                    else:
                        for i in reformat_timetable_3:
                            lesson = re.search(r"[0-9].[А-Я](.)*\s", i).group(0)
                            if teacher_name == "Маликина АВ" or teacher_name == "Ольшина ТА":
                                cabinet = "-"
                            else:
                                cabinet = re.search(
                                    r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|(\bакт)(\bзал)|дист|\d)", i).group(0)
                            number_of_lesson = re.search(r"[0-9]", i).group(0)

                            count_group += 1
                            div_info_lesson.append(
                                f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👥{group_names[count_group]}\n 🧑‍🏫{teacher_name}\n")

                        new_line_n = "\n"
                        msg = (f"📅 {reformat_data.title()}\n\n {f'{new_line_n}'.join(div_info_lesson)}\n\n")

                    url = 'https://api.telegram.org/bot' + \
                          str(os.getenv("BOT_TOKEN")) + '/sendMessage?chat_id=' + \
                          str(teacher_id) + '&text=' + msg
                    requests.get(url=url)

        except HttpError:
            name_day = date_today.strftime("%A")
            format_data = date_today.strftime("%d.%m.%y")

            if name_day == "Sunday":
                msg = (f"📅 {''.join(format_data)}, {''.join(name_day)}\nВыходной день")
                url = 'https://api.telegram.org/bot' + \
                      str(os.getenv("BOT_TOKEN")) + '/sendMessage?chat_id=' + \
                      str(item.id) + '&text=' + msg
                requests.get(url=url)
            else:
                msg = (f"📅 {''.join(format_data)}, {''.join(name_day)}\nНет данных")
                url = 'https://api.telegram.org/bot' + \
                      str(os.getenv("BOT_TOKEN")) + '/sendMessage?chat_id=' + \
                      str(item.id) + '&text=' + msg
                requests.get(url=url)


async def scheduler():
    aioschedule.every(1).minutes.do(send_notification)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)
