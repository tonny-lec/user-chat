---
type: Consultation
title: エージェントの resilience 2層 — 実行基盤の復旧（層A）と判断の立て直し（層B）
description: LangChain の resilience 発表（retry / recovery path / resume / model fallback）の解釈。発表の実体は実行基盤の durable execution（層A）であり、エージェント自身の作業失敗からの自己復帰（層B）とは別物、という層の分離。
tags: [ai-agent, resilience, durable-execution, langgraph, langchain]
timestamp: 2026-08-05T00:00:00+09:00
---

# 相談内容

LangChain が Deep Agents / LangGraph / LangChain への resilience 機能追加を発表
（"retry interrupted work, follow a safe recovery path, resume from a saved state
instead of starting over, and automatically fall back to alternative models when the
primary model fails"）。「こういうエージェントを作ってみたい」が出発点。

途中で2つの解釈仮説が出た:

1. ユーザー仮説①「ここでいう resilience はエージェントの記憶力の話」
2. ユーザー仮説②「障害とはシステム障害ではなく、エージェントが途中で失敗しても
   自力で復帰できるハーネス・自己改善の話」

# 検討・調査

原典と周辺ドキュメントを確認した結果、発表の「障害」は**システム障害**
（プロセス中断・API レート制限・タイムアウト・モデル API 障害）であり、
エージェントの判断ミスの話ではない。根拠:

- "fall back to alternative models **when the primary model fails**" の fails は
  API 呼び出しの失敗。LangChain には実際に `.with_fallbacks()`（API 冗長化）がある。
- LangGraph ドキュメントはこれらを durable execution（checkpoint からの復旧で
  プロセス断を生き延びる）として説明している。

仮説①の検定: 4機能のうち純粋に「記憶」なのは resume のみ。ただし残り3つも
記憶を土台に初めて成立する —

| 機能 | 記憶との関係 |
|---|---|
| resume | 記憶そのもの。保存 state から再開 |
| retry | 「最後の正常 checkpoint から再実行」が肝。記憶がなければ retry = 全部やり直し |
| recovery path | 「安全な」= 一貫性のある保存状態を起点に迂回する、の意 |
| model fallback | 唯一記憶の話ではない（呼び出し層の冗長化）。ただしタスク途中の差し替えには文脈（記憶）の引き渡しが要る |

単一原理への圧縮: **「実行の進捗をプロセス外の記憶に外部化し、何が死んでも
（プロセス・呼び出し・モデル）記憶から続きを編み直せること」= durable execution**。
記憶は土台、4機能は「障害時に記憶からどう続けるか」の4ポリシー。
[LangGraph の概念](/tech/langgraph-concepts.md)の「checkpointer から resume /
time-travel / HITL がタダで出る」の続編として「resilience もタダで出る」を確かめる構図。

# 結論

エージェントの resilience は2層に分離して扱う:

- **層A: 実行の resilience（発表の実体）** — 失敗の主体はインフラ。
  プロセスが死ぬ・API が落ちる → 記憶から続きを再開する。判断の質とは無関係な配管。
- **層B: 判断の resilience（仮説②が指していたもの）** — 失敗の主体はエージェント自身。
  誤った方針・行き詰まりを検知して立て直す。lets-deep-agents の
  failure-review / failure-dashboard の系譜。

重要な帰結: **判断が悪いまま resume すれば、悪い判断のまま忠実に続きをやるだけ**。
層Aは層Bを代替しない（逆も然り）。どちらを作るかで設計が根本から変わるため、
構築相談ではまず層を確定させる。

## 進行中

学習プロジェクトとしてどちらの層を題材にするかは選択中（brainstorming 継続中）。
決まり次第この文書か後続の Decision 文書に追記する。

# Citations

[1] [Durable Execution in LangGraph: Agents That Survive Failure](https://vadim.blog/durable-execution-agents-that-survive-failure-and-resume-where-they-left-off)
[2] [LangGraph Error Handling: Retries & Fallback Strategies](https://machinelearningplus.com/gen-ai/langgraph-error-handling-retries-fallback-strategies/)
[3] [langchain-ai/langgraph — "Build resilient agents."](https://github.com/langchain-ai/langgraph)
