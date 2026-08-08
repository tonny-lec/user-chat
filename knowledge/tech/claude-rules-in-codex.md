---
type: Consultation
title: Claude Code の .claude/rules を Codex CLI で再現する — 完全相当は無く、部分代替3系統
description: Claude Code の .claude/rules（paths glob による条件付きモジュール指示）に完全対応する機能は Codex CLI に存在しない。Codex の "rules" は execpolicy で permissions 相当。部分代替はネスト AGENTS.md・Skills・指示ベース参照の3系統。続編でコミュニティの解消事例（symlink / rulesync・ruler 生成ツール / 上流要望5系統が全て open・無応答）を追記。
tags: [codex, claude-code, harness, agents-md, rules]
timestamp: 2026-08-08T00:00:00+09:00
---

# 相談内容

Claude Code の `.claude/rules` を Codex CLI で再現したい。Codex CLI にも "rules" という機能があるが、
実行コマンドのコントロールであり同じ機能ではなかった。Codex に同様の機能があるか。

# 検討・調査

## まず両者の「rules」は名前が同じだけの別物

| | Claude Code `.claude/rules/` | Codex CLI rules |
|---|---|---|
| 実体 | モジュール化された**指示ファイル**（Markdown） | コマンド実行の**許可ポリシー**（Starlark） |
| 置き場 | `./.claude/rules/*.md`、`~/.claude/rules/*.md` | `~/.codex/rules/*.rules`、信頼済みリポジトリなら `<repo>/.codex/rules/` |
| 中身 | 自然言語の指示。frontmatter `paths:` で glob 条件付き読み込み | `prefix_rule(pattern=["gh","pr","view"], decision="allow")` のようなコマンド接頭辞マッチで allow / prompt / forbidden を決める。`codex execpolicy check` で検証。experimental |
| Claude Code での対応物 | — | settings.json の **permissions**（allow/deny/ask） |

ユーザーの観察どおり、Codex の rules はモデルへの指示注入とは無関係 [2]。

## Claude Code 側の再現対象の正確な仕様（2026-08 時点）

- `./.claude/rules/*.md`（プロジェクト）と `~/.claude/rules/*.md`（ユーザー）。サブディレクトリ再帰・シンボリックリンク対応（プロジェクト間共有に使える）。
- frontmatter `paths:` に glob（brace 展開可）を書くと、**該当ファイルを触ったときだけオンデマンド読み込み**。`paths:` なしなら起動時に CLAUDE.md と同格でロード [1]。
- つまり価値は2つ: **①指示のモジュール分割**と**②パス条件による遅延読み込み（コンテキスト節約）**。

## Codex 側にあるもの・ないもの

- **@import / リンク自動追従 / frontmatter 条件**: 存在しない。AGENTS.md ガイドに一切記載なし [3]。
- **ネスト AGENTS.md**: 存在する。Git ルート→CWD の各階層で `AGENTS.override.md` → `AGENTS.md` → fallback 名の順に発見し空行連結、近い階層が後勝ち。Codex 公式で唯一の「スコープ付き」機構だが、条件は**ディレクトリ階層のみ**（探索範囲の詳細は [codex 単体作業ハーネスの初手設計](/tech/codex-standalone-harness-bootstrap.md) の追記参照）。
- **config.toml の instructions 系**: `model_instructions_file` は組み込み指示の丸ごと置換であり分割読み込みではない。`project_doc_fallback_filenames` でファイル名の代替指定、`project_doc_max_bytes`（デフォルト 32 KiB、**超過は無警告で切り捨て**）[4]。
- **Skills**（`.codex/skills/` の SKILL.md）: 起動時は名前と説明だけ読み、必要時に本文を読む progressive disclosure。条件付き遅延読み込みとして最も近いが、トリガーは**タスク内容との意味的一致**でありパス glob ではない [5]。
- agents.md 公式仕様自体がミニマル指向で、分割・条件付き読み込みの規定はゼロ。モノレポはネストで対応する慣行のみ [6]。

# 結論

**Codex CLI に `.claude/rules` の完全相当（paths glob による条件付きモジュール指示）は存在しない**（2026-08 時点）。
再現は「何を再現したいか」で3系統に分解して使い分ける:

| 再現したい性質 | Codex での手段 | 差分・限界 |
|---|---|---|
| ①指示のモジュール分割 | **ネスト AGENTS.md**: ルートに短い全体規約、`src/api/` 等に各ローカル AGENTS.md を分散配置 | スコープ条件がディレクトリ階層のみ。`**/*.sql` のような横断 glob（CWD と無関係な発火）は表現できない。32 KiB 上限対策も兼ねる |
| ②条件付き遅延読み込み | **Skills**: トピック別ルールを SKILL.md 化し、description にトリガー条件を書く | 発火はパスでなく意味的一致。発火するかはモデル判断で確率的 |
| ③（機構なしの妥協） | AGENTS.md 本文に「X を触るときは docs/Y.md を読め」とパス列挙 | 自動機構ではなく指示ベース。Skills はこのパターンの機構化版 |

実務の推奨: ディレクトリ構造と関心事が一致しているなら①で大半は足りる。横断的関心事
（例: SQL 全般・テスト全般）は②の Skills に載せる。①②で表現できない残りだけ③。
なお「コマンドを制限したい」需要なら Codex の rules（execpolicy）がそのものずばりであり、
Claude Code の permissions との対応で考える。

# 続編: 同じ課題を感じた人たちの解消事例（2026-08-08 調査）

上流要望と実運用の回避策を最新順に調査した結果。

## 解消パターンは3層に収斂

| 層 | 手段 | 代表例 | 限界 |
|---|---|---|---|
| (a) symlink | 単一ソースを各ツールのファイル名へリンク | COLOPL Tech Blog（2025-10-15）: `.agents/rules/base.md` → CLAUDE.md / AGENTS.md / .cursor/rules へリンク [7] | 全ツール同一内容が前提。glob 条件・ツール固有差分は扱えない |
| (b) 生成ツール | 単一ソースから各ツール形式へコンパイル | **rulesync**（★1,295、2026-08-07 リリースの活発さ）: `.rulesync/**/*.md`（frontmatter に glob）→ `rulesync generate` で AGENTS.md / `.claude/` へ変換。Codex にない機能は「simulated」モードで指示文として擬似埋め込み [8][9]。**ruler**（★2,838）: `.ruler/*.md` を連結して配布、glob シミュレートなしのシンプル路線 [10] | rulesync の glob 再現は指示文埋め込みであり、Claude Code の機構的条件ロードと等価ではない |
| (c) Codex 純正 | ネスト AGENTS.md + 指示ベース参照 | 本文の結論①③と同じ | 横断 glob は表現不能 |

## 上流（openai/codex）の状況 — 要望5系統、全て open・メンテナ応答ゼロ

- **#34002**（2026-07-18、open・実在確認済み）: `.codex/rules/` の path-scoped 条件付き読み込みそのものの要望。ネスト AGENTS.md は「ディレクトリ位置」スコープで「ファイル種別」（service層/DTO/テスト）には粗すぎると正確に指摘。
- **#28739**（2026-06-17、活動 2026-08-05）: `AGENTS.local.md`（追加オーバーレイ）+ `@` 参照展開の要望。`AGENTS.override.md` は置換であって追加ではない、という不満。
- **#17401**（2026-04-11、活動 2026-08-01）: `@include` 要望。実測報告あり — **`@/path/file.md` と書いてもリテラル文字列として素通し**される。コミュニティ実装ブランチもマージされず放置。
- **#23788**（2026-05-21）: `~/.codex/instructions/` の自動連結読み込み要望。「既に `~/.claude/rules/*.md` を持っていて Codex でも再利用したい」動機を明記。
- **#24881**（2026-05-28、コメント0）: Skills に `paths:` frontmatter を付ける提案。skills 側から条件付きロードに到達しようとするアプローチ。

含意: 本体対応は当面期待薄。実務は (b) 生成ツール（分割と glob をソース側で持つ）か (c) 純正の範囲で設計するのが現実解。

# Citations

[1] [Claude Code Memory — .claude/rules](https://code.claude.com/docs/en/memory.md)
[2] [Rules | OpenAI Codex](https://developers.openai.com/codex/rules)
[3] [Custom instructions with AGENTS.md | OpenAI](https://developers.openai.com/codex/guides/agents-md)
[4] [Configuration Reference | OpenAI Codex](https://developers.openai.com/codex/config-reference)
[5] [Skills in OpenAI Codex](https://blog.fsck.com/2025/12/19/codex-skills/)
[6] [agents.md 公式仕様](https://agents.md/)
[7] [COLOPL Tech Blog: AIエージェントのルールを symlink で共通化](https://blog.colopl.dev/entry/2025/10/15/110000)
[8] [dyoshikawa/rulesync](https://github.com/dyoshikawa/rulesync)
[9] [Zenn: rulesync で AI 設定を同期](https://zenn.dev/painter/articles/89f630d0a7e378)
[10] [intellectronica/ruler](https://github.com/intellectronica/ruler)
[11] [openai/codex #34002: .codex/rules/ 要望](https://github.com/openai/codex/issues/34002)
[12] [openai/codex #17401: @include 要望](https://github.com/openai/codex/issues/17401)
[13] [openai/codex #28739: AGENTS.local.md 要望](https://github.com/openai/codex/issues/28739)
