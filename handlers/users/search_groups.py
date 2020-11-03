import asyncpg
from aiogram.dispatcher.filters.builtin import Text
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.default import main_menu
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from keyboards.inline import setup_button_inline, setup_callback
from utils.db_api import quick_commands as commands


@dp.message_handler(state=StatesOfBot.start_state)
async def search_groups(message: Message, state: FSMContext):
    data_file, none_list, acc_list = [], [], []

    with open("/home/alien/PycharmProjects/ScheduleBotTelegram/data/name_groups.txt", 'r') as read_file:
        for line in read_file:
            data_file.append(line.strip('\n'))

    for line in data_file:
        if message.text == line:
            acc_list.append(line)
        else:
            none_list.append(line)

    if acc_list:
        await message.answer(f"Группа {message.text} успешно найдена.\n"
                             f"\n"
                             f"Бот находится в разработке, поэтому большинство функций на данный момент недоступно.\n"
                             f"\n"
                             f"Выберите пункт, который вам интересен",
                             reply_markup=main_menu)

        await commands.update_user_name_group(name_group=message.text,
                                              id=message.from_user.id)

        await StatesOfBot.search_groups_state.set()
        await state.finish()
    else:
        await message.answer(f"Группа {message.text} не найдена\n"
                             "Повторите попытку")
        await StatesOfBot.start_state.set()
