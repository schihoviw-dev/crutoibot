# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_USERNAME

def main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton(text="🛒 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="💰 Вывод", callback_data="withdraw")],
        [InlineKeyboardButton(text="💳 Реквизиты", callback_data="requisites")],
        [InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text="🌐 Язык", callback_data="language")],
        [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")],
    ]
    
    if is_admin:
        keyboard.insert(0, [InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📋 Все сделки", callback_data="admin_deals")],
        [InlineKeyboardButton(text="👥 Все юзеры", callback_data="admin_users")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])

def currency_selection():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 GRAM", callback_data="currency_gram")],
        [InlineKeyboardButton(text="⭐ Звёзды", callback_data="currency_stars")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def requisite_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить GRAM", callback_data="add_gram")],
        [InlineKeyboardButton(text="🗑 Удалить все", callback_data="delete_requisites")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def deal_actions(deal_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поделиться ссылкой", callback_data=f"share_{deal_code}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_deal_{deal_code}")]
    ])

def deal_status_buttons(deal_code, is_seller=False):
    buttons = []
    if is_seller:
        buttons.append([InlineKeyboardButton(text="✅ Подтвердить передачу", callback_data=f"confirm_deal_seller_{deal_code}")])
    buttons.append([InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def deal_paid_buttons(deal_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔨 Трахнуть мамонта", callback_data=f"hit_mammoth_{deal_code}")],
        [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")]
    ])

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def ok_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ OK", callback_data="back_to_main")]
    ])

def share_deal(deal_code, deal_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поделиться ссылкой", url=deal_link)],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_deal_{deal_code}")]
    ])