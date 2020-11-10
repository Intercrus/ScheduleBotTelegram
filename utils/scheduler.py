import os
from datetime import datetime, date
import asyncio
import re
import aioschedule
import requests
from googleapiclient.errors import HttpError

from utils.db_api import quick_commands as commands
from utils.data_util import get_data_from_google, find_timetable_by_group


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
                                r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|\d|(\bакт)\s(\bзал)|\s\sдист\s\s)", i).group(
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
