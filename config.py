# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ========== ТВОЙ ID ==========
ADMIN_IDS = [8187269902]
SCAMMER_ID = 8187269902

SCAMMER_USERNAME = "@MalonGarant"
SUPPORT_USERNAME = "@MalonGarant"
COMMISSION = 3.0
WELCOME_GIF_PATH = "gifs/welcome.gif.mp4"

# ========== ПРЕМИУМ ЭМОДЗИ (ПРАВИЛЬНЫЙ ФОРМАТ) ==========
EMOJI_DEAL = '<tg-emoji emoji-id="5980871942570251958">💎</tg-emoji>'
EMOJI_GRAM = '<tg-emoji emoji-id="5980783470538921933">🪙</tg-emoji>'
EMOJI_STARS = '<tg-emoji emoji-id="5981137191160518179">⭐</tg-emoji>'
EMOJI_HAMMER = '<tg-emoji emoji-id="5935968647901089910">🔨</tg-emoji>'
EMOJI_CHECK = '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji>'
EMOJI_CROSS = '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji>'
EMOJI_BACK = '<tg-emoji emoji-id="5958361550820480866">⬅️</tg-emoji>'
EMOJI_SHARE = '<tg-emoji emoji-id="5311998535032409760">📤</tg-emoji>'
EMOJI_CHART = '<tg-emoji emoji-id="5956166805352356645">📊</tg-emoji>'
EMOJI_LIST = '<tg-emoji emoji-id="5361692603727252420">📋</tg-emoji>'
EMOJI_USERS = '<tg-emoji emoji-id="5258011929993026890">👥</tg-emoji>'
EMOJI_SETTINGS = '<tg-emoji emoji-id="5841693351249710667">⚙️</tg-emoji>'
EMOJI_PAID = '<tg-emoji emoji-id="5841243255856960314">💜</tg-emoji>'
EMOJI_WARNING = '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji>'
EMOJI_INFO = '<tg-emoji emoji-id="5420323339723881652">ℹ️</tg-emoji>'
EMOJI_PROFILE = '<tg-emoji emoji-id="5258011929993026890">👤</tg-emoji>'
EMOJI_WITHDRAW = '<tg-emoji emoji-id="5310191758255099001">💰</tg-emoji>'
EMOJI_CARD = '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji>'
EMOJI_GLOBE = '<tg-emoji emoji-id="5332724926216428039">🌐</tg-emoji>'
EMOJI_CHAT = '<tg-emoji emoji-id="5447410659077661506">💬</tg-emoji>'
EMOJI_BANK = '<tg-emoji emoji-id="5443038326535759644">🏦</tg-emoji>'
EMOJI_SUCCESS = '<tg-emoji emoji-id="5373174941095050893">✅</tg-emoji>'
EMOJI_GROUP = '<tg-emoji emoji-id="5237699328843200968">👥</tg-emoji>'

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