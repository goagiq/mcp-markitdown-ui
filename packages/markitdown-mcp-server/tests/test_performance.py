"""Performance tests for MCP server."""

import tempfile
import time
import psutil
import os
from pathlib import Path
from unittest.mock import patch
import pytest

from markitdown_mcp_server.server import MarkItDownMCPServer


class TestPerformance:
    """Performance tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.server = MarkItDownMCPServer()
        self.process = psutil.Process()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def get_memory_usage(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def test_small_file_performance(self):
        """Test performance with small files (< 1KB)."""
        # Create small test file
        test_file = Path(self.temp_dir) / "small.txt"
        test_file.write_text("Small test content" * 10)  # ~200 bytes

        convert_tool = next(t for t in self.server.tools if t.name == "convert_file")
        
        # Measure performance
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        result = convert_tool.call({
            "input_path": str(test_file),
            "output_format": "markdown"
        })
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        assert result["success"] is True
        assert execution_time < 1.0  # Should complete in under 1 second
        assert memory_used < 50  # Should use less than 50MB additional memory

    def test_medium_file_performance(self):
        """Test performance with medium files (1KB - 1MB)."""
        # Create medium test file
        test_file = Path(self.temp_dir) / "medium.txt"
        test_file.write_text("Medium test content " * 1000)  # ~20KB

        convert_tool = next(t for t in self.server.tools if t.name == "convert_file")
        
        # Measure performance
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        result = convert_tool.call({
            "input_path": str(test_file),
            "output_format": "markdown"
        })
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        assert result["success"] is True
        assert execution_time < 5.0  # Should complete in under 5 seconds
        assert memory_used < 100  # Should use less than 100MB additional memory

    def test_large_file_performance(self):
        """Test performance with large files (> 1MB)."""
        # Create large test file
        test_file = Path(self.temp_dir) / "large.txt"
        test_file.write_text("Large test content " * 50000)  # ~1MB

        convert_tool = next(t for t in self.server.tools if t.name == "convert_file")
        
        # Measure performance
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        result = convert_tool.call({
            "input_path": str(test_file),
            "output_format": "markdown"
        })
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        assert result["success"] is True
        assert execution_time < 30.0  # Should complete in under 30 seconds
        assert memory_used < 200  # Should use less than 200MB additional memory

    def test_batch_conversion_performance(self):
        """Test performance with batch conversions."""
        # Create multiple test files
        test_files = []
        for i in range(10):
            test_file = Path(self.temp_dir) / f"batch_test_{i}.txt"
            test_file.write_text(f"Batch test content {i} " * 100)  # ~2KB each
            test_files.append(test_file)

        batch_tool = next(t for t in self.server.tools if t.name == "convert_batch")
        
        # Measure performance
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        result = batch_tool.call({
            "files": [
                {"path": str(f), "output_format": "markdown"}
                for f in test_files
            ]
        })
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        assert result["success"] is True
        assert len(result["data"]["results"]) == 10
        assert execution_time < 10.0  # Should complete in under 10 seconds
        assert memory_used < 150  # Should use less than 150MB additional memory

    def test_concurrent_requests_performance(self):
        """Test performance with concurrent requests."""
        import threading
        import queue
        
        # Create test file
        test_file = Path(self.temp_dir) / "concurrent.txt"
        test_file.write_text("Concurrent test content " * 100)

        convert_tool = next(t for t in self.server.tools if t.name == "convert_file")
        
        results_queue = queue.Queue()
        
        def convert_file():
            """Convert file and put result in queue."""
            try:
                result = convert_tool.call({
                    "input_path": str(test_file),
                    "output_format": "markdown"
                })
                results_queue.put(("success", result))
            except Exception as e:
                results_queue.put(("error", str(e)))

        # Start multiple threads
        threads = []
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        for _ in range(5):
            thread = threading.Thread(target=convert_file)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        # Check results
        success_count = 0
        while not results_queue.empty():
            status, result = results_queue.get()
            if status == "success" and result["success"]:
                success_count += 1

        assert success_count == 5  # All conversions should succeed
        assert execution_time < 15.0  # Should complete in under 15 seconds
        assert memory_used < 250  # Should use less than 250MB additional memory

    def test_format_detection_performance(self):
        """Test format detection performance."""
        # Create test file
        test_file = Path(self.temp_dir) / "detect_test.txt"
        test_file.write_text("Format detection test content")

        detect_tool = next(t for t in self.server.tools if t.name == "detect_format")
        
        # Measure performance
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        result = detect_tool.call({
            "file_path": str(test_file)
        })
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        assert result["success"] is True
        assert execution_time < 0.5  # Should complete in under 0.5 seconds
        assert memory_used < 10  # Should use less than 10MB additional memory

    def test_list_formats_performance(self):
        """Test list formats performance."""
        formats_tool = next(t for t in self.server.tools if t.name == "list_supported_formats")
        
        # Measure performance
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        result = formats_tool.call({})
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        assert result["success"] is True
        assert execution_time < 0.1  # Should complete in under 0.1 seconds
        assert memory_used < 5  # Should use less than 5MB additional memory

    def test_list_plugins_performance(self):
        """Test list plugins performance."""
        plugins_tool = next(t for t in self.server.tools if t.name == "list_plugins")
        
        # Measure performance
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        result = plugins_tool.call({})
        
        end_time = time.time()
        end_memory = self.get_memory_usage()
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        assert result["success"] is True
        assert execution_time < 0.1  # Should complete in under 0.1 seconds
        assert memory_used < 5  # Should use less than 5MB additional memory

    def test_memory_cleanup(self):
        """Test that memory is properly cleaned up after operations."""
        # Create test file
        test_file = Path(self.temp_dir) / "cleanup_test.txt"
        test_file.write_text("Memory cleanup test content " * 1000)

        convert_tool = next(t for t in self.server.tools if t.name == "convert_file")
        
        # Get initial memory usage
        initial_memory = self.get_memory_usage()
        
        # Perform multiple conversions
        for i in range(5):
            result = convert_tool.call({
                "input_path": str(test_file),
                "output_format": "markdown"
            })
            assert result["success"] is True
        
        # Force garbage collection
        import gc
        gc.collect()
        
        # Check final memory usage
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory should not increase significantly after cleanup
        assert memory_increase < 50  # Should not increase by more than 50MB

    def test_response_time_consistency(self):
        """Test that response times are consistent."""
        # Create test file
        test_file = Path(self.temp_dir) / "consistency_test.txt"
        test_file.write_text("Response time consistency test content")

        convert_tool = next(t for t in self.server.tools if t.name == "convert_file")
        
        # Perform multiple conversions and measure times
        times = []
        for _ in range(10):
            start_time = time.time()
            result = convert_tool.call({
                "input_path": str(test_file),
                "output_format": "markdown"
            })
            end_time = time.time()
            
            assert result["success"] is True
            times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        # Response times should be consistent
        assert max_time - min_time < 0.5  # Variation should be less than 0.5 seconds
        assert avg_time < 1.0  # Average should be under 1 second
