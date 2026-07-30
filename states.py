from aiogram.fsm.state import State, StatesGroup

class DealStates(StatesGroup):
    waiting_currency = State()
    waiting_amount = State()
    waiting_description = State()

class RequisiteStates(StatesGroup):
    waiting_gram = State()
    waiting_card = State()