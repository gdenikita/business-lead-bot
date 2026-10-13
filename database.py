import aiosqlite
from datetime import datetime

DB_PATH = "leads.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                name TEXT,
                phone TEXT,
                service TEXT,
                comment TEXT,
                created_at TEXT,
                status TEXT DEFAULT 'new'
            )
        """)
        await db.commit()

async def add_lead(user_id: int, username: str, name: str, phone: str, service: str, comment: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO leads (user_id, username, name, phone, service, comment, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, username, name, phone, service, comment, datetime.now().isoformat())
        )
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM leads") as cursor:
            total = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM leads WHERE status = 'new'") as cursor:
            new = (await cursor.fetchone())[0]
        return {"total": total, "new": new}
