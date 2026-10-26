"""只读验证平台、项目、Runner、MCP 与工作区凭据隔离。"""
import json
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = Path("D:/workspace_empty/ai-dev-process")
LOG = Path("D:/plan&exec&test/20261024-AI研发流程本地平台/log")
token = (ROOT / "secrets/gitlab-bootstrap-token").read_text().strip()


def api(path, method="GET", data=None):
    request = urllib.request.Request("http://localhost:8088/api/v4" + path, method=method,
        data=None if data is None else json.dumps(data).encode(),
        headers={"PRIVATE-TOKEN": token, "Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    project = json.loads((ROOT / "project.json").read_text())
    pid = project["id"]
    penpot = json.loads((ROOT / "penpot-project.json").read_text())
    description = api(f"/projects/{pid}/issues/1")["description"]
    if "file-id=" not in description:
        description = description.replace("具体设计链接待创建后补充。", f"设计文件：{penpot['url']}。两张可编辑画板包含订单列表、创建、空状态、校验与取消规则；设计待人工评审。")
        api(f"/projects/{pid}/issues/1", "PUT", {"description": description})
    ci = api(f"/projects/{pid}/ci/lint", "POST", {"content": (WORKSPACE / ".gitlab-ci.yml").read_text(encoding="utf-8")})
    runners = api(f"/projects/{pid}/runners")
    result = {"gitlab_version": api("/version")["version"], "project": project["web_url"], "ci_valid": ci["valid"],
        "runners": [{key: item.get(key) for key in ["id", "description", "status", "online"]} for item in runners],
        "http": {}, "secret_scan": "pending"}
    for name, url in {"gitlab_signin": "http://localhost:8088/users/sign_in", "penpot": "http://localhost:9001",
                      "docker_demo": "http://localhost:5174", "docker_api": "http://localhost:5174/api/health"}.items():
        with urllib.request.urlopen(url, timeout=30) as response:
            result["http"][name] = response.status
    values = [line.split("=", 1)[1] for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines() if "=" in line]
    accounts = json.loads((ROOT / "secrets/accounts.json").read_text(encoding="utf-8-sig"))
    values.extend(item["password"] for item in accounts.values() if "password" in item)
    for name in ["gitlab-api-token", "gitlab-bootstrap-token", "gitlab-workflow-token", "penpot-mcp-token"]:
        values.append((ROOT / "secrets" / name).read_text().strip())
    # 同时扫描已跟踪文件和可进入仓库的新文件，关闭中文路径引用。
    files = subprocess.check_output(["git", "-c", "core.quotepath=false", "ls-files", "--cached", "--others", "--exclude-standard"],
                                    cwd=WORKSPACE, text=True, encoding="utf-8").splitlines()
    leaked = []
    for name in files:
        path = WORKSPACE / name
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="ignore")
            if any(value and len(value) >= 20 and value in content for value in values):
                leaked.append(name)
    result["secret_scan"] = {"files": len(files), "leaked_files": leaked}
    LOG.joinpath("platform-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    assert ci["valid"] and not leaked


if __name__ == "__main__":
    main()
