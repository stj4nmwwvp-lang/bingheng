# -*- coding: utf-8 -*-
"""冰衡后端接口测试。

运行：
    pip install -r requirements.txt pytest httpx
    python server/seed.py
    pytest tests/test_api.py -q

设计原则：
- 只验证接口契约（字段是否存在、类型是否合理），不写死具体数值——
  数值随 seed 随机种子变化，写死会让测试很脆。
- 页面路由必须在仓库里开箱可访问（这是本次 PR 修的问题）。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "server"))

from app import app  # noqa: E402

client = TestClient(app)


def test_root_lists_pages():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert "pages" in body
    assert body["pages"]["冰衡"] == "/bingheng"


def test_bingheng_page_served():
    """仓库根目录有 index.html，/bingheng 必须能直接访问。"""
    r = client.get("/bingheng")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "冰衡" in r.text


def test_zhixing_page_is_graceful_when_missing():
    """/zhixing 在缺少 zhixing.html 时应返回 404 + 明确提示，而不是 500。"""
    r = client.get("/zhixing")
    assert r.status_code in (200, 404)
    if r.status_code == 404:
        assert "detail" in r.json()


def test_today_contract():
    r = client.get("/api/bh/today")
    assert r.status_code == 200
    body = r.json()
    assert {"date", "cards", "athletes"} <= set(body)
    cards = body["cards"]
    assert {"green", "yellow", "red"} <= set(cards)
    assert body["athletes"], "seed 之后应有运动员"
    a = body["athletes"][0]
    for key in ("athlete_id", "name", "fi", "level", "reason", "suggested_pct"):
        assert key in a
    assert a["level"] in {"green", "yellow", "red", "under"}
    assert 0 <= a["fi"] <= 100


def test_weekly_contract():
    r = client.get("/api/bh/weekly", params={"days": 14})
    assert r.status_code == 200
    body = r.json()
    assert {"anchor", "days", "acwr", "alerts"} <= set(body)
    assert len(body["days"]) == len(body["acwr"])


def test_athlete_contract():
    today = client.get("/api/bh/today").json()
    aid = today["athletes"][0]["athlete_id"]
    r = client.get(f"/api/bh/athlete/{aid}")
    assert r.status_code == 200
    body = r.json()
    assert {"athlete", "series", "metrics"} <= set(body) or "series" in body


def test_athlete_404():
    r = client.get("/api/bh/athlete/NO_SUCH_ID")
    assert r.status_code == 404


def test_taper_contract():
    r = client.get("/api/bh/taper")
    assert r.status_code == 200
    body = r.json()
    assert {"event", "days_left", "plan"} <= set(body)
    assert body["plan"], "减量计划不应为空"
    first = body["plan"][0]
    assert {"d", "target_pct"} <= set(first)


def test_decision_roundtrip():
    today = client.get("/api/bh/today").json()
    a = today["athletes"][0]
    payload = {
        "athlete_id": a["athlete_id"],
        "level": a["level"],
        "suggested_pct": a["suggested_pct"],
        "reason": "pytest 留痕",
        "decided_by": "pytest",
    }
    r = client.post("/api/bh/decisions", json=payload)
    assert r.status_code == 200
    assert r.json().get("ok") is True

    r = client.get("/api/bh/decisions", params={"limit": 5})
    assert r.status_code == 200
    items = r.json().get("items", [])
    assert any(x.get("decided_by") == "pytest" for x in items)


def test_device_404_is_not_500():
    r = client.get("/api/bh/devices/NO_SUCH_DEVICE")
    assert r.status_code in (200, 404)
