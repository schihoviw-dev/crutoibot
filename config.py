# config.py - ПРЕМИУМ ЭМОДЗИ (ВСЕ ID)
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [8187269902]

SCAMMER_USERNAME = "@MalonGarant"
SCAMMER_ID = 8187269902
SUPPORT_USERNAME = "@MalonGarant"
COMMISSION = 3.0
WELCOME_GIF_PATH = "gifs/welcome.gif.mp4"

# ========== ПРЕМИУМ ЭМОДЗИ (ID от @getidbot) ==========

# Для кнопок
PREMIUM_DEAL = "5980871942570251958"          # 💎 Создать сделку
PREMIUM_GRAM = "5980783470538921933"          # 🪙 GRAM
PREMIUM_STARS = "5981137191160518179"         # ⭐ Звёзды
PREMIUM_HAMMER = "5935968647901089910"        # 🔨 Трахнуть мамонта
PREMIUM_CHECK = "5206607081334906820"         # ✅ Подтвердить/OK
PREMIUM_CROSS = "5210952531676504517"         # ❌ Отмена
PREMIUM_BACK = "5958361550820480866"          # ⬅️ Назад
PREMIUM_SHARE = "5311998535032409760"         # 📤 Поделиться
PREMIUM_CHART = "5956166805352356645"         # 📊 Статистика
PREMIUM_LIST = "5361692603727252420"          # 📋 Список сделок
PREMIUM_USERS = "5258011929993026890"         # 👥 Пользователи
PREMIUM_SETTINGS = "5841693351249710667"      # ⚙️ Админ-панель

# Для текста сообщений
PREMIUM_PAID = "5841243255856960314"          # 💜 Статус оплачено
PREMIUM_WARNING = "5447644880824181073"       # ⚠️ Предупреждение
PREMIUM_INFO = "5420323339723881652"          # ℹ️ Информация
PREMIUM_PROFILE = "5258011929993026890"       # 👤 Профиль (тот же что и 11)
PREMIUM_WITHDRAW = "5310191758255099001"      # 💰 Вывод
PREMIUM_CARD = "5445353829304387411"          # 💳 Реквизиты
PREMIUM_GLOBE = "5332724926216428039"         # 🌐 Язык
PREMIUM_CHAT = "5447410659077661506"          # 💬 Поддержка
PREMIUM_BANK = "5443038326535759644"          # 🏦 FunPay
PREMIUM_SUCCESS = "5373174941095050893"       # ✅ Успех
PREMIUM_GROUP = "5237699328843200968"         # 👥 Рефералы

# Алиасы для удобства (чтобы в коде было понятно)
EMOJI_DEAL = PREMIUM_DEAL
EMOJI_GRAM = PREMIUM_GRAM
EMOJI_STARS = PREMIUM_STARS
EMOJI_HAMMER = PREMIUM_HAMMER
EMOJI_CHECK = PREMIUM_CHECK
EMOJI_CROSS = PREMIUM_CROSS
EMOJI_BACK = PREMIUM_BACK
EMOJI_SHARE = PREMIUM_SHARE
EMOJI_CHART = PREMIUM_CHART
EMOJI_LIST = PREMIUM_LIST
EMOJI_USERS = PREMIUM_USERS
EMOJI_SETTINGS = PREMIUM_SETTINGS
EMOJI_PAID = PREMIUM_PAID
EMOJI_WARNING = PREMIUM_WARNING
EMOJI_INFO = PREMIUM_INFO
EMOJI_PROFILE = PREMIUM_PROFILE
EMOJI_WITHDRAW = PREMIUM_WITHDRAW
EMOJI_CARD = PREMIUM_CARD
EMOJI_GLOBE = PREMIUM_GLOBE
EMOJI_CHAT = PREMIUM_CHAT
EMOJI_BANK = PREMIUM_BANK
EMOJI_SUCCESS = PREMIUM_SUCCESS
EMOJI_GROUP = PREMIUM_GROUP

CURRENCIES = {
    "gram": "GRAM",
    "stars": "Звёзды"
}

ERROR_MESSAGES = {
    "no_requisites": f"{EMOJI_WARNING} У вас ещё не добавлен реквизит GRAM!\n\nДобавьте его здесь: Главное меню → Реквизиты → Добавить GRAM",
    "invalid_gram": f"{EMOJI_WARNING} Вы указали неверный адрес кошелька GRAM!\n\n❗ Формат: откройте кошелёк -> скопируйте точный адрес -> вставьте скопированный текст",
    "deal_not_found": f"{EMOJI_CROSS} Сделка не найдена.",
    "deal_already_paid": f"{EMOJI_CROSS} Эта сделка уже оплачена или завершена.",
    "deal_not_joined": f"{EMOJI_CROSS} Мамонт ещё не присоединился к сделке.",
    "access_denied": f"{EMOJI_CROSS} Доступ запрещён.",
    "invalid_amount": f"{EMOJI_CROSS} Введите корректное число",
    "description_too_long": f"{EMOJI_CROSS} Описание слишком длинное (макс 200 символов)"
}