"""创建订单演示设计文件与 MCP Token；不向日志输出 Token。"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
state = json.loads((ROOT / "secrets/penpot-browser-state.json").read_text())
cookie = "; ".join(item["name"] + "=" + item["value"] for item in state["cookies"])


def rpc(name, body=None):
    request = urllib.request.Request("http://localhost:9001/api/rpc/command/" + name,
        data=json.dumps(body or {}).encode(), headers={"Content-Type": "application/json", "Accept": "application/json", "Cookie": cookie})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
            return json.loads(data) if data else None
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"{name}: {error.code}: {error.read().decode()[:1000]}") from None


def main():
    config_path = ROOT / "penpot-project.json"
    if config_path.exists():
        print("Penpot design project already created; refusing to duplicate")
        return
    team = rpc("get-teams")[0]
    project = rpc("create-project", {"teamId": team["id"], "name": "订单管理 AI 研发流程"})
    config = {"team_id": team["id"], "project_id": project["id"]}
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    design = rpc("create-file", {"projectId": project["id"], "name": "订单管理 · 需求与验收原型"})
    (ROOT / "penpot-design-response.json").write_text(json.dumps(design, ensure_ascii=False, indent=2), encoding="utf-8")
    config["file_id"] = design["id"]
    config["url"] = f"http://localhost:9001/#/workspace?team-id={team['id']}&file-id={design['id']}"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    existing = rpc("get-access-tokens")
    token = next((item for item in existing if item.get("type") == "mcp"), None)
    if token is None:
        token = rpc("create-access-token", {"name": "Codex 本地设计协作", "type": "mcp"})
    (ROOT / "secrets/penpot-mcp-token").write_text(token["token"], encoding="utf-8")
    rpc("update-profile-props", {"props": {"mcpEnabled": True}})
    print(json.dumps(config, ensure_ascii=False))


if __name__ == "__main__":
    main()
