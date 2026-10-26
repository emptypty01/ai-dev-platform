# 本地 AI 研发平台

使用 Docker Compose 运行 GitLab、GitLab Runner、Penpot 和示例项目的 MySQL，配合 [ai-dev-process](https://github.com/emptypty01/ai-dev-process) 中的业务代码、Codex CLI 集成与团队研发规范。

## 目录说明

| 路径 | 用途 |
| --- | --- |
| `compose.yaml` | 服务版本、仅本机访问的端口、网络及命名数据卷 |
| `scripts/` | 平台管理、初始化、备份、GitLab API 与 Penpot 辅助脚本 |
| `tools/`、`pyyaml-*.whl` | 已保留的 Python 辅助依赖；wheel 仅适配文件名标注的 Python / Windows 版本 |
| `image-lock.json` | 本地部署时记录的镜像信息 |
| 其他 JSON、Penpot 参考文件 | 首次搭建与流程演练的实例记录、设计参数及参考源码 |
| `.env`、`secrets/` | 仅本地保存的密码和访问凭据，Git 忽略 |
| `backups/` | 仅本地保存的备份，Git 忽略 |

JSON 中的项目编号、原型编号、提交 SHA 和发布结果属于原本本机实例的记录，不代表在新电脑上克隆后已经完成部署、导入或发布。

## 服务入口

| 服务 | 本机地址 |
| --- | --- |
| GitLab | `http://localhost:8088` |
| GitLab SSH | `localhost:8022` |
| Penpot | `http://localhost:9001` |
| 示例 MySQL | `localhost:3307` |

宿主机端口绑定 `127.0.0.1`。现有 Compose 使用固定项目名、容器名和网络名，在同一台电脑上运行第二套前需要调整这些名称及端口。

## 首次启动

需要 Docker Desktop（Linux 容器）和 PowerShell 7；辅助 Python 脚本还需要相应 Python 环境。以下命令在仓库目录运行：

```powershell
# 仅首次初始化；已有 .env 时脚本拒绝覆盖
pwsh -File .\scripts\initialize-secrets.ps1

# 首次拉取镜像，随后启动
docker compose pull
pwsh -File .\scripts\platform.ps1 up
pwsh -File .\scripts\platform.ps1 status
```

初始化脚本生成本机 `.env` 和受限的 `secrets/accounts.json`，请在本机查看对应账号信息。已有环境不要重复生成或替换凭据。当前部署没有因此次提交而重新初始化或重启。

上述步骤启动基础服务；GitLab 开发账号、项目、Runner 注册、Penpot 账号与原型、Codex MCP 配置需要另外初始化或迁移，启动 Compose 不会自动恢复这些内容。

## 日常维护

```powershell
pwsh -File .\scripts\platform.ps1 status
pwsh -File .\scripts\platform.ps1 stop
pwsh -File .\scripts\platform.ps1 up
```

辅助脚本基于现有本机实例编写，部分绑定 `D:/workspace_empty/ai-dev-process`、`D:/plan&exec&test`、Obsidian 路径、Issue / MR 编号及原型编号。迁移电脑或复用流程前应读取并核对脚本参数和写入行为，尤其是初始化、合并、部署、归档及令牌轮换脚本。名为验证的脚本也可能包含初始化补写步骤，不能一概视为只读检查。

## 数据与备份

GitLab 数据、Runner 配置、Penpot 数据库和素材、MySQL 数据主要保存在 Docker 命名数据卷中。此仓库保存部署配置和脚本，不包含这些运行数据；迁移需另行备份、传输并恢复数据卷和本机凭据。

`scripts/backup.ps1` 用于现有平台备份。备份可能包含密码及令牌，因此 `backups/` 和 `secrets/` 均不提交。删除容器不等于删除命名数据卷；执行会删除数据卷的命令前必须核对数据与备份。

## GitHub 提交身份

本地此仓库使用 `emptypty <emptypty2012@gmail.com>`，通过仓库级 Git 配置设置，不修改公司 GitLab 使用的全局身份。克隆到新电脑后若要沿用此身份，在该仓库单独配置：

```powershell
git config --local user.name emptypty
git config --local user.email emptypty2012@gmail.com
```
