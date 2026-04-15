"""Save a live screenshot from the canvas to `screenshot.png`.

Usage: `python -m mcp_py.save_screenshot`
"""
import sys
import asyncio
import base64

sys.path.insert(0, r"C:\Users\Hp\OneDrive\Desktop\Auto Ui\design-mate-mcp")

from mcp_py.server import McpServer
from mcp_py.bridge import CanvasBridge
from mcp_py.tools.catalog import register_catalog
from mcp_py.tools.batch_get import register_batch_get
from mcp_py.tools.batch_design import register_batch_design
from mcp_py.tools.screenshot import register_screenshot
from mcp_py.tools.canvas_ops import register_canvas_ops


async def main():
    url = None
    bridge = CanvasBridge(url) if url else CanvasBridge()

    server = McpServer(name="save-screenshot", version="1.0.0")
    register_catalog(server)
    register_batch_get(server, bridge)
    register_batch_design(server, bridge)
    register_screenshot(server, bridge)
    register_canvas_ops(server, bridge)

    try:
        res = await server.call_tool("get_screenshot", {})
        for c in res.get("content", []):
            if c.get("type") == "image":
                b64 = c.get("data", "")
                if not b64:
                    print("Image data empty")
                    return
                img = base64.b64decode(b64)
                with open("screenshot.png", "wb") as f:
                    f.write(img)
                print("Saved screenshot.png")
                return
        print("No image found in response")
    finally:
        try:
            await bridge.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
"""Save a screenshot from the running canvas to `screenshot.png`.

Run as a module from the repo root:
  python -m mcp_py.save_screenshot
"""
import asyncio
import base64
import os

from .server import McpServer
from .bridge import CanvasBridge
from .tools.catalog import register_catalog
from .tools.batch_get import register_batch_get
from .tools.batch_design import register_batch_design
from .tools.screenshot import register_screenshot
from .tools.canvas_ops import register_canvas_ops


async def main():
    url = os.environ.get("TLDRAW_WS_URL")
    bridge = CanvasBridge(url) if url else CanvasBridge()

    server = McpServer(name="save-screenshot", version="1.0.0")
    register_catalog(server)
    register_batch_get(server, bridge)
    register_batch_design(server, bridge)
    register_screenshot(server, bridge)
    register_canvas_ops(server, bridge)

    try:
        res = await server.call_tool("get_screenshot", {})
        for c in res.get("content", []):
            if c.get("type") == "image":
                b64 = c.get("data", "")
                if not b64:
                    print("Image data empty")
                    return
                img = base64.b64decode(b64)
                out = os.path.join(os.getcwd(), "screenshot.png")
                with open(out, "wb") as f:
                    f.write(img)
                print(f"Saved {out}")
                return
        print("No image found in response")
    finally:
        try:
            await bridge.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
