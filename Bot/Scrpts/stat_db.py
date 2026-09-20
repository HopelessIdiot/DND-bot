# start_db.py

# -----------------------------------------------------------------
#                    Import
# -----------------------------------------------------------------

import asyncio
from pathlib import Path
import aiosqlite as SQL

# -----------------------------------------------------------------
#                    Database
# -----------------------------------------------------------------

Scrpts_dir = Path(__file__).resolve().parent
db_path = Scrpts_dir.parent / "data" / "users.db"

# -----------------------------------------------------------------
#                    Init
# -----------------------------------------------------------------


async def init_db():
    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                games_as_master_count INTEGER DEFAULT 0,
                games_as_player_count INTEGER DEFAULT 0
            )
        """
        )
        await db.commit()


# -----------------------------------------------------------------
#                    Работа с дб
# -----------------------------------------------------------------


async def add_user(user_id: int):
    async with SQL.connect(db_path) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (user_id) VALUES (?)
        """,
            (user_id,),
        )
        await db.commit()


async def update_user_stats(user_id: int, role: int, games_count: int):
    async with SQL.connect(db_path) as db:
        if role == 1:  # Master
            await db.execute(
                """
                UPDATE users SET games_as_master_count = games_as_master_count + ?
                WHERE user_id = ?
            """,
                (games_count, user_id),
            )

        elif role == 2:  # Player
            await db.execute(
                """
                UPDATE users SET games_as_player_count = games_as_player_count + ?
                WHERE user_id = ?
            """,
                (games_count, user_id),
            )

        await db.commit()


async def get_user_stats(user_id: int, role: int):
    async with SQL.connect(db_path) as db:
        if role == 1:  # Master
            async with db.execute(
                """
                SELECT games_as_master_count FROM users WHERE user_id = ?
            """,
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

        elif role == 2:  # Player
            async with db.execute(
                """
                SELECT games_as_player_count FROM users WHERE user_id = ?
            """,
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

        return None