from typing import Optional
from fastapi import APIRouter, Request, Form, Depends, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from services.config import config

router = APIRouter()


ADMIN_PASSWORD_KEY = "admin_password"
DEFAULT_ADMIN_PASSWORD = "admin123"


class AdminLogin(BaseModel):
    password: str


def get_admin_password() -> str:
    return config._config.get(ADMIN_PASSWORD_KEY, DEFAULT_ADMIN_PASSWORD)


def verify_admin(admin_token: Optional[str] = Cookie(None)) -> bool:
    if admin_token != get_admin_password():
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude2API - 管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            font-size: 28px;
            color: #333;
        }
        .logo p {
            color: #666;
            margin-top: 5px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
        }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .error {
            color: #e74c3c;
            text-align: center;
            margin-top: 15px;
        }
        .hint {
            text-align: center;
            color: #999;
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>Claude2API</h1>
            <p>管理后台登录</p>
        </div>
        <form id="loginForm">
            <div class="form-group">
                <label>管理员密码</label>
                <input type="password" id="password" name="password" placeholder="请输入密码" required>
            </div>
            <button type="submit" class="btn">登录</button>
            <div id="error" class="error" style="display:none;"></div>
        </form>
        <div class="hint">默认密码: admin123</div>
    </div>
    <script>
        document.getElementById("loginForm").addEventListener("submit", async (e) => {
            e.preventDefault();
            const password = document.getElementById("password").value;
            const errorDiv = document.getElementById("error");

            try {
                const res = await fetch("/admin/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: "password=" + encodeURIComponent(password)
                });

                if (res.ok) {
                    window.location.href = "/admin/account";
                } else {
                    const data = await res.json();
                    errorDiv.textContent = data.detail || "密码错误";
                    errorDiv.style.display = "block";
                }
            } catch (err) {
                errorDiv.textContent = "登录失败";
                errorDiv.style.display = "block";
            }
        });
    </script>
</body>
</html>
"""


@router.get("/login", response_class=HTMLResponse)
async def admin_login_page():
    return LOGIN_PAGE


@router.post("/login")
async def admin_login(password: str = Form(...)):
    if password != get_admin_password():
        raise HTTPException(status_code=401, detail="密码错误")

    response = RedirectResponse(url="/admin/account", status_code=303)
    response.set_cookie(key="admin_token", value=password, httponly=True)
    return response


@router.get("/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("admin_token")
    return response


def get_account_page(total_accounts: int, active_accounts: int, proxy_status: str, accounts_rows: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude2API - 账号管理</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }}
        .navbar {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }}
        .navbar h1 {{ font-size: 20px; }}
        .navbar-links a {{
            color: white;
            margin-left: 20px;
            text-decoration: none;
        }}
        .navbar-links a:hover {{ text-decoration: underline; }}
        .container {{
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 25px;
            margin-bottom: 20px;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
        }}
        .card-title {{ font-size: 18px; color: #333; }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{ background: #f8f8f8; color: #666; font-weight: 500; }}
        .status {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
        }}
        .status.active {{ background: #e8f5e9; color: #2e7d32; }}
        .status.inactive {{ background: #ffebee; color: #c62828; }}
        .btn-small {{
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            font-size: 13px;
            cursor: pointer;
            margin-right: 5px;
        }}
        .btn-toggle {{ background: #667eea; color: white; }}
        .btn-delete {{ background: #e74c3c; color: white; }}
        .btn-add {{
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }}
        .modal {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            align-items: center;
            justify-content: center;
        }}
        .modal.active {{ display: flex; }}
        .modal-content {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            width: 90%;
            max-width: 500px;
        }}
        .modal-title {{ font-size: 18px; margin-bottom: 20px; }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; color: #333; }}
        .form-group input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
        }}
        .modal-buttons {{ display: flex; gap: 10px; margin-top: 20px; }}
        .btn-cancel {{
            padding: 10px 20px;
            background: #ddd;
            color: #333;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }}
        .btn-save {{
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        .info-item {{
            background: #f8f8f8;
            padding: 15px;
            border-radius: 8px;
        }}
        .info-item h3 {{ font-size: 14px; color: #666; margin-bottom: 5px; }}
        .info-item p {{ font-size: 20px; color: #333; font-weight: 500; }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Claude2API 管理后台</h1>
        <div class="navbar-links">
            <a href="/admin/account">账号管理</a>
            <a href="/admin/config">配置管理</a>
            <a href="/admin/logout">退出登录</a>
        </div>
    </div>

    <div class="container">
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">系统信息</h2>
            </div>
            <div class="info-grid">
                <div class="info-item">
                    <h3>账号总数</h3>
                    <p>{total_accounts}</p>
                </div>
                <div class="info-item">
                    <h3>活跃账号</h3>
                    <p>{active_accounts}</p>
                </div>
                <div class="info-item">
                    <h3>代理状态</h3>
                    <p>{proxy_status}</p>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h2 class="card-title">账号列表</h2>
                <button class="btn-add" onclick="showAddModal()">添加账号</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>账号ID</th>
                        <th>名称</th>
                        <th>邮箱</th>
                        <th>状态</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {accounts_rows}
                </tbody>
            </table>
        </div>

        <div class="card">
            <div class="card-header">
                <h2 class="card-title">API 快速测试</h2>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn-add" onclick="testHealth()">健康检查</button>
                <button class="btn-add" onclick="testModels()">模型列表</button>
            </div>
            <div id="testResult" style="margin-top: 15px; padding: 15px; background: #f8f8f8; border-radius: 8px; display: none;"></div>
        </div>
    </div>

    <!-- 添加账号模态框 -->
    <div id="addModal" class="modal">
        <div class="modal-content">
            <h2 class="modal-title">添加账号</h2>
            <div class="form-group">
                <label>Session Key</label>
                <input type="text" id="newSessionKey" placeholder="从 claude.ai 获取 sessionKey">
            </div>
            <div class="form-group">
                <label>名称 (可选)</label>
                <input type="text" id="newName" placeholder="账号名称">
            </div>
            <div class="form-group">
                <label>邮箱 (可选)</label>
                <input type="text" id="newEmail" placeholder="账号邮箱">
            </div>
            <div class="modal-buttons">
                <button class="btn-cancel" onclick="hideAddModal()">取消</button>
                <button class="btn-save" onclick="addAccount()">添加</button>
            </div>
        </div>
    </div>

    <script>
        function showAddModal() {{
            document.getElementById("addModal").classList.add("active");
        }}
        function hideAddModal() {{
            document.getElementById("addModal").classList.remove("active");
        }}

        async function addAccount() {{
            const sessionKey = document.getElementById("newSessionKey").value;
            const name = document.getElementById("newName").value;
            const email = document.getElementById("newEmail").value;

            if (!sessionKey) {{
                alert("请输入 Session Key");
                return;
            }}

            try {{
                const res = await fetch("/v1/accounts", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ session_key: sessionKey, name, email }})
                }});

                if (res.ok) {{
                    hideAddModal();
                    location.reload();
                }} else {{
                    alert("添加失败: " + await res.text());
                }}
            }} catch (err) {{
                alert("添加失败");
            }}
        }}

        async function toggleAccount(accountId) {{
            try {{
                const res = await fetch("/v1/accounts/" + accountId + "/toggle", {{ method: "POST" }});
                if (res.ok) location.reload();
            }} catch (err) {{
                alert("操作失败");
            }}
        }}

        async function deleteAccount(accountId) {{
            if (!confirm("确定要删除该账号吗?")) return;
            try {{
                const res = await fetch("/v1/accounts/" + accountId, {{ method: "DELETE" }});
                if (res.ok) location.reload();
            }} catch (err) {{
                alert("删除失败");
            }}
        }}

        async function testHealth() {{
            const res = await fetch("/v1/system/health");
            const data = await res.json();
            showTestResult("健康检查", data);
        }}

        async function testModels() {{
            const res = await fetch("/v1/models");
            const data = await res.json();
            showTestResult("模型列表", data);
        }}

        function showTestResult(title, data) {{
            const div = document.getElementById("testResult");
            div.style.display = "block";
            div.innerHTML = "<strong>" + title + ":</strong><br><pre>" + JSON.stringify(data, null, 2) + "</pre>";
        }}
    </script>
</body>
</html>
"""


@router.get("/account", response_class=HTMLResponse)
async def admin_account_page(admin_token: Optional[str] = Cookie(None)):
    if admin_token != get_admin_password():
        return RedirectResponse(url="/admin/login")

    accounts_rows = ""
    for acc in config.accounts:
        account_id = acc.get("account_id", "-")
        name = acc.get("name", "-")
        email = acc.get("email", "-")
        is_active = acc.get("active", True)
        status = "启用" if is_active else "禁用"
        status_class = "active" if is_active else "inactive"
        toggle_text = "禁用" if is_active else "启用"

        accounts_rows += f"""<tr>
            <td>{account_id}</td>
            <td>{name}</td>
            <td>{email}</td>
            <td><span class="status {status_class}">{status}</span></td>
            <td>
                <button class="btn-small btn-toggle" onclick="toggleAccount('{account_id}')">{toggle_text}</button>
                <button class="btn-small btn-delete" onclick="deleteAccount('{account_id}')">删除</button>
            </td>
        </tr>"""

    if not accounts_rows:
        accounts_rows = '<tr><td colspan="5" style="text-align:center;color:#999;">暂无账号</td></tr>'

    total_accounts = len(config.accounts)
    active_accounts = len([a for a in config.accounts if a.get("active", True)])
    proxy_status = "启用" if config.proxy.get("enabled", False) else "禁用"

    return get_account_page(total_accounts, active_accounts, proxy_status, accounts_rows)


def get_config_page(admin_password: str, proxy_checked: str, proxy_http: str, proxy_https: str, server_port: int) -> str:
    return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude2API - 配置管理</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }}
        .navbar {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }}
        .navbar h1 {{ font-size: 20px; }}
        .navbar-links a {{ color: white; margin-left: 20px; text-decoration: none; }}
        .navbar-links a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 800px; margin: 30px auto; padding: 0 20px; }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 25px;
            margin-bottom: 20px;
        }}
        .card-title {{ font-size: 18px; color: #333; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 8px; color: #333; font-weight: 500; }}
        .form-group input, .form-group select {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }}
        .form-group input:focus, .form-group select:focus {{ outline: none; border-color: #667eea; }}
        .checkbox-group {{ display: flex; align-items: center; gap: 10px; }}
        .checkbox-group input {{ width: 20px; height: 20px; }}
        .btn-save {{
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
        }}
        .hint {{ color: #666; font-size: 12px; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Claude2API 管理后台</h1>
        <div class="navbar-links">
            <a href="/admin/account">账号管理</a>
            <a href="/admin/config">配置管理</a>
            <a href="/admin/logout">退出登录</a>
        </div>
    </div>

    <div class="container">
        <div class="card">
            <h2 class="card-title">管理员设置</h2>
            <div class="form-group">
                <label>管理员密码</label>
                <input type="password" id="adminPassword" value="{admin_password}" placeholder="管理员登录密码">
                <div class="hint">修改后需要重新登录</div>
            </div>
        </div>

        <div class="card">
            <h2 class="card-title">代理设置</h2>
            <div class="form-group checkbox-group">
                <input type="checkbox" id="proxyEnabled" {proxy_checked}>
                <label>启用代理</label>
            </div>
            <div class="form-group">
                <label>HTTP 代理</label>
                <input type="text" id="proxyHttp" value="{proxy_http}" placeholder="http://127.0.0.1:7890">
            </div>
            <div class="form-group">
                <label>HTTPS 代理</label>
                <input type="text" id="proxyHttps" value="{proxy_https}" placeholder="http://127.0.0.1:7890">
            </div>
        </div>

        <div class="card">
            <h2 class="card-title">服务器设置</h2>
            <div class="form-group">
                <label>监听端口 (容器内部)</label>
                <input type="number" id="serverPort" value="{server_port}">
                <div class="hint">Docker 部署时此为容器内部端口，外部端口由 docker-compose.yml 决定</div>
            </div>
        </div>

        <button class="btn-save" onclick="saveConfig()">保存配置</button>
        <div id="result" style="margin-top: 15px; text-align: center; color: #2e7d32;"></div>
    </div>

    <script>
        async function saveConfig() {{
            const data = {{
                admin_password: document.getElementById("adminPassword").value,
                proxy: {{
                    enabled: document.getElementById("proxyEnabled").checked,
                    http: document.getElementById("proxyHttp").value,
                    https: document.getElementById("proxyHttps").value
                }},
                server: {{
                    host: "0.0.0.0",
                    port: parseInt(document.getElementById("serverPort").value)
                }},
                accounts: []
            };

            try {{
                const res = await fetch("/admin/config", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify(data)
                }});

                if (res.ok) {{
                    document.getElementById("result").textContent = "配置已保存！";
                    setTimeout(() => location.reload(), 1000);
                }} else {{
                    alert("保存失败");
                }}
            }} catch (err) {{
                alert("保存失败");
            }}
        }}
    </script>
</body>
</html>
"""


@router.get("/config", response_class=HTMLResponse)
async def admin_config_page(admin_token: Optional[str] = Cookie(None)):
    if admin_token != get_admin_password():
        return RedirectResponse(url="/admin/login")

    proxy_checked = "checked" if config.proxy.get("enabled", False) else ""
    proxy_http = config.proxy.get("http", "")
    proxy_https = config.proxy.get("https", "")
    server_port = config.server.get("port", 8000)
    admin_password = get_admin_password()

    return get_config_page(admin_password, proxy_checked, proxy_http, proxy_https, server_port)


@router.post("/config")
async def save_config(request: Request, admin_token: Optional[str] = Cookie(None)):
    if admin_token != get_admin_password():
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()

    if "admin_password" in data:
        config._config["admin_password"] = data["admin_password"]
    if "proxy" in data:
        config._config["proxy"] = data["proxy"]
    if "server" in data:
        config._config["server"] = data["server"]

    config.save()
    return {"message": "配置已保存"}