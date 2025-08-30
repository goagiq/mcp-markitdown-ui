"""Unit tests for MCP tools."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from markitdown_mcp_server.tools.convert import (
    ConvertFileTool, ConvertBatchTool
)
from markitdown_mcp_server.tools.detect import DetectFormatTool
from markitdown_mcp_server.tools.formats import ListSupportedFormatsTool
from markitdown_mcp_server.tools.plugins import ListPluginsTool


class TestConvertFileTool:
    """Test cases for ConvertFileTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = ConvertFileTool()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tool_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "convert_file"
        assert "input_path" in self.tool.input_schema["properties"]
        assert "output_format" in self.tool.input_schema["properties"]

    @patch('markitdown_mcp_server.tools.convert.MarkItDown')
    def test_convert_file_success(self, mock_markitdown):
        """Test successful file conversion."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Test content")

        # Mock MarkItDown response
        mock_result = Mock()
        mock_result.text_content = "# Test Content\n\nTest content"
        mock_result.metadata = {"format": "text", "size": 12}
        
        mock_md = Mock()
        mock_md.convert.return_value = mock_result
        mock_markitdown.return_value = mock_md

        # Test conversion
        result = self.tool.call({
            "input_path": str(test_file),
            "output_format": "markdown"
        })

        assert result["success"] is True
        assert result["data"]["content"] == "# Test Content\n\nTest content"
        assert result["data"]["metadata"]["format"] == "text"
        mock_md.convert.assert_called_once()

    def test_convert_file_invalid_path(self):
        """Test conversion with invalid file path."""
        result = self.tool.call({
            "input_path": "/nonexistent/file.txt",
            "output_format": "markdown"
        })

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_convert_file_missing_parameters(self):
        """Test conversion with missing parameters."""
        result = self.tool.call({
            "input_path": "test.txt"
            # Missing output_format
        })

        assert result["success"] is False
        assert "error" in result
        assert "output_format" in result["error"]

    @patch('markitdown_mcp_server.tools.convert.MarkItDown')
    def test_convert_file_conversion_error(self, mock_markitdown):
        """Test conversion error handling."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Test content")

        # Mock MarkItDown to raise an exception
        mock_md = Mock()
        mock_md.convert.side_effect = Exception("Conversion failed")
        mock_markitdown.return_value = mock_md

        result = self.tool.call({
            "input_path": str(test_file),
            "output_format": "markdown"
        })

        assert result["success"] is False
        assert "error" in result
        assert "Conversion failed" in result["error"]


class TestConvertBatchTool:
    """Test cases for ConvertBatchTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = ConvertBatchTool()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tool_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "convert_batch"
        assert "files" in self.tool.input_schema["properties"]

    @patch('markitdown_mcp_server.tools.convert.MarkItDown')
    def test_convert_batch_success(self, mock_markitdown):
        """Test successful batch conversion."""
        # Create test files
        test_file1 = Path(self.temp_dir) / "test1.txt"
        test_file1.write_text("Test content 1")
        test_file2 = Path(self.temp_dir) / "test2.txt"
        test_file2.write_text("Test content 2")

        # Mock MarkItDown responses
        mock_result1 = Mock()
        mock_result1.text_content = "# Test Content 1\n\nTest content 1"
        mock_result1.metadata = {"format": "text", "size": 15}
        
        mock_result2 = Mock()
        mock_result2.text_content = "# Test Content 2\n\nTest content 2"
        mock_result2.metadata = {"format": "text", "size": 15}

        mock_md = Mock()
        mock_md.convert.side_effect = [mock_result1, mock_result2]
        mock_markitdown.return_value = mock_md

        # Test batch conversion
        result = self.tool.call({
            "files": [
                {"path": str(test_file1), "output_format": "markdown"},
                {"path": str(test_file2), "output_format": "markdown"}
            ]
        })

        assert result["success"] is True
        assert len(result["data"]["results"]) == 2
        assert result["data"]["results"][0]["success"] is True
        assert result["data"]["results"][1]["success"] is True
        assert mock_md.convert.call_count == 2

    def test_convert_batch_empty_list(self):
        """Test batch conversion with empty file list."""
        result = self.tool.call({
            "files": []
        })

        assert result["success"] is False
        assert "error" in result
        assert "empty" in result["error"].lower()

    @patch('markitdown_mcp_server.tools.convert.MarkItDown')
    def test_convert_batch_partial_failure(self, mock_markitdown):
        """Test batch conversion with partial failures."""
        # Create test files
        test_file1 = Path(self.temp_dir) / "test1.txt"
        test_file1.write_text("Test content 1")
        test_file2 = Path(self.temp_dir) / "nonexistent.txt"

        # Mock MarkItDown response for first file only
        mock_result1 = Mock()
        mock_result1.text_content = "# Test Content 1\n\nTest content 1"
        mock_result1.metadata = {"format": "text", "size": 15}

        mock_md = Mock()
        mock_md.convert.side_effect = [mock_result1, Exception("File not found")]
        mock_markitdown.return_value = mock_md

        result = self.tool.call({
            "files": [
                {"path": str(test_file1), "output_format": "markdown"},
                {"path": str(test_file2), "output_format": "markdown"}
            ]
        })

        assert result["success"] is True
        assert len(result["data"]["results"]) == 2
        assert result["data"]["results"][0]["success"] is True
        assert result["data"]["results"][1]["success"] is False


class TestDetectFormatTool:
    """Test cases for DetectFormatTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = DetectFormatTool()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tool_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "detect_format"
        assert "file_path" in self.tool.input_schema["properties"]

    def test_detect_format_success(self):
        """Test successful format detection."""
        # Create a test file with known extension
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Test content")

        result = self.tool.call({
            "file_path": str(test_file)
        })

        assert result["success"] is True
        assert "format" in result["data"]
        assert "confidence" in result["data"]
        assert result["data"]["format"] == "text"

    def test_detect_format_nonexistent_file(self):
        """Test format detection with nonexistent file."""
        result = self.tool.call({
            "file_path": "/nonexistent/file.txt"
        })

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_detect_format_missing_parameter(self):
        """Test format detection with missing parameter."""
        result = self.tool.call({})

        assert result["success"] is False
        assert "error" in result
        assert "file_path" in result["error"]


class TestListSupportedFormatsTool:
    """Test cases for ListSupportedFormatsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = ListSupportedFormatsTool()

    def test_tool_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "list_supported_formats"
        assert len(self.tool.input_schema["properties"]) == 0

    def test_list_supported_formats(self):
        """Test listing supported formats."""
        result = self.tool.call({})

        assert result["success"] is True
        assert "formats" in result["data"]
        assert isinstance(result["data"]["formats"], list)
        assert len(result["data"]["formats"]) > 0

        # Check that each format has required fields
        for format_info in result["data"]["formats"]:
            assert "name" in format_info
            assert "extensions" in format_info
            assert "description" in format_info


class TestListPluginsTool:
    """Test cases for ListPluginsTool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tool = ListPluginsTool()

    def test_tool_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "list_plugins"
        assert len(self.tool.input_schema["properties"]) == 0

    @patch('markitdown_mcp_server.tools.plugins.importlib.metadata')
    def test_list_plugins_success(self, mock_metadata):
        """Test listing plugins successfully."""
        # Mock plugin discovery
        mock_entry_point = Mock()
        mock_entry_point.name = "test_plugin"
        mock_entry_point.dist.metadata = {"Name": "test-plugin", "Version": "1.0.0"}
        
        mock_metadata.entry_points.return_value = {
            "markitdown.converters": [mock_entry_point]
        }

        result = self.tool.call({})

        assert result["success"] is True
        assert "plugins" in result["data"]
        assert isinstance(result["data"]["plugins"], list)

    @patch('markitdown_mcp_server.tools.plugins.importlib.metadata')
    def test_list_plugins_no_plugins(self, mock_metadata):
        """Test listing plugins when none are installed."""
        # Mock no plugins found
        mock_metadata.entry_points.return_value = {}

        result = self.tool.call({})

        assert result["success"] is True
        assert "plugins" in result["data"]
        assert result["data"]["plugins"] == []

    @patch('markitdown_mcp_server.tools.plugins.importlib.metadata')
    def test_list_plugins_error_handling(self, mock_metadata):
        """Test error handling in plugin listing."""
        # Mock exception during plugin discovery
        mock_metadata.entry_points.side_effect = Exception("Plugin discovery failed")

        result = self.tool.call({})

        assert result["success"] is False
        assert "error" in result
        assert "Plugin discovery failed" in result["error"]
