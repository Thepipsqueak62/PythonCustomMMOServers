import aiosqlite

DB_PATH = "mmo_messages.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS player_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                payload TEXT
            )
        """)
        await db.commit()
    print("[Database] Initialized.")

async def insert_player_message(request_id, payload):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO player_messages (request_id, payload) VALUES (?, ?)",
            (request_id, payload)
        )
        await db.commit()