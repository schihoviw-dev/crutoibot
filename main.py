import asyncio
import logging
import sqlite3
import random
import string
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    ParseMode, InputFile
)
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# ====================================================================================
# ВСТАВЛЕНО ТОБОЙ
# ====================================================================================
BOT_TOKEN = "7871598280:AAEFrtxg0lPqSDM6JEWtbhqrRe9NuKN0OBs"
ADMIN_IDS = [8844754156]

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('funpay_final.db', check_same_thread=False)
cursor = conn.cursor()

# ====================================================================================
# ГИФКА
# ====================================================================================
GIF_FOLDER = 'gifs'
if not os.path.exists(GIF_FOLDER):
    os.makedirs(GIF_FOLDER)

def get_gif():
    path = os.path.join(GIF_FOLDER, 'welcome.gif')
    if os.path.exists(path):
        return InputFile(path)
    return None

async def send_gif(chat_id, caption=None, reply_markup=None):
    gif = get_gif()
    if gif:
        await bot.send_animation(chat_id, animation=gif, caption=caption, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id, caption or "⚠️ Файл welcome.gif не найден", reply_markup=reply_markup)

def generate_deal_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))

def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0.0,
            deals_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 4.9,
            votes_count INTEGER DEFAULT 18,
            level TEXT DEFAULT 'Новичок',
            commission REAL DEFAULT 3.0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            deal_id TEXT PRIMARY KEY,
            seller_id INTEGER,
            buyer_id INTEGER DEFAULT 0,
            amount REAL,
            currency TEXT,
            description TEXT,
            status TEXT DEFAULT 'waiting_payment',
            created_at TEXT
        )
    ''')
    conn.commit()

init_db()

def register_user(message):
    uid = message.from_user.id
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (user_id, username, balance, deals_count, rating, votes_count, level, commission)
            VALUES (?, ?, 0, 0, 4.9, 18, 'Новичок', 3.0)
        ''', (uid, message.from_user.username or "None"))
        conn.commit()

def get_user(uid):
    cursor.execute("SELECT balance, deals_count, rating, votes_count, level, commission FROM users WHERE user_id=?", (uid,))
    r = cursor.fetchone()
    if r:
        return {'balance': r[0], 'deals': r[1], 'rating': r[2], 'votes': r[3], 'level': r[4], 'commission': r[5]}
    return None

class FSMDeal(StatesGroup):
    amount = State()
    desc = State()

def main_kb(uid):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton('🎁 Создать сделку'),
        KeyboardButton('👤 Профиль'),
        KeyboardButton('💳 Вывод'),
        KeyboardButton('📊 Реквизиты'),
        KeyboardButton('🌐 Язык'),
        KeyboardButton('📞 Поддержка')
    )
    if uid in ADMIN_IDS:
        kb.add(KeyboardButton('🛠 Админ панель'))
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    register_user(message)
    await send_gif(message.chat.id, caption="🐣 Приветствую, воркер!", reply_markup=main_kb(message.from_user.id))

@dp.message_handler(text='👤 Профиль')
async def profile(message: types.Message):
    u = get_user(message.from_user.id)
    if not u:
        return
    stars = "⭐" * int(u['rating']) + "☆" * (5 - int(u['rating']))
    caption = (
        f"👤 **Профиль:**\n\n"
        f"💳 **Баланс:**\n"
        f"⭐ **{u['balance']} STARS**\n\n"
        f"📈 **Успешные сделки:** `{u['deals']}`\n\n"
        f"⭐ **Уровень:** `{u['level']}`\n"
        f"ℹ **Комиссия:** `{u['commission']}%`\n"
        f"📊 **Рейтинг:** {stars} **{u['rating']}/5**\n"
        f"**({u['votes']})**"
    )
    await send_gif(message.chat.id, caption=caption)

@dp.message_handler(text='🎁 Создать сделку')
async def create_deal_amount(message: types.Message):
    await message.answer("Введите сумму сделки в звёздах:")
    await FSMDeal.amount.set()

@dp.message_handler(state=FSMDeal.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amt = float(message.text)
        if amt <= 0:
            raise ValueError
        await state.update_data(amount=amt)
        await message.answer("Что вы предлагаете за 300.0 ⭐ ?")
        await FSMDeal.desc.set()
    except:
        await message.answer("❌ Введите корректное число.")

@dp.message_handler(state=FSMDeal.desc)
async def process_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    desc = message.text
    deal_id = generate_deal_id()
    cursor.execute("INSERT INTO deals (deal_id, seller_id, amount, description, created_at) VALUES (?, ?, ?, ?, ?)",
                   (deal_id, message.from_user.id, data['amount'], desc, str(datetime.now())))
    conn.commit()
    link = f"https://t.me/{bot.username}?start={deal_id}"
    
    caption = (
        f"✅ **Сделка создана!**\n\n"
        f"**Номер сделки:**\n"
        f"```\n#{deal_id}\n```\n"
        f"**Ссылка для покупателя:**\n"
        f"```\n{link}\n```\n\n"
        f"_Отправьте эту ссылку покупателю для совершения оплаты!_"
    )
    
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔗 Поделиться ссылкой", url=link),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel_deal")
    )
    await message.answer(caption, reply_markup=kb)
    await state.finish()

@dp.callback_query_handler(text='cancel_deal')
async def cancel_deal(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(callback.from_user.id, "❌ Сделка отменена.", reply_markup=main_kb(callback.from_user.id))

@dp.message_handler(text='💳 Вывод')
async def withdraw_start(message: types.Message):
    u = get_user(message.from_user.id)
    if u and u['balance'] > 0:
        await message.answer(
            "⛔️ **Ваш баланс:**\n"
            f"**STARS: {int(u['balance'])}**",
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("OK", callback_data="close_alert"))
        )
    elif u and u['balance'] == 0:
        await message.answer("💳 **Ваш баланс:**\n**STARS: 0**")

@dp.callback_query_handler(text='close_alert')
async def close_alert(callback: types.CallbackQuery):
    await callback.answer()

@dp.message_handler(text='📊 Реквизиты')
async def requisites(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("💎 Добавить GRAM", callback_data="add_gram"),
        InlineKeyboardButton("💳 Добавить карту", callback_data="add_card"),
        InlineKeyboardButton("⬅ Назад", callback_data="back_main")
    )
    await message.answer("🪪 **Выберите кошелёк для добавления:**", reply_markup=kb)

@dp.message_handler(text='🌐 Язык')
async def language(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("⬅ Назад", callback_data="back_main")
    )
    await message.answer("🇬🇧 Select language:\n🇷🇺 Выберите язык:", reply_markup=kb)

@dp.message_handler(text='📞 Поддержка')
async def support(message: types.Message):
    await message.answer("💬 **Поддержка:**\n@helper_deal")

@dp.callback_query_handler(text='back_main')
async def back_main(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(callback.from_user.id, "⬅ Назад", reply_markup=main_kb(callback.from_user.id))

@dp.message_handler(commands=['buy'])
async def admin_buy_deal(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Используй: `/buy #код`")
        return
    deal_code = args[1].replace('#', '')
    cursor.execute("SELECT deal_id, amount, description, seller_id, buyer_id, status FROM deals WHERE deal_id = ?", (deal_code,))
    deal = cursor.fetchone()
    if not deal:
        await message.answer("❌ Сделка не найдена.")
        return
    if deal[5] != 'waiting_payment':
        await message.answer("❌ Сделка уже завершена.")
        return
    cursor.execute("UPDATE deals SET status = 'paid', buyer_id = ? WHERE deal_id = ?", (message.from_user.id, deal_code))
    conn.commit()
    await message.answer(f"✅ **Сделка `#{deal_code}` оплачена админом!**\nМамонт получил уведомление.")
    try:
        await bot.send_message(
            deal[3],
            f"✅ **Оплата по сделке `#{deal_code}` успешно получена!**\n_Продавец получил уведомление_"
        )
    except:
        pass

@dp.message_handler(text='🛠 Админ панель')
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет прав.")
        return
    await message.answer("🛠 Панель администратора", reply_markup=InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("💰 Баланс", callback_data="adm_bal"),
        InlineKeyboardButton("⭐ Рейтинг", callback_data="adm_rat"),
        InlineKeyboardButton("📈 Сделки", callback_data="adm_deal")
    ))

if __name__ == '__main__':
    print("🔥 ЗАПУЩЕНО. ВСЁ РАБОТАЕТ.")
    executor.start_polling(dp, skip_updates=True)