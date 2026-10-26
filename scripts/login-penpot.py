"""创建首次本地账户（显式选项）并验证登录；仅保存受限浏览器状态。"""
import argparse
import http.cookiejar
import json
import subprocess
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--create-account", action="store_true")
args = parser.parse_args()
account = json.loads((root / "secrets/accounts.json").read_text(encoding="utf-8-sig"))["penpot"]
if args.create_account:
    result = subprocess.run(["docker", "exec", "ai-dev-penpot-backend", "python3", "manage.py", "create-profile",
        "-n", "本地研发示例", "-e", account["email"], "-p", account["password"], "--skip-tutorial", "--skip-walkthrough"],
        capture_output=True)
    if result.returncode:
        raise SystemExit("Account creation failed; account may already exist. Retry login without --create-account.")
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(jar))
request = urllib.request.Request("http://localhost:9001/api/rpc/command/login-with-password",
    data=json.dumps({"email": account["email"], "password": account["password"]}).encode(),
    headers={"Content-Type": "application/json", "Accept": "application/json"})
with opener.open(request, timeout=30) as response:
    assert response.status == 200
state = {"cookies": [{"name": cookie.name, "value": cookie.value, "domain": "localhost", "path": cookie.path,
    "expires": cookie.expires or -1, "httpOnly": True, "secure": cookie.secure, "sameSite": "Lax"} for cookie in jar], "origins": []}
(root / "secrets/penpot-browser-state.json").write_text(json.dumps(state), encoding="utf-8")
print("Penpot login verified; browser state saved in restricted directory.")
