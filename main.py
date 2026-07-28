# main.py (дополнено)
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import router

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Регистрируем роутер
    dp.include_router(router)
    
    # Передаём bot_username во все обработчики
    bot_username = (await bot.get_me()).username
    
    # Запускаем бота
    await dp.start_polling(bot, bot_username=bot_username)

if __name__ == "__main__":
    asyncio.run(main())