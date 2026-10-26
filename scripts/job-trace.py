"""保存本地演示作业日志，只输出末尾片段；GitLab 对 masked 变量脱敏。"""
import argparse
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("job_id", type=int)
parser.add_argument("--tail", type=int, default=25)
args = parser.parse_args()
token = (root / "secrets/gitlab-workflow-token").read_text().strip()
query = urllib.request.Request(f"http://localhost:8088/api/v4/projects/1/jobs/{args.job_id}/trace", headers={"PRIVATE-TOKEN": token})
with urllib.request.urlopen(query, timeout=60) as response:
    content = response.read().decode(errors="replace")
for secret_name in ["gitlab-workflow-token", "gitlab-bootstrap-token", "gitlab-api-token", "penpot-mcp-token"]:
    secret = (root / "secrets" / secret_name).read_text().strip()
    if secret:
        content = content.replace(secret, "[REDACTED]")
for line in (root / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and len(line.split("=", 1)[1]) > 20:
        content = content.replace(line.split("=", 1)[1], "[REDACTED]")
output = Path(f"D:/plan&exec&test/20261024-AI研发流程本地平台/log/gitlab-job-{args.job_id}.log")
output.write_text(content, encoding="utf-8")
print("\n".join(content.splitlines()[-args.tail:]))
