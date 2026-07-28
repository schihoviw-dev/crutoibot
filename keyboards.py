from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_USERNAME, E_DEAL, E_GRAM, E_STARS, E_HAMMER, E_CHECK, E_CROSS, E_BACK, E_SHARE, E_CHART, E_LIST, E_USERS, E_SETTINGS, E_PROFILE, E_WITHDRAW, E_CARD, E_GLOBE, E_CHAT, E_GROUP

def main_menu(is_admin=False):
    kb = [
        [InlineKeyboardButton(text=f"{E_DEAL} Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text=f"{E_PROFILE} Профиль", callback_data="profile")],
        [InlineKeyboardButton(text=f"{E_WITHDRAW} Вывод", callback_data="withdraw")],
        [InlineKeyboardButton(text=f"{E_CARD} Реквизиты", callback_data="requisites")],
        [InlineKeyboardButton(text=f"{E_GROUP} Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text=f"{E_GLOBE} Язык", callback_data="language")],
        [InlineKeyboardButton(text=f"{E_CHAT} Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")],
    ]
    if is_admin:
        kb.insert(0, [InlineKeyboardButton(text=f"{E_SETTINGS} Админ-панель", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_CHART} Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text=f"{E_LIST} Все сделки", callback_data="admin_deals")],
        [InlineKeyboardButton(text=f"{E_USERS} Все юзеры", callback_data="admin_users")],
        [InlineKeyboardButton(text=f"{E_BACK} Назад в меню", callback_data="back_to_main")]
    ])

def currency_selection():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_GRAM} GRAM", callback_data="currency_gram")],
        [InlineKeyboardButton(text=f"{E_STARS} Звёзды", callback_data="currency_stars")],
        [InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="back_to_main")]
    ])

def requisite_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_GRAM} Добавить GRAM", callback_data="add_gram")],
        [InlineKeyboardButton(text=f"{E_CROSS} Удалить все", callback_data="delete_requisites")],
        [InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="back_to_main")]
    ])

def deal_actions(deal_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_SHARE} Поделиться ссылкой", callback_data=f"share_{deal_code}")],
        [InlineKeyboardButton(text=f"{E_CROSS} Отмена", callback_data=f"cancel_deal_{deal_code}")]
    ])

def deal_status_buttons(deal_code, is_seller=False):
    kb = []
    if is_seller:
        kb.append([InlineKeyboardButton(text=f"{E_CHECK} Подтвердить передачу", callback_data=f"confirm_deal_seller_{deal_code}")])
    kb.append([InlineKeyboardButton(text=f"{E_CHAT} Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def deal_paid_buttons(deal_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_HAMMER} Трахнуть мамонта", callback_data=f"hit_mammoth_{deal_code}")],
        [InlineKeyboardButton(text=f"{E_CHAT} Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")]
    ])

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_BACK} Назад", callback_data="back_to_main")]
    ])

def ok_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_CHECK} OK", callback_data="back_to_main")]
    ])

def share_deal(deal_code, deal_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{E_SHARE} Поделиться ссылкой", url=deal_link)],
        [InlineKeyboardButton(text=f"{E_CROSS} Отмена", callback_data=f"cancel_deal_{deal_code}")]
    ])