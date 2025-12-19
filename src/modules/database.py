import os
import json
import logging
import aiosqlite
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseAPI:
    """SQLite database API to replace Supabase"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to database.db in the project root
            db_path = str(Path(__file__).parents[2] / "database.db")
        self.db_path = db_path
        self._initialized = False

    async def _ensure_initialized(self):
        """Initialize database connection and create tables if needed"""
        if not self._initialized:
            async with aiosqlite.connect(self.db_path) as db:
                # Read and execute schema
                schema_path = Path(__file__).parents[1] / "db.sql"
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = f.read()
                await db.executescript(schema)
                await db.commit()
            self._initialized = True

    async def _execute(self, query: str, params: tuple = ()):
        """Execute a query and return results"""
        await self._ensure_initialized()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            await db.commit()
            return await cursor.fetchall()

    async def _execute_one(self, query: str, params: tuple = ()):
        """Execute a query and return one result"""
        await self._ensure_initialized()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            await db.commit()
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def add_user_quizz(self, id: str, phone: str, question: str, difficulty: str, type_: str):
        """Add a new quiz entry"""
        query = """
            INSERT INTO quizz (id, user, question, difficulty, type)
            VALUES (?, ?, ?, ?, ?)
        """
        await self._execute(query, (id, phone, question, difficulty, type_))
        return {"id": id, "user": phone, "question": question, "difficulty": difficulty, "type": type_}

    async def get_user_quizz(self, phone: str, type_: str):
        """Get user quiz history"""
        query = """
            SELECT question, correct, difficulty
            FROM quizz
            WHERE user = ? AND type = ?
            ORDER BY created_at DESC
            LIMIT 10
        """
        rows = await self._execute(query, (phone, type_))
        return [dict(row) for row in rows]

    async def get_viewed_signs(self, phone: str) -> List[str]:
        """Get list of viewed signs for a user"""
        query = """
            SELECT sign_viewed
            FROM user
            WHERE phone = ?
            LIMIT 1
        """
        row = await self._execute_one(query, (phone,))
        if row and row.get("sign_viewed"):
            try:
                return json.loads(row["sign_viewed"])
            except json.JSONDecodeError:
                return []
        return []

    async def add_viewed_sign(self, phone: str, signs: List[str]):
        """Update viewed signs for a user"""
        # First, ensure user exists
        user_query = "SELECT id FROM user WHERE phone = ?"
        user = await self._execute_one(user_query, (phone,))
        
        signs_json = json.dumps(signs)
        
        if user:
            # Update existing user
            query = """
                UPDATE user
                SET sign_viewed = ?
                WHERE phone = ?
            """
            await self._execute(query, (signs_json, phone))
        else:
            # Create new user
            query = """
                INSERT INTO user (phone, sign_viewed)
                VALUES (?, ?)
            """
            await self._execute(query, (phone, signs_json))

    async def set_quizz_answer(self, id: str, correct: bool):
        """Update quiz answer correctness"""
        query = """
            UPDATE quizz
            SET correct = ?
            WHERE id = ?
        """
        await self._execute(query, (1 if correct else 0, id))

    async def set_user_plan(self, phone: str, pro: bool):
        """Update user plan (pro status)"""
        # First, ensure user exists
        user_query = "SELECT id FROM user WHERE phone = ?"
        user = await self._execute_one(user_query, (phone,))
        
        if user:
            query = """
                UPDATE user
                SET pro = ?
                WHERE phone = ?
            """
            await self._execute(query, (1 if pro else 0, phone))
        else:
            # Create new user with pro status
            query = """
                INSERT INTO user (phone, pro)
                VALUES (?, ?)
            """
            await self._execute(query, (phone, 1 if pro else 0))

