"""Simple CLI for the MCP Python port.

Commands:
- `start` : run the MCP server (stdio transport)
- `run-real` : run the live runner (connects to canvas)
- `save-screenshot` : save a screenshot to `screenshot.png`
- `smoke` : run the internal smoke test
"""
import argparse
import asyncio
import sys
from pathlib import Path


def run_server():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from mcp_py import index

    asyncio.run(index.main())


def run_real():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from mcp_py import run_real

    asyncio.run(run_real.main())


def save_screenshot():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from mcp_py import save_screenshot

    asyncio.run(save_screenshot.main())


def smoke():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from mcp_py import test_smoke

    asyncio.run(test_smoke.main())


def main(argv=None):
    p = argparse.ArgumentParser(prog="mcp_py")
    p.add_argument("command", choices=["start", "run-real", "save-screenshot", "smoke"])
    args = p.parse_args(argv)

    if args.command == "start":
        run_server()
    elif args.command == "run-real":
        run_real()
    elif args.command == "save-screenshot":
        save_screenshot()
    elif args.command == "smoke":
        smoke()


if __name__ == "__main__":
    main()
