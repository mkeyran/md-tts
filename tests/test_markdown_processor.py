"""
Tests for markdown processor service.
"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.markdown_processor import MarkdownProcessor


class TestMarkdownProcessor:
    """Test cases for MarkdownProcessor."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.processor = MarkdownProcessor()
    
    def test_extract_simple_text(self) -> None:
        """Test extraction of simple markdown text."""
        markdown_text = "# Hello World\n\nThis is a simple paragraph."
        result = self.processor.extract_text(markdown_text)
        
        assert "Hello World" in result
        assert "This is a simple paragraph." in result
        assert "#" not in result
    
    def test_remove_code_blocks(self) -> None:
        """Test that code blocks are removed from text."""
        markdown_text = """# Title

Here is some text.

```python
print("This should not appear")
```

More text here."""
        result = self.processor.extract_text(markdown_text)
        
        assert "Title" in result
        assert "Here is some text." in result
        assert "More text here." in result
        assert "print" not in result
        assert "This should not appear" not in result
    
    def test_remove_inline_code(self) -> None:
        """Test that inline code is removed."""
        markdown_text = "Use the `print()` function to display text."
        result = self.processor.extract_text(markdown_text)
        
        assert "Use the function to display text." in result
        assert "`" not in result
        assert "print()" not in result
    
    def test_clean_urls(self) -> None:
        """Test that URLs are removed from text."""
        markdown_text = "Visit https://example.com for more info."
        result = self.processor.extract_text(markdown_text)
        
        assert "Visit for more info." in result
        assert "https://example.com" not in result
    
    def test_clean_emails(self) -> None:
        """Test that email addresses are removed."""
        markdown_text = "Contact us at test@example.com for help."
        result = self.processor.extract_text(markdown_text)
        
        assert "Contact us at for help." in result
        assert "test@example.com" not in result
    
    def test_clean_markdown_artifacts(self) -> None:
        """Test removal of markdown formatting characters."""
        markdown_text = "This is **bold** and *italic* text with [links](url)."
        result = self.processor.extract_text(markdown_text)
        
        assert "This is bold and italic text with links." in result
        assert "*" not in result
        assert "[" not in result
        assert "]" not in result
        assert "(" not in result
    
    def test_normalize_whitespace(self) -> None:
        """Test that whitespace is normalized."""
        markdown_text = "Text   with    multiple\n\n\nspaces\tand\ttabs."
        result = self.processor.extract_text(markdown_text)
        
        assert result == "Text with multiple spaces and tabs."
    
    def test_create_preview_short_text(self) -> None:
        """Test preview creation for short text."""
        text = "Short text"
        result = self.processor.create_preview(text, 50)
        
        assert result == "Short text"
        assert "..." not in result
    
    def test_create_preview_long_text(self) -> None:
        """Test preview creation for long text."""
        text = "This is a very long text that should be truncated at some reasonable point"
        result = self.processor.create_preview(text, 30)
        
        assert len(result) <= 34  # 30 + "..."
        assert result.endswith("...")
        assert result.startswith("This is a very long text")
    
    def test_create_preview_no_spaces(self) -> None:
        """Test preview creation for text without spaces."""
        text = "verylongtextwithoutanyspacesthatcannotbetruncatedproperly"
        result = self.processor.create_preview(text, 30)
        
        assert len(result) == 33  # 30 + "..."
        assert result.endswith("...")
    
    def test_complex_markdown(self) -> None:
        """Test processing of complex markdown document."""
        markdown_text = """# Main Title

## Subtitle

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2 with `code`
- List item 3

> This is a blockquote

Here's a code block:

```python
def hello():
    return "world"
```

And here's more text after the code.

Visit [our website](https://example.com) or email us at info@example.com."""
        
        result = self.processor.extract_text(markdown_text)
        
        # Should contain main content
        assert "Main Title" in result
        assert "Subtitle" in result
        assert "This is a paragraph with bold and italic text." in result
        assert "List item 1" in result
        assert "This is a blockquote" in result
        assert "And here's more text after the code." in result
        
        # Should not contain code or artifacts
        assert "def hello():" not in result
        assert "return \"world\"" not in result
        assert "https://example.com" not in result
        assert "info@example.com" not in result
        assert "`" not in result
        assert "[" not in result
        assert "#" not in result