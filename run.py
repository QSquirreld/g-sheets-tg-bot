from dotenv import load_dotenv
from handlers import router

import os
import asyncio
import google_table

from aiogram import Bot, Dispatcher

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()


async def headsetter_task():
    while True:
        await asyncio.sleep(10)
        google_table.head_setter()


async def main():
    dp.include_router(router)
    asyncio.create_task(headsetter_task())
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
