from datetime import date, timedelta
import re
from itertools import zip_longest

from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
from aiogram.types import Message
from loader import dp
from utils.db_api import quick_commands as commands
from utils.data_util import get_data_from_google, find_timetable_by_group, find_timetable_by_teacher
from utils.misc import rate_limit


@rate_limit(limit=10)
@dp.message_handler(text="Сегодня")
async def schedule_today(message: Message):
    global data, new_line_n, name_teacher_format, name_teacher
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = date.today()

    if user.name_group != 'None':
        try:
            data = await get_data_from_google(data_today)
            timetable = await find_timetable_by_group(data, group_name)
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
                    lesson = re.search(
                        r"[0-9].[А-Я](.){18}\s|[0-9].[А-Я][А-Я]\s\d\d", i).group(0)

                    if name_teacher_format.strip() == "Маликина АВ" or name_teacher_format.strip() == "Ольшина ТА":
                        cabinet = "-"
                    else:
                        cabinet = re.search(
                            r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|\d|(\bакт)\s(\bзал)|\s\sдист\s\s|до)",
                            i).group(0)

                    number_of_lesson = re.search(r"[0-9]", i).group(0)

                    div_info_lesson.append(
                        f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 🧑‍🏫{name_teacher_format.lstrip()}\n")

                except AttributeError:
                    div_info_lesson.append(timetable)
                    break

            new_line_n = "\n"
            await message.answer(f"📅 {reformat_data.title()}\n\n"
                                 f"{f'{new_line_n}'.join(div_info_lesson)}")
        except HttpError:
            name_day = data_today.strftime("%A")
            format_data = data_today.strftime("%d.%m.%y")

            if name_day == "Sunday":
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Выходной день")
            else:
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Нет данных")

    else:
        try:
            teacher_name = user.teacher
            data = await get_data_from_google(data_today)
            reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
            time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                            "11:30 - 12:50", "13:20 - 14:40",
                            "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
            timetable = await find_timetable_by_teacher(data, teacher_name)
            reformat_timetable = sorted(timetable)

            group_names, div_info_lesson = [], []

            for item in reformat_timetable:
                group_names.append(item.pop(-1))

            reformat_timetable_2 = [
                item for sublist in reformat_timetable for item in sublist]

            def concatenation_of_two_strings(elem):
                for x in zip_longest(elem[::2], elem[1::2], fillvalue=''):
                    yield '  '.join(x)

            reformat_timetable_3 = list(
                concatenation_of_two_strings(reformat_timetable_2))

            count_group = -1
            if not timetable:
                name_day = data_today.strftime("%A")
                format_data = data_today.strftime("%d.%m.%y")
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Ничего не найдено")
            else:
                for i in reformat_timetable_3:
                    lesson = re.search(r"[0-9].[А-Я](.)*\s", i).group(0)
                    if message.text == "Маликина АВ" or message.text == "Ольшина ТА":
                        cabinet = "-"
                    else:
                        cabinet = re.search(
                            r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|(\bакт)(\bзал)|дист|\d)", i).group(0)
                    number_of_lesson = re.search(r"[0-9]", i).group(0)

                    count_group += 1
                    div_info_lesson.append(
                        f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👥{group_names[count_group]}\n 🧑‍🏫{teacher_name.lstrip()}\n")

                new_line_n = "\n"
                await message.answer(f"📅 {reformat_data.title()}\n\n"
                                     f"{f'{new_line_n}'.join(div_info_lesson)}\n\n")

        except HttpError:
            name_day = data_today.strftime("%A")
            format_data = data_today.strftime("%d.%m.%y")

            if name_day == "Sunday":
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Выходной день")
            else:
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Нет данных")

        except IndexError:
            pass


@rate_limit(limit=10)
@dp.message_handler(text="Завтра")
async def schedule_tomorrow(message: Message):
    global data
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group
    data_today = date.today() + timedelta(days=1)

    if user.name_group != 'None':
        try:
            data = await get_data_from_google(data_today)
            timetable = await find_timetable_by_group(data, group_name)
            reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
            time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                            "11:30 - 12:50", "13:20 - 14:40",
                            "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
            reformat_timetable = timetable.split("\n")
            div_info_lesson = []

            for i in reformat_timetable:
                print(reformat_timetable)
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
                    lesson = re.search(
                        r"[0-9].[А-Я](.){18}\s|[0-9].[А-Я][А-Я]\s\d\d", i).group(0)

                    if name_teacher_format.strip() == "Маликина АВ" or name_teacher_format.strip() == "Ольшина ТА":
                        cabinet = "-"
                    else:
                        cabinet = re.search(
                            r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|\d|(\bакт)\s(\bзал)|\s\sдист\s\s|до)", i).group(
                            0)

                    number_of_lesson = re.search(r"[0-9]", i).group(0)

                    div_info_lesson.append(
                        f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 🧑‍🏫{name_teacher_format.lstrip()}\n")

                except AttributeError:
                    div_info_lesson.append(timetable)
                    break

            new_line_n = "\n"
            await message.answer(f"📅 {reformat_data.title()}\n\n"
                                 f"{f'{new_line_n}'.join(div_info_lesson)}")
        except HttpError:
            name_day = data_today.strftime("%A")
            format_data = data_today.strftime("%d.%m.%y")

            if name_day == "Sunday":
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Выходной день")
            else:
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Нет данных")

    else:
        try:
            teacher_name = user.teacher
            data = await get_data_from_google(data_today)
            reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
            time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                            "11:30 - 12:50", "13:20 - 14:40",
                            "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
            timetable = await find_timetable_by_teacher(data, teacher_name)
            reformat_timetable = sorted(timetable)

            group_names = []

            for item in reformat_timetable:
                group_names.append(item.pop(-1))

            reformat_timetable_2 = [
                item for sublist in reformat_timetable for item in sublist]

            def concatenation_of_two_strings(elem):
                for x in zip_longest(elem[::2], elem[1::2], fillvalue=''):
                    yield '  '.join(x)

            reformat_timetable_3 = list(
                concatenation_of_two_strings(reformat_timetable_2))
            div_info_lesson = []

            count_group = -1
            if not timetable:
                name_day = data_today.strftime("%A")
                format_data = data_today.strftime("%d.%m.%y")
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Ничего не найдено")
            else:
                for i in reformat_timetable_3:
                    lesson = re.search(r"[0-9].[А-Я](.)*\s", i).group(0)
                    if message.text == "Маликина АВ" or message.text == "Ольшина ТА":
                        cabinet = "-"
                    else:
                        cabinet = re.search(
                            r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|(\bакт)(\bзал)|дист|\d)", i).group(0)
                    number_of_lesson = re.search(r"[0-9]", i).group(0)

                    count_group += 1
                    div_info_lesson.append(
                        f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👥{group_names[count_group]}\n 🧑‍🏫{teacher_name.lstrip()}\n")

                new_line_n = "\n"
                await message.answer(f"📅 {reformat_data.title()}\n\n"
                                     f"{f'{new_line_n}'.join(div_info_lesson)}\n\n")

        except HttpError:
            name_day = data_today.strftime("%A")
            format_data = data_today.strftime("%d.%m.%y")

            if name_day == "Sunday":
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Выходной день")
            else:
                await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                     f"Нет данных")

        except IndexError:
            pass


@rate_limit(limit=30)
@dp.message_handler(text="Неделя")
async def schedule_for_week(message: Message):
    global data
    user = await commands.select_user(id=message.from_user.id)
    group_name = user.name_group

    if user.name_group != 'None':
        for day in range(7):
            data_today = date.today() + timedelta(days=day)

            try:
                data = await get_data_from_google(data_today)
                timetable = await find_timetable_by_group(data, group_name)
                reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
                time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                                "11:30 - 12:50", "13:20 - 14:40",
                                "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
                reformat_timetable = timetable.split("\n")
                div_info_lesson = []

                for i in reformat_timetable:
                    print(reformat_timetable)
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
                        lesson = re.search(
                            r"[0-9].[А-Я](.){18}\s|[0-9].[А-Я][А-Я]\s\d\d", i).group(0)

                        if name_teacher_format.strip() == "Маликина АВ" or name_teacher_format.strip() == "Ольшина ТА":
                            cabinet = "-"
                        else:
                            cabinet = re.search(
                                r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|\d|(\bакт)\s(\bзал)|\s\sдист\s\s|до)",
                                i).group(0)

                        number_of_lesson = re.search(r"[0-9]", i).group(0)

                        div_info_lesson.append(
                            f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 🧑‍🏫{name_teacher_format.lstrip()}\n")

                    except AttributeError:
                        div_info_lesson.append(timetable)
                        break

                new_line_n = "\n"
                await message.answer(f"📅 {reformat_data.title()}\n\n"
                                     f"{f'{new_line_n}'.join(div_info_lesson)}")
            except HttpError:
                name_day = data_today.strftime("%A")
                format_data = data_today.strftime("%d.%m.%y")

                if name_day == "Sunday":
                    await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                         f"Выходной день")
                    continue
                else:
                    await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                         f"Нет данных")
                    continue
    else:
        teacher_name = user.teacher
        for day in range(7):
            data_today = date.today() + timedelta(days=day)

            try:
                teacher_name = user.teacher
                data = await get_data_from_google(data_today)
                reformat_data = re.sub('^\s+|\n|\r|\s+$', '- ', data[0][0])
                time_lessons = ["0", "08:30 - 09:50", "10:00-11:20",
                                "11:30 - 12:50", "13:20 - 14:40",
                                "14:50 - 16:10", "16:20 - 17:40", "17:50 - 19:10"]
                timetable = await find_timetable_by_teacher(data, teacher_name)
                reformat_timetable = sorted(timetable)

                group_names = []

                for item in reformat_timetable:
                    group_names.append(item.pop(-1))

                reformat_timetable_2 = [
                    item for sublist in reformat_timetable for item in sublist]

                def concatenation_of_two_strings(elem):
                    for x in zip_longest(elem[::2], elem[1::2], fillvalue=''):
                        yield '  '.join(x)

                reformat_timetable_3 = list(
                    concatenation_of_two_strings(reformat_timetable_2))
                div_info_lesson = []

                count_group = -1
                if not timetable:
                    name_day = data_today.strftime("%A")
                    format_data = data_today.strftime("%d.%m.%y")
                    await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                         f"Ничего не найдено")
                    continue
                else:
                    for i in reformat_timetable_3:
                        lesson = re.search(r"[0-9].[А-Я](.)*\s", i).group(0)
                        if message.text == "Маликина АВ" or message.text == "Ольшина ТА":
                            cabinet = "-"
                        else:
                            cabinet = re.search(
                                r"\s\s(\d\d[а-я]|[А-Я][А-Я]|\d\d/\d\d|\d\d|(\bакт)(\bзал)|дист|\d)", i).group(0)
                        number_of_lesson = re.search(r"[0-9]", i).group(0)

                        count_group += 1
                        div_info_lesson.append(
                            f"🕗 {time_lessons[int(number_of_lesson)]} 🕗\n 📖{lesson[2:].lstrip()}\n 🚪{cabinet.lstrip()}\n 👥{group_names[count_group]}\n 🧑‍🏫{teacher_name.lstrip()}\n")

                    new_line_n = "\n"
                    await message.answer(f"📅 {reformat_data.title()}\n\n"
                                         f"{f'{new_line_n}'.join(div_info_lesson)}\n\n")
                    continue

            except HttpError:
                name_day = data_today.strftime("%A")
                format_data = data_today.strftime("%d.%m.%y")

                if name_day == "Sunday":
                    await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                         f"Выходной день")
                    continue
                else:
                    await message.answer(f"📅 {''.join(format_data)}, {''.join(name_day)}\n"
                                         f"Нет данных")
                    continue

            except IndexError:
                continue
