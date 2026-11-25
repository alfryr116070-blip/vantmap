import json, os, subprocess, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")


def run(script, *args, cwd=None):
    return subprocess.run([sys.executable, os.path.join(TOOLS, script), *map(str, args)],
                          capture_output=True, text=True, cwd=cwd)


def minimal_map():
    return {
        "project": {
            "title": "测试地图", "goal": "测试目标", "target_stage": "S2", "updated": "2026-11-24",
            "branches": [{"id": "main1", "name": "主线", "desc": "d"}, {"id": "adjacent", "name": "相邻", "desc": "d"}],
            "verified": True,
            "audit": {"acceptance": {"date": "2026-11-20", "n": 50, "correct": 49, "minor": 1, "wrong": 0, "unsupported": 0, "unreachable": 0, "lower95": 0.9, "rounds": 1}},
        },
        "entries": [{
            "id": "t1", "name": "团队一", "short": "T1", "section": "main", "branch": "main1", "stage": "S1",
            "flags": [], "confidence": "中", "activity": "活跃", "checked": "2026-11-24",
            "evidence": [{"grade": "B", "date": "2026-11-01", "text": "公司称发布了原型。", "url": "https://example.com/a",
                          "quote": "we released a prototype", "verified": "2026-11-24", "progress": True}],
            "product": {"name": "P", "intro": "一个原型。", "status": "已发布原型。", "sources": [{"url": "https://example.com/a", "quote": "we released a prototype"}]},
            "funding": {"kind": "startup", "total_usd": None, "valuation_usd": None, "last_round": None, "sources": [], "cites": {}},
            "openness": [], "gaps": {"field": [], "ours": []},
            "milestone": "公司称发布了原型。", "last_progress": "2026-11-01", "milestone_ref": "https://example.com/a", "milestone_grade": "B",
        }],
        "watch": [], "leads": [], "changes": [], "corrections": [],
        "brief": {"date": "2026-11-24", "headline": "h", "points": [{"text": "主方向 1 个团队，最远 S1。", "refs": ["t1"]}], "you": {"text": "y", "refs": []}},
    }


@pytest.fixture
def mapfile(tmp_path):
    def make(mut=None):
        m = minimal_map()
        if mut: mut(m)
        p = tmp_path / "map.json"
        p.write_text(json.dumps(m, ensure_ascii=False))
        return p
    return make
