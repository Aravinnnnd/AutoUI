"""Spawn the MCP server as a subprocess and send a JSON-RPC `call_tool` request.

This test helps validate the `StdioServerTransport` implementation.
"""
import sys
import subprocess
import json
from time import time

ROOT = r"C:\Users\Hp\OneDrive\Desktop\Auto Ui\design-mate-mcp"

def main():
    cmd = [sys.executable, "-u", "-c", (
        "import sys; sys.path.insert(0, r'" + ROOT + "'); import asyncio, mcp_py.index as idx; asyncio.run(idx.main())"
    )]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give server a moment to start
    time_start = time()
    out = b""
    while time() - time_start < 2:
        line = proc.stdout.readline()
        if not line:
            break
        out += line
        if b"ready" in line:
            break

    # Send request
    req = {"id": "1", "method": "call_tool", "params": {"tool": "list_icons", "args": {}}}
    proc.stdin.write((json.dumps(req) + "\n").encode("utf-8"))
    proc.stdin.flush()

    # Read response
    resp_line = proc.stdout.readline()
    if resp_line:
        try:
            resp = json.loads(resp_line.decode("utf-8"))
            print("Response:", json.dumps(resp, indent=2)[:1000])
        except Exception as e:
            print("Failed to parse response:", resp_line, e)
    else:
        print("No response received. stderr:")
        print(proc.stderr.read().decode("utf-8"))

    # Close stdin to let server exit
    proc.stdin.close()
    proc.wait(timeout=5)


if __name__ == "__main__":
    main()
