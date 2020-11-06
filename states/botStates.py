from aiogram.dispatcher.filters.state import StatesGroup, State


class StatesOfBot(StatesGroup):
    start_state = State()
    search_groups_state = State()
    shedule_state = State()
    search_by_teacher_state = State()

