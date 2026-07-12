---
type: Playbook
title: Codex セッションのトークン消費分析 — 手順と読み違えの罠
description: threads テーブルと rollout の token_count からプロジェクト別トークン消費を分解する手順。tokens_used は fork が親カウンタを複製するため単純合計は過大、実消費は非キャッシュinput+outputの差分で測る。sheetlens 実測で「常駐コンテキスト×ステップ数」が支配項と判明。
tags: [codex, tokens, observability, harness, cost]
timestamp: 2026-07-12T00:00:00+09:00
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
