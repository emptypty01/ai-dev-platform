"""以实际发布与恢复证据更新原操作指南，不创建副本。"""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
process = Path("D:/plan&exec&test/20261024-AI研发流程本地平台")
guide = process / "04-操作实施文档.md"
release = json.loads((root / "release-verification.json").read_text(encoding="utf-8"))
restore = json.loads((process / "log/restore-verification.json").read_text(encoding="utf-8"))
assert release["api_smoke"]["result"] == "passed" and release["api_smoke"]["checks"] == 11
assert restore["mysql"]["result"] == "passed"
text = guide.read_text(encoding="utf-8-sig")
changes = {
    "status: 进行中": "status: 已完成",
    "平台和 Docker 订单示例已运行；真实 MR / Pipeline 演练等待本次 Git 操作授权，不能将 CI 配置校验写成流水线通过。":
        "平台、Codex / Skills / MCP 和 Docker 订单示例已运行。用户已授权并完成真实 MR、main Pipeline、手工本地发布及发布后验证；Issue 保留待业务负责人验收。",
    "-Dtest=OrderServiceTest test": "-Dtest=OrderServiceTest,OrderRequestTest test",
    "2. `backend-targeted`：仅运行 `OrderServiceTest`，保存 JUnit 报告。":
        "2. `backend-targeted`：指定运行 `OrderServiceTest,OrderRequestTest` 共 9 个用例，保存 JUnit 报告。",
    "GitLab CE Free 的批准记录不是强制批准门禁。完成初始化提交后，将主分支配置为禁止直接推送、限制合并角色并保留人工评审记录；生产发布不在本次范围。当前空仓库尚未形成实际主分支保护验证证据。":
        "GitLab CE Free 的批准记录不是强制批准门禁。主分支已配置禁止直接推送、Maintainer 可合并、禁止强推。本次通过 AI 两轴审查及用户明确的合并授权推进；不将自动化审查写成人工业务验收。生产发布不在本次范围。",
    "本次备份 `20261024-115259` 已成功恢复 6 笔订单、1 条成功迁移记录与 1 个 Penpot 设计文件；附件归档可读。完整 GitLab 覆盖恢复未执行。":
        f"交付后完整备份：`{Path(restore['backup']).name}`，包含已提交仓库、MR、CI / 部署记录及服务数据。最新备份已在临时库恢复 {restore['mysql']['restored_orders']} 笔订单、{restore['mysql']['successful_migrations']} 条成功迁移记录与 {restore['penpot_postgres']['restored_design_files']} 个 Penpot 设计文件；附件归档可读，临时库已删除。初次部署备份 `20261024-115259` 也保留。完整 GitLab 覆盖恢复未执行。",
    "已验证：平台登录 / API、两类 Runner online、CI Lint、7 个后端用例、Vue 构建、10 项真实数据库接口场景（含 8 路并发取消）、浏览器操作、8 个 Skills 结构、Codex 上下文、Penpot MCP 创建和导出、完整备份、临时数据库恢复及工作区凭据扫描。":
        "已验证：平台登录 / API、两类 Runner online、CI Lint、9 个后端定向用例、Vue 构建、11 项发布后真实接口场景（含小数数量拒绝和 8 路并发取消）、浏览器操作、8 个 Skills 结构、Codex 上下文与 MCP 调用、Penpot 原型创建和导出、真实 MR / main CI、手工部署、SHA 一致性、重建后订单保留、完整备份、临时数据库恢复及工作区凭据扫描。",
    "待授权后执行：示例代码提交 / 推送、真实 MR 与 Pipeline、合并后的 GitLab 手工发布。":
        "本次 Git 与合并 / 发布操作已经用户明确授权并执行；此授权仅适用于该新建本地示例仓库，不改变其他任务默认不自动提交 / 推送的约定。",
}
for old, new in changes.items():
    assert old in text, "Expected guide passage missing: " + old[:60]
    text = text.replace(old, new)
evidence = f'''### 9.1 本次实际闭环证据

| 环节 | 实际结果 |
| --- | --- |
| 规范基线 | `3f1100c83f763824503449f99488959a002e0bde` |
| 实现分支 | `feat/1-order-workflow`；最终源提交 `91e9f99fee2cd134bc781ec086089d4ac4802a8b` |
| MR | [!1 已合并]({release['mr']}) |
| MR CI | [Pipeline #2 成功](http://localhost:8088/developer/order-workflow-demo/-/pipelines/2)，四项作业通过 |
| main CI/CD | [Pipeline #3 成功]({release['main_pipeline']})，五项作业通过 |
| 手工发布 | [Job #13 成功](http://localhost:8088/developer/order-workflow-demo/-/jobs/13)，环境 `local-demo`，部署 ID 1 |
| 合并 / 发布 SHA | `{release['sha']}` |
| 运行镜像 | 前后端镜像 tag、CI `commit-sha.txt`、GitLab 部署记录均与上述 SHA 一致 |
| 定向测试 | 服务 7 + 请求层 2，共 9 成功、0 失败、0 跳过 |
| 发布后 API | 11 项场景通过，含小数数量 400、8 路并发取消 |
| 持久化 | CI 重建应用容器后原订单 ID 1 仍存在 |
| 当前工作区 | 本地 `main` 与 `origin/main` 一致且干净，演示分支保留 |
| Issue | 技术验收项记录完成，保持 `opened / flow/accept`，待业务负责人验收 |

第一条 MR Pipeline #1 因审查发现必要修复而主动取消，不计为通过。规范轴最终 0 项；需求轴发现小数数量被 Jackson 截断的问题，已关闭浮点转整数、补充请求层测试并完成真实发布后验证。

证据保存在过程目录 `log/release-verification.json`、`release-api-smoke.log`、`release-persistence.json`、`pipeline-2-test-summary.json`、`pipeline-3-test-summary.json` 及各 Job 日志。知识库保留范围、结论与入口，不复制运行日志、口令或 Token。

'''
text = text.replace("## 10. 官方参考", evidence + "## 10. 官方参考")
assert "真实 MR / Pipeline 演练等待" not in text and "当前空仓库" not in text
guide.write_text(text, encoding="utf-8", newline="\n")
print("Updated existing operations guide with completed MR/CI/CD evidence")
