---
type: Reference
title: superpowers プラグイン解剖 — 公開ハーネスの実例読み解き
description: obra/superpowers (MIT) の hook・skill 構造を実物で読み解き、ハーネス設計の技術(強制の機械化・合理化潰し・skill の TDD)を抽出したメモ。
tags: [ai-agent, harness, claude-code, skills, hooks, superpowers]
timestamp: 2026-07-06T00:00:00+09:00
---

# 概要

[ハーネス基礎](/tech/ai-agent-harness-basics.md) の実例として、ローカルにインストール済みの
superpowers v6.1.1(`~/.claude/plugins/cache/claude-plugins-official/superpowers/`)を解剖した記録。
全コードは MIT で公開: https://github.com/obra/superpowers

# 構成

- `plugin.json` — メタデータのみ
- `hooks/` — SessionStart hook 1本(bash)+ Windows 用ポリグリッドラッパー `run-hook.cmd`
- `skills/` — 14 skill、合計約 3,300 行の Markdown。1 skill = 1 ディレクトリ + SKILL.md

# 設計技術(読み解きで抽出したもの)

1. **強制は機械、知識は文書に分離**。「skill を使え」というルールはモデルの記憶に頼らず、
   SessionStart hook がセッション開始のたびに `using-superpowers/SKILL.md` を
   `<EXTREMELY_IMPORTANT>` タグ付きでコンテキストに機械注入する。
2. **合理化の先回り潰し**。skill 本文の主要部は手順ではなく「Red Flags」
   「Common Rationalizations」表 — LLM がサボるときの内心の言い訳
   (「これは簡単だから手順不要」「緊急だから」等)を列挙して事前に反駁する。
   systematic-debugging では言い訳 8 種に対し 1 行ずつ反論が書かれている。
3. **フェーズゲート**。systematic-debugging は「Phase 1(根本原因調査)完了前に修正提案禁止」
   という Iron Law + 4 フェーズ構造。「3回修正に失敗したらアーキテクチャを疑い人間と相談」
   という脱出条件まで定義。
4. **skill 自体を TDD で作る**(writing-skills)。skill なしでエージェントが失敗する
   シナリオを先に観測(RED)→ skill を書く(GREEN)→ 新しい言い訳を見つけて塞ぐ(REFACTOR)。
   「失敗を観測してからルールを書く」原則のskill版。
5. **トークン効率**。頻繁にロードされる skill は 500 語以内を目標と明記。
   重い参照資料は別ファイルに分離し必要時のみ読む。
6. **泥臭い互換対応**。hook スクリプトは Cursor / Claude Code / Copilot CLI で
   JSON 出力形式を分岐し、Windows では cmd/bash ポリグロットで bash を探す。
   公開ハーネスの中身は魔法ではなく普通のエンジニアリング。

# 含まれる skill 一覧(役割別)

- プロセス系: brainstorming, systematic-debugging, test-driven-development, writing-plans
- 実行系: executing-plans, subagent-driven-development, dispatching-parallel-agents, using-git-worktrees
- 品質ゲート系: verification-before-completion, requesting/receiving-code-review, finishing-a-development-branch
- メタ系: using-superpowers(入口), writing-skills(skill の作り方)

# Citations

[1] [obra/superpowers (GitHub)](https://github.com/obra/superpowers)
