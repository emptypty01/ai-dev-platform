"""记录固定上游版本，并将选定技能适配到本团队工作约定。"""
import hashlib
import json
from pathlib import Path

root = Path("D:/workspace_empty/ai-dev-process")
skills = root / ".agents/skills"
manifest_path = root / "docs/agents/skills-source.json"
if manifest_path.exists():
    raise SystemExit("Already adapted; review current files instead of overwriting")
manifest = {"repository": "https://github.com/mattpocock/skills",
            "commit": "5beb35b040e3de97e54fa9e386d7e42d15c295c2", "adapted_on": "2026-10-24", "skills": []}
changes = {
    "implement": '''---
name: implement
description: 根据已确认 GitLab Issue 或规格实施本项目变更，完成定向验证与交付，不自动提交。
disable-model-invocation: true
---
# 实施任务

1. 按 `docs/agents/issue-tracker.md` 读取 Issue、评论、验收标准、设计基线和阻塞项；报告实际分支，不根据名称推断状态。
2. 按用户已确认范围实施；后端任务不自动扩展为前端任务。需要新的业务决定才提问。
3. 在已约定的行为边界读取并应用本项目 `tdd` 技能；普通修复沿用必要定向验证，不强制给文案等低影响修改补测试。
4. 运行具体类 / 用例与必要编译，记录真实命令及结果；不执行全量或全模块测试，除非用户明确要求。
5. 读取本项目 `code-review` 技能，对明确基线或未提交工作区分别审查规范与需求；没有基线时如实标记。
6. 更新原有执行 / 测试主文档，交付变更、验证、未执行与遗留事项。保留工作区；只有用户明确授权具体提交 / 推送操作才执行。
''',
    "to-spec": '''---
name: to-spec
description: 将已讨论内容整理为需求规格草稿，关联 GitLab Issue，明确待确认项与验收行为。
disable-model-invocation: true
---
# 整理规格

读取 `AGENTS.md`、`docs/agents/issue-tracker.md`、关联 Issue 及术语表。综合已有讨论和代码事实，不重问已经解决的问题。

按目标、范围、业务规则、异常边界、验收标准（AC 编号）、方案决策、测试边界和待确认项整理；后端范围不擅自加入前端实施。

需求设计、开发计划和测试分别更新对应需求目录的现行主文档；GitLab 保留必要正文、状态和共享入口。没有确认的内容标讨论稿。

仅在当前用户任务授权创建 / 更新该 Issue 时发布正文；否则给出草稿。确认准入条件由需求 / 技术负责人完成，生成规格不会自动设置 `flow/ready`。
''',
    "to-tickets": '''---
name: to-tickets
description: 将已确认需求拆为可独立验证的 GitLab 任务，列出实际阻塞依赖并保持原有实施范围。
disable-model-invocation: true
---
# 拆分任务

读取完整需求、评论与真实实现。每项任务交付可观察行为，并声明 AC、输入、阻塞项、输出和定向验证范围。

优先按窄而完整的行为切片拆分。后端任务覆盖必要的数据、业务、接口与验证；只有明确包含前端时才纳入 UI。共享变更不能独立保持兼容时考虑 expand–contract，并明确集成验证位置。

先形成任务清单；用户已确认的范围与粒度不重复确认。未解决的业务决定向责任人确认。只在任务发布已获授权时创建 GitLab Issue；支持原生依赖时使用原生关系，否则正文列出真实引用。

不关闭父 Issue，不将待评审任务自动标记为可开发，不生成额外阶段补充稿。
''',
    "grill-me": '''---
name: grill-me
description: 对需求或方案中影响实施的未决分支进行澄清，形成已确认结论与待确认项。
disable-model-invocation: true
---
# 澄清需求

读取并遵循 [grilling](../grilling/SKILL.md) 的决策树方法，同时遵守本仓库 `AGENTS.md`。

先核对代码、Issue 评论和已有文档，避免询问可以自行查明的事实。问题聚焦实际影响范围、业务行为、兼容和验收的决定，不为普通实现细节反复请求许可。

将已确认结论与尚未确定的内容分开记录；需求过程内容更新原阶段主文档。已经授权且不依赖回答的工作可继续推进。
'''
}
for directory in sorted(path for path in skills.iterdir() if path.is_dir()):
    entry = directory / "SKILL.md"
    before = hashlib.sha256(entry.read_bytes()).hexdigest()
    if directory.name in changes:
        entry.write_text(changes[directory.name], encoding="utf-8")
    elif directory.name == "code-review":
        content = entry.read_text(encoding="utf-8")
        content += '''

## 本项目工作区与授权适配

优先服从根 `AGENTS.md`。未提交工作区可在用户明确要求审查时作为审查对象，使用文件清单和实际文件内容，明确标记“未提交工作区”，不伪造 HEAD 或固定 SHA。已有有效提交基线时仍按上文审查差异。

Issue 读取方式见 `docs/agents/issue-tracker.md`。没有需求证据时报告无法判断的范围。没有并行代理能力或未获该工作方式授权时，依次独立完成两轴审查并说明限制。审查不触发提交、推送或全量测试。
'''
        entry.write_text(content, encoding="utf-8")
    entry.write_text(entry.read_text(encoding="utf-8").replace("disable-model-invocation: true\n", ""), encoding="utf-8")
    manifest["skills"].append({"name": directory.name, "upstream_sha256": before,
                                "installed_sha256": hashlib.sha256(entry.read_bytes()).hexdigest(),
                                "adapted": before != hashlib.sha256(entry.read_bytes()).hexdigest()})
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print("Adapted", len(manifest["skills"]), "skills; manifest:", manifest_path)
