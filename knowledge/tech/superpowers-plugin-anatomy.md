---
type: Reference
title: superpowers プラグイン解剖 — 公開ハーネスの実例読み解き
description: obra/superpowers (MIT) の hook・skill 構造を実物で読み解き、ハーネス設計の技術(強制の機械化・合理化潰し・skill の TDD)を抽出したメモ。続編で brainstorming(要件聞き出し)を深掘り — 1問1答プロトコル・HARD-GATE・digraph 状態機械・多層レビュー・visual companion(唯一のコード実装)。
tags: [ai-agent, harness, claude-code, skills, hooks, superpowers, requirements]
timestamp: 2026-07-25T00:00:00+09:00
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

# 続編: brainstorming の解剖 — 要件聞き出しの設計 (2026-07-25, v6.2.0)

「要件をユーザーから聞き出す仕組み」と「コンテキスト収集のハーネス」を目的に
brainstorming skill を深掘りした。結論: **コンテキスト収集をコードで行う機構はほぼ無く、
本体は会話プロトコルの明文化 + ゲートによる強制**。

## 聞き出しの会話プロトコル

- **1 メッセージ 1 質問**。選択式を優先、焦点は purpose / constraints / success criteria の 3 点のみ。
- **質問より先にスコープ判定**。複数サブシステムを含む要求なら質問を始めずに先に分解する
  (「分解が必要なプロジェクトの詳細に質問を浪費しない」)。分解後はサブプロジェクトごとに
  spec → plan → 実装のサイクルを回す。
- コンテキスト収集の実体は「ファイル・docs・直近コミットを探索せよ」という手順書 1 行。
  収集ハーネス(コード)は存在しない。
- 2〜3 案をトレードオフ付きで提示、推奨案を先頭に。全案に YAGNI を適用。
- デザインは**セクション単位で提示し、セクションごとに承認を取る**(全体一括承認にしない)。

## 強制の仕掛け

- `<HARD-GATE>` タグ: デザイン承認まで実装行為を一切禁止。
  さらに「簡単すぎて設計不要」という典型的逃げ道を Anti-Pattern 節で名指しで封鎖
  (todo リスト 1 個でも設計を書け)。
- **プロセスを Graphviz digraph で記述**: 承認ループ(no → revise)を含む状態機械として定義し、
  終端状態を「writing-plans の起動」1 つに固定。他の実装スキルへの分岐を明示的に禁止。
- 出口は多層レビュー: ①セルフレビュー(プレースホルダ・矛盾・曖昧さ・スコープの 4 点)
  → ②ユーザーレビューゲート → ③サブエージェントレビュアー(別ファイルのプロンプトテンプレート。
  「実装計画を壊す問題だけ指摘、文体指摘は禁止」という Calibration 節で指摘の閾値を較正)。

## visual companion — brainstorming 唯一のコード実装

- ローカル HTTP + WebSocket サーバー(`scripts/server.cjs`)。Claude が HTML モックアップを
  ディレクトリに書く → ブラウザが最新ファイルを自動表示 → ユーザーのクリック選択が
  `state_dir/events` に記録され次ターンで Claude が読む、という**ファイルシステム経由の非同期対話チャネル**。
- URL にセッションキーを付与しアクセス制御。HTML はフラグメントで書けばフレームに自動ラップ。
- 過剰使用を抑える規律が本体: 「先に提案するな(視覚で見せた方が明確な質問が初めて出たときだけ、
  単独メッセージで提案)」「承認後も質問ごとにターミナル/ブラウザを判定(UI の話題 ≠ 視覚的質問)」。

## ハーネス細部の追記 (v6.2.0)

- hooks.json の matcher は `startup|clear|compact` — /clear やコンパクト後も再注入される。
- Claude Code は `additional_context` と `hookSpecificOutput` を重複読みするため、
  プラットフォームを環境変数で判別し**片方だけ emit** する(両方出すと二重注入)。
- bash 5.3+ のヒアドキュメントhang回避で printf を使う、などの実戦の傷跡コメントが残っている。

# 含まれる skill 一覧(役割別)

- プロセス系: brainstorming, systematic-debugging, test-driven-development, writing-plans
- 実行系: executing-plans, subagent-driven-development, dispatching-parallel-agents, using-git-worktrees
- 品質ゲート系: verification-before-completion, requesting/receiving-code-review, finishing-a-development-branch
- メタ系: using-superpowers(入口), writing-skills(skill の作り方)

# Citations

[1] [obra/superpowers (GitHub)](https://github.com/obra/superpowers)
