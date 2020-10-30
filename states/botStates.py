from aiogram.dispatcher.filters.state import StatesGroup, State


class StatesOfBot(StatesGroup):
    start_state = State()
    who_you_are_state = State()
    search_groups_state = State()
    parser_state= State()
