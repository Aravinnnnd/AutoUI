"""MCP constants translated from TypeScript.

This module mirrors the values from `mcp/constants.ts` so the rest of the
Python port can import the same configuration constants.
"""

# ─── Bridge / Network ────────────────────────────────────────────────────────

# Default WebSocket relay URL when TLDRAW_WS_URL env var is not set.
DEFAULT_WS_URL: str = "ws://localhost:4000"

# Max time to wait for initial WebSocket connection to canvas (ms).
BRIDGE_CONNECT_TIMEOUT_MS: int = 5000

# Max time to wait for a canvas response before timing out a request (ms).
# Set high because screenshot/image export can be slow.
BRIDGE_REQUEST_TIMEOUT_MS: int = 30000

# Max characters of a logged response body (truncation for safety).
LOG_TRUNCATION_LENGTH: int = 100

# ─── Section Detection ───────────────────────────────────────────────────────
# These values identify "section label" text shapes on the canvas.
# The layout engine creates section markers with a specific fontSize + fill.

# Font size used by section name label shapes.
SECTION_MARKER_FONT_SIZE: int = 11

# Fill color of section name label shapes.
SECTION_MARKER_COLOR: str = "#888888"

# Vertical gap subtracted from the next section marker's Y to define section bounds.
SECTION_BOUNDARY_GAP: int = 10

# Small Y tolerance when filtering shapes that belong to a section.
SECTION_Y_TOLERANCE: int = 5
