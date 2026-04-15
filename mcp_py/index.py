"""Entrypoint for the Python MCP port — mirrors `mcp/index.ts` behavior.

Instantiates the bridge and registers available tools. This module is
intended for interactive testing and development of the Python port.
"""
import asyncio
import os

from .server import McpServer, StdioServerTransport
from .bridge import CanvasBridge

# Tool registrations
from .tools.catalog import register_catalog
from .tools.batch_get import register_batch_get
from .tools.batch_design import register_batch_design
from .tools.screenshot import register_screenshot
from .tools.canvas_ops import register_canvas_ops

async def main() -> None:
    td_url = os.environ.get("TLDRAW_WS_URL")
    bridge = CanvasBridge(td_url) if td_url else CanvasBridge()

    server = McpServer(name="designmate-mcp", version="1.0.0")

    # Register tools
    register_catalog(server)
    register_batch_get(server, bridge)
    register_batch_design(server, bridge)
    register_screenshot(server, bridge)
    register_canvas_ops(server, bridge)

    # Start transport
    transport = StdioServerTransport()
    await server.connect(transport)
    print("designmate-mcp v1.0.0 — ready")
    # If transport runs a background task (e.g. stdio loop), keep running
    if hasattr(transport, "_task") and transport._task is not None:
        try:
            await transport._task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
