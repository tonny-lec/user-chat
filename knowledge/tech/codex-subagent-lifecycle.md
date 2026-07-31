---
type: Consultation
title: Codex サブエージェントのライフサイクル — 使い回されるのは定義でありコンテキストではない
description: 「Codex はサブエージェントを使い回すのでコンテキストが混ざる」という懸念の事実確認。TOML は役割テンプレートで委譲ごとに新規 thread が spawn され親履歴も継承しない — 理想の運用（分割→新規→閉じる）はネイティブ挙動そのもの。Claude Code との機構比較と、委譲文の自己完結・1委譲1仕事・TOML への model/effort 焼き込み等の実践ポイント。
tags: [codex, subagent, claude-code, harness, context-management, lifecycle]
timestamp: 2026-07-31T00:00:00+09:00
---

# 相談内容

Codex のサブエージェントは「用意したサブエージェントをずっと使い回している」ように見える。
コンテキストが混ざるので、適切に分割したタスクを渡し、完了したらそのサブエージェントを閉じ、
次の作業では新しいサブエージェントを呼ぶべきではないか。Claude Code と比較して
Codex でよりよくサブエージェントを使う方法を知りたい。

# 検討・調査

公式ドキュメント（learn.chatgpt.com/docs/agent-configuration/subagents。
developers.openai.com/codex/subagents はここへ恒久リダイレクト）で事実確認（2026-07-31）。

## 確定した機構

- `.codex/agents/*.toml` は公式に「spawned session の **configuration layer**」＝**役割テンプレート**。
  永続インスタンスではない。
- ライフサイクル: 委譲ごとに新規 agent thread を **spawn → 実行 → サマリーを親に返す → thread close**。
- **親の会話履歴は継承しない**。サブエージェントが受け取るのは developer_instructions ＋ 委譲プロンプトのみ
  （継承されるのは sandbox・model・approvals 等の**設定**。AGENTS.md は通常どおり読む）。
- 完了後のスレッドに追加タスクを送る機構（Claude Code の SendMessage 相当）は**ない**。
  完了スレッドへの文書化された操作は close のみ。再依頼は必然的に新規 spawn。
- 実行中のスレッドには **steer**（追加指示）/ **stop** が可能。`/agent` で一覧・切替・検査。
- 並列は同時6スレッド（設定可）・ネスト深さ1（再帰委譲なし）。
  バッチ fan-out は `spawn_agents_on_csv`（CSV 行ごとに並列、各ワーカーが構造化返却）。
- 唯一公式に明文がないのは「同名エージェントへの再委譲時のスレッド再利用」だが、
  spawn/close の語彙と configuration layer の位置づけから新規起動が整合的な読み
  （第三者検証記事も同見解）。

## 前提の訂正

「使い回している」ように見えるのは**同じ役割定義（TOML）を繰り返し参照している**からで、
コンテキストは毎回まっさら。「定義の再利用」と「コンテキストの再利用」は別物で、
Codex がやっているのは前者だけ。懸念していた運用（分割したタスク→新規サブエージェント→
完了で閉じる）は **Codex のネイティブ挙動そのもの**であり、機構を追加する必要はない。

## Claude Code との機構比較

| 観点 | Claude Code | Codex CLI |
|---|---|---|
| 役割定義 | `.claude/agents/*.md`（再利用） | `.codex/agents/*.toml`（再利用） |
| 呼び出し単位 | Task/Agent 呼び出しごとに新規コンテキスト | 委譲ごとに新規 thread |
| 親履歴の継承 | 通常は継承しない（fork のみ全継承） | 継承しない（fork 相当なし） |
| 完了後の継続 | SendMessage で再開可能 | 不可（close のみ） |
| 実行中の介入 | 限定的 | steer / stop（`/agent` で検査） |
| 結果の返り方 | 最終メッセージ | サマリー（公式推奨） |
| 並列・ネスト | 並列可・ネスト可 | 同時6・深さ1 |
| バッチ fan-out | Workflow 等 | `spawn_agents_on_csv` |

# 結論: Codex でよりよく使う実践ポイント

1. **委譲プロンプトの自己完結**が最重要レバー。履歴非継承なので、目的・対象範囲・変更可否・
   成果物形式を毎回書き切る（workspace CLAUDE.md の「委譲時の指示」ルールがそのまま適用可能）。
2. **1委譲1仕事**。コンテキストが混ざる唯一の経路は、steer での無関係タスク注入と
   1委譲文への複数タスク詰め込み。steer は同じ仕事の軌道修正に限定する。
3. **役割 TOML に model / reasoning effort を焼き込む**。
   [ティア×effort 実測](/tech/gpt56-subagent-tier-effort-balance.md)の推奨
   （既定 terra/medium・実装 luna/medium・穴出し luna/high）を役割別 TOML に固定すれば、
   毎回指定なしで最適構成の新規起動になる。Claude Code より細かく制御できる Codex の強み。
4. **完了スレッドは close**。唯一「溜まる」のは開いたままのスレッド一覧。`/agent` で確認して閉じる。
5. **往復が要る仕事は設計で吸収**。SendMessage 相当がないため、レビュー→修正→再レビューは
   (a) スレッドを完了させず steer で回すか、(b) 状態をファイルに書かせて次の委譲文で引き継ぐか。
   長い往復は (b) が安全。

関連: [codex 単体ハーネス初手設計](/tech/codex-standalone-harness-bootstrap.md)（subagents の存在確認と
TOML の基本）、[ハーネスのトークン経済学](/tech/harness-token-economy.md)（サブエージェントが
トークンを増やす条件 — サマリー返却運用はここの「境界フィルタ」に該当）。

# Citations

[1] [Subagents | ChatGPT Learn（公式）](https://learn.chatgpt.com/docs/agent-configuration/subagents)
[2] [Codex CLI vs Claude Code Multi-Agent | Codex Knowledge Base](https://codex.danielvaughan.com/2026/04/09/codex-vs-claude-code-multi-agent/)
[3] [Multi-Agent Orchestration With Codex | Firecrawl](https://www.firecrawl.dev/blog/codex-multi-agent-orchestration)
