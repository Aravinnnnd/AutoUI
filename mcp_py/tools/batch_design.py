"""batch_design tool — create/update/delete shapes on the canvas."""
from typing import Any, Dict
from textwrap import indent


TOOL_DESCRIPTION = """Design UI components on a canvas using a CSS-flexbox-like component tree.

MANDATORY WORKFLOW — YOU MUST FOLLOW THESE STEPS:
1. Call get_design_guide FIRST with the relevant topic to get design methodology
2. Build ONE section at a time (e.g., Navbar, then Hero, then Features)
3. AFTER EVERY batch_design call, you MUST call get_screenshot to verify the result
4. Carefully inspect the screenshot for overlapping, text overflow, spacing, and alignment issues
5. Fix ALL visual issues before proceeding to the next section
6. After all sections are complete, call get_screenshot with mode: "full" for final verification

DO NOT proceed to the next section without first verifying the current section via screenshot.
DO NOT skip screenshot verification — visual bugs compound and are harder to fix later.

Response: Returns created shape IDs, computed bounding boxes, and text overflow warnings.
"""


def format_batch_summary(result: Dict[str, Any]) -> str:
    results = result.get("results", [])
    lines = []
    for r in results:
        if r.get("error"):
            lines.append(f"[FAIL] {r.get('op')}: {r.get('error')}")
            continue
        op = r.get("op")
        if op == "create":
            line = f"[OK] create{(' [' + r.get('ref') + ']') if r.get('ref') else ''}: {r.get('id')} ({r.get('shapeCount') or len(r.get('ids', [])) or 1} shapes)"
            if r.get("computedBounds"):
                line += "\n   Top-level bounds: " + str(r.get("computedBounds")[:3])
            lines.append(line)
            continue
        if op == "update":
            lines.append(f"[OK] update: {r.get('id')}")
            continue
        if op == "delete":
            lines.append(f"[OK] deleted {r.get('deleted')} shape(s)")
            continue
        lines.append(f"[OK] {op}")

    summary = "\n".join(lines)

    warning_text = ""
    if result.get("warnings"):
        warning_lines = [f"  • [{w.get('section', '?')}] {w.get('message')}" for w in result.get("warnings", [])]
        warning_text = "\n\nWARNINGS:\n" + "\n".join(warning_lines) + "\n\nFix these issues before proceeding to the next section."

    bounds_text = ""
    if result.get("computedBounds"):
        bounds = result.get("computedBounds")
        sections = list({b.get("sectionName") for b in bounds if b.get("sectionName")})
        if sections:
            bounds_text = "\n\nComputed sections: " + ", ".join(sections)

    first_ref = (results[0].get("ref") if results and results[0] else "section_name")
    return f"Batch complete ({len(results)} ops):\n{summary}\n\nRefs: {result.get('refMap')}{warning_text}{bounds_text}\n\nMANDATORY: You MUST now call get_screenshot(\"{first_ref}\") to verify this section. DO NOT proceed to the next section until you have visually confirmed this one looks correct. Check for overlapping elements, text overflow, spacing issues, and alignment problems."


def register_batch_design(server, bridge) -> None:
    async def handler(args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = await bridge.send_batch(args.get("operations", []), args.get("clearFirst", False))
            return {"content": [{"type": "text", "text": format_batch_summary(result)}]}
        except Exception as err:
            return {"content": [{"type": "text", "text": f"Error: {err}"}], "isError": True}

    server.register_tool("batch_design", {"description": TOOL_DESCRIPTION, "input_schema": None}, handler)
