# -*- coding: utf-8 -*-
"""今日任务 · 独立的每日待办 + 主动提醒（与正心分离，不污染觉察）"""
import json
import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
DATA_FILE = APP_DIR / "tasks.json"

app = FastAPI(title="今日任务")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def load():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save(data):
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def today():
    return datetime.date.today().isoformat()


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/tasks")
def get_tasks():
    data = load()
    recurring = data.get("recurring", [])
    day = data.get(today(), {})
    done_recurring = day.get("done_recurring", [])
    ad_hoc = day.get("ad_hoc", [])
    tasks = [{"name": r, "done": r in done_recurring, "type": "recurring"} for r in recurring]
    tasks += [{"name": a.get("name", ""), "done": a.get("done", False), "type": "ad_hoc"} for a in ad_hoc]
    done_count = sum(1 for t in tasks if t["done"])
    return {"date": today(), "tasks": tasks, "done": done_count, "total": len(tasks)}


@app.post("/api/tasks")
async def update_tasks(payload: dict):
    data = load()
    data.setdefault("recurring", [])
    day = data.setdefault(today(), {})
    day.setdefault("done_recurring", [])
    day.setdefault("ad_hoc", [])

    action = payload.get("action")
    name = (payload.get("name") or "").strip()

    if action == "toggle":
        ttype = payload.get("type")
        if ttype == "recurring":
            if name in day["done_recurring"]:
                day["done_recurring"].remove(name)
            else:
                day["done_recurring"].append(name)
        else:
            for a in day["ad_hoc"]:
                if a.get("name") == name:
                    a["done"] = not a.get("done", False)
    elif action == "add_ad_hoc":
        if name:
            day["ad_hoc"].append({"name": name, "done": False})
    elif action == "remove_ad_hoc":
        day["ad_hoc"] = [a for a in day["ad_hoc"] if a.get("name") != name]
    elif action == "add_recurring":
        if name and name not in data["recurring"]:
            data["recurring"].append(name)
    elif action == "remove_recurring":
        if name in data["recurring"]:
            data["recurring"].remove(name)

    save(data)
    return get_tasks()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8901)
