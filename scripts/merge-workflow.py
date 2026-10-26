"""仅在指定提交的最新 MR 流水线通过后执行本次已获授权的合并。"""
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("workflow_api", root / "scripts/workflow-api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
expected = "91e9f99fee2cd134bc781ec086089d4ac4802a8b"
mr = api.request("/projects/1/merge_requests/1?with_merge_status_recheck=true")
assert mr["state"] == "opened" and mr["sha"] == expected, "MR source changed or no longer open"
pipeline = mr.get("head_pipeline") or {}
assert pipeline.get("sha") == expected and pipeline.get("status") == "success", "Latest matching MR pipeline has not passed"
description = mr["description"].replace("OrderServiceTest 7 个用例通过", "OrderServiceTest + OrderRequestTest 共 9 个用例通过")
description += f"\n\n## 本次实际 MR 验证\n\n最新 MR Pipeline #{pipeline['id']} 已通过，关联提交 `{expected}`。规范轴最终 0 项；需求轴发现的小数数量截断问题已修复，MockMvc 定向验证小数返回 400、合法整数返回 201。\n\n用户已明确授权检查通过后合并。该授权与 AI 两轴审查分别记录，不宣称业务负责人验收已完成；合并后继续验证 main Pipeline 和 localhost 发布。"
api.request("/projects/1/merge_requests/1", "PUT", {"description": description})
result = api.request("/projects/1/merge_requests/1/merge", "PUT", {"sha": expected, "should_remove_source_branch": False,
    "squash": False, "merge_commit_message": "Merge branch 'feat/1-order-workflow' into 'main'\n\n实现订单管理示例及本地 AI 研发 CI/CD 流程 (#1)"})
(root / "merge-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({key: result.get(key) for key in ["state", "web_url", "merge_commit_sha", "merged_at"]}, ensure_ascii=False))
