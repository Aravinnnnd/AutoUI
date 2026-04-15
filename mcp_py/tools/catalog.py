"""Catalog tools translated from `mcp/tools/catalog.ts`.

Provides `register_catalog(server)` which registers `get_design_guide`,
`list_components`, and `list_icons` handlers on the `McpServer` shim.
"""
from typing import Any, Dict
from ..data.design_guides_loader import DESIGN_GUIDES
from ..data.component_catalog import COMPONENT_CATALOG
from ..data.icon_catalog import ICON_CATALOG


def _join_keys(d: Dict[str, Any]) -> str:
    return ", ".join(d.keys())


def register_catalog(server) -> None:
    # get_design_guide
    async def get_design_guide(args: Dict[str, Any]) -> Dict[str, Any]:
        topic = args.get("topic")
        guide = DESIGN_GUIDES.get(topic)
        if not guide:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown topic: {topic}. Available: {', '.join(DESIGN_GUIDES.keys())}",
                    }
                ],
                "isError": True,
            }
        return {"content": [{"type": "text", "text": guide}]}

    server.register_tool(
        "get_design_guide",
        {
            "description": "Get comprehensive design methodology and patterns for a specific type of design.",
            "input_schema": None,
        },
        get_design_guide,
    )

    # list_components
    async def list_components(_: Dict[str, Any]) -> Dict[str, Any]:
        grouped = {}
        for c in COMPONENT_CATALOG:
            grouped.setdefault(c["category"], []).append(c)

        text = "# Available Components\n\n"
        for category, components in grouped.items():
            text += f"## {category}\n"
            for c in components:
                text += f"- **{c['name']}** — {c['description']}\n  Overrides: {c['overrides']}\n"
            text += "\n"

        text += (
            """## Usage Example

```
{
  "children": [
    { "type": "ref", "ref": "Button/Primary", "overrides": { "label": "Get Started" } },
    { "type": "ref", "ref": "Input", "overrides": { "label": "Email", "placeholder": "you@example.com" }, "width": "fill" },
    { "type": "ref", "ref": "Badge", "overrides": { "text": "New", "variant": "success" } }
  ]
}
```

"""
        )

        return {"content": [{"type": "text", "text": text}]}

    server.register_tool(
        "list_components",
        {"description": "List all available reusable UI components.", "input_schema": None},
        list_components,
    )

    # list_icons
    async def list_icons(_: Dict[str, Any]) -> Dict[str, Any]:
        text = "# Available Icons (Lucide)\n\n"
        total = 0
        for category, icons in ICON_CATALOG.items():
            text += f"## {category}\n"
            text += ", ".join(icons) + "\n\n"
            total += len(icons)
        text += f"**Total: {total} icons**\n\n"
        text += (
            """## Usage
```
{ "type": "icon", "iconName": "search", "width": 20, "iconColor": "#6b7280" }
{ "type": "icon", "iconName": "arrow-right", "width": 16, "iconColor": "#ffffff" }
{ "type": "icon", "iconName": "star", "width": 24, "iconColor": "#f59e0b" }
```

"""
        )
        return {"content": [{"type": "text", "text": text}]}

    server.register_tool(
        "list_icons",
        {"description": "List all available icons grouped by category.", "input_schema": None},
        list_icons,
    )
