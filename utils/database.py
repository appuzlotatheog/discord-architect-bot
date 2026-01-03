import aiosqlite
import json
import os

DB_NAME = "architect.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                server_id INTEGER PRIMARY KEY,
                guild_name TEXT,
                admin_users TEXT,
                settings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                user_id INTEGER,
                request_text TEXT,
                executed_structure TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers (server_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id INTEGER,
                structure_snapshot TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_id) REFERENCES servers (server_id)
            )
        """)
        await db.commit()

def get_db():
    return aiosqlite.connect(DB_NAME)

# Helper to serialize/deserialize JSON
def to_json(data):
    return json.dumps(data) if data else None

def from_json(data):
    return json.loads(data) if data else None
