"""quiz.py のテスト。pytest が test ファイルの dir を sys.path に入れるので直接 import できる。"""

import json

import quiz


def make_doc(root, rel, title=None):
    p = root / "knowledge" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    front = f"---\ntype: Consultation\ntitle: {title or rel}\n---\n" if title else ""
    p.write_text(front + f"# 相談内容\n\nbody of {rel}\n\n# 結論\n\nconclusion of {rel}\n", encoding="utf-8")


def make_history(root, records):
    hist = root / "quiz" / "history.jsonl"
    hist.parent.mkdir(parents=True, exist_ok=True)
    lines = [r if isinstance(r, str) else json.dumps(r, ensure_ascii=False) for r in records]
    hist.write_text("\n".join(lines) + "\n", encoding="utf-8")


def rec(path, verdict, ts):
    return {"ts": ts, "path": path, "verdict": verdict}


def test_scan_excludes_index_and_log(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    make_doc(tmp_path, "tech/index.md")
    make_doc(tmp_path, "log.md")
    make_doc(tmp_path, "work/b.md")
    assert quiz.scan_docs(tmp_path, None) == ["tech/a.md", "work/b.md"]


def test_scan_domain_filter(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    make_doc(tmp_path, "work/b.md")
    assert quiz.scan_docs(tmp_path, "tech") == ["tech/a.md"]


def test_read_history_missing_file_is_empty(tmp_path):
    assert quiz.read_history(tmp_path) == {}


def test_read_history_last_record_wins_and_broken_lines_skipped(tmp_path, capsys):
    make_history(tmp_path, [
        rec("tech/a.md", "wrong", "2026-07-01T10:00:00+09:00"),
        "{broken json",
        rec("tech/a.md", "correct", "2026-07-10T10:00:00+09:00"),
    ])
    latest = quiz.read_history(tmp_path)
    assert latest["tech/a.md"]["verdict"] == "correct"
    assert "壊れた行" in capsys.readouterr().err


def test_pick_no_docs_returns_error(tmp_path):
    (tmp_path / "knowledge").mkdir()
    assert "error" in quiz.pick(tmp_path, None)


def test_pick_prefers_unquizzed(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    make_doc(tmp_path, "tech/b.md")
    make_history(tmp_path, [rec("tech/a.md", "wrong", "2026-07-01T10:00:00+09:00")])
    result = quiz.pick(tmp_path, None)
    assert result["path"] == "tech/b.md"
    assert result["last_verdict"] is None
    assert result["last_quizzed"] is None
    assert result["stats"] == {"total_docs": 2, "unquizzed": 1, "wrong": 1, "partial": 0, "correct": 0}


def test_pick_wrong_beats_partial_and_correct(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    make_doc(tmp_path, "tech/b.md")
    make_doc(tmp_path, "tech/c.md")
    make_history(tmp_path, [
        rec("tech/a.md", "correct", "2026-07-01T10:00:00+09:00"),
        rec("tech/b.md", "wrong", "2026-07-10T10:00:00+09:00"),
        rec("tech/c.md", "partial", "2026-07-02T10:00:00+09:00"),
    ])
    result = quiz.pick(tmp_path, None)
    assert result["path"] == "tech/b.md"
    assert result["last_verdict"] == "wrong"


def test_pick_same_verdict_oldest_first(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    make_doc(tmp_path, "tech/b.md")
    make_history(tmp_path, [
        rec("tech/a.md", "correct", "2026-07-10T10:00:00+09:00"),
        rec("tech/b.md", "correct", "2026-07-01T10:00:00+09:00"),
    ])
    assert quiz.pick(tmp_path, None)["path"] == "tech/b.md"


def test_pick_ignores_history_of_deleted_docs(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    make_history(tmp_path, [
        rec("tech/deleted.md", "wrong", "2026-07-01T10:00:00+09:00"),
        rec("tech/a.md", "correct", "2026-07-02T10:00:00+09:00"),
    ])
    result = quiz.pick(tmp_path, None)
    assert result["path"] == "tech/a.md"
    assert result["stats"]["total_docs"] == 1


def test_pick_domain_filter_applies_rules_within_domain(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    make_doc(tmp_path, "work/b.md")
    make_history(tmp_path, [rec("work/b.md", "wrong", "2026-07-01T10:00:00+09:00")])
    assert quiz.pick(tmp_path, "work")["path"] == "work/b.md"


def test_pick_reads_frontmatter_title(tmp_path):
    make_doc(tmp_path, "tech/a.md", title="実験の題名")
    assert quiz.pick(tmp_path, None)["title"] == "実験の題名"


import subprocess
import sys as _sys
from pathlib import Path as _Path

import pytest

QUIZ_PY = _Path(quiz.__file__)


def test_record_appends_line(tmp_path):
    result = quiz.record(tmp_path, "tech/a.md", "partial", "結論は？")
    line = (tmp_path / "quiz" / "history.jsonl").read_text(encoding="utf-8").strip()
    saved = json.loads(line)
    assert saved == result
    assert saved["path"] == "tech/a.md"
    assert saved["verdict"] == "partial"
    assert saved["question"] == "結論は？"
    assert saved["ts"]  # ISO 8601 が入っている


def test_record_appends_not_overwrites(tmp_path):
    quiz.record(tmp_path, "tech/a.md", "correct", None)
    quiz.record(tmp_path, "tech/b.md", "wrong", None)
    lines = (tmp_path / "quiz" / "history.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert "question" not in json.loads(lines[0])


def test_record_rejects_bad_verdict(tmp_path):
    with pytest.raises(ValueError):
        quiz.record(tmp_path, "tech/a.md", "maybe", None)


def run_cli(args, cwd):
    return subprocess.run(
        [_sys.executable, str(QUIZ_PY), *args],
        capture_output=True, text=True, cwd=cwd,
    )


def test_cli_pick_outputs_json(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    proc = run_cli(["pick", "--root", str(tmp_path)], cwd=tmp_path)
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["path"] == "tech/a.md"


def test_cli_pick_error_exits_1(tmp_path):
    (tmp_path / "knowledge").mkdir()
    proc = run_cli(["pick", "--root", str(tmp_path)], cwd=tmp_path)
    assert proc.returncode == 1
    assert "error" in json.loads(proc.stdout)


def test_cli_record_roundtrip(tmp_path):
    make_doc(tmp_path, "tech/a.md")
    proc = run_cli(
        ["record", "--path", "tech/a.md", "--verdict", "correct", "--question", "Q?", "--root", str(tmp_path)],
        cwd=tmp_path,
    )
    assert proc.returncode == 0
    assert quiz.read_history(tmp_path)["tech/a.md"]["verdict"] == "correct"
