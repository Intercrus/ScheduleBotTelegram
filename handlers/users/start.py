import asyncpg
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text

from keyboards.default import who_you_are
from loader import dp
from utils.db_api import quick_commands as commands
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot


@dp.message_handler(CommandStart(), state=None)
async def bot_start(message: types.Message, state: FSMContext):
    name = message.from_user.full_name
    await commands.add_user(id=message.from_user.id,
                            name=name)

    # count = await commands.count_users()

    await message.answer(f'Привет, {message.from_user.full_name}!\n'
                         "Кем вы являетесь?",
                         reply_markup=who_you_are)
    await StatesOfBot.start_state.set()
    # await StatesOfBot.next()
