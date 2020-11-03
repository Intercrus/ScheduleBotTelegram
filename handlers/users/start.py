import asyncpg
from aiogram import types
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from loader import dp, bot
from utils.db_api import quick_commands as commands
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot


@dp.message_handler(CommandStart(), state=None)
async def command_start(message: types.Message, state: FSMContext):
    name = message.from_user.full_name
    await commands.add_user(id=message.from_user.id,
                            name=name)

    await message.answer(f'Здравствуйте, {message.from_user.full_name}!\n'
                         f'Введите название вашей группы, скопировав из списка\n'
                         f'Например: 2ИС-2', reply_markup=ReplyKeyboardRemove())

    file_name_group = open('/home/alien/PycharmProjects/ScheduleBotTelegram/data/name_groups.txt')
    await bot.send_document(chat_id=message.chat.id, document=file_name_group)
    file_name_group.close()

    await StatesOfBot.start_state.set()
