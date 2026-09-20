# BnS.py

# -----------------------------------------------------------------
#                    Импорт
# -----------------------------------------------------------------

from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject, CommandStart

import re
import random

from stat_db import add_user, get_user_stats 
from game_db import add_enemy, get_player_by_user_id, get_all_players, get_game_by_master_id, update_enemy_hp, get_all_enemies, update_player_stats_by_plr_id, delete_plr_by_plr_id, delete_game


# -----------------------------------------------------------------
#                    Роутер
# -----------------------------------------------------------------

bns_router = Router()
bns_router.message.filter(F.chat.type == "private")


# -----------------------------------------------------------------
#                   Команды
# -----------------------------------------------------------------


@bns_router.message(CommandStart())
async def start(message: types.Message):
    await add_user(message.from_user.id)
    await message.answer(
        "Привет! Это бот для проведения D&D сессий.\n"
        "Используй /stats для просмотра своего профиля."
        "\n\n"
        "Для начала игры, пригласи бота в группу и используй команду /start_game."
    )

@bns_router.message(Command("help"))
async def help(message: types.Message):
    await message.answer(
        "Вот более подробный гайд для контроля игр: \n\n"
        "Для Мастеров:\n"
        "/delete_game - удаляет игру, где вы мастер\n"
        "/add_en [Имя] [Хп] [Видимость хп Врага, 1 или 0] [Видимость Врага, 1 или 0] - добавляет врага\n"
        "/up_en [Имя] [Хп] [Видимость хп Врага, 1 или 0] [Видимость Врага, 1 или 0] - обновит врага\n"
        "/sh_ens - показывает врагов\n"
        "/sap - ( show all players ) показывает всех игроков\n"
        "/del_plr [Айди Игрока] - удаляет игрока из игры по ID( можно увидеть через /sap )\n\n"
        "Для игрока:\n"
        "/asl [STR] [INT]... - ( add stat list ) добавляет вам статы"
    )

#                    Для статов
# -----------------------------------------------

@bns_router.message(Command("stats"))
async def stats_cmd(message: types.Message):
    user_id = message.from_user.id

    master_games = await get_user_stats(user_id, role=1) or 0
    player_games = await get_user_stats(user_id, role=2) or 0

    await message.answer(
        f"Ваша статистика\n\n"
        f"Проведено игр (Мастер): {master_games}\n"
        f"Сыграно игр (Игрок): {player_games}",
        parse_mode="Markdown",
    )


#                    Команды Мастера
# ------------------------------------------------

@bns_router.message(Command("delete_game"))
async def delete_game_func(message: types.Message, command: CommandObject):
    if not command.args:

        if await get_game_by_master_id(message.from_user.id):
            game_id = await get_game_by_master_id(message.from_user.id)

            await delete_game(game_id)
            
            await message.answer(
                f"Игра с ID `{game_id}` успешно удалена!",
                parse_mode="Markdown",
            )

        else:
            await message.answer(
                "У вас нет активной игры!",
                parse_mode="Markdown",
            )
        return

    game_id = command.args.strip()

    await delete_game(game_id)

    await message.answer(
        f"Игра с ID `{game_id}` успешно удалена!",
        parse_mode="Markdown",
    )

@bns_router.message(Command("add_en"))
async def add_enemy_func(message: types.Message, command: CommandObject):
    if not command.args:
        await message.answer(
            " Вы не передали аргументы! Пример: `/add_enemy Гоблин 15`",
            parse_mode="Markdown",
        )
        return

    args = command.args.split(maxsplit=2)

    if len(args) < 2:
        await message.answer(
            "Недостаточно аргументов! Пример: `/add_enemy Гоблин 15 `",
            parse_mode="Markdown",
        )
        return

    enemy_name, enemy_health = args

    try:
        show_hp = args[2]
    except:
        show_hp = 1
    
    try:
        show = args[3]
    except:
        show = 1

    if await get_game_by_master_id(message.from_user.id):
        game_id = await get_game_by_master_id(message.from_user.id)
    else:
        await message.answer(
                "Недостаточно аргументов! Пример: `/add_enemy Гоблин 15`",
                parse_mode="Markdown",
            )
        return

    try:
        enemy_health = int(enemy_health)
    except ValueError:
        await message.answer(
            " Здоровье врага должно быть числом! Пример: `/add_enemy Гоблин 12`",
            parse_mode="Markdown",
        )
        return

    await add_enemy(game_id, enemy_name, enemy_health, show_hp, show)
    await message.answer(
        f" Враг {enemy_name} ({enemy_health} HP) добавлен в игру `{game_id}`!",
        parse_mode="Markdown",
    )

@bns_router.message(Command("up_en"))
async def update_enemy_func(message: types.Message, command: CommandObject):

    if not command.args:
            await message.answer(
                " Вы не передали аргументы! Пример: `/update Гоблин 15`",
                parse_mode="Markdown",
            )
            return
    
    args = command.args.split(maxsplit=2)
    
    if len(args) < 1:
        await message.answer(
            "Недостаточно аргументов1! Пример: `/update_enemy Гоблин 15 `",
            parse_mode="Markdown",
        )
        return
    
    enemy_name, enemy_health = args
    
    if await get_game_by_master_id(message.from_user.id):
        game_id = await get_game_by_master_id(message.from_user.id)
    else:
        await message.answer(
                "Недостаточно аргументов2! Пример: `/update_enemy Гоблин 15`",
                parse_mode="Markdown",
            )
        return

    int_enemy_heath = None
    try:
        int_enemy_heath = int(enemy_health)
    except:
        pass

    if enemy_name and int_enemy_heath:
        await update_enemy_hp(game_id, enemy_name, int_enemy_heath)
        
        await message.answer(
            f"Изменено хп у '{enemy_name}' на '{int_enemy_heath}'",
            parse_mode="Markdown",
        )

    else:

        await message.answer(
            "Недостаточно аргументов3! Пример: `/update_enemy Гоблин 15`",
            parse_mode="Markdown",
        )

@bns_router.message(Command("sh_ens"))
async def show_enemies_func(message: types.Message, command: CommandObject):

    game_id = None
    if await get_game_by_master_id(message.from_user.id):
            game_id = await get_game_by_master_id(message.from_user.id)
    else:
        await message.answer(
                "У вас нет активной игры!",
                parse_mode="Markdown",
            )
        return

    ens = await get_all_enemies(game_id)
    if not ens:
        await message.answer("В вашей игре пока нет добавленных врагов.")
        return

    lines = []

    for enemy in ens:
        text = f"ID: {enemy[0]}, Имя: {enemy[1]}, Хп: {enemy[2]}, Видимость хп: {enemy[3]}, Видимость: {enemy[4]}"
        lines.append(text)

    response = "\n".join(lines)
    await message.answer(response)

@bns_router.message(Command("sap"))
async def show_all_players_func(message: types.Message):
    game_data = await get_game_by_master_id(message.from_user.id)
    
    if not game_data:
        await message.answer("Вы не являетесь мастером активной игры.")
        return
    
    game_id = game_data if isinstance(game_data, str) else game_data.get("game_id")
    players = await get_all_players(game_id)
    
    if not players:
        await message.answer("В этой игре пока нет зарегистрированных участников.")
        return
    elif len( players ) == 0:
        await message.answer(text="В игре нет активных игроков!")
        return
        
    text = "Список игроков в игре:\n\n"
    
    for i, player in enumerate(players, start=1):
        name = player["name"]
        hp = player["hp"]
        stats = player["stats"]

        if stats:
            stats_str = ", ".join(f"{k}: {v}" for k, v in stats.items())
        else:
            stats_str = "не заполнены"
            
        text += f"{i}{name} |  HP: `{hp}`\n"
        text += f"    Статы: `{stats_str}`\n\n"
        

    await message.answer(text)

@bns_router.message(Command("del_plr"))
async def delete_player_handler(message: types.Message, command: CommandObject):
    game_id = await get_game_by_master_id(message.from_user.id)
    if not game_id:
        message.answer(
            "Вы не являетесь мастером активной игры."
        )

    target_plr_id = None

    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        player = await get_player_by_user_id(target_user_id)
        if player:
            target_plr_id = player["plr_id"]
    
    elif command.args:
        try:
            target_plr_id = int(command.args.strip())
        except ValueError:
            await message.answer("Неверный формат ID. Укажите числовой `plr_id`.")
            return

    if not target_plr_id:
        await message.answer(
            "Неправильно вызвана команда?\n"
            "Сделайте ответ на сообщение игрока с командой /del_plr\n"
            "Или укажите его ID: del_plr [plr_id]",
        )
        return

    await delete_plr_by_plr_id(game_id, target_plr_id)

    await message.answer(
        f"Персонаж с ID {target_plr_id} успешно удален из игры.", 
    )

@bns_router.message(Command("roll"))
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

#                    Команды Игрока
# ------------------------------------------------

@bns_router.message(Command("asl"))
async def add_stat_list(message: types.Message, command: CommandObject):
    text = command.args

    if not text:
        await message.answer(
            "Нет статов!"
        )
        return
    
    def get_stat(pattern, txt):
        match = re.search(pattern, txt)
        return int(match.group(1)) if match else None

    stats_dict = {
        "STR": get_stat(r"STR:\s*(\d+)", text),
        "DEX": get_stat(r"DEX:\s*(\d+)", text),
        "CON": get_stat(r"CON:\s*(\d+)", text),
        "INT": get_stat(r"INT:\s*(\d+)", text),
        "WIS": get_stat(r"WIS:\s*(\d+)", text),
        "CHA": get_stat(r"CHA:\s*(\d+)", text),
    }

    responce = "" 
    for key, value in stats_dict.items():
        if value is None:
            responce += f"{key}: None\n"
        else:
            responce += f"{key}: {value}\n"

    player = await get_player_by_user_id(message.from_user.id)
    if player is None:
        await message.answer("Вы еще не в игре")
        return
    
    await update_player_stats_by_plr_id(player["plr_id"], stats_dict)

    try:
        await message.answer(
            f"Ваши статы обновлены на:\n{responce}"
        )
    except Exception:
        pass