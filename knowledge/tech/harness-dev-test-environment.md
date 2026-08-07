---
type: Consultation
title: サンドボックス下のコーディングエージェントにハーネスを作らせるときのテスト環境
description: codex のサンドボックス制約でエージェントのテスト実行が失敗し回避コードが増殖する問題への処方箋。根因は「エージェントの実行環境 ≠ ユーザーの実行環境」の非対称。隔離を外側（コンテナ/VM）へ移すのが根治、codex exec のデフォルト read-only が即効の確認点、テスト2レーン分割と環境起因失敗の三分類ガードを併用する。
tags: [ai-agent, harness, codex, sandbox, testing, failure-observation]
timestamp: 2026-08-07T00:00:00+09:00
---

# 相談内容

ハーネスやエージェントループをコーディングエージェント（codex）に開発させると、
サンドボックス制約のためエージェント側が TUI のユーザーより大幅に弱い権限で動く。
結果、(1) テスト段階で環境起因の実行エラーが頻発し、(2) それを回避するための
不要なテストやコードが増え、(3) 開発が終わらない・過剰に時間がかかる。

# 検討・調査

## 問題の構造

根因は1つ: **エージェントのテスト実行環境 ≠ 成果物の実行環境（ユーザーの TUI）**。
ハーネス開発は題材が最悪の組み合わせ — テスト対象自体がプロセス起動・ネットワーク
（API 呼び出し）・ホーム下の設定ファイル（`~/.codex` 等）・hook 発火を必要とし、
サンドボックスが遮断するものと正確に重なる。

回避コードが増殖する機序: エージェントの目的関数は「テストを緑にする」なので、
**環境起因の失敗をコード起因と誤分類**して mock・skip・リトライを実装してしまう。
これは縮退解（[skill をハーネス化する強制点の設計](/tech/skill-to-harness-enforcement.md)
の縮退解ガードが対象とするもの）の一種。

## codex サンドボックスの現行仕様（2026-08-07 サブエージェント調査＋原典スポットチェック）

公式ドキュメントは developers.openai.com/codex/* → learn.chatgpt.com/docs/* に移転（308）。

- `sandbox_mode`: `read-only` / `workspace-write` / `danger-full-access` の3値（変更なし）。
- **`codex exec` のデフォルトは read-only**（"By default, `codex exec` runs in a read-only
  sandbox."）。スクリプトやサブプロセスから `codex exec` を呼ぶ構成では、これだけで
  「TUI より大幅に制約される」現象の大部分を説明しうる。書き込みには
  `--sandbox workspace-write` の明示が必要。
- ネットワーク: `[sandbox_workspace_write] network_access = true` で opt-in（キー存続）。
  ほかに `writable_roots` で書き込み可能ディレクトリを追加できる。
- `approval_policy`: 現行値は `untrusted` / `on-request` / `never`。**旧 `on-failure` は
  現行ドキュメントから消滅**。granular 形式（`sandbox_approval` 等の個別フラグ）が追加。
- エスカレーション: TUI には sandbox 越え承認の機構（実装レベルで
  `with_escalated_permissions`、PR #12839 等）があるが、**非対話モードでは承認者が
  いないため事実上使えない**（この最後の点は明文なしの推測）。`--ask-for-approval never`
  でもサンドボックス境界自体は維持される。
- 公式の容認ライン: "Use `danger-full-access` only in a controlled environment
  (for example, an isolated CI runner or container)."（原典照合済み）。devcontainer を
  外側の隔離境界とする運用も案内あり。ただし信頼できるリポジトリ限定の強い警告付き
  （コンテナ内の認証情報ごと持ち出されうる）。
- サブエージェント単位の上書き: `.codex/agents/*.toml` で `sandbox_mode` を役割別に
  設定可能（存続。未指定は親から継承）。

# 結論

対策は4方針。継続的にハーネス開発をするなら方針1が根治、即効は方針2、
方針3・4はどの環境でも入れる価値がある。

## 方針1（根治）: 隔離の担い手を外側へ移す

使い捨てコンテナ/VM（devcontainer、Docker、必要なら E2B 等）の中で codex を
`danger-full-access`（または workspace-write + network）で走らせる。
[サンドボックスと長時間自律](/tech/agent-sandboxing-and-long-running-envs.md)の
「隔離の強さと自律時間は交換関係」の応用 — 隔離をコンテナ境界へ移せば内側は自由に
でき、**エージェントとユーザーの能力差そのものが消える**。テストは本番同等の権限で走る。
公式もこの運用を条件付きで容認している。注意2点: 信頼できるリポジトリ限定/コンテナに
渡す認証情報は最小権限に。

## 方針2（即効）: codex 側の設定を明示する

1. **`codex exec` を呼んでいる箇所を全部見直す** — デフォルト read-only なので、
   `--sandbox workspace-write` の明示がなければテスト実行はほぼ失敗する。
2. `~/.codex/config.toml` または プロジェクト `.codex/config.toml` に
   `sandbox_mode = "workspace-write"` + `[sandbox_workspace_write] network_access = true`。
   テストが書く一時ディレクトリが workspace 外なら `writable_roots` に追加。
3. テスト実行役のサブエージェントにだけ `.codex/agents/*.toml` で広い
   `sandbox_mode` を与える設計も可能（権限を役割で絞る）。

## 方針3（設計）: テストを2レーンに分ける

- **functional core / imperative shell**: ループ制御・パース・状態遷移は純ロジックに
  寄せ、サンドボックス内で完結するユニットテストにする。プロセス起動・API 呼び出し・
  ネットワークは薄いアダプタに隔離。
- **LLM/プロセス境界は偽入力で切る**: hook は偽 JSON のパイプテスト
  （[codex ハーネス初手](/tech/codex-standalone-harness-bootstrap.md)で実証済みの手順）、
  エージェントループは記録済みトランスクリプトの record-replay で決定的にテスト。
  実 LLM・実プロセスを使うテストは統合レーンへ送る。
- **verify の2レーン化**: `./verify --lane sandbox`（エージェントが回す）と
  `./verify --lane full`(ユーザー・CI・コンテナで回す)。統合テストにはタグを付け、
  サンドボックス内では実行せず SKIP 件数を報告させる。
  実環境でもエージェントループの実測テストは高価・非決定的なので、この分割は
  サンドボックス問題がなくても価値がある。

## 方針4（契約）: 回避コード増殖のガード

- **失敗の三分類を機械化**: (a) コード起因 (b) テスト起因 (c) 環境起因
  （permission denied・ネットワーク拒否など sandbox 特有のエラーパターン）。
  (c) を検出したら修正ループに入らず**報告して停止**、を AGENTS.md に明記。
- mock 追加・skip 追加・テスト削除は、環境起因と判断した場合ユーザー承認必須
  （縮退解ガードの適用）。
- DoD を「sandbox レーン全緑 + full レーンの SKIP 一覧を報告」と定義し、
  full レーンの実行はユーザーか CI が担う。「全テストを自力で緑にする」を
  完了条件から外すことが、回避コードを書く動機そのものを消す。

## 一般化できる原則

**エージェントに開発させるものの実行環境と、エージェント自身のテスト実行環境の差分は、
開発開始前に列挙して「埋める（方針1・2）」か「設計で切る（方針3）」かを決めておく。**
差分を放置すると、エージェントは環境差をコードで埋めようとして縮退解を量産する。

# Citations

[1] [Non-interactive mode（learn.chatgpt.com）](https://learn.chatgpt.com/docs/non-interactive-mode) — codex exec デフォルト read-only・danger-full-access の容認条件（原典照合済み）
[2] [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference) — sandbox_mode・network_access・writable_roots
[3] [Agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security) — devcontainer 運用と警告
[4] [Sandboxing 概念](https://learn.chatgpt.com/docs/sandboxing)
[5] [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md) — サブエージェント単位の sandbox_mode 上書き
[6] エスカレーション実装の一次ソース: [openai/codex PR #12839](https://github.com/openai/codex/pull/12839)、[PR #13051](https://github.com/openai/codex/pull/13051)
[7] 関連: [サンドボックスと長時間自律](/tech/agent-sandboxing-and-long-running-envs.md)、[codex ハーネス初手](/tech/codex-standalone-harness-bootstrap.md)、[skill のハーネス化と強制点](/tech/skill-to-harness-enforcement.md)
