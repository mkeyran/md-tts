"""
Service for processing markdown text and extracting plain text for TTS.
"""

import re

import markdown
from bs4 import BeautifulSoup


class MarkdownProcessor:
    """Process markdown text and extract clean text for TTS."""

    def __init__(self) -> None:
        self.md = markdown.Markdown(extensions=["extra", "codehilite"])

    def extract_text(self, markdown_text: str) -> str:
        """
        Extract plain text from markdown for TTS conversion.

        Args:
            markdown_text: Raw markdown text

        Returns:
            Clean text suitable for TTS
        """
        # Convert markdown to HTML
        html = self.md.convert(markdown_text)

        # Parse HTML and extract text
        soup = BeautifulSoup(html, "html.parser")

        # Remove code blocks entirely
        for code_block in soup.find_all(["code", "pre"]):
            code_block.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up the text
        text = self._clean_text(text)

        return text

    def _clean_text(self, text: str) -> str:
        """Clean up extracted text for better TTS pronunciation."""
        # Remove multiple whitespaces and newlines
        text = re.sub(r"\s+", " ", text)

        # Remove URLs
        text = re.sub(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "",
            text,
        )

        # Remove email addresses
        text = re.sub(r"\S+@\S+", "", text)

        # Remove markdown artifacts that might remain (but preserve basic punctuation)
        text = re.sub(r"[#*_`~\[\]]", "", text)
        text = re.sub(
            r"\([^)]*\)", "", text
        )  # Remove content in parentheses (likely URLs)

        # Clean up punctuation spacing
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"([,.!?;:])\s*", r"\1 ", text)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def create_preview(self, text: str, max_length: int = 100) -> str:
        """Create a preview of the text for display."""
        if len(text) <= max_length:
            return text

        # Find the last space before max_length
        preview = text[:max_length]
        last_space = preview.rfind(" ")

        if last_space > max_length // 2:  # If there's a reasonable space
            preview = preview[:last_space]

        return preview + "..."
