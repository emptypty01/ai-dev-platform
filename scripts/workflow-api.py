"""本次已授权的本地 GitLab 演练辅助入口，凭据不进入命令参数。"""
import argparse
import datetime
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://localhost:8088/api/v4"


def request(path, method="GET", data=None, admin=False):
    token_file = "gitlab-bootstrap-token" if admin else "gitlab-workflow-token"
    token = (ROOT / "secrets" / token_file).read_text().strip()
    query = urllib.request.Request(BASE + path, method=method, data=None if data is None else json.dumps(data).encode(),
                                  headers={"PRIVATE-TOKEN": token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(query, timeout=90) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"{method} {path}: HTTP {error.code}: {error.read().decode(errors='replace')[:900]}") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare-token", "get", "post", "put", "delete"])
    parser.add_argument("path", nargs="?")
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--admin", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare-token":
        token_path = ROOT / "secrets/gitlab-workflow-token"
        if not token_path.exists():
            result = request("/users/2/personal_access_tokens", "POST", {"name": "authorized-local-workflow",
                "scopes": ["api", "write_repository"], "expires_at": (datetime.date.today() + datetime.timedelta(days=7)).isoformat()}, admin=True)
            token_path.write_text(result["token"], encoding="utf-8")
        print("Workflow credential prepared in restricted directory; value not printed")
        return
    data = json.loads(args.body_file.read_text(encoding="utf-8-sig")) if args.body_file else None
    result = request(args.path, args.action.upper(), data, admin=args.admin)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized)


if __name__ == "__main__":
    main()
