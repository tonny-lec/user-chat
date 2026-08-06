---
type: Reference
title: superpowers プラグイン解剖 — 公開ハーネスの実例読み解き
description: obra/superpowers (MIT) の hook・skill 構造を実物で読み解き、ハーネス設計の技術(強制の機械化・合理化潰し・skill の TDD)を抽出したメモ。続編で brainstorming を深掘り、第3回で全14 skill を通読 — 全体は「次の skill を名指しする」開発ライフサイクルのパイプラインであり、規律系3種(TDD/debugging/verification)が Iron Law で横串を刺す構造。
tags: [ai-agent, harness, claude-code, skills, hooks, superpowers, requirements]
timestamp: 2026-08-07T00:00:00+09:00
---

# 概要

[ハーネス基礎](/tech/ai-agent-harness-basics.md) の実例として、ローカルにインストール済みの
superpowers v6.1.1(`~/.claude/plugins/cache/claude-plugins-official/superpowers/`)を解剖した記録。
全コードは MIT で公開: https://github.com/obra/superpowers

# 構成

- `plugin.json` — メタデータのみ
- `hooks/` — SessionStart hook 1本(bash)+ Windows 用ポリグリッドラッパー `run-hook.cmd`
- `skills/` — 14 skill、合計約 3,300 行の Markdown。1 skill = 1 ディレクトリ + SKILL.md

# 設計技術(読み解きで抽出したもの)

1. **強制は機械、知識は文書に分離**。「skill を使え」というルールはモデルの記憶に頼らず、
   SessionStart hook がセッション開始のたびに `using-superpowers/SKILL.md` を
   `<EXTREMELY_IMPORTANT>` タグ付きでコンテキストに機械注入する。
2. **合理化の先回り潰し**。skill 本文の主要部は手順ではなく「Red Flags」
   「Common Rationalizations」表 — LLM がサボるときの内心の言い訳
   (「これは簡単だから手順不要」「緊急だから」等)を列挙して事前に反駁する。
   systematic-debugging では言い訳 8 種に対し 1 行ずつ反論が書かれている。
3. **フェーズゲート**。systematic-debugging は「Phase 1(根本原因調査)完了前に修正提案禁止」
   という Iron Law + 4 フェーズ構造。「3回修正に失敗したらアーキテクチャを疑い人間と相談」
   という脱出条件まで定義。
4. **skill 自体を TDD で作る**(writing-skills)。skill なしでエージェントが失敗する
   シナリオを先に観測(RED)→ skill を書く(GREEN)→ 新しい言い訳を見つけて塞ぐ(REFACTOR)。
   「失敗を観測してからルールを書く」原則のskill版。
5. **トークン効率**。頻繁にロードされる skill は 500 語以内を目標と明記。
   重い参照資料は別ファイルに分離し必要時のみ読む。
6. **泥臭い互換対応**。hook スクリプトは Cursor / Claude Code / Copilot CLI で
   JSON 出力形式を分岐し、Windows では cmd/bash ポリグロットで bash を探す。
   公開ハーネスの中身は魔法ではなく普通のエンジニアリング。

# 続編: brainstorming の解剖 — 要件聞き出しの設計 (2026-07-25, v6.2.0)

「要件をユーザーから聞き出す仕組み」と「コンテキスト収集のハーネス」を目的に
brainstorming skill を深掘りした。結論: **コンテキスト収集をコードで行う機構はほぼ無く、
本体は会話プロトコルの明文化 + ゲートによる強制**。

## 聞き出しの会話プロトコル

- **1 メッセージ 1 質問**。選択式を優先、焦点は purpose / constraints / success criteria の 3 点のみ。
- **質問より先にスコープ判定**。複数サブシステムを含む要求なら質問を始めずに先に分解する
  (「分解が必要なプロジェクトの詳細に質問を浪費しない」)。分解後はサブプロジェクトごとに
  spec → plan → 実装のサイクルを回す。
- コンテキスト収集の実体は「ファイル・docs・直近コミットを探索せよ」という手順書 1 行。
  収集ハーネス(コード)は存在しない。
- 2〜3 案をトレードオフ付きで提示、推奨案を先頭に。全案に YAGNI を適用。
- デザインは**セクション単位で提示し、セクションごとに承認を取る**(全体一括承認にしない)。

## 強制の仕掛け

- `<HARD-GATE>` タグ: デザイン承認まで実装行為を一切禁止。
  さらに「簡単すぎて設計不要」という典型的逃げ道を Anti-Pattern 節で名指しで封鎖
  (todo リスト 1 個でも設計を書け)。
- **プロセスを Graphviz digraph で記述**: 承認ループ(no → revise)を含む状態機械として定義し、
  終端状態を「writing-plans の起動」1 つに固定。他の実装スキルへの分岐を明示的に禁止。
- 出口は多層レビュー: ①セルフレビュー(プレースホルダ・矛盾・曖昧さ・スコープの 4 点)
  → ②ユーザーレビューゲート → ③サブエージェントレビュアー(別ファイルのプロンプトテンプレート。
  「実装計画を壊す問題だけ指摘、文体指摘は禁止」という Calibration 節で指摘の閾値を較正)。

## visual companion — brainstorming 唯一のコード実装

- ローカル HTTP + WebSocket サーバー(`scripts/server.cjs`)。Claude が HTML モックアップを
  ディレクトリに書く → ブラウザが最新ファイルを自動表示 → ユーザーのクリック選択が
  `state_dir/events` に記録され次ターンで Claude が読む、という**ファイルシステム経由の非同期対話チャネル**。
- URL にセッションキーを付与しアクセス制御。HTML はフラグメントで書けばフレームに自動ラップ。
- 過剰使用を抑える規律が本体: 「先に提案するな(視覚で見せた方が明確な質問が初めて出たときだけ、
  単独メッセージで提案)」「承認後も質問ごとにターミナル/ブラウザを判定(UI の話題 ≠ 視覚的質問)」。

## ハーネス細部の追記 (v6.2.0)

- hooks.json の matcher は `startup|clear|compact` — /clear やコンパクト後も再注入される。
- Claude Code は `additional_context` と `hookSpecificOutput` を重複読みするため、
  プラットフォームを環境変数で判別し**片方だけ emit** する(両方出すと二重注入)。
- bash 5.3+ のヒアドキュメントhang回避で printf を使う、などの実戦の傷跡コメントが残っている。

# 第3回: 全14 skill 通読 (2026-08-07, v6.2.0)

「意識せず使っている」状態を脱するため全 SKILL.md(計約3,200行)を通読。最大の発見:
**14 skill はバラバラの道具箱ではなく、各 skill が終端で次の skill を名指しする
1本のパイプライン + 横串の規律 + メタ層**という3層構造になっている。

## 層1: メインパイプライン(開発ライフサイクル)

```
brainstorming → writing-plans → (subagent-driven-development | executing-plans)
                                → finishing-a-development-branch
```

- **brainstorming**: 実装前の要件・設計対話。HARD-GATE(設計承認まで実装禁止)、
  1メッセージ1質問、2-3案+推奨提示、spec を `docs/superpowers/specs/` に保存。
  終端状態は「writing-plans の起動」に固定(他 skill への分岐を明示禁止)。
- **writing-plans**: spec を「コードベースの文脈ゼロの熟練者」向け実装計画に変換。
  タスクは 2-5 分の bite-sized ステップ(test 書く→fail 確認→実装→pass 確認→commit)、
  プレースホルダ禁止(「TBD」「適切にエラー処理」は plan failure)、
  タスク間 Interfaces(Consumes/Produces)を明記、型名の後方一致まで self-review。
  完了時に実行方式 2 択(subagent-driven 推奨 / inline)をユーザーに提示。
- **subagent-driven-development**(最大・503行): タスクごとに新品の implementer
  subagent + 毎タスク2観点レビュー(spec 準拠+品質) + 最後に全ブランチレビュー。
  実運用の傷跡が濃い: compaction 後の再ディスパッチ事故対策の**ledger ファイル**
  (`.superpowers/sdd/<plan>/progress.md`)、fix loop は5ラウンド上限
  (1-3 は同じ implementer を resume、4-5 は上位モデルで新品)、上限到達で
  裁定(park with ruling / load-bearing なら BLOCKED 報告)、
  モデル階層選択(機械的タスクは安いモデル、最終レビューは最上位)、
  dispatch prompt に履歴を貼らない(実例: 42k 字中 99% が貼られた履歴)。
- **executing-plans**: subagent が使えない環境向けの縮退版。計画を批判的に読んで
  から着手、ブロッカーで推測せず停止。終端は finishing-a-development-branch。
- **finishing-a-development-branch**: 全テスト green を確認してから
  3択メニュー(ローカル merge / PR / branch 維持)を提示し人間に委ねる。
  discard は「ユーザーが明示的に求め、`discard` とタイプした場合のみ」。

## 層2: 横串の規律 skill(パイプライン各所から呼ばれる)

3つとも同じ型: **Iron Law 1行 + フェーズゲート + Red Flags + 合理化反駁表**。

- **test-driven-development**: `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST`。
  RED(fail を目視)→GREEN(最小実装)→REFACTOR。テストより先に書いたコードは
  「参照用に残す」も禁止で削除。「後からテストでも同じ」への反駁が最も厚い
  (tests-after は「何をするか」、tests-first は「何をすべきか」を検証する)。
- **systematic-debugging**: `NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST`。
  4フェーズ(Root Cause → Pattern → Hypothesis → Implementation)+
  「3回修正失敗したらアーキテクチャを疑い人間と相談」の脱出弁。
- **verification-before-completion**: `NO COMPLETION CLAIMS WITHOUT FRESH
  VERIFICATION EVIDENCE`。「このメッセージ内で検証コマンドを実行していないなら
  pass と言えない」。subagent の成功報告も VCS diff で独立検証せよと明記。
  「Great!」「Done!」等の満足表現自体を検証前は禁止。

## 層3: 支援・メタ skill

- **requesting-code-review**: reviewer subagent への依頼手順。BASE/HEAD SHA を渡し
  code-reviewer.md テンプレを充填。「diff を自分でレビューしない(コンテキスト温存)」。
- **receiving-code-review**: レビューを受ける側の規律。**"You're absolutely right!"
  を名指しで禁止**、感謝表現も禁止(行動で示す)。外部レビューは実装前に
  コードベース照合、YAGNI チェック(未使用機能の「ちゃんと実装」提案は削除を逆提案)。
  不明項目が1つでもあれば全部止めて先に確認(部分理解での着手禁止)。
- **using-git-worktrees**: 隔離作業場の確保。native tool(EnterWorktree 等)優先、
  無ければ `.worktrees/` に git worktree(gitignore 確認必須)、ベースラインテストまで。
- **dispatching-parallel-agents**: 独立した失敗が複数あるとき 1 problem = 1 agent で
  同一メッセージ並列起動。関連疑いがあれば並列化しない。
- **using-superpowers**(入口): SessionStart で機械注入される唯一の skill。
  「1% でも該当可能性があれば skill を起動せよ」+ 12 個の red-flag 思考パターン表。
  冒頭の `<SUBAGENT-STOP>` タグで「dispatch された subagent はこの skill を無視せよ」
  と定め、subagent が毎回 brainstorming を起動する自己適用ループを封じている。
- **writing-skills**: skill 作成の TDD(既記録)に加え、SDO(Skill Discovery
  Optimization)が実践的: **description には発動条件だけ書き、手順を要約しない**
  (要約すると agent が本文を読まずに description だけで動く実測例あり)。
  禁止形と処方形の使い分け表(Match the Form to the Failure)—
  規律違反には禁止+反駁表、出力形状の問題には処方(recipe)。禁止形は
  形状問題に対して no-guidance 対照より悪化する実測結果まで書いてある。

## 使う側としての実践的含意

1. **skill は自動では発動しない**。機械注入されるのは using-superpowers だけで、
   残り 13 は「Claude が description を見て Skill ツールで読む」。つまり発動率は
   モデルの自制心依存 — 確実に使わせたいときはユーザーが名指しするのが速い。
2. **パイプラインに乗ると出口まで長い**。brainstorming に入ると
   spec → plan → SDD → finishing まで一本道に設計されている。軽い変更で
   全行程が過剰なときは、乗せる前に止める判断が要る(skill 側は「simple でも
   やれ」と主張するため、ユーザー指示でしか止まらない)。
3. **成果物の置き場が固定**: spec は `docs/superpowers/specs/`、plan は
   `docs/superpowers/plans/`、SDD の作業台帳は `.superpowers/sdd/<plan名>/progress.md`。
   セッションが死んでも ledger と git log から再開できる設計。
4. 自作 harness への流用価値が高いのは: Iron Law + 反駁表の型、ledger による
   compaction 耐性、fix loop の上限と裁定ルール、SDO の「description に手順を
   書かない」原則。関連: [skill-to-harness-enforcement](/tech/skill-to-harness-enforcement.md)

# 含まれる skill 一覧(役割別)

- パイプライン: brainstorming → writing-plans → subagent-driven-development /
  executing-plans → finishing-a-development-branch
- 横串の規律: test-driven-development, systematic-debugging, verification-before-completion
- 支援: requesting/receiving-code-review, using-git-worktrees, dispatching-parallel-agents
- メタ系: using-superpowers(入口), writing-skills(skill の作り方)

# Citations

[1] [obra/superpowers (GitHub)](https://github.com/obra/superpowers)
