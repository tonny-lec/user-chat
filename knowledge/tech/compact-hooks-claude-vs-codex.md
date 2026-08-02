---
type: Reference
title: PreCompact/PostCompact フック — Claude Code と Codex CLI の比較
description: 両ハーネスとも pre/post 両フックを持つ（2026-08 現在）。差分は有無ではなくブロック方式（decision:block vs continue:false）と要約への介入可否。ネット上の「片方にはない」情報は古い。Codex が要約介入を拒否した設計意図の考察（仮説）付き。
tags: [claude-code, codex, hooks, compaction, harness, design-philosophy]
timestamp: 2026-08-03T00:00:00+09:00
---

# PreCompact/PostCompact フック — Claude Code と Codex CLI の比較

## TL;DR

**2026-08 現在、両ハーネスとも PreCompact / PostCompact の両方を持つ。**
「Claude Code に PostCompact はない（SessionStart source:compact で代替）」
「Codex にフック機構はない」はどちらも**古い情報**。実務上の差分は
①要約への介入可否 ②ブロックのセマンティクス の 2 点。

## 比較表

| 観点 | Claude Code | Codex CLI |
|---|---|---|
| PreCompact / PostCompact | 両方あり | 両方あり（PR #19905、2026-05-07 merge。現在 Stable・デフォルト有効） |
| matcher | `manual` / `auto` | 同じ（`trigger` への regex） |
| compaction のブロック | exit code 2 または `{"decision": "block"}` | `{"continue": false}` で停止。`decision:block`/exit 2 は**意図的に非サポート**（PR の Out of Scope） |
| 要約への介入 | PreCompact の `hookSpecificOutput.additionalContext` で compact 指示に追加可能 | **不可**。要約内容・プレビュー・カスタム指示はフックに渡されない（明示的にスコープ外） |
| 入力ペイロード | `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `compaction_trigger` | `session_id`, `turn_id`, `subagent`, `cwd`, `transcript_path`, `model`, `trigger` |
| PostCompact | ブロック不可。stdin に `compact_summary`（生成要約の全文）を受領 — 要約の観測が可能 | 副作用専用。要約本文は渡されない |
| SessionStart の compact ソース | あり（matcher `compact`、v2.1.214+） | あり |
| 設定場所 | settings.json | `~/.codex/hooks.json` / `<repo>/.codex/hooks.json` / config.toml `[hooks]`（Claude Code の設計をほぼ踏襲） |

## 実務上の要点

1. **「compact で失われたくない情報を守る」戦略が異なる。**
   Claude Code は PreCompact の additionalContext で要約器に直接指示できる。
   Codex は要約に触れられないので、`transcript_path` から**全文が消える前に外部退避**し、
   PostCompact / SessionStart(compact) で再注入する迂回になる。
2. **ブロックの意味が違う。** Claude Code は「この compact を拒否」、
   Codex は「continue:false でターンごと停止」。拒否して続行の選択肢は Codex にない。
3. **どちらも「フックから compaction を能動的に発火」はできない。**
   Codex 側は Issue #23153 で要望中（open）。
4. **自動 compaction 閾値**: Codex は `model_auto_compact_token_limit`（+ `_scope`）で調整可。
5. **情報の鮮度に注意。** Codex hooks は 2026-03 experimental → 2026-05 安定化と新しく、
   逆に Claude Code の PostCompact 追加も比較的最近。両方向に古い言説が流通しており、
   本件の調査でもサブエージェント 1 体が古い認識（Claude Code に PostCompact なし）を
   報告してきた。**この種の仕様は必ず原典（公式 docs / ソース）で裏取りする。**

## 設計意図の考察（仮説、2026-08-03 の相談より）

前提の整理: Codex の additionalContext 不在は「未実装」ではなく PR #19905 の Out of Scope で
**明示的に拒否**されたもの。問うべきは「なぜ後回しか」ではなく「なぜ断ったか」。

**中心仮説 v1（反証済み・2026-08-03 同日）**: 「Codex hooks は観測と拒否権のみで
モデルコンテキストへの書き込み権を持たない」— これは誤り。schema.rs の原典確認で、
Codex も SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / SubagentStart（+docs 上
Stop / SubagentStop）で `additionalContext` 注入可、`updated_input` / `updatedMCPToolOutput` で
ツール入出力の書き換えまで可能と判明。詳細は
[hooks 全機能比較](/tech/hooks-feature-comparison-claude-vs-codex.md)。

**中心仮説 v2（改訂）**: Codex が閉じているのは hooks 全体ではなく **compaction パイプライン
だけ**（ブロック不可・注入不可・要約プレビューなし）。通常ターンへの注入は次のターンで
訂正が効く回復可能な介入だが、compaction への注入は**セッションの永続記憶そのものを
書き換える**——汚染された要約は以後のグラウンドトゥルースになり、回復不能かつ気づきにくい。
だから他はすべて Claude Code 互換で開けつつ、そこだけ聖域にしたと読む。
Claude Code は対照的に compaction を両方向に開いている（PreCompact で `custom_instructions`
受領+ブロック可、PostCompact で `compact_summary` 全文受領）。

聖域化を支える実務的動機（推測）:

1. **要約プロンプトを閉じて品質保証**: ユーザー文字列の混入は劣化の切り分け・再現性・
   サポート負担を悪化させる。
2. **注入面の最小化**: フック出力→要約器プロンプト直結は、レビューを経ない injection チャネル。
3. **compaction をサーバ側へ動かす自由度**: クライアントフックからの介入を API として
   約束すると移行の足枷になる。

**Codex 側の一理**: 「要約器に指示して守ってもらう」は確率的機構（無視されたら終わり）、
「transcript を外部退避して PostCompact / SessionStart(compact) で再注入」は決定的機構。
祈りを打点に数えない設計。ただし additionalContext の実用的な軽さ（ファイル退避を書く
までもない一言を守れる）は捨てている。ハーネス選択の指針: 失敗が安い短タスクは確率的操縦で
速度を、長時間自律実行は試行回数が増えるぶん決定的機構に寄せる。

**反証可能な予測**: 将来 Codex に要約介入が入るとしても「自由文注入」ではなく
「compact 後に保持するファイル/範囲を宣言する」宣言的 API の形になる。
Issue #23153（フックからの compaction 発火要望）の捌かれ方が試金石。

## 未検証の第三者分析（使うならスポットチェック要）

- Codex の compaction 後は「要約 1 メッセージ + 直近ユーザーメッセージ ~20k トークン」のみ残る、
  閾値は context window の 90% 超に設定しても無視される — simzhou / badlogic / danielvaughan の
  解析記事にあるがソース未確認。

## 関連

- [codex 単体作業ハーネスの初手設計](/tech/codex-standalone-harness-bootstrap.md) — Codex hooks の設定配置・trust 要件
- [GPT/Codex 通説の実測検証](/tech/gpt-codex-quirk-findings.md) — 長セッション/compaction 劣化仮説
- [ハーネス観測基盤の構想](/tech/harness-observability-platform.md) — rollout の `context_compacted` イベント

# Citations

[1] [Claude Code hooks 公式ドキュメント](https://code.claude.com/docs/en/hooks)
[2] [openai/codex PR #19905: Add compact lifecycle hooks](https://github.com/openai/codex/pull/19905)
[3] [Codex hooks 公式ドキュメント](https://developers.openai.com/codex/hooks)
[4] [openai/codex compact.rs（ペイロード定義の原典）](https://github.com/openai/codex/blob/main/codex-rs/hooks/src/events/compact.rs)
[5] [Issue #23153: フックから compaction を発火させたい（open）](https://github.com/openai/codex/issues/23153)
