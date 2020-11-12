from aiogram.dispatcher.filters.state import StatesGroup, State


class StatesOfBot(StatesGroup):
    start_state = State()
    choice_student_or_teacher = State()
    enter_teacher = State()
    enter_student = State()
    search_groups_state = State()
    schedule_state = State()
    search_by_teacher_state = State()
    search_by_name_group = State()
    search_by_spec_day = State()

