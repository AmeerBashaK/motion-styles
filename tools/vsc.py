"""Tiny client for the local VS Code MCP bridge (http://127.0.0.1:3712/mcp).

Usage:
  python vsc.py info
  python vsc.py push <target-file> <source-file>   # write source content into target via VS Code, then save
  python vsc.py diag [file]
  python vsc.py open <file> [line]
"""
import json, os, sys, urllib.request

URL = "http://127.0.0.1:3712/mcp"
_id = 0


def call(method, params=None):
    global _id
    _id += 1
    body = json.dumps({"jsonrpc": "2.0", "id": _id, "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(URL, body, {"Content-Type": "application/json",
                                             "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=30) as r:
        msg = json.loads(r.read().decode())
    if "error" in msg:
        raise RuntimeError(msg["error"])
    return msg["result"]


def tool(name, **args):
    res = call("tools/call", {"name": name, "arguments": args})
    text = "".join(c.get("text", "") for c in res.get("content", []))
    if res.get("isError"):
        raise RuntimeError(f"{name}: {text}")
    return text


def push(target, source):
    target = os.path.abspath(target)
    with open(source, encoding="utf-8") as f:
        content = f.read()
    if not os.path.exists(target):  # the bridge edits documents; give it one to open
        os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, "w", encoding="utf-8").close()
    tool("open_file", path=target)
    tool("execute_command", command="editor.action.selectAll")
    tool("replace_text", path=target, text=content, save=True)
    print(f"pushed {os.path.basename(target)} ({len(content)} chars) via VS Code")


if __name__ == "__main__":
    call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                        "clientInfo": {"name": "claude-vsc", "version": "1"}})
    cmd = sys.argv[1]
    if cmd == "info":
        print(tool("get_workspace_info"))
    elif cmd == "push":
        push(sys.argv[2], sys.argv[3])
    elif cmd == "diag":
        print(tool("get_diagnostics", **({"path": sys.argv[2]} if len(sys.argv) > 2 else {})))
    elif cmd == "open":
        print(tool("open_file", path=sys.argv[2], **({"line": int(sys.argv[3])} if len(sys.argv) > 3 else {})))
