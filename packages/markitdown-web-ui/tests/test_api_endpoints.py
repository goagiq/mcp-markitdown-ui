"""Tests for FastAPI endpoints."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient

from markitdown_web_ui.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

    def test_ui_endpoint(self, client):
        """Test UI endpoint."""
        response = client.get("/ui")
        assert response.status_code == 200


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_get_formats(self, client):
        """Test getting supported formats."""
        response = client.get("/api/formats")
        assert response.status_code == 200
        data = response.json()
        assert "formats" in data
        assert isinstance(data["formats"], list)
        assert len(data["formats"]) > 0

    @patch('markitdown_web_ui.api.routes.MarkItDown')
    def test_convert_file_success(self, mock_markitdown, client, temp_dir):
        """Test successful file conversion."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")

        # Mock MarkItDown response
        mock_result = Mock()
        mock_result.text_content = "# Test Content\n\nTest content"
        mock_result.metadata = {"format": "text", "size": 12}
        
        mock_md = Mock()
        mock_md.convert.return_value = mock_result
        mock_markitdown.return_value = mock_md

        # Test file upload and conversion
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/convert",
                files={"file": ("test.txt", f, "text/plain")},
                data={"output_format": "markdown"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "content" in data["data"]
        assert data["data"]["content"] == "# Test Content\n\nTest content"

    def test_convert_file_no_file(self, client):
        """Test conversion without file."""
        response = client.post(
            "/api/convert",
            data={"output_format": "markdown"}
        )
        assert response.status_code == 400

    def test_convert_file_invalid_format(self, client, temp_dir):
        """Test conversion with invalid format."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/convert",
                files={"file": ("test.txt", f, "text/plain")},
                data={"output_format": "invalid_format"}
            )

        assert response.status_code == 400

    @patch('markitdown_web_ui.api.routes.MarkItDown')
    def test_convert_file_error(self, mock_markitdown, client, temp_dir):
        """Test conversion error handling."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")

        # Mock MarkItDown to raise exception
        mock_md = Mock()
        mock_md.convert.side_effect = Exception("Conversion failed")
        mock_markitdown.return_value = mock_md

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/convert",
                files={"file": ("test.txt", f, "text/plain")},
                data={"output_format": "markdown"}
            )

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_detect_format_success(self, client, temp_dir):
        """Test format detection."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/detect",
                files={"file": ("test.txt", f, "text/plain")}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "format" in data["data"]
        assert data["data"]["format"] == "text"

    def test_detect_format_no_file(self, client):
        """Test format detection without file."""
        response = client.post("/api/detect")
        assert response.status_code == 400


class TestMCPEndpoints:
    """Test MCP integration endpoints."""

    def test_mcp_health(self, client):
        """Test MCP health endpoint."""
        response = client.get("/mcp/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @patch('markitdown_web_ui.mcp_integration.mcp_client')
    def test_mcp_convert_file(self, mock_mcp_client, client, temp_dir):
        """Test MCP file conversion endpoint."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")

        # Mock MCP client response
        mock_response = {
            "success": True,
            "data": {
                "content": "# Test Content\n\nTest content",
                "metadata": {"format": "text", "size": 12}
            }
        }
        mock_mcp_client.call_tool.return_value = mock_response

        with open(test_file, "rb") as f:
            response = client.post(
                "/mcp/convert",
                files={"file": ("test.txt", f, "text/plain")},
                data={"output_format": "markdown"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["content"] == "# Test Content\n\nTest content"

    @patch('markitdown_web_ui.mcp_integration.mcp_client')
    def test_mcp_batch_convert(self, mock_mcp_client, client):
        """Test MCP batch conversion endpoint."""
        # Mock MCP client response
        mock_response = {
            "success": True,
            "data": {
                "results": [
                    {
                        "success": True,
                        "data": {"content": "# File 1", "metadata": {}}
                    },
                    {
                        "success": True,
                        "data": {"content": "# File 2", "metadata": {}}
                    }
                ]
            }
        }
        mock_mcp_client.call_tool.return_value = mock_response

        batch_data = {
            "files": [
                {"path": "/path/to/file1.txt", "output_format": "markdown"},
                {"path": "/path/to/file2.txt", "output_format": "markdown"}
            ]
        }

        response = client.post(
            "/mcp/batch",
            json=batch_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["results"]) == 2

    @patch('markitdown_web_ui.mcp_integration.mcp_client')
    def test_mcp_detect_format(self, mock_mcp_client, client):
        """Test MCP format detection endpoint."""
        # Mock MCP client response
        mock_response = {
            "success": True,
            "data": {
                "format": "text",
                "confidence": 0.95,
                "metadata": {"size": 12}
            }
        }
        mock_mcp_client.call_tool.return_value = mock_response

        response = client.post(
            "/mcp/detect",
            json={"file_path": "/path/to/file.txt"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["format"] == "text"

    @patch('markitdown_web_ui.mcp_integration.mcp_client')
    def test_mcp_list_formats(self, mock_mcp_client, client):
        """Test MCP list formats endpoint."""
        # Mock MCP client response
        mock_response = {
            "success": True,
            "data": {
                "formats": [
                    {
                        "name": "Text",
                        "extensions": [".txt"],
                        "description": "Plain text files"
                    }
                ]
            }
        }
        mock_mcp_client.call_tool.return_value = mock_response

        response = client.get("/mcp/formats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "formats" in data["data"]

    @patch('markitdown_web_ui.mcp_integration.mcp_client')
    def test_mcp_list_plugins(self, mock_mcp_client, client):
        """Test MCP list plugins endpoint."""
        # Mock MCP client response
        mock_response = {
            "success": True,
            "data": {
                "plugins": [
                    {
                        "name": "test_plugin",
                        "version": "1.0.0",
                        "description": "Test plugin"
                    }
                ]
            }
        }
        mock_mcp_client.call_tool.return_value = mock_response

        response = client.get("/mcp/plugins")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "plugins" in data["data"]

    @patch('markitdown_web_ui.mcp_integration.mcp_client')
    def test_mcp_upload_and_convert(self, mock_mcp_client, client, temp_dir):
        """Test MCP upload and convert endpoint."""
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Test content")

        # Mock MCP client response
        mock_response = {
            "success": True,
            "data": {
                "content": "# Test Content\n\nTest content",
                "metadata": {"format": "text", "size": 12}
            }
        }
        mock_mcp_client.call_tool.return_value = mock_response

        with open(test_file, "rb") as f:
            response = client.post(
                "/mcp/upload-and-convert",
                files={"file": ("test.txt", f, "text/plain")},
                data={"output_format": "markdown"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["content"] == "# Test Content\n\nTest content"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_404_endpoint(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test method not allowed error."""
        response = client.put("/api/formats")
        assert response.status_code == 405

    @patch('markitdown_web_ui.mcp_integration.mcp_client')
    def test_mcp_client_error(self, mock_mcp_client, client):
        """Test MCP client error handling."""
        # Mock MCP client to raise exception
        mock_mcp_client.call_tool.side_effect = Exception("MCP error")

        response = client.get("/mcp/formats")

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "error" in data


class TestFileHandling:
    """Test file handling scenarios."""

    def test_large_file_upload(self, client, temp_dir):
        """Test large file upload handling."""
        # Create a large test file (simulate large file)
        test_file = Path(temp_dir) / "large.txt"
        test_file.write_text("x" * 1024 * 1024)  # 1MB file

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/convert",
                files={"file": ("large.txt", f, "text/plain")},
                data={"output_format": "markdown"}
            )

        # Should handle large files gracefully
        assert response.status_code in [200, 413]  # 413 if too large

    def test_unsupported_file_type(self, client, temp_dir):
        """Test unsupported file type handling."""
        # Create file with unsupported extension
        test_file = Path(temp_dir) / "test.xyz"
        test_file.write_text("Test content")

        with open(test_file, "rb") as f:
            response = client.post(
                "/api/convert",
                files={"file": ("test.xyz", f, "application/octet-stream")},
                data={"output_format": "markdown"}
            )

        # Should handle unsupported files gracefully
        assert response.status_code in [200, 400, 422]
