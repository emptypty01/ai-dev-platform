"""以本地示例账户验证网页登录，保存受限浏览器状态，不打印口令或 Cookie。"""
import html
import http.cookiejar
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent.parent
account = json.loads((root / "secrets/accounts.json").read_text(encoding="utf-8-sig"))["developer"]
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(jar))
with opener.open("http://localhost:8088/users/sign_in", timeout=30) as response:
    page = response.read().decode()
token = html.unescape(re.search(r'name="authenticity_token" value="([^"]+)"', page).group(1))
body = urllib.parse.urlencode({"authenticity_token": token, "user[login]": account["username"],
    "user[password]": account["password"], "user[remember_me]": "0"}).encode()
with opener.open(urllib.request.Request("http://localhost:8088/users/sign_in", data=body,
    headers={"Content-Type": "application/x-www-form-urlencoded", "Origin": "http://localhost:8088",
             "Referer": "http://localhost:8088/users/sign_in"}), timeout=30) as response:
    if "/users/sign_in" in response.url:
        raise RuntimeError("GitLab login did not leave sign-in page")
with opener.open("http://localhost:8088/api/v4/user", timeout=30) as response:
    user = json.load(response)
assert user["username"] == account["username"]
state = {"cookies": [{"name": cookie.name, "value": cookie.value, "domain": "localhost", "path": cookie.path,
    "expires": cookie.expires or -1, "httpOnly": cookie.name == "_gitlab_session", "secure": cookie.secure, "sameSite": "Lax"}
    for cookie in jar], "origins": []}
(root / "secrets/gitlab-browser-state.json").write_text(json.dumps(state), encoding="utf-8")
print("GitLab browser login passed:", user["username"], "user ID", user["id"])
