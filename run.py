import asyncio
import logging
from aiogram import Bot, Dispatcher
import os
from app.handlers import router
from dotenv import load_dotenv



load_dotenv()
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()



async def main():
    load_dotenv()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
        
