import json
from .database import get_db, to_json, from_json

class MemoryManager:
    def __init__(self, guild_id):
        self.guild_id = guild_id

    async def get_context(self, limit=5):
        """Fetch recent conversation history for this server."""
        async with get_db() as db:
            async with db.execute(
                "SELECT request_text, executed_structure, timestamp FROM conversations WHERE server_id = ? ORDER BY id DESC LIMIT ?",
                (self.guild_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                history = []
                for row in reversed(rows): # Return in chronological order
                    history.append({
                        "request": row[0],
                        "structure": from_json(row[1]),
                        "timestamp": row[2]
                    })
                return history

    async def store_interaction(self, user_id, request_text, executed_structure):
        """Store a new interaction in the history."""
        async with get_db() as db:
            # Ensure server exists
            await db.execute(
                "INSERT OR IGNORE INTO servers (server_id) VALUES (?)",
                (self.guild_id,)
            )
            
            await db.execute(
                "INSERT INTO conversations (server_id, user_id, request_text, executed_structure) VALUES (?, ?, ?, ?)",
                (self.guild_id, user_id, request_text, to_json(executed_structure))
            )
            await db.commit()

    async def create_backup(self, structure_snapshot):
        """Create a backup of the current server structure."""
        async with get_db() as db:
            await db.execute(
                "INSERT INTO backups (server_id, structure_snapshot) VALUES (?, ?)",
                (self.guild_id, to_json(structure_snapshot))
            )
            await db.commit()

    async def get_backups(self, limit=5):
        """Fetch recent backups."""
        async with get_db() as db:
            async with db.execute(
                "SELECT id, structure_snapshot, timestamp FROM backups WHERE server_id = ? ORDER BY id DESC LIMIT ?",
                (self.guild_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                return [{
                    "id": row[0],
                    "structure": from_json(row[1]),
                    "timestamp": row[2]
                } for row in rows]

    async def get_backup(self, backup_id):
        """Fetch a specific backup."""
        async with get_db() as db:
            async with db.execute(
                "SELECT structure_snapshot FROM backups WHERE id = ? AND server_id = ?",
                (backup_id, self.guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                return from_json(row[0]) if row else None
