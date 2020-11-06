import os
from datetime import datetime, date
import asyncio
import aioschedule
import requests
from utils.db_api import quick_commands as commands
from utils.data_util import get_data_from_google, find_timetable_by_group


async def send_notification():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    date_today = date.today()

    users = await commands.select_all_users_for_notification(current_time)

    if not users:
        pass
    else:
        data = await get_data_from_google(date_today)
        for item in users:
            timetable = await find_timetable_by_group(data, item.name_group)
            msg = f'Расписание на {date_today.strftime("%d.%m.%Y")}\n\n{timetable}'
            url = 'https://api.telegram.org/bot' + \
                str(os.getenv("BOT_TOKEN")) + '/sendMessage?chat_id=' + \
                str(item.id) + '&text=' + msg
            requests.get(url=url)


async def scheduler():
    aioschedule.every(1).minutes.do(send_notification)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)
