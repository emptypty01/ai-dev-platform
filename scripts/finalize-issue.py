"""记录本次实际技术交付；保留 Issue 待业务负责人验收，不自动关闭。"""
import importlib.util
import json
import re
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent.parent
log = Path("D:/plan&exec&test/20261024-AI研发流程本地平台/log")
spec = importlib.util.spec_from_file_location("workflow_api", root / "scripts/workflow-api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
release = json.loads((root / "release-verification.json").read_text(encoding="utf-8"))
assert release["api_smoke"]["checks"] == 11 and release["api_smoke"]["result"] == "passed"
with urllib.request.urlopen("http://localhost:5174/api/orders", timeout=20) as response:
    orders = json.load(response)
previous = next(item for item in orders if item["id"] == 1)
assert previous["itemName"] == "演示机械键盘" and previous["status"] == "CANCELLED"
persistence = {"old_order_id": 1, "retained_after_ci_container_recreation": True, "release_sha": release["sha"]}
log.joinpath("release-persistence.json").write_text(json.dumps(persistence, ensure_ascii=False, indent=2), encoding="utf-8")
issue = api.request("/projects/1/issues/1")
description = issue["description"]
description = re.sub(r"- \[ \] (AC-0[1-6])", r"- [x] \1", description)
description = description.split("## 实际状态")[0] + f'''## 实际状态

本次技术演练已完成，Issue 保留 opened / flow/accept，等待业务负责人验收；不将技术验证或 MR 合并当作业务验收。

- MR !1：{release['mr']}，已合并。
- MR Pipeline #2：四项自动检查成功。
- main Pipeline #3：{release['main_pipeline']}，五项作业成功，包括手工发布 Job #13。
- 实际制品与前后端镜像 SHA：`{release['sha']}`。
- 定向验证：服务 7 + 请求 2 共 9 个用例；发布后 11 项 API 场景，包括小数数量拒绝与 8 路并发取消。
- CI 重建应用容器后原订单 ID 1 仍保留，独立 MySQL 数据未丢失。
- 规范轴 0 项；需求轴发现 1 项小数数量截断问题，已修复并验证。
- 部署：http://localhost:5174；环境 local-demo。
- 原 Pipeline #1 为必要修复主动取消，不计为成功。
- 未执行：全量回归、生产发布、GitLab 运行实例覆盖恢复、业务负责人验收。
- 操作指南：知识库 20@领域/2003@AI开发流程/GitLab与Penpot本地AI研发流程实施指南.md。
- 测试主文档：D:\\plan&exec&test\\20261024-AI研发流程本地平台\\03-测试文档.md。
'''
result = api.request("/projects/1/issues/1", "PUT", {"description": description, "labels": "type/feature,flow/accept"})
mr = api.request("/projects/1/merge_requests/1")
body = mr["description"].split("\n\n## 最终发布核对")[0].replace("本 MR 真实流水线验证中", "MR #2、main #3 和手工发布 #13 均通过")
body += f"\n\n## 最终发布核对\n\nmain Pipeline #3 与部署 Job #13 成功；制品和两个运行镜像均绑定 `{release['sha']}`。发布后 11 项 API 场景通过（含小数数量 400、8 路并发取消），旧订单在容器重建后保留。Issue 已转待验收并保持打开；业务验收、全量回归和生产发布未执行。"
api.request("/projects/1/merge_requests/1", "PUT", {"description": body, "labels": "type/feature"})
log.joinpath("issue-final-state.json").write_text(json.dumps({"iid": result["iid"], "state": result["state"],
    "labels": result["labels"], "task_completion_status": result.get("task_completion_status")}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"issue": result["web_url"], "state": result["state"], "labels": result["labels"], "persistence": persistence}, ensure_ascii=False))
