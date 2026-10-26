"""调用已配置的本地 Penpot MCP，用于可复查的初始化与验证。"""
import argparse
import json
import subprocess
from pathlib import Path

WORKSPACE = Path("D:/workspace_empty/ai-dev-process")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool")
    parser.add_argument("--arguments-file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    process = subprocess.Popen(["python", str(WORKSPACE / "scripts/penpot_mcp.py")], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, text=True, encoding="utf-8")
    def send(request):
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        if "id" in request:
            return json.loads(process.stdout.readline())
    try:
        initialized = send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "local-platform-setup", "version": "1"}}})
        if "error" in initialized:
            raise RuntimeError(initialized["error"])
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        if args.tool != "list":
            arguments = json.loads(args.arguments_file.read_text(encoding="utf-8-sig")) if args.arguments_file else {}
            request.update(method="tools/call", params={"name": args.tool, "arguments": arguments})
        response = send(request)
        if args.output:
            args.output.write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.tool == "list":
            print(json.dumps(response, ensure_ascii=False, indent=2))
        else:
            result = response.get("result", {})
            for content in result.get("content", []):
                if content.get("type") == "text":
                    print(content["text"])
            if "error" in response or result.get("isError"):
                raise SystemExit(1)
    finally:
        process.terminate()


if __name__ == "__main__":
    main()
