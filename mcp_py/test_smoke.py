import asyncio
from mcp_py.server import McpServer
from mcp_py.tools.catalog import register_catalog
from mcp_py.tools.batch_get import register_batch_get
from mcp_py.tools.batch_design import register_batch_design
from mcp_py.tools.screenshot import register_screenshot
from mcp_py.tools.canvas_ops import register_canvas_ops


class DummyBridge:
    async def get_snapshot(self):
        return {"shapes": [{"id": "s1", "type": "pen-text", "y": 10, "props": {"content": "Navbar", "fontSize": 11, "fill": "#888888"}}]}

    async def send_batch(self, operations, clearFirst=False):
        return {"results": [{"op": "create", "id": "id1", "ref": (operations[0].get("ref") if operations else None), "shapeCount": 1}], "refMap": {}}

    async def get_screenshot(self, opts=None):
        return {"image": "data:image/png;base64,", "width": 100, "height": 100, "mode": (opts.get("mode") if opts else "full")}

    async def clear(self):
        return None

    async def zoom_to_fit(self):
        return None


async def main():
    server = McpServer(name="test", version="0.0.0")
    register_catalog(server)
    bridge = DummyBridge()
    register_batch_get(server, bridge)
    register_batch_design(server, bridge)
    register_screenshot(server, bridge)
    register_canvas_ops(server, bridge)

    res = await server.call_tool("list_icons", {})
    print("list_icons (truncated):\n", res["content"][0]["text"][:300])

    res2 = await server.call_tool("list_components", {})
    print("list_components (truncated):\n", res2["content"][0]["text"][:300])

    res3 = await server.call_tool("batch_get", {"ids": ["s1"]})
    print("batch_get:\n", res3["content"][0]["text"])

    res4 = await server.call_tool("batch_design", {"operations": [{"op": "create", "type": "pen-frame", "x": 0, "y": 0, "props": {}}]})
    print("batch_design (truncated):\n", res4["content"][0]["text"][:300])

    res5 = await server.call_tool("get_screenshot", {})
    print("get_screenshot content types:", [c.get("type") for c in res5["content"]])

    res6 = await server.call_tool("clear_canvas", {})
    print("clear_canvas:\n", res6["content"][0]["text"])

    res7 = await server.call_tool("zoom_to_fit", {})
    print("zoom_to_fit:\n", res7["content"][0]["text"])


if __name__ == "__main__":
    asyncio.run(main())
