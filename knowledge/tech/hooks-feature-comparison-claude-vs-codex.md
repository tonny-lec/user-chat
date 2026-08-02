---
type: Reference
title: hooks 全機能比較 — Claude Code と Codex CLI
description: Claude Code は 30 イベント、Codex は 11 イベントで Claude スキーマ互換（エンジン名も ClaudeHooksEngine）。Codex も 7 イベントでコンテキスト注入可能で「観測と拒否権のみ」説は誤り。閉じているのは compaction パイプラインだけ。
tags: [claude-code, codex, hooks, harness, observability]
timestamp: 2026-08-03T00:00:00+09:00
---

# hooks 全機能比較 — Claude Code と Codex CLI

2026-08-03 調査。サブエージェント 2 体の並列調査 + 原典スポットチェック
（schema.rs の `additional_context` 5 struct、Claude docs の `compact_summary`）済み。

## TL;DR

1. **Codex hooks は Claude Code hooks の意図的なサブセット互換実装**。エンジン名からして
   `ClaudeHooksEngine`（codex-rs/hooks/src/engine/mod.rs）で、フィールド名は同一
   （`permissionDecision` / `additionalContext` / `hookSpecificOutput` / `stop_hook_active` 等）。
   ただし公式 docs に互換の明示宣言はなく、設定 JSON はコピペでは動かない（形式翻訳が必要）。
2. **「Codex hooks は観測と拒否権のみ、コンテキスト書き込み不可」は誤り**（当初仮説、反証済み）。
   Codex も 7 イベントで `additionalContext` 注入可、さらに `updated_input`（PreToolUse）や
   `updatedMCPToolOutput`（PostToolUse）でツール入出力の書き換えまでできる。
3. **本当に閉じているのは compaction パイプラインだけ**。Codex の PreCompact/PostCompact は
   ブロック不可・注入不可・要約プレビューなし（`systemMessage` の UI 表示のみ）。
   Claude Code は PreCompact でブロック+`custom_instructions` 受領、PostCompact で
   `compact_summary`（生成要約の全文）を受け取れる — 操縦も観測も開いている。
4. **観測面はむしろ Claude Code のほうが広い**。イベント数 30 vs 11 で、観測専用イベント
   （InstructionsLoaded / MessageDisplay / FileChanged / CwdChanged / StopFailure /
   PostToolUseFailure / PostToolBatch / ConfigChange 等）は Claude Code 側に偏在。
   Codex 独自の観測拡張は `turn_id`（ソースに "Codex extension" と明記）と `model` くらい。

## Codex CLI: 全 11 イベント

| イベント | ブロック | コンテキスト注入 | 備考 |
|---|---|---|---|
| SessionStart | `continue:false` | ✅ additionalContext | source: startup/resume/clear |
| SessionEnd | 不可 | ❌ | timeout 既定 1 秒（上限 3 秒） |
| UserPromptSubmit | decision:block / exit 2 | ✅ + 平文 stdout も可 | |
| PreToolUse | permissionDecision:deny 推奨 | ✅ + `updated_input` で入力書き換え | hosted tools は経路外 |
| PermissionRequest | deny | ❌ | |
| PostToolUse | decision:block / exit 2 | ✅ + `updatedMCPToolOutput` | |
| PreCompact | **不可**（意図的） | **不可**（systemMessage の UI 表示のみ） | trigger: manual/auto |
| PostCompact | 不可 | 不可・**要約本文も渡されない** | |
| SubagentStart | 不可 | ✅ | agent_id/agent_type |
| SubagentStop | exit 2 | ✅（JSON 必須） | |
| Stop | decision:block（理由必須） | ✅（JSON 必須） | last_assistant_message あり |

- 共通 stdin: `session_id, transcript_path, cwd, hook_event_name, model, permission_mode`（+ turn スコープは `turn_id`）。
- 注入上限: 既定 ~2,500 トークン、超過は **spilling**（全文ディスク退避 + 切り詰めプレビューのみモデルへ）。Codex 独自機構。
- 信頼モデル: 非マネージドフックは `/hooks` で信頼レビューを通すまで実行されない。定義変更で再レビュー。
- exit code: 0=成功（stdout JSON パース）/ 2=ブロック（stderr が理由）/ 他=fail-open。
- タイムアウト既定 600 秒。複数フックは並行実行・順序保証なし。

## Claude Code: 30 イベント（2026-08 現在）

Codex にもある 11 相当（SessionStart/SessionEnd/UserPromptSubmit/PreToolUse/PermissionRequest/
PostToolUse/PreCompact/PostCompact/SubagentStart/SubagentStop/Stop）に加えて:

- **観測専用**: InstructionsLoaded（CLAUDE.md 等のロード）/ MessageDisplay（表示差し替えのみ可）/
  Notification / FileChanged / CwdChanged / StopFailure（API エラー終了）/ PermissionDenied
- **介入系**: UserPromptExpansion（スラコマ展開のブロック）/ PostToolUseFailure /
  PostToolBatch（並列ツール一括完了後・次モデル呼び出し前に注入）/ ConfigChange（設定変更のブロック）/
  Elicitation・ElicitationResult（MCP フォームの自動入力・上書き）
- **ライフサイクル**: Setup / TaskCreated / TaskCompleted / TeammateIdle / WorktreeCreate（git 既定動作の置換）/ WorktreeRemove

機能面の要点:

- 平文 stdout がコンテキストに入るのは UserPromptSubmit / UserPromptExpansion / SessionStart の 3 つのみ。他は `hookSpecificOutput.additionalContext`。上限 10,000 文字（超過はファイル退避 + プレビュー）。
- PreToolUse: `permissionDecision` allow/deny/ask/**defer** + `updatedInput`。優先順位 deny > defer > ask > allow。
- **compaction は両方向に開いている**: PreCompact = ブロック可 + `custom_instructions` 受領、PostCompact = `compact_summary` 全文受領。
- ハンドラ 5 種: command / http / mcp_tool / prompt（高速モデル判定）/ agent（実験的）。`async: true` でバックグラウンド実行、`asyncRewake` で Claude を起こす。
- Stop の `decision:block` は連続 8 回でオーバーライドされる。`last_assistant_message` / `background_tasks` / `session_crons` を受領。
- デバッグ: `claude --debug` → `~/.claude/debug/<session-id>.txt`（マッチ・exit code・stdout/stderr 全文）。transcript_path は非同期書き込みでラグあり（最終応答は last_assistant_message を使えと明記）。
- 設定は各レベル（user/project/local/managed/plugin/frontmatter）**マージ**で全部走る。settings/plugin のフックはサブエージェント内でも発火。

## 実務上の使い分け・含意

1. **Codex で足りるもの**: ツールゲート（PreToolUse deny）、Stop 強制、セッション初期化注入、
   サブエージェント観測。Claude Code 用フックの移植は「イベントとフィールドはほぼ同名、
   設定形式だけ翻訳」で成立する（実績: knowledge-record-reminder.sh の移植、2026-07-13）。
2. **Codex にないので設計を変えるもの**: compaction 介入（→ 外部退避 + SessionStart(compact) 再注入）、
   設定変更ガード（ConfigChange 相当なし）、表示制御（MessageDisplay 相当なし）、
   ツール一括後の注入（PostToolBatch 相当なし）。
3. **鮮度の罠（今回も再現）**: 2026-04 時点の二次資料は「PreToolUse は注入不可」、別の調査は
   「Claude Code に SubagentStart はない」と報告したが、どちらも現行原典で否定された。
   hooks 仕様は数ヶ月単位で拡張されるため、**必ず現行の原典（docs 原文 Markdown / schema.rs）で裏取りする**。

## 関連

- [PreCompact/PostCompact フックの比較](/tech/compact-hooks-claude-vs-codex.md) — compaction に特化した詳細と設計意図の考察
- [codex 単体作業ハーネスの初手設計](/tech/codex-standalone-harness-bootstrap.md) — Codex hooks の trust 要件・配置・worktree の罠

# Citations

[1] [Claude Code hooks リファレンス（原文 Markdown）](https://code.claude.com/docs/en/hooks.md)
[2] [Codex hooks 公式ドキュメント](https://learn.chatgpt.com/docs/hooks)（developers.openai.com/codex/hooks から 308 移転）
[3] [codex-rs/hooks/src/schema.rs（wire 型の原典）](https://github.com/openai/codex/blob/main/codex-rs/hooks/src/schema.rs)
[4] [openai/codex PR #19905: Compact Lifecycle Hooks](https://github.com/openai/codex/pull/19905)
