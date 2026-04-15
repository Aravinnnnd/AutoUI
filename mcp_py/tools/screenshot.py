"""get_screenshot tool — capture PNG screenshots of the canvas."""
from typing import Any, Dict


def register_screenshot(server, bridge) -> None:
    async def handler(args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if args.get("mode") == "section" and not args.get("sectionName"):
                return {"content": [{"type": "text", "text": 'Error: mode "section" requires sectionName to be provided. Pass sectionName or omit mode.'}], "isError": True}

            opts: Dict[str, Any] = {}
            if args.get("sectionName"):
                opts["sectionName"] = args.get("sectionName")
            if args.get("shapeIds"):
                opts["shapeIds"] = args.get("shapeIds")
            if args.get("mode"):
                opts["mode"] = args.get("mode")

            result = await bridge.get_screenshot(opts if opts else None)

            image_data = result.get("image", "")
            base64_data = image_data.replace("data:image/png;base64,", "")
            screenshot_mode = result.get("mode") or ("section" if args.get("sectionName") else "full")

            inspection_note = ""
            if screenshot_mode == "section":
                inspection_note = f"\n\nThis is a SECTION screenshot of \"{args.get('sectionName') or 'selected shapes'}\" with ~25% surrounding context included.\nCarefully inspect for: overlapping elements, text overflow, inconsistent spacing, alignment issues, and missing padding.\nIf you see ANY visual problems, fix them with batch_design before proceeding."
            else:
                inspection_note = "\n\nThis is a FULL CANVAS screenshot.\nReview the overall composition: section spacing, visual hierarchy, alignment consistency, and any overlapping elements."

            return {"content": [
                {"type": "image", "data": base64_data, "mimeType": "image/png"},
                {"type": "text", "text": f"Screenshot captured ({result.get('width')}×{result.get('height')}px).{inspection_note}"},
            ]}
        except Exception as err:
            message = str(err)
            is_conn = any(token in message.lower() for token in ("connect", "timeout", "econnrefused", "socket", "websocket"))
            suffix = "\n\nMake sure the canvas is running (cd canvas && bun run dev)." if is_conn else ""
            return {"content": [{"type": "text", "text": f"Screenshot error: {message}{suffix}"}], "isError": True}

    server.register_tool("get_screenshot", {"description": "Capture a PNG screenshot of the canvas.", "input_schema": None}, handler)
