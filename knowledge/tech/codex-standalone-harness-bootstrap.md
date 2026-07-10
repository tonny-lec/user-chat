---
type: Consultation
title: codex 単体作業ハーネスの初手設計 — 最初の1本は観測装置
description: gpt-5.6 GA を機に「環境非依存・codex のみで完結」するハーネスを作る相談。Codex CLI 2026 のハーネス面（ネイティブ subagents・安定版 hooks）を確認し、10案から検証ループキット（verify 契約+Stop hook 強制+縮退解ガード）を採用。
tags: [ai-agent, harness, codex, gpt-5.6, failure-observation, hooks, subagents]
timestamp: 2026-07-10T23:00:00+09:00
---

# 相談内容

gpt-5.6 が GA したのを機に、codex に「小さく単体で完結したハーネス」を作らせたい。
確定した前提（2往復の確認で判明。初回は前提を取り違えた）:

1. **環境非依存** — ハーネスのバンドル（1ディレクトリ/リポジトリ）だけで稼働する。
   このPCの既存資産（lets-deep-agents の log.tsv・~/.claude 等）に依存しない。
2. **codex のみで完結** — サブエージェントも codex。Claude Code は関与しない。
3. 目的は実用＋ codex 環境の整備。

# 検討・調査

## Codex CLI 2026 のハーネス面（Web 調査で確認・2026-07-10）

Codex CLI は Claude Code とほぼ同等のハーネス面を持つと判明。「分業機構を自作する
必要がある」という当初の想定は誤りだった。

| 層 | Codex CLI での実体 |
|---|---|
| 文書層 | AGENTS.md。D4 実証済みで 5.6 は正当化付き上書きにも維持（[観測フロー](/tech/model-migration-observation-flow.md)） |
| サブエージェント | ネイティブ。`.codex/agents/*.toml`（プロジェクトスコープ可）。`developer_instructions`/`model`/`sandbox_mode` を役割別に上書き、省略分は親から継承。同時6・ネスト深さ1 |
| ルール強制 (hooks) | v0.124.0 で安定。SessionStart / PreToolUse / PostToolUse / Stop / SubagentStart / SubagentStop 等。hooks.json または config.toml インライン |
| 権限 | sandbox_mode・approvals（サブエージェント単位でも指定可） |

未確認事項（実装前に要事実確認）: Stop hook が Claude Code の `decision:block` 相当の
ブロックをできるか / transcript へのアクセス方法 / プロジェクトスコープ hooks の正確な配置。

## AGENTS.md の探索範囲 — CLAUDE.md との差分（2026-07-10 追記）

Codex は AGENTS.md を階層的に読むが、**上限は Git リポジトリルート**。探索順:

1. グローバル: `~/.codex/AGENTS.override.md` → なければ `~/.codex/AGENTS.md`（1つだけ）
2. `.git` のあるディレクトリをプロジェクトルートとし、そこから cwd まで下りながら
   各階層で `AGENTS.override.md` → `AGENTS.md`（1ディレクトリ最大1ファイル）
3. ルート側→cwd 側の順に連結（cwd に近いほど後＝実質優先）。合計 32 KiB
   （`project_doc_max_bytes`）で打ち切り

**Claude Code との挙動差**: Claude Code は git ルートを越えて親ディレクトリを home まで
遡る（`~/workspace/CLAUDE.md` のようなワークスペース共通層が効く）が、Codex は
リポジトリ外の中間階層を読まない。マシン共通ルールは `~/.codex/AGENTS.md` に置くか、
リポジトリ内へコピー/シンボリックリンクするしかない。バンドル完結型ハーネス（本題材）
には影響なし — リポジトリ内で閉じるため。

## 提案の変遷（前提と事実が変わるたびに推奨が動いた記録）

- R1（前提誤解: このPC上の想定）: 既存 log.tsv への合流 → **環境非依存の前提に違反**し廃案。
- R2（分業機構が未知と想定）: codex exec ラッパー `sub.sh` の自作分業キット →
  **ネイティブ subagents の存在で作るものが消滅**し廃案。
- R3（事実確定後）: 最大の未知が消えたので、原則「新環境の初手は観測」に回帰。

# 結論

## v1（初手）: 失敗観測ループ、Stop hook 強制・バンドル完結版

1リポジトリに閉じる構成。外部依存は codex CLI と認証のみ:

- `log/failures.tsv` — バンドル内の失敗ログ
- 記録スクリプト1本 — 形式検証つき追記（ログの直接編集禁止）
- **Stop hook** — セッション終了時に記録を強制。`knowledge-record-reminder.sh` と同じ
  設計パターン（発火条件も機械が判断・セッション1回・fail-open）を codex hooks に移植
- `AGENTS.md` — 記録規約数行
- （同梱可・ほぼタダ）イベント発火ログ hook — PostToolUse/SubagentStart 等を1行ログ。
  [散らかり対策](/tech/harness-sprawl-and-interference.md)の観測可能性をバンドル内で確保

## v2（失敗を1件観測してから）: 検証ループキット

`./verify` 実行の強制 + `.codex/agents/reviewer.toml`（独立レビュアー）+
SubagentStop hook でのレビュー結果ログ。[強制強度](/tech/skill-to-harness-enforcement.md)は
最上位の検証ループ層。

## 残る設計判断

バンドルの形: (a) テンプレートリポジトリ（プロジェクトごとに複製）か
(b) 作業をバンドル内で行う自己完結ワークスペースか。運用イメージ次第。

## codex への依頼文に含める検証条件

「実装前に公式 Hooks リファレンスで入出力仕様を確認」「偽入力のパイプテストで
発火5シナリオ（発火・記録済み・短会話・重複防止・再発火防止）を検証してから配線」—
Claude 側 hook 開発で実証済みの TDD 手順をそのまま指定する。

## 一般化できる原則

1. **新しい実行環境にハーネスを持ち込むときの初手は、強制ではなく観測の最小ループ**。
   その環境の失敗分布が分かる前に作った強制は、防ぐ相手のいない儀式になる。
2. **題材選定は「最大の未知」に引っ張られ、未知が消えると観測初手の原則に戻る**。
   R2 で分業キットを推したのは分業機構が未知だったからで、ネイティブ対応の確認で消えた。
   前提・事実の確認1つで推奨が丸ごと変わる — 題材決めの前の事実確認は安い保険。

## 採用決定（2026-07-10）: 広い候補出しの結果、検証ループキットに決定

推奨（失敗観測ループ）を一旦引っ込め、10案を4カテゴリ（観測・記録 / 検証・品質 /
安全・権限 / 分業・文書）で提示した結果、本人が**検証ループキット**を選択。
選択軸として提示したのは (1) どの失敗が一番痛いか (2) どの codex 機構を体験したいか
(3) 単体完結度、の3つ。

確定した設計の要点:

- **verify 契約**: `./verify` がエントリポイント。プロジェクト固有の検査は `verify.d/`
  に置く（キット本体は環境非依存、差し替え点を1箇所に限定）。
  **`verify.d/` が空なら fail** — 空検証で緑を偽装する縮退解を封じる。
- **強制点は Stop hook**: セッション中に作業ツリーが変わったのに、最後の変更以降の
  verify 成功記録がなければターン終了をブロック。fail-open・再発火防止つき。
- **実行履歴を tsv 記録**（時刻・tree-hash・結果）— 検証履歴が観測データを兼ねる。
- **自己改竄ガード**: verify.d/ や hooks の変更を tree-hash と発火ログで観測可能にし、
  AGENTS.md に「検査の削除・緩和はユーザー承認が要る」の例外条項を置く（D4 知見の運用）。
- reviewer サブエージェントは v2 に送る（失敗観測後）。

## ステータス（2026-07-10）

題材決定（検証ループキット）。codex への依頼文を作成済み（会話内で提示）。実装は codex が担当。

# Examples

v1 バンドルの骨格イメージ:

```
codex-harness/
├── AGENTS.md              # 記録規約（数行）
├── .codex/
│   └── hooks.json         # Stop hook + 発火ログ hook
├── bin/log-failure.py     # 形式検証つき追記
└── log/
    ├── failures.tsv
    └── events.log
```

# Citations

[1] [Subagents – Codex（OpenAI Developers）](https://developers.openai.com/codex/subagents)
[2] [Hooks – Codex（OpenAI Developers）](https://developers.openai.com/codex/hooks)
[3] [Codex CLI in 2026: What's New](https://codex.danielvaughan.com/2026/03/27/codex-cli-in-2026-whats-new/)
[5] [Custom instructions with AGENTS.md（OpenAI Developers）](https://developers.openai.com/codex/guides/agents-md)
[4] 関連: [ハーネス基礎](/tech/ai-agent-harness-basics.md)、[資産マップ](/tech/my-agent-assets-map.md)、[eval 入門](/tech/evals-for-practitioners.md)
