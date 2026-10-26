"""将当前操作指南归档至指定 Obsidian 目录，并核对正文未混入本机凭据。"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
source = Path("D:/plan&exec&test/20261024-AI研发流程本地平台/04-操作实施文档.md")
target = Path("D:/Obsidian/Notes-LiveSync/20@领域/2003@AI开发流程/GitLab与Penpot本地AI研发流程实施指南.md")
content = source.read_text(encoding="utf-8-sig")
values = [line.split("=", 1)[1] for line in (root / ".env").read_text(encoding="utf-8-sig").splitlines() if "=" in line]
accounts = json.loads((root / "secrets/accounts.json").read_text(encoding="utf-8-sig"))
values.extend(item["password"] for item in accounts.values() if "password" in item)
for name in ["gitlab-api-token", "gitlab-bootstrap-token", "gitlab-workflow-token", "penpot-mcp-token"]:
    values.append((root / "secrets" / name).read_text().strip())
assert not any(value and len(value) >= 20 and value in content for value in values), "Credential detected in guide"
if target.exists():
    previous = target.read_text(encoding="utf-8-sig")
    assert previous.startswith("---") and "2026-10-24" in previous and "本机实际部署" in previous, "Existing unrelated note; refusing overwrite"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(content, encoding="utf-8")
assert target.read_text(encoding="utf-8") == content
print("Archived:", target)
print("Characters:", len(content), "; credential scan passed; current execution status preserved")
