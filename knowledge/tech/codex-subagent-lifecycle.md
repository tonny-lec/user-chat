---
type: Consultation
title: Codex サブエージェントのライフサイクル — スレッド再利用は機構でなく親モデルの選択、縛る場所は AGENTS.md
description: 「Codex はサブエージェントを使い回すのでコンテキストが混ざる」という懸念の事実確認。TOML は役割テンプレートで親履歴は非継承だが、multi-agent v2 の followup_task により既存スレッドへの ID 指定タスク追加（コンテキスト蓄積）が可能で、新規 spawn と再利用は親モデルの実行時判断。「新タスクは新規スレッド」は正しい規律だが実現場所は機構でなく AGENTS.md の明文ルール。Claude Code との機構比較付き。
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
- **親の会話履歴は継承しない**。サブエージェントが受け取るのは developer_instructions ＋ 委譲プロンプトのみ
  （継承されるのは sandbox・model・approvals 等の**設定**。AGENTS.md は通常どおり読む）。
- multi-agent v2 のオーケストレーションは **6プリミティブ**:
  `spawn_agent` / `send_message` / **`followup_task`** / `wait_agent` / `list_agents` / `close_agent`。
- **`followup_task` により、既存スレッドへ ID 指定で追加タスクを送れる**。そのスレッドの
  コンテキストは蓄積・継続する。「サブエージェント呼び出し時にセッションIDを指定して
  使い回しているように見える」という観測の正体はこれ（実際に使い回している）。
- close したスレッドには送れない。v2 では opaque な thread ID から path-based addressing に移行。
- 実行中のスレッドには steer / stop も可能。`/agent` で一覧・切替・検査。
- 並列は同時6スレッド（設定可）・ネスト深さ1（再帰委譲なし）。
  バッチ fan-out は `spawn_agents_on_csv`（CSV 行ごとに並列、各ワーカーが構造化返却）。

## 論点の同定: 再利用は機構の強制ではなく親モデルの実行時判断

新規 spawn（`spawn_agent`）と既存スレッドへの追加タスク（`followup_task`）は**同列の
プリミティブ**として存在し、どちらを選ぶかはオーケストレーター（親モデル）の裁量。
親にとってスレッド再利用は「ファイル再読み込み不要でトークンが安い」楽な選択肢なので、
**放っておくと再利用に寄る**（観測どおり）。つまり:

- 「定義（TOML）の再利用」と「スレッド（コンテキスト）の再利用」は別物で、後者も実在する。
- 「新タスクは新規スレッドで」という直観は正しい規律だが、**実現場所は機構ではなく
  AGENTS.md の明文ルール**。書いていない注意は払われない
  （[gpt-5.6 プロファイル](/tech/gpt-56-model-profile.md)の系 — 自由度を残すと親は楽な縮退解=再利用に落ちる）。

## Claude Code との機構比較

| 観点 | Claude Code | Codex CLI |
|---|---|---|
| 役割定義 | `.claude/agents/*.md`（再利用） | `.codex/agents/*.toml`（再利用） |
| 新規起動 | Task/Agent 呼び出し（新規コンテキスト） | `spawn_agent`（新規 thread） |
| 既存への追加タスク | SendMessage（完了後も再開可） | `followup_task`（close 前まで） |
| 親履歴の継承 | 通常は継承しない（fork のみ全継承） | 継承しない（fork 相当なし） |
| デフォルトの寄り | ハーネスが新規 spawn を既定に誘導 | 親モデルの裁量が大きく再利用に寄りがち |
| 実行中の介入 | 限定的 | steer / stop（`/agent` で検査） |
| 結果の返り方 | 最終メッセージ | サマリー（公式推奨） |
| 並列・ネスト | 並列可・ネスト可 | 同時6・深さ1 |
| バッチ fan-out | Workflow 等 | `spawn_agents_on_csv` |

両者とも「新規 or 継続」の二択を持つ点は同型。差は**デフォルトの癖** — Claude Code は
ハーネス側が「呼び出しごと新規」を既定に敷き、継続（SendMessage）を例外扱いにしている。
Codex は followup_task が同列にあり、選択が親モデルの判断に委ねられている。

# 結論: Codex でよりよく使う実践ポイント

1. **スレッド運用規律を AGENTS.md に明文化する**（本相談の核心）。例:
   「独立した新タスクは `spawn_agent` で新規スレッドを起動する。`followup_task` は
   同一タスクの軌道修正・追加質問・修正確認に限る。タスクが完了したスレッドは close する」。
   機構は両方許すので、縛らなければ親は再利用に寄る。
2. **再利用が正しい場面も残す**: 同じ仕事の反復（レビュー→修正→再確認）は、蓄積した文脈が
   価値になるので followup_task が適切。判断基準は「次のメッセージは同じ仕事の続きか、別の仕事か」。
   別の仕事なら新規 — 新規 spawn の追加コスト（ファイル再読み込み）は、無関係文脈の
   混入リスクより安い。
3. **委譲プロンプトの自己完結**。履歴非継承なので、目的・対象範囲・変更可否・
   成果物形式を毎回書き切る（workspace CLAUDE.md の「委譲時の指示」ルールがそのまま適用可能）。
4. **役割 TOML に model / reasoning effort を焼き込む**。
   [ティア×effort 実測](/tech/gpt56-subagent-tier-effort-balance.md)の推奨
   （既定 terra/medium・実装 luna/medium・穴出し luna/high）を役割別 TOML に固定すれば、
   毎回指定なしで最適構成の新規起動になる。Claude Code より細かく制御できる Codex の強み。
5. **規律が守られているか観測する**: SubagentStart / SubagentStop hook で spawn と followup を
   1行ログに落とせば、「新タスクなのに followup された」違反を事後検出できる
  （強制はプロンプト層・観測は hook 層、の分担）。

関連: [codex 単体ハーネス初手設計](/tech/codex-standalone-harness-bootstrap.md)（subagents の存在確認と
TOML の基本）、[ハーネスのトークン経済学](/tech/harness-token-economy.md)（サブエージェントが
トークンを増やす条件 — サマリー返却運用はここの「境界フィルタ」に該当）。

# Examples

## AGENTS.md オーケストレーション方針ブロック（現行版・2026-07-31）

hook なし・プロンプト層のみの運用（本人の選択: まず規律だけ入れて挙動を見る）。
AGENTS.md は常駐コンテキストなので、貼るのはこのブロックだけに絞る:

```markdown
## サブエージェント運用方針

- スレッドの選択: 独立した新タスクは新規スレッドを起動する（spawn_agent）。
  既存スレッドへの追加指示（followup_task）は「同一タスクの軌道修正・追加質問・
  修正結果の確認」に限る。判断基準は「次の依頼は直前の仕事の続きか」— 続きで
  なければ新規。迷ったら新規。
- タスクが完了し結果を受け取ったスレッドは close する。閉じずに次のタスクへ移らない。
- 委譲文は自己完結させる: 目的 / 対象範囲・ファイルパス / 変更可否（調査のみなら
  「編集禁止」と明記）/ 成果物と報告形式 / 「再委譲しないこと」。
  親会話の文脈は渡らない前提で毎回書き切る。
- サブエージェントには生ログでなく要約を報告させる（発見・リスク・推奨を file:line 付きで）。
- 独立した調査・作業が複数あるときは並列に spawn する（逐次に1つずつ起動しない）。
```

補足（AGENTS.md には書かない設計判断）:
- 役割別の model / reasoning effort は `.codex/agents/*.toml` 側に焼き込む
  （[ティア×effort 実測](/tech/gpt56-subagent-tier-effort-balance.md)の推奨構成）。
- 違反の観測（SubagentStart hook でのログ）は今回見送り。規律だけで挙動が
  変わるかをまず観測し、「新タスクなのに followup された」違反を体感したら hook 層を足す
  （[初手は観測](/tech/codex-standalone-harness-bootstrap.md)の原則）。

# 記録メモ（訂正履歴）

初稿は公式ドキュメントの spawn/close 語彙から「再依頼は必然的に新規 spawn」と書いたが、
ユーザーの実観測（呼び出し時のセッションID指定）の指摘を受けて調査し直し、
`followup_task` の存在を確認して同日中に訂正。教訓: 公式概要ページのライフサイクル記述は
プリミティブの全列挙ではない — ユーザーの実観測は仕様理解より強い証拠として扱う。

# Citations

[1] [Subagents | ChatGPT Learn（公式）](https://learn.chatgpt.com/docs/agent-configuration/subagents)
[2] [Codex CLI Multi-Agent Orchestration v2: Complete Guide | Codex Knowledge Base](https://codex.danielvaughan.com/2026/04/11/codex-cli-multi-agent-orchestration-v2-complete-guide/)
[3] [Codex Multi-Agent System Architecture（内部ツールセットの抽出 gist）](https://gist.github.com/serialx/f842f7b41d0f74ff5f64845e4afbc260)
[4] [Multi-Agent Orchestration With Codex | Firecrawl](https://www.firecrawl.dev/blog/codex-multi-agent-orchestration)
[5] [Codex CLI vs Claude Code Multi-Agent | Codex Knowledge Base](https://codex.danielvaughan.com/2026/04/09/codex-vs-claude-code-multi-agent/)
