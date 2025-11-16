from aiogram.fsm.state import StatesGroup, State

class MovieStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_choice = State()
    waiting_for_confirmation = State()