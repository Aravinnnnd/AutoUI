"""Canvas operation tools — clear_canvas and zoom_to_fit."""
from typing import Any, Dict


def register_canvas_ops(server, bridge) -> None:
    async def clear_handler(_: Dict[str, Any]) -> Dict[str, Any]:
        try:
            await bridge.clear()
            return {"content": [{"type": "text", "text": "Canvas cleared — ready for new design."}]}
        except Exception as err:
            return {"content": [{"type": "text", "text": f"Error: {err}"}], "isError": True}

    server.register_tool("clear_canvas", {"description": "Remove all shapes from the canvas. Use before starting a completely new design.", "input_schema": None}, clear_handler)

    async def zoom_handler(_: Dict[str, Any]) -> Dict[str, Any]:
        try:
            await bridge.zoom_to_fit()
            return {"content": [{"type": "text", "text": "Zoomed to fit all shapes."}]}
        except Exception as err:
            return {"content": [{"type": "text", "text": f"Error: {err}"}], "isError": True}

    server.register_tool("zoom_to_fit", {"description": "Zoom the canvas viewport to fit all shapes.", "input_schema": None}, zoom_handler)
