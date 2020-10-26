from aiogram.dispatcher.filters.builtin import Text
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.default import main_menu
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from keyboards.inline import setup_button_inline, setup_callback


@dp.message_handler(Text(equals=["Студент", "Преподаватель"]), state=StatesOfBot.start_state)
async def accept_groups(message: Message, state: FSMContext):
    await message.answer(f"Вы {message.text}. Переходите к следующему пункту",
                         reply_markup=ReplyKeyboardRemove())

    await message.answer(f"Введите название вашей группы, скопировав из списка\n"
                         "Например 2ГУ")

    file_name_group = open('/home/alien/PycharmProjects/SheduleBotTelegram/handlers/users/name_groups')
    await bot.send_document(chat_id=message.chat.id, document=file_name_group)
    file_name_group.close()

    await StatesOfBot.who_you_are_state.set()


@dp.message_handler(state=StatesOfBot.who_you_are_state)
async def search_groups(message: Message, state: FSMContext):
    # await message.answer(f"main_menu state. welcome ~/")
    await message.answer(message.text)
    data_file = []
    with open("/home/alien/PycharmProjects/SheduleBotTelegram/handlers/users/name_groups", 'r') as read_file:
        for line in read_file:
            data_file.append(line.strip('\n'))
    none_list = []
    acc_list = []
    for line in data_file:
        if message.text == line:
            acc_list.append(line)
        else:
            none_list.append(line)
    if acc_list:
        await message.answer(f"Группа {message.text} успешно найдена."
                             f"Выберите пункт, который вам интересен",
                             reply_markup=main_menu)
        await StatesOfBot.search_groups_state.set()
        await state.finish()
    else:
        await message.answer(f"Группа {message.text} не найдена\n"
                             "Повторите попытку")
        await StatesOfBot.who_you_are_state.set()




