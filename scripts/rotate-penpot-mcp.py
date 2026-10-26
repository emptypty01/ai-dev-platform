"""轮换 Penpot MCP 密钥并清除本次过程日志中的旧值。"""
import json
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent.parent
token_path = root / "secrets/penpot-mcp-token"
old = token_path.read_text().strip()
state = json.loads((root / "secrets/penpot-browser-state.json").read_text())
cookie = "; ".join(item["name"] + "=" + item["value"] for item in state["cookies"])
request = urllib.request.Request("http://localhost:9001/api/rpc/command/create-access-token",
    data=json.dumps({"name": "Codex 本地设计协作", "type": "mcp"}).encode(),
    headers={"Content-Type": "application/json", "Accept": "application/json", "Cookie": cookie})
with urllib.request.urlopen(request) as response:
    token = json.load(response)["token"]
token_path.write_text(token, encoding="utf-8")
logs = Path("D:/plan&exec&test/20261024-AI研发流程本地平台/log")
touched = 0
for file in logs.rglob("*"):
    if not file.is_file() or file.suffix not in {".log", ".yml", ".yaml", ".json", ".md"}:
        continue
    content = file.read_text(encoding="utf-8", errors="replace")
    if old in content:
        file.write_text(content.replace(old, "[REVOKED-AND-REDACTED]"), encoding="utf-8")
        touched += 1
print(f"MCP token rotated; previous token invalidated; redacted files: {touched}")
