"""
Database models for TTS conversion history.
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversionHistory:
    """Database model for conversion history."""

    def __init__(self, db_path: str = "storage/history.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    markdown_text TEXT NOT NULL,
                    text_preview TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'pending',
                    file_size INTEGER,
                    file_path TEXT
                )
            """)
            conn.commit()
            logger.info("Database initialized")

    def add_conversion(
        self,
        conversion_id: str,
        markdown_text: str,
        text_preview: str,
        title: str | None = None,
        status: str = "pending",
    ) -> None:
        """
        Add a new conversion to history.

        Args:
            conversion_id: Unique conversion ID
            markdown_text: Original markdown text
            text_preview: Preview of converted text
            title: Optional title
            status: Conversion status
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO conversions (id, title, markdown_text, text_preview, status)
                VALUES (?, ?, ?, ?, ?)
            """,
                (conversion_id, title, markdown_text, text_preview, status),
            )
            conn.commit()
            logger.info(f"Added conversion to history: {conversion_id}")

    def update_conversion(
        self,
        conversion_id: str,
        status: str | None = None,
        file_size: int | None = None,
        file_path: str | None = None,
    ) -> None:
        """
        Update conversion details.

        Args:
            conversion_id: Conversion ID to update
            status: New status
            file_size: File size in bytes
            file_path: Path to generated file
        """
        updates = []
        params = []

        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if file_size is not None:
            updates.append("file_size = ?")
            params.append(file_size)

        if file_path is not None:
            updates.append("file_path = ?")
            params.append(str(file_path))

        if updates:
            params.append(conversion_id)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    f"""
                    UPDATE conversions 
                    SET {", ".join(updates)}
                    WHERE id = ?
                """,
                    params,
                )
                conn.commit()
                logger.info(f"Updated conversion: {conversion_id}")

    def get_conversion(self, conversion_id: str) -> dict | None:
        """
        Get conversion by ID.

        Args:
            conversion_id: Conversion ID

        Returns:
            Conversion data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM conversions WHERE id = ?
            """,
                (conversion_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_history(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """
        Get conversion history.

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            List of conversion history items
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM conversions 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_conversion(self, conversion_id: str) -> bool:
        """
        Delete conversion from history.

        Args:
            conversion_id: Conversion ID to delete

        Returns:
            True if deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                DELETE FROM conversions WHERE id = ?
            """,
                (conversion_id,),
            )
            conn.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted conversion: {conversion_id}")
            return deleted

    def cleanup_old_records(self, max_age_days: int = 30) -> int:
        """
        Clean up old conversion records.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of records deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                f"""
                DELETE FROM conversions 
                WHERE created_at < datetime('now', '-{max_age_days} days')
            """
            )
            conn.commit()
            deleted = cursor.rowcount
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} old conversion records")
            return deleted
