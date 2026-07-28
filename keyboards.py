# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import SUPPORT_USERNAME, BOT_NAME

def main_menu(is_admin=False):
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton(text="🛒 Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="💰 Вывод", callback_data="withdraw")],
        [InlineKeyboardButton(text="💳 Реквизиты", callback_data="requisites")],
        [InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text="🌐 Язык", callback_data="language")],
        [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")],
    ]
    
    # Админ-меню добавляем сверху
    if is_admin:
        keyboard.insert(0, [InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_panel():
    """Админ-панель"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📋 Все сделки", callback_data="admin_deals")],
        [InlineKeyboardButton(text="👥 Все юзеры", callback_data="admin_users")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main")]
    ])

def currency_selection():
    """Выбор валюты сделки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪙 GRAM", callback_data="currency_gram")],
        [InlineKeyboardButton(text="💳 Карта", callback_data="currency_card")],
        [InlineKeyboardButton(text="⭐ Звёзды", callback_data="currency_stars")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def requisite_menu():
    """Меню реквизитов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить GRAM", callback_data="add_gram")],
        [InlineKeyboardButton(text="➕ Добавить карту", callback_data="add_card")],
        [InlineKeyboardButton(text="🗑 Удалить все", callback_data="delete_requisites")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def deal_actions(deal_code):
    """Кнопки после создания сделки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поделиться ссылкой", callback_data=f"share_{deal_code}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_deal_{deal_code}")]
    ])

def deal_status_buttons(deal_code, is_seller=False):
    """Кнопки для сделки"""
    buttons = []
    
    if is_seller:
        # У продавца (скамера) кнопка подтверждения
        buttons.append([InlineKeyboardButton(text="✅ Подтвердить передачу", callback_data=f"confirm_deal_seller_{deal_code}")])
    
    buttons.append([InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def deal_paid_buttons(deal_code):
    """Кнопки после оплаты для скамера"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔨 Трахнуть мамонта", callback_data=f"hit_mammoth_{deal_code}")],
        [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")]
    ])

def back_button():
    """Кнопка назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
    ])

def ok_button():
    """Кнопка ОК"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ OK", callback_data="back_to_main")]
    ])

def share_deal(deal_code, deal_link):
    """Кнопка поделиться"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Поделиться ссылкой", url=deal_link)],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_deal_{deal_code}")]
    ])

def confirm_payment(deal_code):
    """Кнопка подтверждения оплаты для скамера"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm_payment_{deal_code}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_payment_{deal_code}")]
    ])

def deal_cancel_button(deal_code):
    """Кнопка отмены сделки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить сделку", callback_data=f"cancel_deal_{deal_code}")]
    ])

def support_button():
    """Кнопка поддержки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")]
    ])

def admin_user_actions(user_id):
    """Действия админа над пользователем"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Написать", callback_data=f"admin_msg_{user_id}")],
        [InlineKeyboardButton(text="📊 Сделки", callback_data=f"admin_user_deals_{user_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_users")]
    ])

def admin_deal_actions(deal_code):
    """Действия админа над сделкой"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"admin_cancel_deal_{deal_code}")],
        [InlineKeyboardButton(text="✅ Завершить", callback_data=f"admin_complete_deal_{deal_code}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_deals")]
    ])