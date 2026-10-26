"""初始化本地私有项目、示例 Issue 和两个隔离用途的 Runner；不创建代码提交。"""
import datetime
import json
import secrets
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS = ROOT / "secrets"
BASE = "http://localhost:8088/api/v4"


def main():
    token = (SECRETS / "gitlab-bootstrap-token").read_text(encoding="utf-8-sig").strip()
    def api(path, method="GET", data=None):
        request = urllib.request.Request(BASE + path, method=method,
            data=None if data is None else json.dumps(data).encode(),
            headers={"PRIVATE-TOKEN": token, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response) if response.status != 204 else None
        except urllib.error.HTTPError as error:
            body = error.read().decode(errors="replace")
            raise RuntimeError(f"GitLab {method} {path} failed ({error.code}): {body[:700]}") from None

    accounts_path = SECRETS / "accounts.json"
    accounts = json.loads(accounts_path.read_text(encoding="utf-8-sig"))
    if "developer" not in accounts:
        accounts["developer"] = {"username": "developer", "email": "developer@local.test", "password": secrets.token_hex(24)}
        accounts_path.write_text(json.dumps(accounts, ensure_ascii=False, indent=2), encoding="utf-8")
    developer = accounts["developer"]
    users = api("/users?username=developer")
    user = users[0] if users else api("/users", "POST", {"username": developer["username"], "name": "本地研发示例",
        "email": developer["email"], "password": developer["password"], "skip_confirmation": True,
        "can_create_group": False, "projects_limit": 5})
    projects = api("/projects?search=order-workflow-demo&simple=true")
    project = next((item for item in projects if item["path_with_namespace"] == "developer/order-workflow-demo"), None)
    if project is None:
        project = api(f"/projects/user/{user['id']}", "POST", {"name": "订单管理 AI 研发流程示例", "path": "order-workflow-demo",
            "visibility": "private", "initialize_with_readme": False, "default_branch": "main",
            "description": "Java 21 + Maven + Spring Boot + MySQL / Vue 3 + Vite，GitLab Issues + Penpot + Codex CLI 流程示例"})
    project_id = project["id"]
    (ROOT / "project.json").write_text(json.dumps({"id": project_id, "web_url": project["web_url"],
        "path_with_namespace": project["path_with_namespace"], "http_url_to_repo": project["http_url_to_repo"]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    api(f"/projects/{project_id}", "PUT", {"only_allow_merge_if_pipeline_succeeds": True,
        "only_allow_merge_if_all_discussions_are_resolved": True, "auto_devops_enabled": False,
        "shared_runners_enabled": False, "remove_source_branch_after_merge": False})
    api("/application/settings", "PUT", {"signup_enabled": False})
    api_token_path = SECRETS / "gitlab-api-token"
    if not api_token_path.exists():
        expires = (datetime.date.today() + datetime.timedelta(days=90)).isoformat()
        pat = api(f"/users/{user['id']}/personal_access_tokens", "POST", {"name": "local-codex-issue-reader", "scopes": ["read_api"], "expires_at": expires})
        api_token_path.write_text(pat["token"], encoding="utf-8")

    colors = {"flow/backlog": "#6B7280", "flow/clarify": "#C97B00", "flow/ready": "#2864DC", "flow/doing": "#184DBA",
              "flow/review": "#7655B8", "flow/accept": "#258065", "flow/done": "#267538", "type/feature": "#4D70A1"}
    labels = {label["name"] for label in api(f"/projects/{project_id}/labels?per_page=100")}
    for name, color in colors.items():
        if name not in labels:
            api(f"/projects/{project_id}/labels", "POST", {"name": name, "color": color})
    existing = api(f"/projects/{project_id}/issues?state=all&per_page=100")
    title = "订单管理示例：创建、查询与幂等取消"
    issue = next((item for item in existing if item["title"] == title), None)
    if issue is None:
        description = '''## 目标与范围
通过独立订单示例演练 GitLab Issues、Penpot、Codex CLI、Skills 与 CI/CD。后端 Java 21 + Maven + Spring Boot + MySQL；前端 Vue 3 + Vite。

## 业务规则
- 商品名称 1–80 字，数量 1–1000，单价 0.01–99999999.99，最多两位小数。
- 总金额由后端按数量乘单价使用十进制计算。
- 状态 NEW → CANCELLED；重复取消保持原结果，不删除历史。
- 本地演示不包含支付、库存、用户权限和生产部署。

## 验收标准
- [ ] AC-01 创建合法订单，返回订单号、NEW 状态及精确金额。
- [ ] AC-02 列表显示最近 100 笔订单；前端可筛选状态。
- [ ] AC-03 非法名称、数量和金额返回 400。
- [ ] AC-04 取消订单、重复取消保持一致；不存在返回 404。
- [ ] AC-05 刷新与重启后数据库记录保留。
- [ ] AC-06 MR 运行定向测试与构建，默认受保护分支可手工发布本地环境。

## 设计与过程入口
- Penpot：http://localhost:9001，具体设计链接待创建后补充。
- 过程目录：D:\\plan&exec&test\\20261024-AI研发流程本地平台。
- 工作区：D:\\workspace_empty\\ai-dev-process。
- 平台：D:\\docker\\ai-dev-platform。

## 定向验证
- mvn -f backend/pom.xml -B -ntp -Dtest=OrderServiceTest test
- python scripts/smoke_orders.py
- 前端构建与创建 / 取消浏览器验证

## 实际状态
代码与本地验证进行中；Git 提交 / 推送尚未授权。MR、Pipeline、发布和业务验收未执行，不能将本地检查视为平台流水线成功。
'''
        issue = api(f"/projects/{project_id}/issues", "POST", {"title": title, "description": description,
            "labels": "type/feature,flow/doing", "assignee_ids": [user["id"]]})
    (ROOT / "issue.json").write_text(json.dumps({"iid": issue["iid"], "web_url": issue["web_url"]}, ensure_ascii=False, indent=2), encoding="utf-8")

    runner_records_path = SECRETS / "runners.json"
    runners = json.loads(runner_records_path.read_text()) if runner_records_path.exists() else []
    for name, tag, access in [("local-verify", "local-docker", "not_protected"), ("local-deploy", "local-deploy", "ref_protected")]:
        if not any(item["name"] == name for item in runners):
            runner = api("/user/runners", "POST", {"runner_type": "project_type", "project_id": project_id,
                "description": name, "tag_list": [tag], "run_untagged": False, "locked": True, "access_level": access})
            runners.append({"name": name, "id": runner["id"], "token": runner["token"]})
            runner_records_path.write_text(json.dumps(runners, indent=2), encoding="utf-8")
    config = ['concurrent = 1', 'check_interval = 3', 'shutdown_timeout = 30', '']
    for runner in runners:
        deploy = runner["name"] == "local-deploy"
        config += ['[[runners]]', f'name = {json.dumps(runner["name"])}', 'url = "http://gitlab:8088"',
            f'token = {json.dumps(runner["token"])}', 'executor = "docker"', 'clone_url = "http://gitlab:8088"',
            'limit = 1', '[runners.docker]', 'image = "python:3.12-slim"', 'privileged = false',
            'network_mode = "ai-dev-platform-net"', 'pull_policy = "if-not-present"',
            'memory = "1g"', 'cpus = "2"', 'shm_size = 268435456',
            'volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock"]' if deploy else 'volumes = ["/cache"]']
        if deploy:
            config += ['allowed_images = ["docker:29.4.0-cli"]']
        config += ['']
    config_path = SECRETS / "runner-config.toml"
    config_path.write_text("\n".join(config), encoding="utf-8")
    subprocess.run(["docker", "cp", str(config_path), "ai-dev-runner:/etc/gitlab-runner/config.toml"], check=True, capture_output=True)
    subprocess.run(["docker", "restart", "ai-dev-runner"], check=True, capture_output=True)
    env_lines = (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines()
    db_password = next(line.split("=", 1)[1] for line in env_lines if line.startswith("MYSQL_PASSWORD="))
    variables = api(f"/projects/{project_id}/variables")
    if not any(item["key"] == "DB_PASSWORD" for item in variables):
        api(f"/projects/{project_id}/variables", "POST", {"key": "DB_PASSWORD", "value": db_password,
            "masked": True, "protected": True, "environment_scope": "local-demo"})
    print(json.dumps({"project": project["web_url"], "issue": issue["web_url"],
                      "runners": [{"name": item["name"], "id": item["id"]} for item in runners],
                      "code_commits": "not_created"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
