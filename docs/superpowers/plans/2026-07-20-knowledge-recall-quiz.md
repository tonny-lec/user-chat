# /quiz knowledge 想起クイズ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** knowledge/ 文書の結論想起を鍛える対話式クイズ。履歴駆動で未出題・誤答文書を優先出題する `/quiz` スキルと選択・記録スクリプトを作る。

**Architecture:** 決定的な部分（文書スキャン・履歴突合・優先度計算・結果追記）は uv single-file Python スクリプト `quiz.py`、LLM にしかできない部分（出題文生成・自由回答の採点・解説）は SKILL.md の指示で Fable が担う。履歴は `quiz/history.jsonl` に追記式で git 管理。

**Tech Stack:** Python 3.11+（uv single-file、PEP 723、外部依存ゼロ）、pytest（`uv run --with pytest`）、Claude Code プロジェクトスキル。

**Spec:** `docs/superpowers/specs/2026-07-20-knowledge-recall-quiz-design.md`

## Global Constraints

- quiz.py は外部依存ゼロ（標準ライブラリのみ）。frontmatter の title は素朴な行パースで取る（YAML ライブラリを入れない）。
- 予約名 `index.md`・`log.md` は出題対象から除外する。
- verdict は `correct` / `partial` / `wrong` の3値のみ。
- quiz.py は git 操作をしない。
- 壊れた JSONL 行は stderr に警告してスキップし、処理を止めない。
- このリポジトリ（user-chat）は main に直接コミットする運用（親 CLAUDE.md のブランチ規則は適用外）。

## File Structure

```
.claude/skills/quiz/
├── SKILL.md                  # Task 3: Fable への手順書
└── scripts/
    ├── quiz.py               # Task 1-2: pick / record CLI
    └── test_quiz.py          # Task 1-2: pytest テスト
quiz/
└── history.jsonl             # 実行時に record が生成（コミットは運用に同乗）
```

---

### Task 1: quiz.py — pick（スキャン・履歴突合・優先度規則）

**Files:**
- Create: `.claude/skills/quiz/scripts/quiz.py`
- Test: `.claude/skills/quiz/scripts/test_quiz.py`

**Interfaces:**
- Produces: `scan_docs(root: Path, domain: str | None) -> list[str]`（knowledge/ 相対 posix パスのソート済みリスト）、`read_history(root: Path) -> dict[str, dict]`（path → 最新記録）、`pick(root: Path, domain: str | None) -> dict`（成功時 `{path, title, last_verdict, last_quizzed, stats}`、対象0件時 `{"error": ...}`）。Task 2 の CLI がこれらを呼ぶ。

- [ ] **Step 1: 失敗するテストを書く**

`.claude/skills/quiz/scripts/test_quiz.py` を作成:

```python
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
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `cd /home/tonny/workspace/user-chat && uv run --with pytest pytest .claude/skills/quiz/scripts/test_quiz.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'quiz'`（collection error）

- [ ] **Step 3: quiz.py の pick 部分を実装する**

`.claude/skills/quiz/scripts/quiz.py` を作成:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""knowledge 想起クイズの出題選択と履歴記録。

pick:   knowledge/**/*.md と quiz/history.jsonl を突合し、
        未出題 > wrong > partial > correct（各グループ内は受験日が古い順）で1件選ぶ。
record: 受験結果を quiz/history.jsonl に1行追記する。
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

RESERVED = {"index.md", "log.md"}
VERDICTS = ("correct", "partial", "wrong")
VERDICT_PRIORITY = {"wrong": 0, "partial": 1, "correct": 2}


def scan_docs(root: Path, domain: str | None) -> list[str]:
    knowledge = root / "knowledge"
    docs = []
    for p in sorted(knowledge.rglob("*.md")):
        if p.name in RESERVED:
            continue
        rel = p.relative_to(knowledge).as_posix()
        if domain and not rel.startswith(domain.rstrip("/") + "/"):
            continue
        docs.append(rel)
    return docs


def read_history(root: Path) -> dict[str, dict]:
    """path → 最新記録。履歴は追記式なので後の行が勝つ。"""
    latest: dict[str, dict] = {}
    hist = root / "quiz" / "history.jsonl"
    if not hist.exists():
        return latest
    for lineno, line in enumerate(hist.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            path, verdict, ts = record["path"], record["verdict"], record["ts"]
        except (json.JSONDecodeError, KeyError, TypeError):
            print(f"warning: history.jsonl:{lineno} 壊れた行をスキップ", file=sys.stderr)
            continue
        latest[path] = {"path": path, "verdict": verdict, "ts": ts}
    return latest


def read_title(root: Path, rel: str) -> str:
    lines = (root / "knowledge" / rel).read_text(encoding="utf-8").splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("title:"):
                return line[len("title:"):].strip()
    return rel


def pick(root: Path, domain: str | None) -> dict:
    docs = scan_docs(root, domain)
    if not docs:
        return {"error": "対象文書が0件（knowledge/ とドメイン指定を確認）"}
    history = read_history(root)
    quizzed = {p: history[p] for p in docs if p in history}
    unquizzed = [p for p in docs if p not in history]

    stats = {"total_docs": len(docs), "unquizzed": len(unquizzed)}
    for v in VERDICTS:
        stats[v] = sum(1 for r in quizzed.values() if r["verdict"] == v)
    stats = {k: stats[k] for k in ("total_docs", "unquizzed", "wrong", "partial", "correct")}

    if unquizzed:
        chosen, last = random.choice(unquizzed), None
    else:
        chosen = min(
            quizzed,
            key=lambda p: (VERDICT_PRIORITY.get(quizzed[p]["verdict"], 99), quizzed[p]["ts"]),
        )
        last = quizzed[chosen]
    return {
        "path": chosen,
        "title": read_title(root, chosen),
        "last_verdict": last["verdict"] if last else None,
        "last_quizzed": last["ts"] if last else None,
        "stats": stats,
    }
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `cd /home/tonny/workspace/user-chat && uv run --with pytest pytest .claude/skills/quiz/scripts/test_quiz.py -v`
Expected: PASS（11 passed）

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/quiz/scripts/quiz.py .claude/skills/quiz/scripts/test_quiz.py
git commit -m "feat(quiz): pick — 文書スキャン・履歴突合・優先度規則（未出題>wrong>partial>correct、古い順）"
```

---

### Task 2: quiz.py — record と CLI

**Files:**
- Modify: `.claude/skills/quiz/scripts/quiz.py`（末尾に record と main を追加）
- Test: `.claude/skills/quiz/scripts/test_quiz.py`（テスト追加）

**Interfaces:**
- Consumes: Task 1 の `pick(root, domain)`。
- Produces: `record(root: Path, path: str, verdict: str, question: str | None) -> dict`（追記した記録を返す。不正 verdict は `ValueError`）、CLI `quiz.py pick [--domain D] [--root P]` / `quiz.py record --path P --verdict V [--question Q] [--root P]`（stdout に JSON、エラー時 exit code 1）。Task 3 の SKILL.md がこの CLI を呼ぶ。

- [ ] **Step 1: 失敗するテストを書く**

`test_quiz.py` の末尾に追加:

```python
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
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `cd /home/tonny/workspace/user-chat && uv run --with pytest pytest .claude/skills/quiz/scripts/test_quiz.py -v`
Expected: FAIL — `AttributeError: module 'quiz' has no attribute 'record'`（Task 1 のテストは PASS のまま）

- [ ] **Step 3: record と main を実装する**

`quiz.py` の末尾（`pick` の後）に追加:

```python
def record(root: Path, path: str, verdict: str, question: str | None) -> dict:
    if verdict not in VERDICTS:
        raise ValueError(f"verdict は {VERDICTS} のいずれか: {verdict!r}")
    entry = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "path": path,
        "verdict": verdict,
    }
    if question:
        entry["question"] = question
    hist = root / "quiz" / "history.jsonl"
    hist.parent.mkdir(parents=True, exist_ok=True)
    with hist.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_pick = sub.add_parser("pick", help="優先度規則で出題文書を1件選ぶ")
    p_pick.add_argument("--domain", help="knowledge/ 直下のサブディレクトリ名で絞る（例: tech）")
    p_pick.add_argument("--root", type=Path, default=Path.cwd(), help="リポジトリルート（既定: cwd）")

    p_rec = sub.add_parser("record", help="受験結果を履歴に追記する")
    p_rec.add_argument("--path", required=True, help="knowledge/ 相対の文書パス")
    p_rec.add_argument("--verdict", required=True, choices=VERDICTS)
    p_rec.add_argument("--question", help="出題の一行要約")
    p_rec.add_argument("--root", type=Path, default=Path.cwd())

    args = parser.parse_args()
    if args.command == "pick":
        result = pick(args.root, args.domain)
    else:
        try:
            result = record(args.root, args.path, args.verdict, args.question)
        except ValueError as e:
            result = {"error": str(e)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if "error" in result else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `cd /home/tonny/workspace/user-chat && uv run --with pytest pytest .claude/skills/quiz/scripts/test_quiz.py -v`
Expected: PASS（17 passed）

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/quiz/scripts/quiz.py .claude/skills/quiz/scripts/test_quiz.py
git commit -m "feat(quiz): record と CLI — JSONL 追記、verdict 検証、pick/record サブコマンド"
```

---

### Task 3: SKILL.md と実環境での動作確認

**Files:**
- Create: `.claude/skills/quiz/SKILL.md`

**Interfaces:**
- Consumes: Task 2 の CLI（`uv run .claude/skills/quiz/scripts/quiz.py pick|record`）。
- Produces: `/quiz` として呼べるプロジェクトスキル。

- [ ] **Step 1: SKILL.md を書く**

`.claude/skills/quiz/SKILL.md` を作成:

````markdown
---
name: quiz
description: knowledge/ 文書の結論想起クイズ。ユーザーが /quiz を呼んだ、または「クイズ出して」「理解度を試したい」と言ったときに使用。履歴駆動で未出題・誤答文書を優先出題し、自由回答を3段階で採点して記録する。
---

# knowledge 想起クイズ

knowledge/ の文書の「結論」を思い出せるかを試す。選択と記録はスクリプト、出題と採点だけを担う。

## フロー

1. **選ぶ**: `uv run .claude/skills/quiz/scripts/quiz.py pick` を実行。
   ユーザーが領域を指定していれば `--domain <dir>`（例: `/quiz tech` → `--domain tech`）。
   `error` が返ったら内容を伝えて終了。
2. **読む**: 選ばれた `knowledge/<path>` を読む。
3. **出題する**: `# 結論` の内容を隠した想起問題を1問出す。
   - 見せてよい: title、`# 相談内容` にある背景・問い。
   - 見せない: 結論・要点・推奨・結論を示唆する見出し。
   - pick の stats から進捗を1行添える（例: 「未出題 60/66」）。
4. **待つ**: ユーザーの回答が来るまで採点しない。ヒントを求められたら結論そのものではなく文脈を1つだけ足す。
5. **採点する**（3段階）。解説では文書の実際の結論を引用し、回答との差分（言えた点・欠けた点）を必ず示す:
   - `correct` — 結論の核心的主張を自分の言葉で再現できている。
   - `partial` — 方向は合っているが、核心の一部または重要な限定条件が欠けている。
   - `wrong` — 核心を再現できていない、または逆のことを言っている。
6. **記録する**: `uv run .claude/skills/quiz/scripts/quiz.py record --path <path> --verdict <verdict> --question "<出題の一行要約>"`
7. **続ける?**: 「もう1問?」と聞く。続行なら 1 へ。終了時、`quiz/history.jsonl` の変更はセッション終わりの knowledge commit に含める。

## 境界

- 採点を甘くしない。partial と correct の境界は「限定条件まで言えたか」。
- 1回の出題は1文書1問。複数文書をまたぐ問題は作らない。
- quiz.py を編集しない（バグを見つけたら報告のみ）。
````

- [ ] **Step 2: 実環境で pick を動作確認する**

Run: `cd /home/tonny/workspace/user-chat && uv run .claude/skills/quiz/scripts/quiz.py pick`
Expected: exit 0、実在する文書パスと `"unquizzed": 67` 相当の stats を含む JSON（66+今回の新規文書。件数は実行時点の文書数に一致すること）

Run: `cd /home/tonny/workspace/user-chat && uv run .claude/skills/quiz/scripts/quiz.py pick --domain tech`
Expected: exit 0、`tech/` 配下のパス

- [ ] **Step 3: 実環境で record → pick の履歴反映を確認し、確認後に履歴を消す**

```bash
cd /home/tonny/workspace/user-chat
uv run .claude/skills/quiz/scripts/quiz.py record --path tech/ai-agent-harness-basics.md --verdict wrong --question "動作確認"
cat quiz/history.jsonl
rm quiz/history.jsonl   # 動作確認の偽データを残さない
```

Expected: record が JSON を返し、cat で1行の JSONL が見える。rm 後はクリーン。

- [ ] **Step 4: 全テストを最終確認する**

Run: `cd /home/tonny/workspace/user-chat && uv run --with pytest pytest .claude/skills/quiz/scripts/test_quiz.py -v`
Expected: PASS（17 passed）

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/quiz/SKILL.md
git commit -m "feat(quiz): SKILL.md — /quiz の出題・採点・記録フローと境界"
```
