from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_USERNAME

# ID премиум-эмодзи для кнопок (чистые ID, без тегов!)
ICON_DEAL = "5980871942570251958"      # 💎
ICON_GRAM = "5980783470538921933"      # 🪙
ICON_STARS = "5981137191160518179"     # ⭐
ICON_HAMMER = "5935968647901089910"    # 🔨
ICON_CHECK = "5206607081334906820"     # ✅
ICON_CROSS = "5210952531676504517"     # ❌
ICON_BACK = "5958361550820480866"      # ⬅️
ICON_SHARE = "5311998535032409760"     # 📤
ICON_CHART = "5956166805352356645"     # 📊
ICON_LIST = "5361692603727252420"      # 📋
ICON_USERS = "5258011929993026890"     # 👥
ICON_SETTINGS = "5841693351249710667"  # ⚙️
ICON_PROFILE = "5258011929993026890"   # 👤
ICON_WITHDRAW = "5310191758255099001"  # 💰
ICON_CARD = "5445353829304387411"      # 💳
ICON_GLOBE = "5332724926216428039"     # 🌐
ICON_CHAT = "5447410659077661506"      # 💬
ICON_GROUP = "5237699328843200968"     # 👥

def main_menu(is_admin=False):
    kb = [
        [InlineKeyboardButton(
            text="Создать сделку",
            callback_data="create_deal",
            icon_custom_emoji_id=ICON_DEAL
        )],
        [InlineKeyboardButton(
            text="Профиль",
            callback_data="profile",
            icon_custom_emoji_id=ICON_PROFILE
        )],
        [InlineKeyboardButton(
            text="Вывод",
            callback_data="withdraw",
            icon_custom_emoji_id=ICON_WITHDRAW
        )],
        [InlineKeyboardButton(
            text="Реквизиты",
            callback_data="requisites",
            icon_custom_emoji_id=ICON_CARD
        )],
        [InlineKeyboardButton(
            text="Рефералы",
            callback_data="referrals",
            icon_custom_emoji_id=ICON_GROUP
        )],
        [InlineKeyboardButton(
            text="Язык",
            callback_data="language",
            icon_custom_emoji_id=ICON_GLOBE
        )],
        [InlineKeyboardButton(
            text="Поддержка",
            url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}",
            icon_custom_emoji_id=ICON_CHAT
        )],
    ]
    if is_admin:
        kb.insert(0, [InlineKeyboardButton(
            text="Админ-панель",
            callback_data="admin_panel",
            icon_custom_emoji_id=ICON_SETTINGS
        )])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Статистика", callback_data="admin_stats", icon_custom_emoji_id=ICON_CHART)],
        [InlineKeyboardButton(text="Все сделки", callback_data="admin_deals", icon_custom_emoji_id=ICON_LIST)],
        [InlineKeyboardButton(text="Все юзеры", callback_data="admin_users", icon_custom_emoji_id=ICON_USERS)],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_main", icon_custom_emoji_id=ICON_BACK)]
    ])

def currency_selection():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="GRAM", callback_data="currency_gram", icon_custom_emoji_id=ICON_GRAM)],
        [InlineKeyboardButton(text="Звёзды", callback_data="currency_stars", icon_custom_emoji_id=ICON_STARS)],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main", icon_custom_emoji_id=ICON_BACK)]
    ])

def requisite_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить GRAM", callback_data="add_gram", icon_custom_emoji_id=ICON_GRAM)],
        [InlineKeyboardButton(text="Удалить все", callback_data="delete_requisites", icon_custom_emoji_id=ICON_CROSS)],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main", icon_custom_emoji_id=ICON_BACK)]
    ])

def deal_actions(deal_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться ссылкой", callback_data=f"share_{deal_code}", icon_custom_emoji_id=ICON_SHARE)],
        [InlineKeyboardButton(text="Отмена", callback_data=f"cancel_deal_{deal_code}", icon_custom_emoji_id=ICON_CROSS)]
    ])

def deal_status_buttons(deal_code, is_seller=False):
    kb = []
    if is_seller:
        kb.append([InlineKeyboardButton(
            text="Подтвердить передачу",
            callback_data=f"confirm_deal_seller_{deal_code}",
            icon_custom_emoji_id=ICON_CHECK
        )])
    kb.append([InlineKeyboardButton(
        text="Поддержка",
        url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}",
        icon_custom_emoji_id=ICON_CHAT
    )])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def deal_paid_buttons(deal_code):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Трахнуть мамонта",
            callback_data=f"hit_mammoth_{deal_code}",
            icon_custom_emoji_id=ICON_HAMMER
        )],
        [InlineKeyboardButton(
            text="Поддержка",
            url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}",
            icon_custom_emoji_id=ICON_CHAT
        )]
    ])

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main", icon_custom_emoji_id=ICON_BACK)]
    ])

def ok_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="OK", callback_data="back_to_main", icon_custom_emoji_id=ICON_CHECK)]
    ])

def share_deal(deal_code, deal_link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться ссылкой", url=deal_link, icon_custom_emoji_id=ICON_SHARE)],
        [InlineKeyboardButton(text="Отмена", callback_data=f"cancel_deal_{deal_code}", icon_custom_emoji_id=ICON_CROSS)]
    ]) 