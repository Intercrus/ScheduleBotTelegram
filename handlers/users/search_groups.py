from keyboards.default import main_menu
from loader import dp, bot
from aiogram.dispatcher import FSMContext
from states.botStates import StatesOfBot
from utils.db_api import quick_commands as commands
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import types


@dp.message_handler(state=StatesOfBot.start_state, text="Студент")
async def command_start(message: types.Message, state: FSMContext):
    name = message.from_user.full_name
    await commands.add_user(id=message.from_user.id,
                            name=name)

    await message.answer(
        f'Введите название вашей группы, скопировав из списка\n'
        f'Например: 2ИС-2', reply_markup=ReplyKeyboardRemove())

    file_name_group = open("/src/data/name_groups.txt")
    await bot.send_document(chat_id=message.chat.id, document=file_name_group)
    file_name_group.close()

    await StatesOfBot.enter_student.set()


@dp.message_handler(state=StatesOfBot.start_state, text="Преподаватель")
async def command_start(message: types.Message, state: FSMContext):
    name = message.from_user.full_name
    await commands.add_user(id=message.from_user.id,
                            name=name)

    await message.answer(
        f'Введите ваше ФИО, скопировав из списка\n'
        f'Например: Опуховская АА', reply_markup=ReplyKeyboardRemove())

    file_name_group = open("/src/data/name_teachers.txt")
    await bot.send_document(chat_id=message.chat.id, document=file_name_group)
    file_name_group.close()

    await StatesOfBot.enter_teacher.set()


@dp.message_handler(state=StatesOfBot.enter_student)
async def search_groups(message: Message, state: FSMContext):
    data_file, none_list, acc_list = [], [], []

    with open("/src/data/name_groups.txt", 'r') as read_file:
        for line in read_file:
            data_file.append(line.strip('\n'))

    for line in data_file:
        if message.text == line:
            acc_list.append(line)
        else:
            none_list.append(line)

    if acc_list:
        await message.answer(f"Группа {message.text} успешно найдена.\n"
                             f"Выберите пункт, который вам интересен",
                             reply_markup=main_menu)

        await commands.update_user_name_group(name_group=message.text,
                                              id=message.from_user.id)

        await commands.update_user_teacher(teacher="None",
                                           id=message.from_user.id)

        await StatesOfBot.search_groups_state.set()
        await state.finish()
    else:
        await message.answer(f"Группа {message.text} не найдена\n"
                             "Повторите попытку")
        await StatesOfBot.enter_student.set()


@dp.message_handler(state=StatesOfBot.enter_teacher)
async def search_groups(message: Message, state: FSMContext):
    data_file, none_list, acc_list = [], [], []

    with open("/src/data/name_teachers.txt", 'r') as read_file:
        for line in read_file:
            data_file.append(line.strip('\n'))

    for line in data_file:
        if message.text == line:
            acc_list.append(line)
        else:
            none_list.append(line)

    if acc_list:
        await message.answer(f"Преподаватель {message.text} успешно найден.\n"
                             f"Выберите пункт, который вам интересен",
                             reply_markup=main_menu)

        await commands.update_user_name_group(name_group="None",
                                              id=message.from_user.id)

        await commands.update_user_teacher(teacher=message.text,
                                           id=message.from_user.id)

        await StatesOfBot.search_groups_state.set()
        await state.finish()
    else:
        await message.answer(f"Преподаватель {message.text} не найден\n"
                             "Повторите попытку")
        await StatesOfBot.enter_teacher.set()
