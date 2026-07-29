import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [8187269902]
SCAMMER_ID = 8187269902
SCAMMER_USERNAME = "@MalonGarant"
SUPPORT_USERNAME = "@helper_fp"
COMMISSION = 3.0
WELCOME_GIF_PATH = "gifs/welcome.gif.mp4"

# ========== ПРЕМИУМ ЭМОДЗИ ==========
E_BANK = '<tg-emoji emoji-id="5224607267797606837">🏦</tg-emoji>'
E_DEAL = '<tg-emoji emoji-id="5980871942570251958">💎</tg-emoji>'
E_GRAM = '<tg-emoji emoji-id="5980783470538921933">🪙</tg-emoji>'
E_STARS = '<tg-emoji emoji-id="5981137191160518179">⭐</tg-emoji>'
E_RUB = '💰'
E_HAMMER = '<tg-emoji emoji-id="5935968647901089910">🔨</tg-emoji>'
E_CHECK = '<tg-emoji emoji-id="5206607081334906820">✅</tg-emoji>'
E_CROSS = '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji>'
E_BACK = '<tg-emoji emoji-id="5958361550820480866">⬅️</tg-emoji>'
E_SHARE = '<tg-emoji emoji-id="5311998535032409760">📤</tg-emoji>'
E_CHART = '<tg-emoji emoji-id="5956166805352356645">📊</tg-emoji>'
E_LIST = '<tg-emoji emoji-id="5361692603727252420">📋</tg-emoji>'
E_USERS = '<tg-emoji emoji-id="5258011929993026890">👥</tg-emoji>'
E_SETTINGS = '<tg-emoji emoji-id="5841693351249710667">⚙️</tg-emoji>'
E_PAID = '<tg-emoji emoji-id="5841243255856960314">💜</tg-emoji>'
E_WARNING = '<tg-emoji emoji-id="5447644880824181073">❗️</tg-emoji>'
E_PROFILE = '<tg-emoji emoji-id="5258011929993026890">👤</tg-emoji>'
E_WITHDRAW = '<tg-emoji emoji-id="5310191758255099001">💰</tg-emoji>'
E_CARD = '<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji>'
E_GLOBE = '<tg-emoji emoji-id="5332724926216428039">🌐</tg-emoji>'
E_CHAT = '<tg-emoji emoji-id="5447410659077661506">💬</tg-emoji>'
E_SUCCESS = '<tg-emoji emoji-id="5373174941095050893">✅</tg-emoji>'
E_GROUP = '<tg-emoji emoji-id="5237699328843200968">👥</tg-emoji>'
E_UP = '<tg-emoji emoji-id="5445355530111437729">👆</tg-emoji>'
E_DOWN = '<tg-emoji emoji-id="5443127283898405358">👇</tg-emoji>'
E_RU = '<tg-emoji emoji-id="5291734595862018096">🇷🇺</tg-emoji>'
E_US = '<tg-emoji emoji-id="5294447773947543583">🇺🇸</tg-emoji>'
E_TR = '<tg-emoji emoji-id="5292218402453075461">🇹🇷</tg-emoji>'
E_GIFT = '<tg-emoji emoji-id="5981137191160518179">⭐</tg-emoji>'

CURRENCIES = {
    "gram": "грам",
    "card": "карта",
    "stars": "звезд"
}

ERROR_MESSAGES = {
    "no_requisites": f"{E_WARNING} <b>У вас ещё не добавлен реквизит!</b>\n\nДобавьте его здесь: Главное меню → Реквизиты → Добавить",
    "invalid_gram": f"{E_WARNING} <b>Вы указали неверный адрес кошелька!</b>\n\n❗ Формат: откройте кошелёк -> скопируйте точный адрес -> вставьте скопированный текст",
    "invalid_card": f"{E_WARNING} <b>Неверный формат карты!</b>\n\nВведите 16 цифр",
    "deal_not_found": f"{E_CROSS} <b>Сделка не найдена.</b>",
    "deal_already_paid": f"{E_CROSS} <b>Эта сделка уже оплачена или завершена.</b>",
    "deal_not_joined": f"{E_CROSS} <b>Мамонт ещё не присоединился к сделке.</b>",
    "access_denied": f"{E_CROSS} <b>Доступ запрещён.</b>",
    "invalid_amount": f"{E_CROSS} <b>Введите корректное число</b>",
    "description_too_long": f"{E_CROSS} <b>Описание слишком длинное (макс 200 символов)</b>"
}

# ===== РЕЙТИНГ И СДЕЛКИ ДЛЯ СКАМЕРОВ =====
SCAMMER_STATS = {
    "8187269902": {"deals": 64, "rating": 5.0},   # Ты (админ)
    "8844754156": {"deals": 64, "rating": 5.0},   # Новый скамер
    # Добавляй других сюда
}

def load_admins_from_file():
    """Загружает ID скамеров из файла admins.txt"""
    admins = []
    try:
        with open("admins.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        admins.append(int(line))
                    except:
                        pass
        print(f"✅ Загружено скамеров из admins.txt: {len(admins)}")
    except FileNotFoundError:
        print("⚠️ Файл admins.txt не найден, создаю новый...")
        with open("admins.txt", "w") as f:
            f.write("# Список ID скамеров (без админ-панели)\n")
            f.write("# Каждый ID на новой строке\n")
            f.write("8187269902\n")
            f.write("8844754156\n")
        admins = [8187269902, 8844754156]
    
    return admins

SCAMMER_IDS = load_admins_from_file()
print(f"📋 SCAMMER_IDS: {SCAMMER_IDS}")