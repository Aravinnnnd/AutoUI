import asyncio

from mcp_py.server import McpServer
from mcp_py.tools.catalog import register_catalog
from mcp_py.tools.batch_get import register_batch_get
from mcp_py.tools.batch_design import register_batch_design
from mcp_py.tools.screenshot import register_screenshot
from mcp_py.tools.canvas_ops import register_canvas_ops


class DummyBridge:
    async def get_snapshot(self):
        return {
            "shapes": [
                {
                    "id": "s1",
                    "type": "pen-text",
                    "y": 10,
                    "props": {"content": "Navbar", "fontSize": 11, "fill": "#888888"},
                }
            ]
        }

    async def send_batch(self, operations, clearFirst=False):
        return {
            "results": [
                {"op": "create", "id": "id1", "ref": (operations[0].get("ref") if operations else None), "shapeCount": 1}
            ],
            "refMap": {},
        }

    async def get_screenshot(self, opts=None):
        return {"image": "data:image/png;base64,", "width": 100, "height": 100, "mode": (opts.get("mode") if opts else "full")}

    async def clear(self):
        return None

    async def zoom_to_fit(self):
        return None


def _make_server(bridge=None):
    server = McpServer(name="pytest-smoke", version="0.0.0")
    register_catalog(server)
    if bridge is None:
        bridge = DummyBridge()
    register_batch_get(server, bridge)
    register_batch_design(server, bridge)
    register_screenshot(server, bridge)
    register_canvas_ops(server, bridge)
    return server


def test_list_icons_and_components():
    server = _make_server()
    res = asyncio.run(server.call_tool("list_icons", {}))
    assert isinstance(res, dict) and "content" in res
    assert isinstance(res["content"], list) and res["content"]
    assert res["content"][0].get("text")

    res2 = asyncio.run(server.call_tool("list_components", {}))
    assert isinstance(res2, dict) and "content" in res2
    assert isinstance(res2["content"], list) and res2["content"]
    assert res2["content"][0].get("text")


def test_batch_and_screenshot_and_canvas_ops():
    server = _make_server()

    res3 = asyncio.run(server.call_tool("batch_get", {"ids": ["s1"]}))
    assert isinstance(res3, dict) and "content" in res3

    res4 = asyncio.run(
        server.call_tool(
            "batch_design",
            {"operations": [{"op": "create", "type": "pen-frame", "x": 0, "y": 0, "props": {}}]},
        )
    )
    assert isinstance(res4, dict) and "content" in res4

    res5 = asyncio.run(server.call_tool("get_screenshot", {}))
    assert isinstance(res5, dict) and "content" in res5
    types = [c.get("type") for c in res5["content"]]
    assert any(t in ("image", "text") for t in types)

    res6 = asyncio.run(server.call_tool("clear_canvas", {}))
    assert isinstance(res6, dict) and "content" in res6

    res7 = asyncio.run(server.call_tool("zoom_to_fit", {}))
    assert isinstance(res7, dict) and "content" in res7
