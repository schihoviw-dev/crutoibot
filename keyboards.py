# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    SUPPORT_USERNAME,
    EMOJI_DEAL, EMOJI_GRAM, EMOJI_STARS, EMOJI_HAMMER,
    EMOJI_CHECK, EMOJI_CROSS, EMOJI_BACK, EMOJI_SHARE,
    EMOJI_CHART, EMOJI_LIST, EMOJI_USERS, EMOJI_SETTINGS,
    EMOJI_PROFILE, EMOJI_WITHDRAW, EMOJI_CARD, EMOJI_GLOBE,
    EMOJI_CHAT, EMOJI_GROUP
)

def main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text=f"{EMOJI_DEAL} Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text=f"{EMOJI_PROFILE} Профиль", callback_data="profile")],
        [InlineKeyboardButton(text=f"{EMOJI_WITHDRAW} Вывод", callback_data="withdraw")],
        [InlineKeyboardButton(text=f"{EMOJI_CARD} Реквизиты", callback_data="requisites")],
        [InlineKeyboardButton(text=f"{EMOJI_GROUP} Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text=f"{EMOJI_GLOBE} Язык", callback_data="language")],
        [InlineKeyboardButton(text=f"{EMOJI_CHAT} Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")],
    ]
    
    if is_admin:
        keyboard.insert(0, [InlineKeyboardButton(text=f"{EMOJI_SETTINGS} Админ-панель", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{EMOJI_CHART} Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text=f"{EMOJI_LIST} Все сделки", callback_data="admin_deals")],
        [InlineKeyboardButton(text=f"{EMOJI_USERS} Все юзеры", callback_data="admin_users")],
        [InlineKeyboardButton(text=f"{EMOJI_BACK} Назад в меню", callback_data="back_to_main")]
    ])

def currency_selection():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{EMOJI_GRAM} GRAM", callback_data="currency_gram")],
        [InlineKeyboardButton(text=f"{EMOJI_STARS} Звёзды", callback_data="currency_stars")],
        [InlineKeyboardButton(text=f"{EMOJI_BACK} Назад", callback_data="back_to_main")]
    ])

def requisite_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{EMOJI_GRAM} Добавить GRAM", callback_data="add_gram")],
        [InlineKeyboardButton(text=f"{EMOJI_CROSS} Удалить все", callback_data="delete_requisites")],
        [InlineKeyboardButton(text=f"{EMOJI_BACK} Назад", callback_data="back_to_main")]
    ])

def deal_actions(deal_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{EMOJI_SHARE} Поделиться ссылкой", callback_data=f"share_{deal_code}")],
        [InlineKeyboardButton(text=f"{EMOJI_CROSS} Отмена", callback_data=f"cancel_deal_{deal_code}")]
    ])

def deal_status_buttons(deal_code, is_seller=False):
    buttons = []
    if is_seller:
        buttons.append([InlineKeyboardButton(text=f"{EMOJI_CHECK} Подтвердить передачу", callback_data=f"confirm_deal_seller_{deal_code}")])
    buttons.append([InlineKeyboardButton(text=f"{EMOJI_CHAT} Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def deal_paid_buttons(deal_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{EMOJI_HAMMER} Трахнуть мамонта", callback_data=f"hit_mammoth_{deal_code}")],
        [InlineKeyboardButton(text=f"{EMOJI_CHAT} Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")]
    ])

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{EMOJI_BACK} Назад", callback_data="back_to_main")]
    ])

def ok_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{EMOJI_CHECK} OK", callback_data="back_to_main")]
    ])

def share_deal(deal_code, deal_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{EMOJI_SHARE} Поделиться ссылкой", url=deal_link)],
        [InlineKeyboardButton(text=f"{EMOJI_CROSS} Отмена", callback_data=f"cancel_deal_{deal_code}")]
    ])