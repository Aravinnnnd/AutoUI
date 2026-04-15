"""batch_get tool — read shapes from the canvas with optional filtering."""
from typing import Any, Dict
import json
from ..constants import SECTION_MARKER_FONT_SIZE, SECTION_MARKER_COLOR, SECTION_BOUNDARY_GAP, SECTION_Y_TOLERANCE


def register_batch_get(server, bridge) -> None:
    async def handler(args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            state = await bridge.get_snapshot()
            shapes = state.get("shapes", []) if isinstance(state, dict) else []

            if args.get("ids"):
                s = set(args["ids"])
                shapes = [x for x in shapes if x.get("id") in s]

            if args.get("types"):
                s = set(args["types"])
                shapes = [x for x in shapes if x.get("type") in s]

            if args.get("name"):
                name = args.get("name")
                def content_of(s):
                    return (s.get("props") or {}).get("content") or s.get("content")

                name_shape = next((s for s in shapes if s.get("type") == "pen-text" and content_of(s) == name and (s.get("props") or {}).get("fontSize") == SECTION_MARKER_FONT_SIZE), None)
                if name_shape:
                    name_y = name_shape.get("y")
                    all_name_shapes = sorted([
                        s for s in shapes if s.get("type") == "pen-text" and (s.get("props") or {}).get("fontSize") == SECTION_MARKER_FONT_SIZE and (s.get("props") or {}).get("fill") == SECTION_MARKER_COLOR
                    ], key=lambda x: x.get("y", 0))
                    idx = next((i for i, s in enumerate(all_name_shapes) if s.get("id") == name_shape.get("id")), None)
                    next_name = all_name_shapes[idx + 1] if idx is not None and idx + 1 < len(all_name_shapes) else None
                    section_end = next_name.get("y") - SECTION_BOUNDARY_GAP if next_name else float("inf")
                    shapes = [s for s in shapes if s.get("y", 0) >= (name_y - SECTION_Y_TOLERANCE) and s.get("y", 0) < section_end]

            return {"content": [{"type": "text", "text": json.dumps({"count": len(shapes), "shapes": shapes}, indent=2)}]}
        except Exception as err:
            return {"content": [{"type": "text", "text": f"Error: {err}"}], "isError": True}

    server.register_tool(
        "batch_get",
        {"description": "Read shapes from the canvas with optional filtering.", "input_schema": None},
        handler,
    )
