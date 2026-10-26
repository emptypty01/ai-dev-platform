"""仅供本地演示仓库 Git 的 ASKPASS 使用，不直接调用或打印到日志。"""
import sys
from pathlib import Path

if "username" in " ".join(sys.argv[1:]).lower():
    print("developer")
else:
    print(Path("D:/docker/ai-dev-platform/secrets/gitlab-workflow-token").read_text().strip())
