"""Convert file tools for MarkItDown MCP server."""

import asyncio
import time
from typing import Any, Dict

from markitdown import MarkItDown

from .base import BaseTool


class ConvertFileTool(BaseTool):
    """Tool for converting a single file to Markdown."""

    def _get_description(self) -> str:
        return "Convert a single file to Markdown format"

    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to convert"
                },
                "file_url": {
                    "type": "string",
                    "description": "URL of the file to convert"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["markdown", "html", "plain"],
                    "default": "markdown",
                    "description": "Output format"
                },
                "options": {
                    "type": "object",
                    "properties": {
                        "use_docintel": {
                            "type": "boolean",
                            "default": False,
                            "description": "Use Document Intelligence"
                        },
                        "endpoint": {
                            "type": "string",
                            "description": "Document Intelligence endpoint"
                        },
                        "use_plugins": {
                            "type": "boolean",
                            "default": False,
                            "description": "Use third-party plugins"
                        }
                    }
                }
            },
            "required": ["file_path"] or ["file_url"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the file conversion."""
        self._validate_arguments(arguments)
        self._log_execution(arguments)

        start_time = time.time()
        
        try:
            # Initialize MarkItDown
            markitdown = MarkItDown()
            
            # Get file path or URL
            file_path = arguments.get("file_path")
            file_url = arguments.get("file_url")
            
            if not file_path and not file_url:
                raise ValueError("Either file_path or file_url must be provided")
            
            # Get options
            options = arguments.get("options", {})
            output_format = arguments.get("output_format", "markdown")
            
            # Convert the file
            if file_path:
                result = markitdown.convert_file(file_path)
            else:
                result = markitdown.convert_file(file_url)
            
            conversion_time = time.time() - start_time
            
            # Prepare response
            response = {
                "success": True,
                "content": result.content,
                "metadata": {
                    "original_format": result.metadata.get("format", "unknown"),
                    "file_size": result.metadata.get("file_size", 0),
                    "conversion_time": conversion_time
                }
            }
            
            self._log_result(response)
            return response
            
        except Exception as e:
            conversion_time = time.time() - start_time
            response = {
                "success": False,
                "error": str(e),
                "metadata": {
                    "conversion_time": conversion_time
                }
            }
            
            self._log_result(response)
            return response


class ConvertBatchTool(BaseTool):
    """Tool for converting multiple files to Markdown."""

    def _get_description(self) -> str:
        return "Convert multiple files to Markdown format"

    def _get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file"
                            },
                            "file_url": {
                                "type": "string",
                                "description": "URL of the file"
                            }
                        }
                    },
                    "description": "List of files to convert"
                },
                "batch_options": {
                    "type": "object",
                    "properties": {
                        "parallel": {
                            "type": "boolean",
                            "default": True,
                            "description": "Process files in parallel"
                        },
                        "max_workers": {
                            "type": "number",
                            "default": 4,
                            "description": "Maximum parallel workers"
                        }
                    }
                }
            },
            "required": ["files"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the batch conversion."""
        self._validate_arguments(arguments)
        self._log_execution(arguments)

        start_time = time.time()
        
        try:
            files = arguments.get("files", [])
            batch_options = arguments.get("batch_options", {})
            parallel = batch_options.get("parallel", True)
            max_workers = batch_options.get("max_workers", 4)
            
            if not files:
                raise ValueError("No files provided for conversion")
            
            # Initialize MarkItDown
            markitdown = MarkItDown()
            
            results = []
            successful = 0
            failed = 0
            
            if parallel:
                # Process files in parallel
                tasks = []
                for file_info in files:
                    task = self._convert_single_file(markitdown, file_info)
                    tasks.append(task)
                
                # Execute tasks with semaphore to limit concurrency
                semaphore = asyncio.Semaphore(max_workers)
                async def limited_task(task):
                    async with semaphore:
                        return await task
                
                limited_tasks = [limited_task(task) for task in tasks]
                file_results = await asyncio.gather(*limited_tasks, return_exceptions=True)
                
                for i, result in enumerate(file_results):
                    if isinstance(result, Exception):
                        results.append({
                            "file_path": files[i].get("file_path", files[i].get("file_url")),
                            "success": False,
                            "error": str(result)
                        })
                        failed += 1
                    else:
                        results.append(result)
                        if result["success"]:
                            successful += 1
                        else:
                            failed += 1
            else:
                # Process files sequentially
                for file_info in files:
                    result = await self._convert_single_file(markitdown, file_info)
                    results.append(result)
                    if result["success"]:
                        successful += 1
                    else:
                        failed += 1
            
            total_time = time.time() - start_time
            
            response = {
                "results": results,
                "summary": {
                    "total_files": len(files),
                    "successful": successful,
                    "failed": failed,
                    "total_time": total_time
                }
            }
            
            self._log_result(response)
            return response
            
        except Exception as e:
            total_time = time.time() - start_time
            response = {
                "results": [],
                "summary": {
                    "total_files": 0,
                    "successful": 0,
                    "failed": 0,
                    "total_time": total_time,
                    "error": str(e)
                }
            }
            
            self._log_result(response)
            return response

    async def _convert_single_file(self, markitdown: MarkItDown, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single file."""
        try:
            file_path = file_info.get("file_path")
            file_url = file_info.get("file_url")
            
            if not file_path and not file_url:
                return {
                    "file_path": file_path or file_url,
                    "success": False,
                    "error": "Either file_path or file_url must be provided"
                }
            
            if file_path:
                result = markitdown.convert_file(file_path)
            else:
                result = markitdown.convert_file(file_url)
            
            return {
                "file_path": file_path or file_url,
                "success": True,
                "content": result.content
            }
            
        except Exception as e:
            return {
                "file_path": file_info.get("file_path") or file_info.get("file_url"),
                "success": False,
                "error": str(e)
            }
