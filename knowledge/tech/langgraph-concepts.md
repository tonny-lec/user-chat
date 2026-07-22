---
type: Reference
title: LangGraph の概念 — チェックポイント付き BSP ループから全概念を導く
description: LangGraph の全概念を Pregel 由来の super-step ループ1個に還元した理解モデル。lets-langgraph の実コードで接地済み。
tags: [langgraph, agent-framework, mental-model, tech]
timestamp: 2026-07-21T00:00:00+09:00
---

# 圧縮された核

LangGraph のランタイムは Google Pregel（BSP: Bulk Synchronous Parallel）の移植。
全概念は次の1ループ（**super-step**）のどこに住むかで説明がつく:

```
1. 起動予約されたノードを全部並列実行
2. 各ノードは Partial<State>（書き込み希望）を返す
3. バリア後、reducer で state にマージ
4. この時点の state をチェックポイント保存
5. エッジ評価で次の起動を予約 → 1 へ（なければ終了）
```

# 概念のループ上の住所

| 概念 | 住所 | 要点 |
|---|---|---|
| State / Annotation | ループが運ぶデータ | ミュータブルなオブジェクトではなくチャネルの集合。ノードは直接書けない |
| Reducer | ステップ3 | 並列実行の必然。上書き / concat / レコードマージを宣言的に決める |
| Node | ステップ2 | `(state) => Partial<State>`。副作用はここ |
| Edge / conditional | ステップ5 | 静的 or state を見る分岐関数 |
| Command | ステップ2+5 | ノードが state 更新と goto を同時に返す。分岐がノード内判断に依存するとき |
| Send | ステップ5 | 動的 fan-out（map-reduce の map）。合流は concat 型 reducer が受ける — **Send と concat-reducer は対** |
| Checkpointer / thread_id | ステップ4 | 毎 super-step 境界で state 全体を永続化。resume・time-travel・HITL がタダで出る |
| interrupt() | ステップ4の応用 | 例外でループ停止。`Command({resume})` で**ノード先頭から再実行**され interrupt() が値を返す |
| Subgraph | ノード位置 | グラフの再帰埋め込み。親子でスキーマが違ってよい |

# 非自明な罠

- **resume はノード先頭からの再実行** — interrupt より前の副作用は二重実行される。
  interrupt 専用の小ノードを分離し、高コスト副作用は手前のノードに置く。
- ループは自己エッジで表現。無限ループは `recursionLimit`（既定25 super-step）で切られるため、
  リトライ上限は state で持つ。
- 並列ノードが reducer なしの同一キーに書くと実行時エラー。「並列化するなら reducer」は機構上の必然。
- `MemorySaver` はプロセス内メモリ — **プロセスを跨ぐ resume は成立しない**。跨ぐなら SqliteSaver 系。
- streaming 3モード: `values`（各ステップ後の全 state）/ `updates`（差分）/ `messages`（LLM トークン）。

# Examples（lets-langgraph での接地）

1. **reducer 3パターン** — `src/graph/state.ts`: `humanAnswers` = concat（履歴蓄積）、
   `status` = last-write-wins、`attemptByComponent` = レコードマージ。
   「上書きか蓄積か」の設計判断がそのまま reducer 選択。
2. **interrupt の正しい分離** — `src/graph/buildGraph.ts`: LLM 呼び出し等の副作用は
   `evaluateRequirementsNode`、`interrupt()` は `humanGateNode` に分離済み。再実行の罠を回避する形。
3. **MemorySaver の穴を自前で埋めた構造** — `interrupts/*.json` を artifactStore に書き出す
   自作永続化は、MemorySaver の揮発性の補填。SqliteSaver 系に替えれば自前実装を削れる可能性。

# 向き不向き

チェックポイントも並列合流も要らない直列パイプラインには不向き — 素の関数合成のほうが薄い。
LangGraph の価値は「毎ステップ永続化」から派生する resume / time-travel / HITL に集約される。

関連: [自作エージェント資産マップ](/tech/my-agent-assets-map.md)

# Citations

[1] [LangGraph docs — Graph API concepts](https://langchain-ai.github.io/langgraph/concepts/low_level/)
[2] [Pregel: A System for Large-Scale Graph Processing (Google, 2010)](https://research.google/pubs/pub37252/)
