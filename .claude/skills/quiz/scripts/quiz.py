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
