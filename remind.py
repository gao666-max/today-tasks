# -*- coding: utf-8 -*-
"""今日任务 · 提醒：弹通知列出未完成的任务，点击打开。加 --force 强制弹（测试）"""
import os
import sys
import json
import socket
import datetime
import subprocess
import winreg

from winotify import Notification

HERE = os.path.dirname(os.path.abspath(__file__))
APP_ID = "ZhengXinTasksReminder"
URL = "http://127.0.0.1:8901"
PORT = 8901


def register_aumid():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\AppUserModelId\ZhengXinTasksReminder")
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "今日任务")
        winreg.CloseKey(key)
    except Exception:
        pass


def server_running():
    try:
        s = socket.create_connection(("127.0.0.1", PORT), timeout=1)
        s.close()
        return True
    except Exception:
        return False


def ensure_server():
    if server_running():
        return
    flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
    subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags,
    )


def unfinished():
    f = os.path.join(HERE, "tasks.json")
    if not os.path.exists(f):
        return []
    try:
        data = json.loads(open(f, encoding="utf-8").read())
    except Exception:
        return []
    today = datetime.date.today().isoformat()
    day = data.get(today, {})
    done = day.get("done_recurring", [])
    ad_hoc = day.get("ad_hoc", [])
    out = [r for r in data.get("recurring", []) if r not in done]
    out += [a.get("name", "") for a in ad_hoc if not a.get("done", False)]
    return out


def main():
    todos = unfinished()
    if not todos and "--force" not in sys.argv:
        return  # 全做完了不打扰
    if todos:
        msg = "未完成：" + "、".join(todos[:5]) + ("…" if len(todos) > 5 else "")
    else:
        msg = "今天的任务都做完啦，休息一下～"
    register_aumid()
    ensure_server()
    Notification(app_id=APP_ID, title="今日任务", msg=msg, duration="short", launch=URL).show()


if __name__ == "__main__":
    main()
