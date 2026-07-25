---
type: Reference
title: hermes-agent / pi / Archon 比較 — 3つは競合ではなくスタックの別の層
description: NousResearch hermes-agent（自己改善する常駐パーソナルエージェント）、badlogic の pi（最小主義の自己拡張コーディングハーネス）、coleam00 の Archon（エージェントを部品として編成するワークフローエンジン）の比較。3者は同一カテゴリの競合ではなく層が違い、Archon は pi を実際にプロバイダとして取り込んでいる。
tags: [ai-agent, harness, comparison, oss]
timestamp: 2026-07-25T00:00:00+09:00
---

# 質問

hermes-agent / pi / Archon の3つのAIエージェントを比較したい。

# 結論 — 3つは競合ではなく層が違う

| | hermes-agent | pi | Archon |
|---|---|---|---|
| 一言 | 自己改善する常駐パーソナルエージェント | 最小主義のコーディングエージェント／ハーネス | エージェントを部品として編成するワークフローエンジン（自身は LLM を持たない） |
| 層 | エージェント本体（汎用・生活密着） | エージェント本体（コーディング特化） | エージェントの**上**のオーケストレーション層 |
| 開発元 | Nous Research（Hermes モデルの開発元） | Mario Zechner (badlogic, libgdx 作者) / Earendil Works | Cole Medin (coleam00, AI系YouTuber) |
| 設計思想 | 学習ループ内蔵の最大主義（スキル自動生成・メモリ・自己改善） | 最小主義＋自己拡張（ツール4つ・プロンプト1k トークン未満・MCP 拒否） | 「賢いエージェントより決定論的プロセス」（YAML ワークフロー・検証ゲート） |
| モデル/実行部 | 18+ プロバイダ、ChatGPT/Claude/Copilot サブスク流用（グレーゾーン込み） | 主要プロバイダ＋ローカル、サブスク OAuth、プロバイダ間コンテキスト引継ぎ | Claude Code / Codex / **pi** の3 SDK をラップ |
| IF | TUI・メッセージング6種・デーモン常駐・デスクトップ・ACP | TUI・print/JSON・RPC・SDK | CLI・Web UI (Mission Control)・Slack/Telegram/GitHub Webhook |
| 言語/ライセンス | Python / MIT | TypeScript / MIT | TypeScript (Bun) / MIT |
| Stars (2026-07-25 実測) | 220k | 77k | 23k |

- **hermes-agent**: 「育つエージェント」。スキル自動生成・使用中自己改善・クロスセッション記憶の閉ループが売り。裏の目的はエージェント利用トラジェクトリを Hermes モデルの学習に還流させるデータフライホイール（README に research-ready と明記）。実行系は local/Docker/SSH/Modal/Daytona 等6バックエンド。
- **pi**: Claude Code への反動（アップデートで壊れる・注入コンテキストが不透明）から生まれた「完全に可視で安定なハーネス」。ツールは read/write/edit/bash の4つのみ、MCP を明確に拒否し「拡張は pi 自身に TypeScript で書かせる」。パーミッションシステムを意図的に持たず OS レベル隔離を案内する正直さ。OpenClaw が pi のコンポーネント上に構築されている。
- **Archon**: 3度ピボットした現行版（2026-04〜）は「harness builder」。開発ワークフローを YAML の DAG（固定ステップ＋AI ステップ＋ゲート）で定義し、実行ごとに git worktree を切って艦隊並列実行。全プロンプト・diff の監査証跡付き。**MCP サーバー / RAG / タスク管理は旧第2期(Python)の話**で、現行版とは別物 — Web 上の解説は世代の区別に注意。

## 関係図（3者はつながっている）

- Archon は pi を第3のプロバイダとして統合済み（pi のマルチプロバイダ性で Gemini/Groq 等を一括獲得。Issue #965）。pi が計画を書き人間が承認して Claude Code が実装する混成ワークフローも存在。
- hermes-agent は OpenClaw の競合（移行コマンド持ち）で、その OpenClaw は pi 上に構築されている。

## 選び方

- 常駐する生活アシスタント（メッセージング・cron・記憶）が欲しい → hermes-agent
- 自分専用に改造し尽くせる透明なコーディングエージェントが欲しい → pi
- 既存エージェント（Claude Code 等）の作業を反復可能なプロセスに固定し並列化したい → Archon（エージェントの代替ではなく上に被せる）

## 一般化できる知見

- 2026年のエージェント OSS は「エージェント本体の優劣」から「層の分化」へ移行: 本体（hermes/pi）・ハーネス編成層（Archon）・実行部品化（Archon が Claude Code や pi を SDK として扱う）。「どれが強いか」より「どの層の道具か」を先に問うのが正しい比較軸。
- モデル屋が作るエージェント（hermes）にはデータフライホイール動機が埋まっている。個人が作るエージェント（pi）は既存品の複雑性への反動が動機。コミュニティ発（Archon）は潮流追随のピボットが激しい — 出自が設計思想を予言する。

関連: [hermes-agent の ChatGPT サブスクログイン実装](/tech/hermes-agent-chatgpt-login.md)

# Citations

[1] [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
[2] [Hermes Agent 公式ドキュメント: Architecture](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture)
[3] [earendil-works/pi（旧 badlogic/pi-mono）](https://github.com/badlogic/pi-mono)
[4] [Mario Zechner: What I learned building an opinionated and minimal coding agent](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)
[5] [Armin Ronacher: Pi: The Minimal Agent Within OpenClaw](https://lucumr.pocoo.org/2026/1/31/pi/)
[6] [coleam00/Archon](https://github.com/coleam00/Archon)
[7] [archon.diy](https://archon.diy)
[8] [Better Stack: Archon AI 解説](https://betterstack.com/community/guides/ai/archon-ai/)
[9] [Archon Issue #965: Pi 統合](https://github.com/coleam00/Archon/issues/965)
