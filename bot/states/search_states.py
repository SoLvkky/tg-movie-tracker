from aiogram.fsm.state import StatesGroup, State

class SearchStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_category = State()
    waiting_for_choice = State()
    waiting_for_confirmation = State()