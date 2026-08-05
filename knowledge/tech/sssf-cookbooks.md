---
type: Reference
title: SSSF (Super Simple Software Factory) cookbooks 全9ファイルの読解
description: disler の SSSF スキルの cookbooks 9ファイルを精読した要約。決定論的 Python (ADW) がシーケンス・リトライ・受入を握り、エージェントはグラフ内の境界付きノードという「agent proposes, code disposes」設計。v1 の実行系は pi。
tags: [ai-agents, harness, orchestration, pi, claude-skills]
timestamp: 2026-08-06T00:00:00+09:00
---

# SSSF cookbooks 読解

対象: https://github.com/disler/super-simple-software-factory/tree/main/.claude/skills/sssf/cookbooks （2026-08-06 時点、全9ファイル・約850行）

## 中核設計（全ファイルに通底する原理）

- **Agent proposes, code disposes**。ADW (AI Developer Workflow) と呼ぶ決定論的 Python スクリプトがシーケンス・リトライ・受入判定を所有し、エージェントはその中の境界付きノード。テスト実行のような「コマンドが既知」の仕事はエージェントに再発見させず `kind="code"` フェーズで直接実行する。
- **フェーズモデル**: 全実行は `engineer`（人間の依頼記録）/ `agent`（プロンプト→型付き envelope→ゲート検証）/ `code`（git 操作等の決定論的ステップ）の3種のフェーズ列。**全フェーズはデフォルト `fail`** で、正常終了して初めて success に反転する（成功は獲得するもの）。
- **Envelope**: エージェントの出力チャネルは2つだけ — `context_handoff/` への参照ファイルと、宣言された Pydantic 型に対してパースされる最終 JSON。次エージェントの user.md に `{{previous_envelope}}` として注入される。JSON 不正時は再起動ではなく**同一セッションへの再プロンプト**（コンテキスト維持、回数制限つき）。
- **出力契約は同期された三つ組**: `data_types.py` の型 ↔ user.md の `## Report` JSON 例 ↔ 呼び出し側の `output_type=`。1つ触ったら3つ同時に編集。ドリフトすると全呼び出しが補正リトライの税を払う。
- **ゲート**: `gate(envelope, run) -> GateReport`。主張を検証する（予測しない）、数はプロパティで表現（`len==3` 禁止）、1件失敗しても全件チェック、pass にも証拠ノートを書く。違反はエージェント再起動ではなく同一セッションへの補正として返る（フェーズの `retries` が上限）。「計画の質・コードの趣味」はゲート不能 — それはレビュアーエージェントか人間の仕事。
- **オーケストレーターの姿勢**: スキルを読む Claude は「起動・監視・報告」のみ。対象アプリのコードを読まない・直さない。修正は config/プロンプト/ADW の変更として意図的に行い再実行する。
- **観測**: SQLite (WAL) の trace db に全イベントが落ち、stdout の各行も `log` イベントとして同録（端末と UI が構造的に同じ物語を語る）。ハングは「赤」でなく「無音」になるので、phases→procs→kill の順で読む。

## 各ファイルの役割

| ファイル | 内容 |
|---|---|
| `sssf_overview.md` | 起動時に読む唯一のファイル。リポジトリ構造（adws/、adw_modules/、adw_data/）、フェーズモデル、envelope、次に読む cookbook の表。読了後は ADW 一覧を出して**待つ**（先回りの調査はコンテキストの浪費と明記） |
| `install.md` | `install.py` でテンプレートを対象リポジトリに刻印。既存ファイルは全スキップ（冪等、`--force` は全上書きなので注意）。post-install チェックリスト（env・pi・モデル解決・gitignore・git repo・スモークテスト） |
| `create_adw.md` | 新規 ADW の設計手順: ①どのエージェントをどの順で ②コードが働く場所はどこ ③ループはあるか ④各呼び出しは何を証明するか。canonical スケルトン（uv 単一ファイルスクリプト）と非交渉ルール（REQUIRED_AGENTS 宣言、型付き handoff、4引数ルール、thin に保つ） |
| `update_adw.md` | フェーズ追加/削除、ゲート追加、有界 fix ループ。3つの区別が肝: gate リトライ vs JSON リトライ（別勘定）/ フェーズリトライ vs fix ループ / 「テストフェーズは赤スイートでも成功」（ランナーは仕事をした。失敗は `run.finish(accepted=)` で run 全体に付ける） |
| `create_config.md` | `sssf.config.yaml` 生成。原則「one agent, one prompt, one purpose」。エージェントが誰か（model・thinking・プロンプト対）は config、どう使うか（output_type）は呼び出し側 |
| `update_config.md` | ロスターの再調整。モデルは常に `provider/model-id`。**モデル変更はセッション無効化**（thinking 変更はしない）。tools 許可リストの解決規則と「拡張が登録するツールも許可リストに明記しないと無言で落ちる」罠 |
| `update_modules.md` | 低レベルロジックは全部 `adw_modules/` へ。モジュール別責務表、`print()` 禁止（Console 経由で db 同録）、4引数ルール、出力型の追加（三つ組編集）、ゲートの書き方 |
| `how_to_prompt_for_the_eng.md` | 毎起動前に読む翻訳規律。「意図は依頼者のもの、精密さはお前のもの」— 明確化はするが再設計しない。4行形式（ask / Where / Done means / Out of scope）。チェーン選択は「指名されたらそれ、なければ作業が正当化する最長の合成チェーン」。起動後は送ったプロンプト verbatim・選んだ ADW と理由・adw_id を報告 |
| `run_adw.md` | 起動と監視。ロスター（config）の聞き取り表現の解釈、**勝手にロスターを替えない**、`--adw-id` でのセッション継続、sqlite ポーリングのクエリ集（rowid カーソル）、ハング対応、報告の型 |

## 拾う価値のある個別の工夫

- `PhaseParams` が **description の空欄・名前の言い換えを構築時に raise** する — 「読めないトレースを db に残す前に落とす」というルールの機構化。
- `quality.as_envelope()`: 決定論的なテスト結果を envelope の形に整形して builder に渡す — 受け手のエージェントは出所がコードか他エージェントか区別できない（インターフェース統一）。
- プロンプト規律の「ハーネスに語りかけるな」: 「reviewer を使え」「2回リトライ」は ADW の選択で表現するもので、エージェントが読む散文に書かない。
- 起動時の overview に「今調べたものは全部、実作業のコンテキストからの前借り」と lazy-load を設計として明文化。

## 関連

- [hermes-agent / pi / Archon 比較](/tech/hermes-pi-archon-comparison.md) — SSSF v1 の実行系は pi（`pi -p --mode json`、`--session-id` で create-or-continue）。Archon と同様「pi をプロバイダとして取り込む上位層」の実例。
- [LLM の構造的事実9つとハーネス設計レバー](/tech/llm-structural-facts-to-harness-levers.md) — 「JSON 不正は同一セッション再プロンプト」「ゲート違反は補正として返す」は、コンテキスト維持を最優先するレバー配置の実装例。

# Citations

[1] [super-simple-software-factory cookbooks](https://github.com/disler/super-simple-software-factory/tree/main/.claude/skills/sssf/cookbooks)
