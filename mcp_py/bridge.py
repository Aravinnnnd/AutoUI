"""CanvasBridge — async WebSocket bridge translated from the TS implementation.

Implements request/response semantics via requestId and asyncio Futures.
Uses the `websockets` library as the client.
"""
from __future__ import annotations
import asyncio
import json
from typing import Any, Callable, Dict, Optional
import websockets

from .constants import (
    DEFAULT_WS_URL,
    BRIDGE_CONNECT_TIMEOUT_MS,
    BRIDGE_REQUEST_TIMEOUT_MS,
    LOG_TRUNCATION_LENGTH,
)


class CanvasBridge:
    def __init__(self, url: str = DEFAULT_WS_URL) -> None:
        self.url = url
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._handlers: Dict[str, asyncio.Future] = {}
        self._request_id = 0
        self._connected = False
        self._recv_task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        if self._connected:
            return

        try:
            self._ws = await asyncio.wait_for(websockets.connect(self.url), BRIDGE_CONNECT_TIMEOUT_MS / 1000)
            self._connected = True
            self._recv_task = asyncio.create_task(self._recv_loop())
        except asyncio.TimeoutError:
            raise RuntimeError(f"Connection timeout: Could not connect to canvas at {self.url}. Make sure the canvas is running")
        except Exception as exc:
            msg = str(exc)
            if "Connection refused" in msg or "ECONNREFUSED" in msg:
                raise RuntimeError(f"Cannot connect to canvas at {self.url}. Make sure the canvas is running")
            raise

    async def _recv_loop(self) -> None:
        assert self._ws is not None
        try:
            async for raw in self._ws:
                try:
                    msg = json.loads(raw)
                except Exception:
                    print("[bridge] failed to parse canvas response as JSON")
                    continue

                if not isinstance(msg, dict):
                    print("[bridge] dropped non-object response from canvas")
                    continue

                request_id = msg.get("requestId")
                if not isinstance(request_id, str):
                    print("[bridge] dropped response without valid requestId:", str(msg)[:LOG_TRUNCATION_LENGTH])
                    continue

                fut = self._handlers.pop(request_id, None)
                if fut:
                    if msg.get("error"):
                        fut.set_exception(RuntimeError(msg.get("error")))
                    else:
                        fut.set_result(msg)
                else:
                    print(f"[bridge] no handler for requestId: {request_id} (stale or unexpected)")
        finally:
            self._connected = False

    async def send(self, command: Dict[str, Any]) -> Any:
        if not self._connected or not self._ws:
            await self.connect()

        self._request_id += 1
        request_id = str(self._request_id)

        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        self._handlers[request_id] = fut

        async def _send_payload() -> None:
            assert self._ws is not None
            payload = {**command, "requestId": request_id}
            await self._ws.send(json.dumps(payload))

        await _send_payload()

        def _on_timeout() -> None:
            if not fut.done():
                fut.set_exception(RuntimeError(f"Request timeout: Widget did not respond within {BRIDGE_REQUEST_TIMEOUT_MS/1000}s for command '{command.get('type')}'"))
                self._handlers.pop(request_id, None)

        loop.call_later(BRIDGE_REQUEST_TIMEOUT_MS / 1000, _on_timeout)
        result = await fut
        return result

    async def send_batch(self, operations: list, clear_first: bool = False) -> Dict[str, Any]:
        return await self.send({"type": "batch", "operations": operations, "clearFirst": clear_first})

    async def get_screenshot(self, opts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"type": "screenshot"}
        if opts:
            payload.update(opts)
        return await self.send(payload)

    async def create_shape(self, shape: Dict[str, Any]) -> Dict[str, Any]:
        return await self.send({"type": "create", "shape": shape})

    async def update_shape(self, id: str, props: Dict[str, Any]) -> None:
        await self.send({"type": "update", "id": id, "props": props})

    async def delete_shapes(self, ids: list) -> None:
        await self.send({"type": "delete", "ids": ids})

    async def get_snapshot(self) -> Dict[str, Any]:
        return await self.send({"type": "snapshot"})

    async def clear(self) -> None:
        await self.send({"type": "clear"})

    async def zoom_to_fit(self) -> None:
        await self.send({"type": "zoom_to_fit"})

    async def disconnect(self) -> None:
        if self._ws:
            await self._ws.close()
            self._ws = None
            self._connected = False
        if self._recv_task:
            self._recv_task.cancel()
