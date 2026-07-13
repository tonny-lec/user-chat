---
type: Consultation
title: Dify + dbt で BI グラフは作れるか — 会話型アドホック分析なら◎、常設ダッシュボードなら✕
description: 2つは直接連携しない。dbtがマートと指標定義を整え、DifyがNL→SQL→ECharts描画の会話UIを担う分業なら成立。ダッシュボード用途はdbtネイティブBI（Lightdash等）が正解。
tags: [dify, dbt, bi, data-visualization, text-to-sql, echarts]
timestamp: 2026-07-13T00:00:00+09:00
---

# 相談内容

Dify と dbt を組み合わせたら BI 分析用のグラフを柔軟に作れるか。

# 検討・調査

- dbt と Dify は直接連携する製品ではない。dbt はグラフを描かず、Dify はデータ変換をしない。
- 成立する構成: `DWH マート層（dbt が構築）← SQL ← Dify チャットフロー（NL→SQL→実行→ECharts 描画）`
- Dify 側の描画能力は実在: 公式マーケットプレイスの ECharts Chart Generator プラグインで
  棒・折れ線・円などをチャット返答内に描画できる。Excel→EChart 変換ボット等の実例多数。
- dbt の貢献はグラフの手前。マート整備＋カラム説明・リネージの機械可読メタデータで
  LLM の SQL 生成の推測を潰す（[三層×AIの整理](/tech/semantic-layer-ontology-dbt.md)の構図そのまま）。
- dbt Semantic Layer (MetricFlow) まで入れると SQL 生成が決定的になり、定義済み指標の
  範囲では精度がほぼ 100% に近づく（dbt 公式ブログ 2026 ベンチマーク）。
  Dify からは Semantic Layer API を叩くカスタムツール1個で接続可。

# 結論

「柔軟に作れるか」は用途で割れる:

| 用途 | 評価 |
|---|---|
| 会話でアドホックに聞いてグラフで返す | ◎ Dify + dbt マートで成立。柔軟さの本領 |
| 常設ダッシュボード・定期更新・ドリルダウン | ✕ Dify のグラフは会話に埋まる静的な一枚絵。保存・対話操作なし |
| 定型レポート自動生成・配信 | △ 組めるが BI ツールのスケジュール配信の方が楽 |

- ダッシュボード要件なら dbt の相方は BI ツール（Lightdash は dbt 定義を直接読む /
  Metabase / Superset）。最近の BI は AI 質問機能を内蔵し始めており、
  「会話で聞く」体験だけなら Dify を挟まず済む可能性もある。
- **現場への接続**: [dbt パイロット処方箋](/tech/semantic-layer-ontology-dbt.md)の
  ステップ4「metric を定義し AI に聞かせて縦に貫通」の AI 実装として Dify は手頃。
  チャットフロー1本＋DWH クエリのカスタムツール＋ECharts プラグインで
  「質問したらグラフが返る」デモまで到達でき、経営層向けの縦切り成果物になる。
- 鉄則は前回と同じ: **Dify を向ける先は必ずマート（将来は metric）**。レイク直結の
  text-to-SQL が一番事故る。

# Citations

[1] [ECharts Chart Generator - Dify Marketplace](https://marketplace.dify.ai/plugins/langgenius/echarts)
[2] [Semantic Layer vs. Text-to-SQL: 2026 Benchmark Update - dbt Developer Blog](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026)
[3] [Best BI Tools for dbt Teams (2026) - Omni Analytics](https://omni.co/articles/best-bi-tools-for-dbt-teams-governed-semantic-layer-ai-queries-and-embedded-analytics-2026)
[4] [Why Semantic Layers Make Enterprise Text-to-SQL Safer](https://datalakehousehub.com/blog/2026-05-semantic-layers-text-to-sql/)
[5] [Dify で Excel データを ECharts グラフに自動変換 - Qiita](https://qiita.com/engchina/items/7a57bb7f887df44ef4be)
