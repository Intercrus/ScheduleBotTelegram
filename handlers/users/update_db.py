from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command
from aiogram.utils.markdown import hcode

from loader import dp
from utils.db_api import quick_commands as commands


@dp.message_handler(Command("email"))
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer("Пришли мне свой имейл")
    await state.set_state("email")


@dp.message_handler(state="email")
async def enter_email(message: types.Message, state: FSMContext):
    email = message.text
    await commands.update_user_email(email=email, id=message.from_user.id)
    user = await commands.select_user(id=message.from_user.id)
    await message.answer("Данные обновлены. Запись в БД: \n" +
                         hcode(f"id={user.id}\n"
                               f"name={user.name}\n"
                               f"email={user.email}"))
    await state.finish()
