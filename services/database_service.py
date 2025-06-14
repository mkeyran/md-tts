"""
Database service for managing conversion history.
"""

import logging
from datetime import datetime

from models.database import ConversionHistory
from models.schemas import HistoryItem, HistoryResponse

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing conversion history database operations."""

    def __init__(self, db_path: str = "storage/history.db"):
        """
        Initialize database service.

        Args:
            db_path: Path to SQLite database file
        """
        self.db = ConversionHistory(db_path)
        logger.info("Database service initialized")

    def create_conversion_record(
        self, conversion_id: str, markdown_text: str, title: str | None = None
    ) -> None:
        """
        Create a new conversion record.

        Args:
            conversion_id: Unique conversion ID
            markdown_text: Original markdown text
            title: Optional title
        """
        # Create text preview (first 200 characters)
        text_preview = markdown_text[:200].strip()
        if len(markdown_text) > 200:
            text_preview += "..."

        self.db.add_conversion(
            conversion_id=conversion_id,
            markdown_text=markdown_text,
            text_preview=text_preview,
            title=title,
            status="pending",
        )

    def update_conversion_success(
        self, conversion_id: str, file_path: str, file_size: int
    ) -> None:
        """
        Update conversion as completed successfully.

        Args:
            conversion_id: Conversion ID
            file_path: Path to generated audio file
            file_size: Size of generated file in bytes
        """
        self.db.update_conversion(
            conversion_id=conversion_id,
            status="completed",
            file_path=file_path,
            file_size=file_size,
        )

    def update_conversion_failed(self, conversion_id: str, error: str) -> None:
        """
        Update conversion as failed.

        Args:
            conversion_id: Conversion ID
            error: Error message
        """
        self.db.update_conversion(
            conversion_id=conversion_id, status=f"failed: {error}"
        )

    def get_conversion_details(self, conversion_id: str) -> dict | None:
        """
        Get conversion details by ID.

        Args:
            conversion_id: Conversion ID

        Returns:
            Conversion details or None if not found
        """
        return self.db.get_conversion(conversion_id)

    def get_conversion_history(
        self, limit: int = 50, offset: int = 0
    ) -> HistoryResponse:
        """
        Get conversion history.

        Args:
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            History response with list of items
        """
        records = self.db.get_history(limit=limit, offset=offset)

        items = []
        for record in records:
            # Parse datetime string
            created_at = datetime.fromisoformat(
                record["created_at"].replace("Z", "+00:00")
            )

            # Create download URL if file exists
            download_url = None
            if record["status"] == "completed" and record["file_path"]:
                download_url = f"/download/{record['id']}"

            item = HistoryItem(
                id=record["id"],
                title=record["title"],
                text_preview=record["text_preview"],
                created_at=created_at,
                status=record["status"],
                file_size=record["file_size"],
                download_url=download_url,
            )
            items.append(item)

        return HistoryResponse(items=items)

    def delete_conversion_record(self, conversion_id: str) -> bool:
        """
        Delete conversion record.

        Args:
            conversion_id: Conversion ID to delete

        Returns:
            True if deleted, False if not found
        """
        return self.db.delete_conversion(conversion_id)

    def cleanup_old_records(self, max_age_days: int = 30) -> int:
        """
        Clean up old conversion records.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of records deleted
        """
        return self.db.cleanup_old_records(max_age_days)
