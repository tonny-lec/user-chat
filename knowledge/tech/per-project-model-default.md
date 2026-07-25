---
type: Playbook
title: プロジェクト単位で Claude Code のモデルを固定する — /model はグローバルに書く
description: /model コマンドは ~/.claude/settings.json に全プロジェクト共通で保存されるため、特定プロジェクトだけモデルを変えたいときはプロジェクトの .claude/settings.json に model + effortLevel を書き、グローバル側を元に戻す2段構え。
tags: [claude-code, settings, model]
timestamp: 2026-07-25T00:00:00+09:00
---

# 課題

「このプロジェクトだけデフォルトモデルを変えたい」。しかし `/model` で選ぶと
**グローバル** (`~/.claude/settings.json` の `model` キー) に保存され、全プロジェクトに効いてしまう。

# 手順

1. **プロジェクト側に固定を書く** — `<project>/.claude/settings.json` に追記:

   ```json
   {
     "model": "claude-fable-5[1m]",
     "effortLevel": "high"
   }
   ```

   - 設定の合成順は user → project → local（後勝ち）。project の `model` が user 設定を上書きする。
   - `[1m]` サフィックスは 1M コンテキスト版の指定。`/model` の UI で選ぶと付くことがあるので、意図した値かを確認する。
   - このマシンだけにしたい場合は `settings.local.json`（gitignore 済み）に書く。リポジトリに追従させたいなら `settings.json` にコミット。

2. **グローバル側を元に戻す** — `/model` が書き換えた `~/.claude/settings.json` の `model` を以前の値に戻す。

3. **検証** — `jq -e '.model, .effortLevel' <file>` で両ファイルの JSON 構文と値を確認。

4. **反映は次セッションから**。モデルは起動時に決まるため、開いているセッションには効かない。

# 元の値が分からないときの復元手がかり

- `~/.claude/settings.json.bak` — 直近の自動バックアップ。
- `~/.claude.json` — `grep -o '"model"[^,]*' ~/.claude.json` でプロジェクト別の履歴的な model 値が拾え、変遷（例: opus-4-7 → opus-5 → fable-5）が読める。
- `fallbackModel` 配列の先頭も「以前の常用モデル」の傍証になる。
- `~/.claude` は git 管理外なのでコミット履歴には頼れない。

# Examples

user-chat（この部屋）に適用済み: プロジェクト側 `claude-fable-5[1m]` + `high`、
グローバルは `claude-opus-5` に戻した（2026-07-25, commit f7b3ea4）。

関連: [このPCのエージェント資産マップ](/tech/my-agent-assets-map.md)
