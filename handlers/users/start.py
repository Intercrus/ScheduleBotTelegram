import asyncpg
from aiogram import types
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from loader import dp, bot
from utils.db_api import quick_commands as commands
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from keyboards.default.choice_stud_or_teach_kb import choice_kb


@dp.message_handler(CommandStart(), state=None)
async def command_start(message: types.Message, state: FSMContext):

    await message.answer(f'👋 Здравствуйте, {message.from_user.full_name}!\n'
                         f'Кем вы являетесь?', reply_markup=choice_kb)

    await StatesOfBot.start_state.set()
