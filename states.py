# states.py
from aiogram.fsm.state import State, StatesGroup

class DealStates(StatesGroup):
    """Состояния для создания сделки"""
    waiting_currency = State()      # Ожидание выбора валюты
    waiting_amount = State()        # Ожидание ввода суммы
    waiting_description = State()   # Ожидание ввода описания

class RequisiteStates(StatesGroup):
    """Состояния для добавления реквизитов"""
    waiting_gram = State()          # Ожидание ввода адреса GRAM
    waiting_card = State()          # Ожидание ввода карты
    waiting_stars = State()         # Ожидание ввода звёзд (если нужно)

class AdminStates(StatesGroup):
    """Состояния для админ-действий"""
    waiting_send_message = State()  # Ожидание текста для рассылки
    waiting_set_deals = State()     # Ожидание количества сделок
    waiting_set_rating = State()    # Ожидание рейтинга
    waiting_user_id = State()       # Ожидание ID пользователя
    waiting_deal_code = State()     # Ожидание кода сделки

class ProfileStates(StatesGroup):
    """Состояния для профиля"""
    waiting_edit_name = State()     # Ожидание изменения имени
    waiting_edit_username = State() # Ожидание изменения юзернейма

class WithdrawStates(StatesGroup):
    """Состояния для вывода"""
    waiting_amount = State()        # Ожидание суммы вывода
    waiting_method = State()        # Ожидание метода вывода

class ReferralStates(StatesGroup):
    """Состояния для рефералов"""
    waiting_referral = State()      # Ожидание реферального кода