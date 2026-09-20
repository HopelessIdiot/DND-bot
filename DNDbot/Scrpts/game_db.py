# game_db.py

# -----------------------------------------------------------------
#                   Импорт
# -----------------------------------------------------------------

from pathlib import Path
import aiosqlite as SQL
import random
import string
import json as js

# -----------------------------------------------------------------
#                    дб
# -----------------------------------------------------------------

Scrpts_dir = Path(__file__).resolve().parent
db_path = Scrpts_dir.parent / "data" / "game.db"

# -----------------------------------------------------------------
#                    Функции
# -----------------------------------------------------------------

def generate_game_id() -> str:
    digits = "".join(random.choices(string.digits, k=5))
    letters = "".join(random.choices(string.ascii_uppercase, k=4))
 
    extra_digits = "".join(random.choices(string.digits, k=3))
    return f"GAME-{digits}-{letters}-{extra_digits}"

# -----------------------------------------------------------------
#                    Инициализация дб
# -----------------------------------------------------------------


async def init_db():
    async with SQL.connect(db_path) as db:
       
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                master_id INTEGER NOT NULL
            )
        """)

        
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS enemies (
                enemy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                enemy_name TEXT NOT NULL,
                enemy_hp INTEGER NOT NULL,
                show_hp INTEGER NOT NULL DEFAULT 1 CHECK (show_hp IN (0, 1)),
                show INTEGER NOT NULL DEFAULT 1 CHECK (show IN (0, 1))
            )
        """
        )

        await db.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    plr_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    name TEXT,
                    hp INTEGER,
                    stats TEXT
                )
            """
                )

        await db.commit()

# -----------------------------------------------------------------
#                    Работа с дб
# -----------------------------------------------------------------


#                           Игра
#------------------------------------------------------------------

async def delete_game(game_id: str):
    
    async with SQL.connect(db_path) as db:
        
        await db.execute(
            """
            DELETE FROM enemies WHERE game_id = ?
        """,
            (game_id,),
        )

        
        await db.execute(
            """
            DELETE FROM games WHERE game_id = ?
        """,
            (game_id,),
        )

        await db.execute(
                    """
                    DELETE FROM players WHERE game_id = ?
                """,
                    (game_id,),
                )
        

        await db.commit()

async def create_game(chat_id: int, master_id: int) -> str:
    game_id = generate_game_id()

    async with SQL.connect(db_path) as db:

        await db.execute(
            """
            INSERT OR REPLACE INTO games (game_id, chat_id, master_id) VALUES (?, ?, ?)
        """,
            (game_id, chat_id, master_id)
        )
        await db.commit()

    return game_id

async def get_game_by_chat_id(chat_id: int):
    async with SQL.connect(db_path) as db:
        async with db.execute(
            """
            SELECT game_id FROM games WHERE chat_id = ? 
        """,
            (chat_id,),
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def get_game_by_game_id(game_id: str):
    async with SQL.connect(db_path) as db:
        async with db.execute(
            """
            SELECT chat_id FROM games WHERE game_id = ?
        """,
            (game_id,),
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def get_game_by_master_id(user_id: int):
    async with SQL.connect(db_path) as db:
        async with db.execute(
            """
            SELECT game_id FROM games WHERE master_id = ?
        """,
            (user_id,),
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

#                           Враги
#------------------------------------------------------------------

async def add_enemy(game_id: str, enemy_name: str, enemy_hp: int, show_hp: int, show: int):
    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            INSERT INTO enemies (game_id, enemy_name, enemy_hp, show_hp, show) VALUES (?, ?, ?, ?, ?)
        """,
            (game_id, enemy_name, enemy_hp, show_hp, show),
        )
        await db.commit()

async def get_all_enemies(game_id: str):
    async with SQL.connect(db_path) as db:
        async with db.execute(
            """
            SELECT enemy_id, enemy_name, enemy_hp, show_hp, show FROM enemies WHERE game_id = ?
        """,
            (game_id,),
        ) as cursor:
            return await cursor.fetchall()

async def delete_enemy_by_id(enemy_id: int):
    
    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            DELETE FROM enemies WHERE enemy_id = ?
        """,
            (enemy_id,),
        )
        await db.commit()

async def clear_all_enemies(game_id: str):
    """Очищает всех врагов конкретной игры."""
    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            DELETE FROM enemies WHERE game_id = ?
        """,
            (game_id,),
        )
        await db.commit()

async def update_enemy_hp(game_id: str, enemy_name: str, new_hp: int):
    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            UPDATE enemies SET enemy_hp = ? WHERE game_id = ? AND enemy_name = ?
        """,
            (new_hp, game_id, enemy_name),
        )
        await db.commit()

#                           Игроки
#------------------------------------------------------------------

async def add_player(game_id: str, user_id: int, name: str, hp: int, stats: dict):

    try:
        js_stats = js.dumps(stats, ensure_ascii=False)
    except:
        js_stats = "0"

    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            INSERT INTO players (game_id, user_id, name, hp, stats) VALUES(?,?,?,?,?)
        """,
            (game_id, user_id, name, hp, js_stats)
        )
        await db.commit()

async def update_plr_by_plr_id(plr_id: int, name: str, hp: int, stats: dict):

    js_stats = js.dumps(stats, ensure_ascii=False) if stats else None

    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            UPDATE players 
            SET name = ?, hp = ?, stats = ? 
            WHERE plr_id = ?
        """,
            (name, hp, js_stats, plr_id),
        )
        await db.commit()

async def update_player_stats_by_plr_id(plr_id: int, stats: dict):
    js_stats = js.dumps(stats, ensure_ascii=False) if stats else None

    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            UPDATE players 
            SET stats = ? 
            WHERE plr_id = ?
        """,
            (js_stats, plr_id),
        )
        await db.commit()

async def get_player_by_plr_id(plr_id: int):
    
    async with SQL.connect(db_path) as db:
        async with db.execute(
            """
            SELECT plr_id, game_id, user_id, name, hp, stats 
            FROM players WHERE plr_id = ?
        """,
            (plr_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            
            stats_dict = js.loads(row[5]) if row[5] else {}

            return {
                "plr_id": row[0],
                "game_id": row[1],
                "user_id": row[2],
                "name": row[3],
                "hp": row[4],
                "stats": stats_dict,
            }

async def get_player_by_user_id(user_id: int):
    async with SQL.connect(db_path) as db:
        async with db.execute(
            """
            SELECT plr_id, game_id, user_id, name, hp, stats 
            FROM players WHERE user_id = ?
        """,
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            
            stats_dict = js.loads(row[5]) if row[5] else {}

            return {
                "plr_id": row[0],
                "game_id": row[1],
                "user_id": row[2],
                "name": row[3],
                "hp": row[4],
                "stats": stats_dict,
            }
        
async def get_all_players(game_id: str):
    
    async with SQL.connect(db_path) as db:
        async with db.execute(
            """
            SELECT plr_id, game_id, user_id, name, hp, stats 
            FROM players WHERE game_id = ?
        """,
            (game_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            players_list = []
            
            for row in rows:

                stats_dict = js.loads(row[5]) if row[5] else {}

                players_list.append({
                    "plr_id": row[0],
                    "game_id": row[1],
                    "user_id": row[2],
                    "name": row[3],
                    "hp": row[4],
                    "stats": stats_dict,
                })
                
            return players_list

async def delete_plr_by_plr_id(game_id, plr_id: int):
    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            DELETE FROM players WHERE plr_id = ? AND game_id = ?
            """,
            (plr_id, game_id),
        )
        await db.commit()