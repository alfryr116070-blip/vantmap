import json, os, glob
from conftest import run, ROOT


def test_example_maps_pass_check():
    maps = json.load(open(os.path.join(ROOT, "data/maps.json")))["maps"]
    assert maps
    for m in maps:
        r = run("check.py", os.path.join(ROOT, m["map"]), m.get("updated", "2026-11-24"))
        assert r.returncode == 0, m["id"] + "\n" + r.stdout[-2000:]


def test_minimal_map_passes(mapfile):
    r = run("check.py", mapfile(), "2026-11-24")
    assert r.returncode == 0, r.stdout


def test_last_round_must_be_object(mapfile):
    def mut(m): m["entries"][0]["funding"]["last_round"] = "C 轮 50 亿美元"
    r = run("check.py", mapfile(mut), "2026-11-24")
    assert r.returncode == 1 and "last_round" in r.stdout


def test_verified_true_requires_passing_acceptance(mapfile):
    def mut(m): m["project"]["audit"]["acceptance"].update(minor=5)
    r = run("check.py", mapfile(mut), "2026-11-24")
    assert r.returncode == 1 and "verified" in r.stdout


def test_tier2_money_needs_key_check(mapfile):
    def mut(m):
        m["watch"] = [{"id": "w1", "name": "W", "short": "W", "branch": "main1", "stage_rough": "S1",
                       "one_line": "公司称完成 3000 万美元融资。", "why": "规模未知", "checked": "2026-11-24",
                       "sources": [{"url": "https://example.com/w", "quote": "raised $30M", "grade": "C", "date": None}]}]
    r = run("check.py", mapfile(mut), "2026-11-24")
    assert r.returncode == 1 and "key_checked" in r.stdout


def test_tier3_lead_cannot_carry_claims(mapfile):
    def mut(m):
        m["leads"] = [{"id": "l-abc", "title": "X", "url": "https://example.com/x", "source": "example.com",
                       "date": None, "found": "2026-11-24", "matched": None, "branch_guess": None, "stage": "S2"}]
    r = run("check.py", mapfile(mut), "2026-11-24")
    assert r.returncode == 1


def test_derive_is_idempotent(mapfile, tmp_path):
    p = mapfile()
    run("derive.py", p, "2026-11-24")
    a = p.read_text()
    run("derive.py", p, "2026-11-24")
    assert p.read_text() == a
    m = json.loads(a)["entries"][0]
    assert m["last_progress"] == "2026-11-01"


def test_cache_check_catches_non_verbatim_quote(tmp_path):
    drafts = [{"id": "t1", "url": "https://example.com/a", "quote": "we shipped a product", "date": "2026-11-01",
               "passage": "On 1 Nov 2026 we released a prototype."}]
    d = tmp_path / "d.json"; d.write_text(json.dumps(drafts))
    r = run("cache_check.py", d, tmp_path)
    assert r.returncode == 1
    drafts[0]["quote"] = "we released a prototype"
    d.write_text(json.dumps(drafts))
    assert run("cache_check.py", d, tmp_path).returncode == 0


def test_cache_check_rejects_unseen_year(tmp_path):
    drafts = [{"id": "t1", "url": "https://example.com/a", "quote": "released v2", "date": "2026-04-21",
               "passage": "21 Apr — released v2"}]
    d = tmp_path / "d.json"; d.write_text(json.dumps(drafts))
    assert run("cache_check.py", d, tmp_path).returncode == 1


def _feed(tmp_path, mapfile, items, extra=()):
    p = mapfile(lambda m: m["project"].__setitem__("sources", [{"id": "s1", "name": "S1", "url": "https://example.com/news", "covers": ["t1"]}]))
    it = tmp_path / "items.json"; it.write_text(json.dumps({"items": items}))
    fd = tmp_path / "feed.json"
    out = tmp_path / "out"
    return p, it, fd, out


def test_feed_baseline_then_hits(tmp_path, mapfile):
    items = [{"url": "https://example.com/news/1", "title": "团队一 releases version 2 of the prototype", "date": "2026-11-23", "source_id": "s1", "relevant": True}]
    p, it, fd, out = _feed(tmp_path, mapfile, items)
    r = run("feed.py", p, fd, it, "2026-11-24", out)          # no feed.json yet -> baseline, no hits
    assert r.returncode == 0 and json.load(open(out / "hits.json")) == []
    items.append({"url": "https://example.com/news/2", "title": "T1 announces funding round for its prototype", "date": "2026-11-24", "source_id": "s1", "relevant": True})
    it.write_text(json.dumps({"items": items}))
    r = run("feed.py", p, fd, it, "2026-11-25", out, "--since", "2026-11-22")
    hits = json.load(open(out / "hits.json"))
    assert len(hits) == 1 and hits[0]["matched"] == ["t1"]


def test_feed_short_titles_do_not_collide_across_sources(tmp_path, mapfile):
    p, it, fd, out = _feed(tmp_path, mapfile, [])
    fd.write_text(json.dumps({"last_run": "2026-11-20", "seen": {}, "titles": {}}))
    items = [{"url": "https://github.com/a/x/releases/tag/v1.4.6", "title": "v1.4.6", "date": "2026-11-23", "source_id": "s1", "relevant": True},
             {"url": "https://github.com/b/y/releases/tag/v1.4.6", "title": "v1.4.6", "date": "2026-11-23", "source_id": "s2", "relevant": True}]
    it.write_text(json.dumps({"items": items}))
    r = run("feed.py", p, fd, it, "2026-11-24", out, "--since", "2026-11-18")
    assert "new 2" in r.stdout


def test_cost_report(tmp_path, mapfile):
    def mut(m): m["project"]["run_stats"] = [{"date": "2026-11-24", "usage_by_model": {"opus": {"input": 1_000_000, "output": 100_000}}}]
    r = run("cost.py", mapfile(mut))
    assert r.returncode == 0 and "6.00 USD" in r.stdout and "ESTIMATE" not in r.stdout
