"""Minimal MCP server shim for the Python port.

Provides a tiny `McpServer` API compatible enough for the translated tools
to register handlers. This is not a full implementation of the Model Context
Protocol SDK — it's a lightweight scaffold to run and test translated tools.
"""
from typing import Any, Awaitable, Callable, Dict
import asyncio

ToolHandler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


class McpServer:
    def __init__(self, *, name: str, version: str):
        self.name = name
        self.version = version
        self._tools: Dict[str, Dict] = {}

    def register_tool(self, name: str, meta: Dict[str, Any], handler: ToolHandler) -> None:
        """Register a tool handler by name.

        meta may contain `description` and `input_schema` keys (optional).
        Handler must be an async function accepting args dict and returning a dict.
        """
        self._tools[name] = {"meta": meta, "handler": handler}

    async def connect(self, transport: Any) -> None:
        """Simulate connecting the server to a transport.

        If the transport exposes an async `connect(server)` method, call it.
        Otherwise this is a no-op placeholder so translated code can run.
        """
        if hasattr(transport, "connect"):
            maybe = transport.connect(self)
            if asyncio.iscoroutine(maybe):
                await maybe

    # Helper to call a registered tool (for testing)
    async def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        tool = self._tools.get(name)
        if not tool:
            raise KeyError(f"Tool not registered: {name}")
        handler: ToolHandler = tool["handler"]
        return await handler(args)


class StdioServerTransport:
    """Lightweight stub for the stdio transport.

    The real Node version wires stdin/stdout JSON-RPC. For this Python port we
    expose the same class so `index.py` can import and call connect() without
    requiring the full transport implementation immediately.
    """
    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def connect(self, server: McpServer) -> None:
        """Start an asyncio task that listens on stdin for JSON-RPC requests.

        Supported request shape (newline-delimited JSON):
          { "id": <id>, "method": "call_tool", "params": { "tool": <name>, "args": {...} } }

        Response written to stdout as JSON with the same `id`:
          { "id": <id>, "result": <tool result> }

        This is a minimal implementation intended for local development and
        testing. It runs until stdin is closed.
        """
        if self._running:
            return
        self._running = True
        loop = asyncio.get_running_loop()
        self._task = loop.create_task(self._run_stdio_loop(server))

    async def _run_stdio_loop(self, server: McpServer) -> None:
        import sys
        import json

        loop = asyncio.get_running_loop()

        def _readline_blocking() -> bytes:
            try:
                return sys.stdin.buffer.readline()
            except Exception:
                return b""

        while True:
            line = await loop.run_in_executor(None, _readline_blocking)
            if not line:
                break  # EOF
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line.decode("utf-8")) if isinstance(line, (bytes, bytearray)) else json.loads(line)
            except Exception as e:
                # write error response and continue
                err = {"id": None, "error": f"Invalid JSON: {e}"}
                try:
                    sys.stdout.write(json.dumps(err) + "\n")
                    sys.stdout.flush()
                except Exception:
                    pass
                continue

            # Handle simple JSON-RPC call_tool method
            req_id = msg.get("id")
            method = msg.get("method")
            params = msg.get("params") or {}

            if method == "call_tool":
                tool_name = params.get("tool")
                args = params.get("args") or {}
                try:
                    result = await server.call_tool(tool_name, args)
                    resp = {"id": req_id, "result": result}
                except Exception as e:
                    resp = {"id": req_id, "error": str(e)}
                try:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
                except Exception:
                    pass
            else:
                # unknown method
                resp = {"id": req_id, "error": f"Unknown method: {method}"}
                try:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
                except Exception:
                    pass

        self._running = False

    async def close(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass
