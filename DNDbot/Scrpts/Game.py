# Game.py

# -----------------------------------------------------------------
#                    Импорт
# -----------------------------------------------------------------

from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from game_db import init_db, create_game, get_game_by_chat_id, get_all_enemies, add_player

import random
import re

# -----------------------------------------------------------------
#                    Роутер
# -----------------------------------------------------------------

game_router = Router()
game_router.message.filter(F.chat.type.in_({"group", "supergroup"}))

# -----------------------------------------------------------------
#                    Команды
# -----------------------------------------------------------------

@game_router.message(Command("start"))
async def start_session_cmd(message: types.Message):
    await message.answer("Привет! Это бот для проведения D&D сессий. Используй команду /start_game, чтобы начать игру.")

@game_router.message(Command("help"))
async def help(message: types.Message):
    await message.answer(
            "Вот более подробный гайд: \n\n",
            "/roll [d(любое чило)] - позволяет кинуть кубик на четное d\n",
            "/sh_ens - показывает всех врагов"

    )

@game_router.message(Command("start_game"))
async def start_game(message: types.Message):
    chat_id = message.chat.id
    master_id = message.from_user.id

    await init_db()
    game_id = await create_game(chat_id, master_id)

    button = InlineKeyboardButton(text="Присоединиться", callback_data="JOIN")
    buttons = InlineKeyboardMarkup(inline_keyboard=[[button]])
    
    await message.answer(
        f"Новая D&D сессия создана!\n\n",
        reply_markup=buttons,
        parse_mode="Markdown",
    )

    try:
        await message.bot.send_message(
            chat_id=message.from_user.id,
            text=f"Вы запустили игру в чате {message.chat.title}!"
            f"Ваш ID игры: `{game_id}`\n\n"
        )
    except Exception:
        pass    

@game_router.message(Command("roll"))
async def roll_cmd(message: types.Message, command: CommandObject):

    result = None
    txt = None
    
    if not command.args:
        result = random.randint(1, 20)
        txt = f"Результат броска d20: {result}"

    else:
        command_args = command.args.strip()
        split = re.split(r"d(\d+)", command_args)

        num = None

        try:
            num = int(split[1])
        except (IndexError, ValueError):
            txt = "Неверный формат команды. Используйте /roll d20 или /roll dX, где X - количество граней."
        
        if split[1] == "":
            result = random.randint(1, 20)
            txt = f"Результат броска d20: {result}"

        else:
            if num%2 == 0:
                result = random.randint(1, num)

                txt = f"Результат броска d{num}: {result}"

            else:
                txt = "Неверный формат команды. Используйте /roll d20 или /roll dX, где X - количество граней."

    await message.reply(txt)  

@game_router.message(Command("sh_en"))
async def sh_ens(message: types.Message, command: CommandObject):

    game_id = None
    if await get_game_by_chat_id(message.chat.id):
            game_id = await get_game_by_chat_id(message.chat.id)
    else:
        await message.answer(
                "У вас нет активной игры!",
                parse_mode="Markdown",
            )
        return

    ens = await get_all_enemies(game_id)

    lines = []

    if  len(ens) > 0:
        for enemy in ens:
            if enemy[4] != 0:
                if enemy[3] == 1:
                    text = f"{enemy[1]}"
                else:
                    text = f"{enemy[1]}, хп: {enemy[2]}"
            lines.append(text)
    else:
        response = "Врагов нет!"

    response = "\n".join(lines)
    await message.answer(response)

# -----------------------------------------------------------------
#                    Callback
# -----------------------------------------------------------------

@game_router.callback_query(lambda c: c.data == "JOIN")
async def callback_procced(callback: types.CallbackQuery):

    game_id = None
    if await get_game_by_chat_id(callback.message.chat.id):
            game_id = await get_game_by_chat_id(callback.message.chat.id)
    else:
        await callback.answer(
                "У вас нет активной игры!",
                parse_mode="Markdown",
            )
        return

    await add_player(game_id, callback.from_user.id, callback.from_user.username, 0, {"i": "loh"})

    try:
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=f"Вы зашли в игру в чате **{callback.message.chat.title}**!\n\n",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Не удалось отправить личное сообщение: {e}")