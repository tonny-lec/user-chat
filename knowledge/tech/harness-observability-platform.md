---
type: Consultation
title: エージェント観測基盤の構想 — 失敗シグナルは追加を駆動するが削除を駆動しない
description: ハーネス/hook/skill の観測・可視化基盤の構想相談と deep-research 結果。失敗観測は片翼で、淘汰には利用観測（発火率・生存率）が要る。計装は自作不要（Claude Code は skill_activated/hook_execution 等の公式 OTel イベントを持つ）、ハーネス資産の観測は標準化・既製品とも空白地帯、自作するのは受け口と閲覧UIだけ。
tags: [ai-agent, harness, observability, telemetry, claude-code]
timestamp: 2026-07-12T00:00:00+09:00
---

# 相談内容

ハーネス・hook・skill をエージェントに作らせる運用が定着してきた。仮説は2つ:

1. これらは「失敗から修正して洗練されていく」のが基本運用ではないか。
2. 失敗だけでなく「使われていないコンポーネント」「無駄なフロー」も観測すべきで、
   常時観測・可視化できる基盤を先に作り、その上でハーネスを育てれば改善が高速に回るのではないか。

この仮説の検証と、開発のための情報収集（既存ツール・標準化動向・観測シグナルの実践例）。

# 検討・調査

## 仮説1の検証: 失敗観測駆動は正しいが「片翼」

失敗観測駆動（[ハーネス基礎](/tech/ai-agent-harness-basics.md)）は追加・修正を駆動するが、
**削除・淘汰を駆動しない**。使われていないコンポーネントは失敗を起こさない — 何もしないから。
[ハーネスの散らかりと干渉](/tech/harness-sprawl-and-interference.md)で出た結論
「作る速度に淘汰の速度が追いついていない」がこの穴の正体で、淘汰には
「消して失敗が再発するか」テストと発火ログという**利用観測**が必要。
つまり仮説2（未使用・冗長の観測）は仮説1の欠落を正確に補完している。

## 観測すべきシグナルのマトリクス

指標の語彙は [eval 入門](/tech/evals-for-practitioners.md) のハーネス層別検証がそのまま使える。
観測基盤が集めるのは実質「3層 × 3シグナル」:

| 層 | 失敗シグナル | 利用シグナル（未使用検出） | 冗長シグナル |
|----|------------|------------------------|------------|
| hook | エラー・block の妥当性 | 発火ログ（いつ・何が・何を返したか） | 同一イベントの多重発火（1イベント1オーナー違反） |
| skill | 遵守率（発動後に従ったか） | 発火率（呼ばれるべき時に呼ばれたか） | トリガー記述の重なり・発火の奪い合い |
| 文書層（CLAUDE.md） | 規約違反の観測 | 規約の生存率 | 矛盾・重複指示 |

## 仮説2の検証: telemetry-first は正しいが platform-first は罠

- **観測を先に入れること（telemetry-first）は正しい**。淘汰も干渉デバッグも観測なしでは回らない。
- ただし「基盤」を最初から作り込むと、誰も消費しないダッシュボードという
  **それ自体が未使用コンポーネント**になる。観測基盤も1本のハーネスであり、
  自分自身の淘汰テスト（観測データを実際に読んで意思決定した回数が証拠）に合格し続ける必要がある。
- この環境には最小版が既に存在する: failure-review / failure-dashboard skill、
  lets-deep-agents の log.tsv、発火ログの構想。**ゼロから建てず、既存の観測断片を
  共通スキーマに合流させ、可視化は薄く載せる**のが起点。

# 結論

1. 「失敗から修正」は基本運用として正しいが、それだけでは肥大化する一方。
   削除・淘汰を駆動する利用観測（発火ログ・発火率・生存率）を対にして初めてループが閉じる。
2. 観測シグナルは「3層（hook/skill/文書）× 3種（失敗/利用/冗長）」のマトリクスで設計する。
3. 順序は telemetry-first（観測点を先に仕込む）であって platform-first（基盤を作り込む）ではない。
   基盤は「観測データを読んで意思決定した回数」を証拠に育てる。

# 調査結果（deep-research 2026-07-12。証拠ラベル: 【検証済】=敵対的検証3-0票+原典スポットチェック、【一致】=独立複数ソース一致、【未検証】=単一ソースのみ）

## 1. 計装は自作不要 — Claude Code は公式にハーネス資産レベルのテレメトリを持つ【検証済】

`CLAUDE_CODE_ENABLE_TELEMETRY=1` + 標準 `OTEL_*` 環境変数で OTel 3シグナル
（メトリクス・イベント・トレース(β)）を OTLP/Prometheus に export できる [1]。
決定的なのはイベントの粒度が「LLM 呼び出し」ではなく**ハーネス資産**であること:

- `claude_code.skill_activated`（`skill.name`・`invocation_trigger`=user-slash/claude-proactive 付き → **発火率がそのまま取れる**）
- `claude_code.hook_execution_start/_complete`・`hook_registered`（`hook_event`・`hook_name` 付き → 発火ログの公式版）
- `claude_code.tool_decision`（ツールごとの許可/拒否とその決定元）
- メトリクス属性に `skill.name`・`agent.name`・`plugin.name`・`mcp_tool.name`、全イベントに `prompt.id`（UUID）→ コンポーネント別集計とプロンプト単位のトレース再構成が可能

## 2. Codex CLI も OTLP export 対応、ただし穴あり【検証済】

config.toml の `[otel]` で logs/metrics/traces を独立に otlp-http/otlp-grpc へ export [2]。
既知の穴（codex-cli 0.105.0 時点、2026-02 の issue #12913）: `codex exec`（ヘッドレス）は
**メトリクスがゼロ**（対話モードは~50個出る）、`codex mcp-server` は OTel 未初期化で全シグナル無し。
補完材料【未検証】: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` が全イベントストリームを持ち、
`codex resume`/`fork` を支える load-bearing な安定インターフェース。

## 2b. Codex CLI の観測面の実地調査（このPC・codex-cli 0.144.1、2026-07-12）【実測】

Web調査の続きとしてローカルの実物を検分した結果。**Codex の観測資産は rollout JSONL +
SQLite 群で、Claude Code より生データは厚いが、ハーネス資産のラベルが無い**。

観測に使える資産（すべて `~/.codex/`）:

- **rollout JSONL**（`sessions/YYYY/MM/DD/rollout-*.jsonl`、289本蓄積）: 全イベントストリーム。
  `session_meta`（model・cwd・cli_version・context_window）、**ターンごとの `turn_context`
  （approval_policy・sandbox_policy・permission_profile・model・effort・personality・comp_hash）**、
  `custom_tool_call`/`_output`（status付き）、`token_count`（ステップ単位）、`sub_agent_activity`、
  `patch_apply_end`、`mcp_tool_call_end`、`turn_aborted`、`context_compacted`。
  turn_context がターン単位の設定スナップショットなので、**介入前後比較（ハーネスA/B測定）の
  結合キーとして優秀**。
- **state_5.sqlite の `threads` テーブル**: セッション索引が既に集計済み
  （rollout_path・cwd・model_provider・sandbox_policy・approval_mode・**tokens_used**・title）。
  JSONL をパースせずに SQL で横断集計できる受け口がすでにある。
- **logs_2.sqlite**（内部トレーシング約17万行）: `codex_otel::*` が生きており、`[otel]` 未設定でも
  メトリクス export 自体は内部で動いている。デバッグ用でハーネスシグナルは無い。

決定的なギャップ（Claude Code との差）:

- **skill はイベントにならない**。ツール呼び出しの実体はほぼ `exec`（直近60セッションで
  custom_tool_call 1,483件中 exec 1,490+42件）で、skill 発動は exec に溶けて区別不能。
- **hook は「介入した時だけ」痕跡が残る**（当初「記録ゼロ」と書いたが実セッション検分で訂正）。
  Stop hook がブロック/継続を出すと `<hook_prompt hook_run_id="stop:0:...">` マーカー付き
  user message として rollout に記録される。ただし発火して素通り（pass）したケースは無痕跡
  → **発火率の分母が取れない**。hook_prompt マーカーは「hook の介入がセッションをどう変えたか」を
  追う結合キーとして有用。

## 2c. 自己記録の設計 — hook と skill で信頼性が非対称（2026-07-12 続き）

「skill と hook が自己記録なら Codex に検証基盤を作るべきか」への答え: **基盤は不要、差分2つ**。

- **hook: 観測はラッパーで機械化、検証は普通のテスト**。hooks.json の command を
  `log-wrap.sh <実コマンド>` に差し替えれば、hook 本体に手を入れず全 hook の
  発火時刻・exit code・所要時間が log.tsv に落ちる（〜30行）。モデルの遵守に依存しない
  機械記録なので信頼できる。検証は [eval 入門](/tech/evals-for-practitioners.md)の結論どおり
  ユニットテストで足りる（率不要）。実例: stop_gate.py（116行）には現状ログが1行も無い。
- **skill: 自己記録は測定器と測定対象が同一になる罠**。skill の自己記録はモデルに echo
  させる形になるため、マーカー欠落が「発火しなかった」のか「発火したが記録をサボった」のか
  区別できない — skill 遵守を測りたいのに記録行為自体が遵守の一部。
  → 発火率・遵守率は自己申告ではなく **rollout への外部述語**（skill が定める行動パターンが
  transcript に現れたかの grep 判定）で測る。eval 入門の発火率手法の判定器を rollout に
  向けるだけで、基盤ではなく述語の集合。arXiv 2605.10039 の `@tracked` マーカーは
  モデル自己申告方式の例（統計量で弱さを補った研究計測）で、個人環境なら rollout 直読が強い。

一般化: **自己記録の信頼性は「誰が書くか」で決まる。機械（hook ラッパー）が書けば観測、
モデルが書けば自己申告 — 後者は測定に使わず、外部述語で置き換える。**

| シグナル | Claude Code | Codex CLI 0.144.1 |
|---------|-------------|-------------------|
| skill 発火 | `skill_activated`（公式イベント） | 無し → skill 側で自己記録するしかない |
| hook 発火 | `hook_execution_start/_complete` | 無し → hook 自身が log.tsv に1行吐く |
| ツール実行 | `tool_decision`（許可/拒否付き） | rollout の `custom_tool_call` + turn_context |
| セッション索引 | transcripts JSONL（要パース） | `threads` テーブル（SQL可・tokens_used集計済み） |
| 有効化 | 環境変数1つ | rollout/SQLite は**常時オン**（設定不要） |

→ 基盤の Codex 側取り込みは「OTel を立てる」より **rollout JSONL + threads テーブルを直接読む**
のが正解（常時オン・設定不要・過去289セッション分が既にある）。`[otel]` は token/latency の
時系列が欲しくなったら追加する。

## 3. 標準化: エージェント操作までは標準あり、ハーネス資産は空白地帯【一致】

OTel GenAI semantic conventions は `execute_tool {tool.name}`・`invoke_agent` 等
エージェント動作のスパンを定義するが、まだ **Development 段階**（2026年に専用リポジトリ
open-telemetry/semantic-conventions-genai へ移動したばかり = 動く標準）。
OpenLLMetry の agent-observability RFC も提案段階で、対象はオーケストレーション
フレームワーク（LangGraph 等）。**CLAUDE.md・hooks・skills のようなハーネス資産の
観測は標準化の対象外** — 自作基盤が埋める空白はここ。

## 4. 既存プラットフォームはハーネス資産の利用観測をやらない【一致】

Langfuse/LangSmith/Braintrust の守備範囲はトレース・eval・プロンプト管理まで。
ハーネス設定資産（hooks・ツール定義・CLI設定）の利用状況・未使用検出を扱う製品は
比較記事群でゼロ。Braintrust の eval は「事前定義した失敗モードしか測れない」=
未知の失敗発見は守備範囲外。例外的に Laminar は trace 全データへの SQL と、
Claude Code/Codex が trace を読んで修正する debugger ループを持ち、改善ループに最も近い。
需要の実証: claude-code の feature request #35319（org で skill が4週間で67→183本に増殖、
使用データ0件で未使用検出不能）が per-skill 分析・**90日ゼロ呼び出し=廃止候補**・
高呼び出し低成功率などまさに「失敗以外のシグナル」を要求している【未検証】。
（注: 公式 docs は現在 skill_activated を載せており、issue の「per-skill 不能」は解消済みの可能性）

## 5. 遵守率は機械測定できる（研究事例）【未検証・原典未読】

arXiv 2605.10039（Claude Code 1,650セッションの要因計画実験）: 構文検出可能なマーカー指示
+ AST パースで遵守率を二値測定（16,050関数）。知見: CLAUDE.md の構造4変数（サイズ・位置・
分割・AGENTS.md との矛盾）は遵守率に効果なし、遵守率は**セッション内で減衰**
（生成ステップごとオッズ約5.6%低下、最初の3〜4関数に集中）。
→ 文書層の「生存率」測定の実装参考例。減衰するなら観測も時系列で持つ必要がある。

## 6. アプローチ論: 見立てと外部ソースが一致【一致】

- Hamel Husain (evals FAQ): 観測プラットフォームから始めるな、まず実トレース50〜100件の
  error analysis。ベンダーはコア機能がコモディティで結局その上に自作する。
  ただし**カスタムのデータ閲覧UIは最高ROIの投資**（汎用プラットフォームでは代替不能）。
- Thoughtworks Technology Radar: "Incremental developer platform" / Team Topologies の
  **Thinnest Viable Platform**（wiki 1枚から始めてよい）。フル自作もチケット駆動も両極とも失敗モード。

→ 本文の結論（telemetry-first ○ / platform-first ×）と独立ソースが一致。
自作すべきは「受け口（collector+ストア）と閲覧UI」だけで、計装は公式機構に乗る。

## 推奨アーキテクチャ（この環境向け）

1. **計装**: Claude Code は `CLAUDE_CODE_ENABLE_TELEMETRY=1`、Codex は `[otel]`（exec の
   メトリクス欠落は JSONL rollout で補完）。自作 hook の1行ログは既存 log.tsv に合流。
2. **受け口**: ローカル OTel Collector（または直接ファイル export）→ 単一ストア。
   SigNoz に Claude Code 用既製ダッシュボードあり【未検証】だが、まず薄く始めるなら
   OTLP→JSONL/SQLite で十分。
3. **可視化**: 既存 failure-dashboard skill に「利用シグナル」面（skill別発火数・
   90日ゼロ呼び出し・hook 多重発火）を追加する形で薄く。
4. **淘汰への接続**: ゼロ呼び出しリスト → 「消して失敗が再発するか」テストの入力にする。

関連: [強制点の設計](/tech/skill-to-harness-enforcement.md)（層が下ほど観測も機械化しやすい）、
[モデル移行観測フロー](/tech/model-migration-observation-flow.md)（観測データの比較器としての使い方）。

# Citations

[1] [Claude Code Monitoring (公式)](https://code.claude.com/docs/en/monitoring-usage) — skill_activated/hook_execution/tool_decision イベントと skill.name 等の属性（原典確認済 2026-07-12）
[2] [Codex config reference (公式)](https://developers.openai.com/codex/config-reference) — `[otel]` セクション
[3] [codex issue #12913](https://github.com/openai/codex/issues/12913) — exec/mcp-server のテレメトリ欠落報告
[4] [OTel GenAI semconv リポジトリ](https://github.com/open-telemetry/semantic-conventions-genai) — 2026年に本体から分離（原典確認済: 移動を確認）
[5] [claude-code issue #35319](https://github.com/anthropics/claude-code/issues/35319) — skill 利用分析の feature request（67→183本・使用データ0件）
[6] [arXiv 2605.10039](https://arxiv.org/abs/2605.10039) — CLAUDE.md 遵守率の要因計画実験
[7] [Hamel Husain: LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/) — error analysis first・カスタム閲覧UIが最高ROI
[8] [Thoughtworks: Incremental developer platform](https://www.thoughtworks.com/radar/techniques/incremental-developer-platform) — Thinnest Viable Platform
