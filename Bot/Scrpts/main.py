# -----------------------------------------------------------------
#                _____
#               |#####|
#               |#|
#               |#####|
#               |#|
#               |#####|

# -----------------------------------------------------------------
#                    Import
# -----------------------------------------------------------------

import asyncio
from pathlib import Path
from aiogram import Bot, Dispatcher

from BnS import bns_router
from Game import game_router
from stat_db import init_db

# -----------------------------------------------------------------
#                    Variables & Files
# -----------------------------------------------------------------

TOKEN_PATH = Path(__file__).resolve().parent.parent / "data" / "Token.txt"

try:
    TOKEN = TOKEN_PATH.read_text(encoding="utf-8").strip()
    print(f"Token loaded from {TOKEN_PATH}")
except FileNotFoundError:
    print(f"Error: {TOKEN_PATH} not found")
    exit(1)

# -----------------------------------------------------------------
#                    Startup
# -----------------------------------------------------------------


async def main():
    await init_db()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(bns_router)
    dp.include_router(game_router)

    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())