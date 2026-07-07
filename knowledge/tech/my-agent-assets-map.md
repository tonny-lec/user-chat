---
type: Reference
title: このPCのエージェント資産マップ — 何がどこにあり、何をしているか
description: ~/.claude と ~/workspace 配下のエージェント関連資産（設定・hooks・skills・プラグイン・プロジェクト）の棚卸しマップ。自分の環境を教材として理解するための索引。
tags: [ai-agent, claude-code, inventory, harness, dotfiles]
timestamp: 2026-07-06T22:30:00+09:00
---

「PCにあるものはだいたいエージェントに作ってもらったので理解できていない」という状態を
解消するための地図。[ハーネス基礎](/tech/ai-agent-harness-basics.md)の層構造モデルに
実物を対応付けてある。2026-07-06 時点の棚卸し。

## 層構造と実物の対応

| ハーネスの層 | このPCでの実体 |
|---|---|
| コンテキスト注入 | `~/workspace/CLAUDE.md`（親・オーケストレーター指針）＋各プロジェクトの CLAUDE.md / AGENTS.md |
| ルール強制 (hooks) | 自作 Stop hook 2本（下記） |
| 手順知識 (skills) | superpowers プラグイン群 ＋ 自作6本 ＋ 失敗レビュー系2本 |
| 権限 | `~/.claude/settings.json` の permissions（読み取り系を自動許可、`git push main`・`git reset --hard`・`.env` 読取などを拒否） |
| 分業 | 親 CLAUDE.md のサブエージェント委譲ルール |

## ユーザー全体設定（`~/.claude/`）

- `settings.json` — 本体。model/言語/権限プリセット/プラグイン有効化/Stop hook 登録/statusline。
- `skills/` — 2本ともシンボリックリンクで `lets-deep-agents/claude-assets/skills/` の
  `failure-dashboard`・`failure-review` を指す。
- `plugins/` — 3プラグイン: superpowers v6.1.1 / claude-code-setup / claude-md-management
  （マーケットプレイスは anthropics/claude-plugins-official のみ）。
- `hooks/` `agents/` `commands/` は空。フック実体はプロジェクト側にある。
- それ以外（`projects/` `sessions/` `backups/` `history.jsonl` 等）は Claude Code の
  実行ログ・状態で、手動で触るものではない。

### 既知のズレ（dotfiles と実体）

`dotfiles/README.md` は「settings.json・agents・skills は dotfiles からのリンク」と
書いているが、実際は: `settings.json` は実ファイル / `skills` は lets-deep-agents を指す /
`agents` は存在しない（dotfiles 側に `design-reviewer.md` があるが未リンク）。
意図した状態か要確認。

## 自作 hook 2本（このPCの「機械強制」の実例）

1. `lets-deep-agents/scripts/stop-hook-reminder.sh` — 全セッション適用
   （`~/.claude/settings.json` から発火）。transcript 40行以上なら `decision:block` で
   ターン終了をブロックし、失敗カタログ照合レビューを強制。セッション1回のみ。
2. `user-chat/.claude/hooks/knowledge-record-reminder.sh` — user-chat 専用。
   transcript 30行以上かつ `knowledge/log.md` がセッション開始より古ければブロックし
   OKF 記録を強制。コメントに「レベル1（善意頼み）→レベル3（機械強制）への配線」と
   設計思想が明記されている → [強制点の設計](/tech/skill-to-harness-enforcement.md)。

## workspace プロジェクト一覧

| パス | 何か | エージェント関連設定 |
|---|---|---|
| `codex-analysis/` | Codex CLI を委譲にどう使うか検証する研究リポジトリ | 独自 CLAUDE.md、bash/python ハーネス多数 |
| `codex-break-down/` | OpenAI Codex (OSS) のコード解析。PLAN.md が実行計画 | 独自 CLAUDE.md |
| `codex-os/` | Codex の上に被せる自律成長型ハーネス（Rust `cos`） | skill: codex-review、AGENTS.md |
| `docs/` | 共通ドキュメント2本（ハーネス技術選定・シェルガイドライン） | 親 CLAUDE.md から参照される側 |
| `dotfiles/` | 個人設定管理。install.sh がリンクを張る | claude/ に settings・agents・skills の原本 |
| `lets-deep-agents/` | 失敗の記録・分析基盤（catalog.md + log.tsv + dashboard.py） | 失敗レビュー系 skill 2本の実体 |
| `lets-langgraph/` | LangGraph (TS) 製 AI 駆動開発ハーネス CLI | AGENTS.md、.agents/ |
| `tech-digest/` | RSS 巡回ダイジェスト (Python)。星付け記事を OKF に蒸留 | skill 2本、knowledge/、AGENTS.md |
| `verifiability-dojo/` | 検証可能性を鍛える TS 製 eval 道場 | CLAUDE.md、skill-map/ |
| `user-chat/` | Fableの部屋（この相談スペース） | Stop hook 1本 + knowledge/ |

## 規模感

自作 hook 2本 / 自作 skill 6本＋失敗レビュー系2本 / プラグイン3件 /
CLAUDE.md・AGENTS.md はほぼ全プロジェクトに配置。ワークスペースの大半が
「エージェント/ハーネスの研究・運用」がテーマ。

# Examples

自分の環境を教材にする読み順（小さく・自作で・思想が明快な順）:

1. `user-chat/.claude/hooks/knowledge-record-reminder.sh`（40行。hook の入出力 JSON、
   `decision:block`、冪等化マーカー、静かな無効化まで一通り学べる最良の教材）
2. `~/.claude/settings.json`（権限の allow/deny と hook 登録がどう書かれるか）
3. `lets-deep-agents/` の README → stop-hook-reminder.sh → failure-log.sh → dashboard.py
   （hook→skill→シェル→Python と多段連携する実運用系）
4. superpowers プラグインの中身 → [解剖メモ](/tech/superpowers-plugin-anatomy.md)

# Citations

[1] 棚卸し実施: 2026-07-06、Explore サブエージェントによる読み取り調査＋スポットチェック。
