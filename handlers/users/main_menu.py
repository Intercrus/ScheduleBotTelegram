import datetime
import time
import re
from pprint import pprint
import apiclient
import httplib2
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

from aiogram.dispatcher.filters.builtin import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from keyboards.default import main_menu
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from keyboards.inline.setup_button_inline import setup_button
from keyboards.inline.setup_callback import *
from keyboards.inline.search_button_inline import *
from keyboards.inline.search_callback import *
from utils.misc.parsing import get_schedules_data


@dp.message_handler(text="Настройки")
async def setup_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно настроить",
                         reply_markup=setup_button)


@dp.message_handler(text="Поиск")
async def search_keyboard(message: Message):
    await message.answer(f"Выберите то, что нужно найти",
                         reply_markup=search_button)


@dp.message_handler(text="Сегодня")
async def schedule_today(message: Message):
    get_schedules_data()
    await message.answer("ok.")


@dp.message_handler(text="Завтра")
async def shedule_tomorrow(message: Message):
    pass


@dp.callback_query_handler(text_contains="advertisement")
async def get_ad(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(message_id=call.message.message_id,
                             chat_id=call.message.chat.id)
    await call.message.answer("Подробности @scytheofdeath")

# @dp.message_handler(state=StatesOfBot.search_groups_state)
# async def main_menu(message: Message, state: FSMContext):
#     pass
#
#
#     await message.answer(f"setup",
#                      reply_markup=setup_button)
#
#     await StatesOfBot.main_menu_state.set()
