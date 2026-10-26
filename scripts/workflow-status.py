"""读取本地 MR / Pipeline / Job 状态，保存可核对的公开执行元数据。"""
import importlib.util
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("workflow_api", root / "scripts/workflow-api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
pipelines = api.request("/projects/1/pipelines?per_page=20")
report = {"pipelines": []}
for pipeline in pipelines:
    item = {key: pipeline[key] for key in ["id", "ref", "sha", "status", "source", "web_url"] if key in pipeline}
    jobs = api.request(f"/projects/1/pipelines/{pipeline['id']}/jobs?per_page=100")
    item["jobs"] = [{key: job.get(key) for key in ["id", "name", "stage", "status", "failure_reason", "web_url"]} for job in jobs]
    report["pipelines"].append(item)
mr = api.request("/projects/1/merge_requests/1")
report["mr"] = {key: mr.get(key) for key in ["iid", "state", "sha", "detailed_merge_status", "web_url", "merge_commit_sha"]}
(root / "workflow-status.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
if "--brief" in sys.argv:
    for pipeline in report["pipelines"]:
        print(f"Pipeline {pipeline['id']} {pipeline['ref']} {pipeline['status']} " +
              ", ".join(f"{job['name']}={job['status']}" for job in pipeline["jobs"]))
    print("MR:", report["mr"]["state"], report["mr"]["detailed_merge_status"])
else:
    print(json.dumps(report, ensure_ascii=False, indent=2))
