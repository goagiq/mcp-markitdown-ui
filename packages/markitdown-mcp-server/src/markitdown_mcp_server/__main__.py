"""Main entry point for the MarkItDown MCP Server."""

import asyncio
import logging
import sys

from .server import MarkItDownMCPServer


def main() -> None:
    """Run the MarkItDown MCP Server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    server = MarkItDownMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
