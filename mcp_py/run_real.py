"""Attempt a live run against a tldraw canvas via WebSocket.

This script registers the real tools with a `CanvasBridge` and then
calls `batch_get` and `get_screenshot` to exercise live behavior. If the
canvas isn't running at `ws://localhost:4000` it will print the error.
"""
import asyncio
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

    server = McpServer(name="designmate-mcp", version="1.0.0")
    register_catalog(server)
    register_batch_get(server, bridge)
    register_batch_design(server, bridge)
    register_screenshot(server, bridge)
    register_canvas_ops(server, bridge)

    async def _with_retries(func, *args, attempts=4, base_delay=0.5, **kwargs):
        last_exc = None
        for i in range(attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                delay = base_delay * (2 ** i)
                print(f"Attempt {i+1}/{attempts} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
        raise last_exc

    try:
        print("Attempting live batch_get (this will connect to the canvas)...")
        try:
            res = await _with_retries(server.call_tool, "batch_get", {})
            print("batch_get result:", res["content"][0]["text"][:400])
        except Exception as e:
            print("batch_get error after retries:", e)

        print("Attempting live get_screenshot (this may be slow)...")
        try:
            res = await _with_retries(server.call_tool, "get_screenshot", {})
            types = [c.get("type") for c in res.get("content", [])]
            print("get_screenshot returned content types:", types)
        except Exception as e:
            print("get_screenshot error after retries:", e)
    finally:
        # Ensure bridge is cleanly disconnected to stop recv loop tasks
        try:
            await bridge.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())
