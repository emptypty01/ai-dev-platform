"""只为已合并的实际 main SHA，在必需检查成功后触发本地手工发布。"""
import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("workflow_api", root / "scripts/workflow-api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
merged = json.loads((root / "merge-result.json").read_text(encoding="utf-8"))
expected = merged["merge_commit_sha"]
pipelines = api.request("/projects/1/pipelines?ref=main&per_page=20")
pipeline = next(item for item in pipelines if item["sha"] == expected)
jobs = api.request(f"/projects/1/pipelines/{pipeline['id']}/jobs?per_page=100")
required = {"handoff", "backend-targeted", "frontend-build", "backend-package"}
assert {item["name"] for item in jobs if item["name"] in required} == required
assert all(item["status"] == "success" for item in jobs if item["name"] in required), "Required main checks not all successful"
deploy = next(item for item in jobs if item["name"] == "deploy-local")
assert deploy["status"] == "manual", "Local deployment is no longer waiting for manual trigger"
protection = api.request("/projects/1/protected_branches/main")
assert any(item.get("access_level") == 0 for item in protection["push_access_levels"]), "main is not protected against direct push"
result = api.request(f"/projects/1/jobs/{deploy['id']}/play", "POST")
(root / "deployment-job.json").write_text(json.dumps({"pipeline_id": pipeline["id"], "sha": expected, "job": result},
    ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"pipeline": pipeline["web_url"], "job_id": result["id"], "status": result["status"], "sha": expected}, ensure_ascii=False))
