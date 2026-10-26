"""在用户已授权的演示范围内保护主分支并创建真实 MR，不自动合并。"""
import json
from pathlib import Path
import importlib.util

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("workflow_api", root / "scripts/workflow-api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
existing = api.request("/projects/1/protected_branches")
if any(item["name"] == "main" for item in existing):
    api.request("/projects/1/protected_branches/main", "DELETE")
protection = api.request("/projects/1/protected_branches", "POST", {"name": "main", "push_access_level": 0,
    "merge_access_level": 40, "allow_force_push": False})
Path("D:/plan&exec&test/20261024-AI研发流程本地平台/log/main-protection.json").write_text(json.dumps(protection, ensure_ascii=False, indent=2), encoding="utf-8")
print("main protected: no direct push; Maintainer merge; force push disabled")
