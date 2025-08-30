"""Integration tests for MCP server."""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch
import pytest

from markitdown_mcp_server.server import MarkItDownMCPServer


class TestMCPServerIntegration:
    """Integration tests for MCP server."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.server = MarkItDownMCPServer()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_server_initialization(self):
        """Test server initialization."""
        assert self.server is not None
        assert hasattr(self.server, 'tools')
        assert len(self.server.tools) > 0

    def test_tool_registration(self):
        """Test that all tools are properly registered."""
        tool_names = [tool.name for tool in self.server.tools]
        expected_tools = [
            "convert_file",
            "convert_batch", 
            "detect_format",
            "list_supported_formats",
            "list_plugins"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_convert_file_integration(self):
        """Test complete convert_file workflow."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Test content for integration test")

        # Find the convert_file tool
        convert_tool = next(t for t in self.server.tools if t.name == "convert_file")
        
        # Test conversion
        result = convert_tool.call({
            "input_path": str(test_file),
            "output_format": "markdown"
        })

        assert result["success"] is True
        assert "data" in result
        assert "content" in result["data"]
        assert "metadata" in result["data"]

    def test_convert_batch_integration(self):
        """Test complete convert_batch workflow."""
        # Create test files
        test_file1 = Path(self.temp_dir) / "test1.txt"
        test_file1.write_text("Test content 1")
        test_file2 = Path(self.temp_dir) / "test2.txt"
        test_file2.write_text("Test content 2")

        # Find the convert_batch tool
        batch_tool = next(t for t in self.server.tools if t.name == "convert_batch")
        
        # Test batch conversion
        result = batch_tool.call({
            "files": [
                {"path": str(test_file1), "output_format": "markdown"},
                {"path": str(test_file2), "output_format": "markdown"}
            ]
        })

        assert result["success"] is True
        assert "data" in result
        assert "results" in result["data"]
        assert len(result["data"]["results"]) == 2

    def test_detect_format_integration(self):
        """Test complete detect_format workflow."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Test content")

        # Find the detect_format tool
        detect_tool = next(t for t in self.server.tools if t.name == "detect_format")
        
        # Test format detection
        result = detect_tool.call({
            "file_path": str(test_file)
        })

        assert result["success"] is True
        assert "data" in result
        assert "format" in result["data"]
        assert "confidence" in result["data"]

    def test_list_supported_formats_integration(self):
        """Test complete list_supported_formats workflow."""
        # Find the list_supported_formats tool
        formats_tool = next(t for t in self.server.tools if t.name == "list_supported_formats")
        
        # Test formats listing
        result = formats_tool.call({})

        assert result["success"] is True
        assert "data" in result
        assert "formats" in result["data"]
        assert isinstance(result["data"]["formats"], list)
        assert len(result["data"]["formats"]) > 0

    def test_list_plugins_integration(self):
        """Test complete list_plugins workflow."""
        # Find the list_plugins tool
        plugins_tool = next(t for t in self.server.tools if t.name == "list_plugins")
        
        # Test plugins listing
        result = plugins_tool.call({})

        assert result["success"] is True
        assert "data" in result
        assert "plugins" in result["data"]
        assert isinstance(result["data"]["plugins"], list)

    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        # Find the convert_file tool
        convert_tool = next(t for t in self.server.tools if t.name == "convert_file")
        
        # Test with nonexistent file
        result = convert_tool.call({
            "input_path": "/nonexistent/file.txt",
            "output_format": "markdown"
        })

        assert result["success"] is False
        assert "error" in result

        # Test with missing parameters
        result = convert_tool.call({
            "input_path": "test.txt"
            # Missing output_format
        })

        assert result["success"] is False
        assert "error" in result


class TestEndToEndWorkflow:
    """Test end-to-end workflows."""

    def test_complete_file_conversion_workflow(self):
        """Test complete file conversion workflow."""
        # Create test file
        temp_dir = tempfile.mkdtemp()
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content for end-to-end workflow")

        try:
            server = MarkItDownMCPServer()
            
            # Step 1: Detect format
            detect_tool = next(t for t in server.tools if t.name == "detect_format")
            format_result = detect_tool.call({
                "file_path": str(test_file)
            })
            assert format_result["success"] is True
            detected_format = format_result["data"]["format"]

            # Step 2: Convert file
            convert_tool = next(t for t in server.tools if t.name == "convert_file")
            convert_result = convert_tool.call({
                "input_path": str(test_file),
                "output_format": "markdown"
            })
            assert convert_result["success"] is True
            assert "content" in convert_result["data"]

            # Step 3: Verify content
            content = convert_result["data"]["content"]
            assert "Test content" in content
            assert len(content) > 0

        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_batch_processing_workflow(self):
        """Test complete batch processing workflow."""
        # Create test files
        temp_dir = tempfile.mkdtemp()
        test_files = []
        
        for i in range(3):
            test_file = Path(temp_dir) / f"test{i}.txt"
            test_file.write_text(f"Test content {i}")
            test_files.append(test_file)

        try:
            server = MarkItDownMCPServer()
            
            # Step 1: List supported formats
            formats_tool = next(t for t in server.tools if t.name == "list_supported_formats")
            formats_result = formats_tool.call({})
            assert formats_result["success"] is True
            assert len(formats_result["data"]["formats"]) > 0

            # Step 2: Batch convert
            batch_tool = next(t for t in server.tools if t.name == "convert_batch")
            batch_result = batch_tool.call({
                "files": [
                    {"path": str(f), "output_format": "markdown"}
                    for f in test_files
                ]
            })
            assert batch_result["success"] is True
            assert len(batch_result["data"]["results"]) == 3

            # Step 3: Verify all conversions succeeded
            for result in batch_result["data"]["results"]:
                assert result["success"] is True
                assert "content" in result["data"]

        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_error_recovery_workflow(self):
        """Test error recovery in workflows."""
        temp_dir = tempfile.mkdtemp()
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")

        try:
            server = MarkItDownMCPServer()
            
            # Test workflow with mixed success/failure
            batch_tool = next(t for t in server.tools if t.name == "convert_batch")
            batch_result = batch_tool.call({
                "files": [
                    {"path": str(test_file), "output_format": "markdown"},
                    {"path": "/nonexistent/file.txt", "output_format": "markdown"}
                ]
            })

            assert batch_result["success"] is True
            assert len(batch_result["data"]["results"]) == 2
            assert batch_result["data"]["results"][0]["success"] is True
            assert batch_result["data"]["results"][1]["success"] is False

        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)



