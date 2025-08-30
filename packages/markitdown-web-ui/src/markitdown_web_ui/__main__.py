"""Main entry point for the MarkItDown Web UI."""

import uvicorn
from .app import create_app


def main() -> None:
    """Run the MarkItDown Web UI."""
    app = create_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8100,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
