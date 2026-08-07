---
type: Consultation
title: TUI と headless（claude -p / codex exec）— 同じループエンジンの2つの入り口
description: 「ワンショット」は入力を1回渡すだけで中では TUI と同一の agentic loop が丸ごと回る（非対話 ≠ 非エージェント）。TUI はハーネスを育てる工程の入り口、headless は育ったハーネスを機械に運転させる工程の入り口。CI・cron・パイプライン・fan-out はすべて headless が土台で、規模が上がると CLI ワンショットから SDK へ進む。
tags: [ai-agent, harness, headless, cli, agentic-loop, orchestration]
timestamp: 2026-08-08T00:00:00+09:00
---

# 相談内容

harness や agentic loop を作っている人は、TUI を使わず `claude -p` や `codex exec` の
ワンショットだけで仕組みを動かしているのか？ コーディングエージェントは TUI で
対話的に使うものだと思っていたが、実は違うのか。

# 検討・調査

## 誤解の正体: 「ワンショット」≠「1回の LLM 呼び出し」

`claude -p "..."` / `codex exec "..."` は**入力を1回渡すだけ**であって、中では TUI と
完全に同じ agentic loop が回る — ツール実行、複数ターンの往復、hooks の発火、
サブエージェント起動まで全部。終わったら結果を stdout に吐いて終了するだけ。
**非対話（non-interactive）であって非エージェント（non-agentic）ではない。**

構造として、TUI が本体でヘッドレスが簡易版なのではなく、**ループエンジンが本体で
TUI はその上の人間用フロントエンド（一皮）**。両者は同じエンジンの2つの入り口。
だから TUI で育てた hooks / skills / CLAUDE.md（AGENTS.md）は headless 実行でも
そのまま発火する。

## 使い分けは「運転席に誰が座るか」

| 工程 | 入り口 | 理由 |
|---|---|---|
| ハーネスを**育てる**（hook 調整・失敗観測・デバッグ） | TUI | 人間がループの中にいて観察・介入する |
| 育ったハーネスを**機械に運転させる** | `-p` / `exec` | 自動化の中に人間が座っていない — 対話 UI は物理的に使えない |

「仕組みを動かす」側の実例はどれも headless が土台:

- **CI**: GitHub Actions の claude-code-action は内部的にヘッドレス実行。
- **cron / routines**: 定期実行に対話の余地がない。
- **パイプラインの1工程**: スクリプトが `codex exec` を呼び出力をパースして次工程へ
  （[SSSF cookbooks](/tech/sssf-cookbooks.md) の「agent proposes, code disposes」構成が典型 —
  決定論的コードがシーケンスを所有し、エージェントは境界付きノードとして headless 起動される）。
- **マルチエージェント fan-out**: オーケストレータが N 個のヘッドレス実行を並列起動。
  Claude Code の Agent / Workflow ツールも内部は同じ構図。
- **eval・回帰テスト**: 同じプロンプトを決定的に流して比較する。

## 段階論: CLI ワンショット → SDK

CLI の `-p` は「シェルから使える SDK」。jq とパイプで済む規模ならそれで十分。
構造化した制御（ストリーム処理・セッション継続・型付き応答）が要る規模になったら
Claude Agent SDK や `codex exec --json` のストリームパースへ進む。入り口の形式が
変わるだけで、回っているループは同じ。

# 結論

- harness / agentic loop を作る人は、**開発は TUI・運用は headless** の両輪で使う。
  「仕組みとして動かす」段では `-p` / `exec` が土台になる — 理由は単純で、
  自動化の中に人間が座っていないから。
- 「TUI で対話的にやるもの」という直感は**ハーネスを育てる工程については正しい**。
  変わるのは運転席が人間から機械に代わる瞬間。
- この構図の罠は既に自分の記録にもある:
  [サンドボックス下ハーネス開発のテスト環境](/tech/harness-dev-test-environment.md)の
  「`codex exec` はデフォルト read-only」は、まさにスクリプトから headless 起動する
  世界で踏む罠（TUI と headless で権限デフォルトが違う）。**入り口が2つある以上、
  設定・権限・環境のデフォルトが入り口ごとに違いうる**ことは headless 運用の
  チェックポイントになる。

# Citations

[1] 関連: [AIエージェントの「ハーネス」とは何か](/tech/ai-agent-harness-basics.md)、[サンドボックス下ハーネス開発のテスト環境](/tech/harness-dev-test-environment.md)、[SSSF cookbooks](/tech/sssf-cookbooks.md)
