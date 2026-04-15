# design-mate-mcp (Python port)

This repository contains a TypeScript MCP server and a parallel Python port under `mcp_py/` for development and testing.

Quick start (Windows cmd.exe):

1. Start the canvas dev server (in a separate terminal):

```cmd
cd "C:\Users\Hp\OneDrive\Desktop\Auto Ui\design-mate-mcp\canvas"
npm install
npm run dev
```

2. Run the Python MCP server (stdio transport):

```cmd
cd "C:\Users\Hp\OneDrive\Desktop\Auto Ui\design-mate-mcp"
python -m mcp_py.cli start
```

3. Use the CLI helper commands:

- Run live runner (connects to canvas): `python -m mcp_py.cli run-real`
- Save a screenshot to `screenshot.png`: `python -m mcp_py.cli save-screenshot`
- Run internal smoke test: `python -m mcp_py.cli smoke`

Dependencies:

- Python packages: see `mcp_py/requirements.txt` (install with `pip install -r mcp_py/requirements.txt`).
- Node packages: run `npm install` in `canvas/` before `npm run dev`.

Notes:

- `StdioServerTransport` supports a minimal JSON-RPC `call_tool` method over newline-delimited JSON on stdin/stdout.
- This Python port is intended for development and testing; it is not a drop-in replacement for the full MCP SDK.
