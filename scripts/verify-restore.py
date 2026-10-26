"""将备份恢复到专门创建的临时数据库验证，再删除本脚本创建的数据库；不覆盖现有业务库。"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = Path("D:/plan&exec&test/20261024-AI研发流程本地平台/log")


def run(arguments, data=None):
    result = subprocess.run(["docker", *arguments], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError("Restore verification step failed: " + result.stderr.decode(errors="replace")[:500])
    return result.stdout.decode(errors="replace").strip()


def mysql(statement):
    return run(["exec", "-i", "ai-dev-demo-mysql", "sh", "-c", 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -N'],
               data=statement.encode())


def main():
    backup = sorted(path for path in (ROOT / "backups").iterdir() if path.is_dir())[-1]
    stamp = re.sub(r"\D", "", backup.name)
    mysql_database = "ai_restore_check_" + stamp
    pg_database = "penpot_restore_check_" + stamp
    assert re.fullmatch(r"ai_restore_check_\d+", mysql_database)
    assert re.fullmatch(r"penpot_restore_check_\d+", pg_database)
    result = {"backup": str(backup), "gitlab_restore": "未执行；备份生成与文件存在性已验证，未覆盖运行实例"}
    exists = mysql(f"SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = '{mysql_database}'")
    if exists != "0":
        raise RuntimeError("Temporary MySQL database already exists; refusing to overwrite")
    mysql(f"CREATE DATABASE {mysql_database} CHARACTER SET utf8mb4")
    try:
        run(["exec", "-i", "ai-dev-demo-mysql", "sh", "-c", f'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot {mysql_database}'],
            data=(backup / "ai-workflow.sql").read_bytes())
        count = mysql(f"SELECT COUNT(*) FROM {mysql_database}.demo_order")
        migrations = mysql(f"SELECT COUNT(*) FROM {mysql_database}.flyway_schema_history WHERE success = 1")
        assert int(count) > 0 and migrations == "1"
        result["mysql"] = {"restored_orders": int(count), "successful_migrations": int(migrations), "result": "passed"}
    finally:
        mysql(f"DROP DATABASE {mysql_database}")
    exists = run(["exec", "ai-dev-penpot-postgres", "psql", "-U", "penpot", "-d", "penpot", "-tAc",
                  f"SELECT COUNT(*) FROM pg_database WHERE datname = '{pg_database}'"])
    if exists != "0":
        raise RuntimeError("Temporary PostgreSQL database already exists; refusing to overwrite")
    run(["exec", "ai-dev-penpot-postgres", "createdb", "-U", "penpot", pg_database])
    try:
        run(["cp", str(backup / "penpot.dump"), "ai-dev-penpot-postgres:/tmp/restore-verify.dump"])
        run(["exec", "ai-dev-penpot-postgres", "pg_restore", "-U", "penpot", "-d", pg_database,
             "--no-owner", "--exit-on-error", "/tmp/restore-verify.dump"])
        count = run(["exec", "ai-dev-penpot-postgres", "psql", "-U", "penpot", "-d", pg_database, "-tAc",
                     'SELECT COUNT(*) FROM public.file WHERE deleted_at IS NULL'])
        assert int(count) > 0
        result["penpot_postgres"] = {"restored_design_files": int(count), "result": "passed"}
    finally:
        run(["exec", "ai-dev-penpot-postgres", "dropdb", "-U", "penpot", pg_database])
    entries = run(["run", "--rm", "-v", f"{backup}:/backup:ro", "python:3.12-slim", "tar", "-tzf", "/backup/penpot-assets.tar.gz"])
    result["penpot_assets"] = {"archive_entries": len(entries.splitlines()), "archive_readable": True}
    result["temporary_databases"] = "removed"
    LOG.joinpath("restore-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
