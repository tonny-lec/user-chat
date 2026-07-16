---
type: Playbook
title: Codex セッションのトークン消費分析 — 手順と読み違えの罠
description: threads テーブルと rollout の token_count からプロジェクト別トークン消費を分解する手順。tokens_used は fork が親カウンタを複製するため単純合計は過大、実消費は非キャッシュinput+outputの差分で測る。sheetlens 実測で「常駐コンテキスト×ステップ数」が支配項と判明。手順1〜3は docs/codex-token-report.py にスクリプト化済み。
tags: [codex, tokens, observability, harness, cost]
timestamp: 2026-07-17T00:00:00+09:00
---

# 手順（sheetlens 分析で確立）

1. **セッション一覧**: `~/.codex/state_5.sqlite` の `threads` を cwd で絞る
   （`rollout_path`・`tokens_used`・`created_at/updated_at`・`source`・`title`）。
2. **fork の識別**: `source` に `subagent.thread_spawn` があれば fork。
   親 thread_id・agent_path（フェーズ名）・nickname もここに入っている。
3. **実消費の算出**: rollout の `token_count` イベントの `total_token_usage` について
   **(input - cached_input) + output** をファイル先頭と末尾で差分する。
   これが「モデルが新規に読んだ+書いた」量。
4. **構造の分解**: `last_token_usage.input_tokens` の系列 = 各ステップの送信コンテキスト
   （中央値・最大を見る）。`context_compacted` 回数、ツール出力サイズ、
   exec 入力の頻度分布（先頭70字で Counter）でループ・小分けパッチの指紋を取る。

# 読み違えの罠（実測で踏んだもの）

- **`tokens_used` の単純合計は大幅な過大**。fork は親の transcript とカウンタを
  丸ごと複製して始まるため、親150Mなら子も150Mからカウントする。
  sheetlens では見かけ21億 → fork除外の実消費974万（220倍の差）。
- **99%キャッシュでも無料ではない**。API換算でキャッシュ入力は約1割課金相当、
  サブスクでは rate limit を消費（重み付けは非公開）。
- **rate limit の used_percent をセッション開始/終了で比較しない**。
  窓（5h）を跨ぐとリセットが挟まり無意味。

# 実務環境への持ち出しキット（2026-07-13）

「実務で gpt-5.6 + Codex CLI を使う」向けの持ち出し構成。持っていくのは実質1ファイル:
`~/workspace/docs/harness-token-budget.md`（設計7則＋S1-S3/D1。マシン固有パスを一般化済み —
state_N 自動検出・fork 除外入り D1 クエリ）＋実務マシンの AGENTS.md に3行ポインタ。

ハーネス不要で初日から効く運転習慣（効果順）:
1. スレッド寿命=課題1件（長生きスレッドが最大の敵。課題が変わったら /new）
2. fork 控えめ（親 transcript 複製。fresh + issue/対象ファイルのハンドオフで足りるか先に問う）
3. 生ログを入れない（テストは失敗のみ・grep 一致行のみ・head 上限）
4. 全文を書かせない（出力は約5倍単価・キャッシュ不可）
5. ステップをまとめる（1step=常駐全再送）
設定: 未使用 MCP を繋がない / AGENTS.md 3行ポインタ / effort はむやみに下げない
（120ラン実測: agentic では low が medium より高い）/ プレフィックスに変動値を入れない。
計測は週1で本 Playbook の手順1〜3。

# 観測スクリプト化と業務PC展開（2026-07-17）

業務PCでの「どこが無駄か不明」相談を受け、手順1〜3+支配項分解を単一ファイルにスクリプト化:
**`~/workspace/docs/codex-token-report.py`**（stdlib のみ・読み取り専用・state_N 自動検出・
fork 分離・長生きスレッド/太い常駐/fork超過の3警告付き）。
`python3 codex-token-report.py --days 7 [--cwd <repo>]` で週次レポートが出る。

これで持ち出しキットは4点セットに確定:
1. `docs/harness-token-budget.md`（設計7則+検収述語）
2. `docs/codex-token-report.py`（観測。まずこれを実行してから打ち手を選ぶ）
3. `docs/codex-token-watch.sh`（測定の自動化。.bashrc から source すると週1で
   バックグラウンド生成→次のシェル起動時に警告だけ1度表示。表示済みはクリア、
   スロットルは `.stamp` 別ファイル。同期実行しないので起動を遅くしない）
4. `~/.codex/AGENTS.md` 末尾の3行ポインタ（見出し「## ハーネス作成」+2行。文面はローカルの同ファイル末尾からコピー）

導入手順（業務PC）: 上記3ファイルを同一ディレクトリに置く → `.bashrc` に
`source <置き場>/codex-token-watch.sh` を1行 → AGENTS.md に3行追記。以後は何もしない
（週1で警告が勝手に出る。全文レポートが見たいときだけ `codex-token-report.py --days 7`）。

**測定のトークンコストは 0**。スクリプトはローカルの sqlite/JSONL を読むだけで
モデルに一切触れない。トークンを消費する測定になるのは「エージェントに測定させた」
場合だけなので、測定は必ずエージェント外（シェル直実行 or watch の自動実行）で行う。

ローカル実測の教訓（2026-07-17, 直近30日）: main 48.7M に対し **fork が 392M と8倍**、
常駐コンテキスト中央値 100K 超が 35/128 本。自分の環境ですら無駄の在り処は
「観測するまで直感と違う」の再確認になった。

# 消費の支配項と改善レバー（sheetlens 実測: 17.5h・893step・fresh 200万/セッション）

支配項は **常駐コンテキスト（中央値202K）× ステップ数（893）** の再送。fresh は薄い。

1. **セッション寿命を課題1件に切る**（最効）: backlog ループを1スレッドで回さず
   issue ごとに fresh スレッド。常駐 20万→数万で送信総量 1/4〜1/10。
2. **fork をやめ fresh + ハンドオフ**: sheetlens は161本中122本が fork で、
   フェーズ処理の子が全員親の全履歴を継承。子に必要なのは issue + 対象モジュールのみ。
3. **ステップ数の圧縮**: 小分けパッチ38連発など。1step = 常駐全再送なので線形に効く。
4. **計測の常設化**: 手順1〜3を30行スクリプトにして Stop hook から
   「fresh / steps / max_context / fork数」を log.tsv に1行。閾値超で警告。

関連: [ハーネスのトークン経済学](/tech/harness-token-economy.md)（コストモデル側。本文書はその測定手順にあたる。
経済学の D1 述語=凍結タスク×N回比較は、本手順3の fresh 差分で実装できる）、
[エージェント観測基盤の構想](/tech/harness-observability-platform.md)（rollout 直読が正解の理由・自己記録の非対称）、
[ハーネスの散らかりと干渉](/tech/harness-sprawl-and-interference.md)（観測→淘汰の接続）。
