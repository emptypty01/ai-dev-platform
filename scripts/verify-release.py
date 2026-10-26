"""核对实际 main Pipeline、部署、SHA 制品与订单定向场景。"""
import importlib.util
import json
import subprocess
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent.parent
workspace = Path("D:/workspace_empty/ai-dev-process")
log = Path("D:/plan&exec&test/20261024-AI研发流程本地平台/log")
spec = importlib.util.spec_from_file_location("workflow_api", root / "scripts/workflow-api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
merged = json.loads((root / "merge-result.json").read_text(encoding="utf-8"))
expected = merged["merge_commit_sha"]
pipeline = next(item for item in api.request("/projects/1/pipelines?ref=main&per_page=20") if item["sha"] == expected)
assert pipeline["status"] == "success", "Main pipeline is not successful"
jobs = api.request(f"/projects/1/pipelines/{pipeline['id']}/jobs?per_page=100")
assert len(jobs) == 5 and all(item["status"] == "success" for item in jobs)
result = {"sha": expected, "main_pipeline": pipeline["web_url"], "mr": merged["web_url"],
          "jobs": [{key: item[key] for key in ["id", "name", "status", "web_url"]} for item in jobs], "images": {}}
for container in ["ai-order-backend", "ai-order-frontend"]:
    image = subprocess.check_output(["docker", "inspect", container, "--format", "{{.Config.Image}}"], text=True).strip()
    assert image.endswith(":" + expected)
    result["images"][container] = image
token = (root / "secrets/gitlab-workflow-token").read_text().strip()
package = next(item for item in jobs if item["name"] == "backend-package")
query = urllib.request.Request(f"http://localhost:8088/api/v4/projects/1/jobs/{package['id']}/artifacts/backend/target/commit-sha.txt",
                               headers={"PRIVATE-TOKEN": token})
with urllib.request.urlopen(query, timeout=30) as response:
    artifact_sha = response.read().decode().strip()
assert artifact_sha == expected
result["artifact_sha"] = artifact_sha
smoke = subprocess.run(["python", str(workspace / "scripts/smoke_orders.py"), "--base-url", "http://localhost:5174"],
    cwd=workspace, capture_output=True, text=True, encoding="utf-8")
log.joinpath("release-api-smoke.log").write_text(smoke.stdout + smoke.stderr, encoding="utf-8")
assert smoke.returncode == 0, "Release API smoke failed; see process log"
result["api_smoke"] = json.loads(smoke.stdout)
deployments = api.request("/projects/1/deployments?environment=local-demo&per_page=20")
deployment = next(item for item in deployments if item["sha"] == expected and item["status"] == "success")
result["deployment"] = {key: deployment.get(key) for key in ["id", "sha", "status", "ref", "created_at"]}
result["test_summary"] = api.request(f"/projects/1/pipelines/{pipeline['id']}/test_report_summary")["total"]
assert result["test_summary"]["count"] == 9 and result["test_summary"]["success"] == 9
local_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=workspace, text=True).strip()
assert local_sha == expected
assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=workspace, text=True).strip()
log.joinpath("release-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
(root / "release-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
