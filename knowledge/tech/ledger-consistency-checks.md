---
type: Playbook
title: 台帳整合性チェッカー集 — requirements から順に、辺ごとの専用プロンプト
description: 整合性スイープを分解した対象特化のチェックプロンプト C1〜C13。導出の依存順（requirements→items/existing→db-design→process→meta-sync→migration→scenario/acceptance→backlog→docs）に並び、どれも単独で実行できる。
tags: [consistency-check, verification, prompts, playbook, db-design]
timestamp: 2026-07-28T00:00:00+09:00
---

大きな1本（[プロンプト集](/tech/db-design-flow-prompts.md)の整合性スイープ）を
辺ごとに分解した専用チェッカー。気になる箇所だけ単独で打てる。

## 共通規律（全チェック共通 — 各プロンプトの冒頭に暗黙で適用）

- 読むだけ。修正・生成をしない（×の解消は差分提案→人間承認で別途）。
- 台帳は 02_metadata/ 配下。
- 報告は件数＋パターン。×の件だけ個票（対象と内容1行）。
- **検分した母数を必ず報告。母数0の○は無効** — 「対象消失の疑い」として×。
- 実行順の目安: 上流から（上流の×は下流の×を量産するため、上流を直して
  から下流を見る）。

## C1. requirements 自体の健全性

```markdown
requirements.md 単体の健全性を検査せよ。読むだけ。
1. REQ-ID の重複・欠番（欠番は事実として報告 — 詰め直すな）
2. スコープ宣言: 対象外 REQ-ID が実在するか / 対象外と DEC の矛盾
3. DEC の重複・矛盾（同じ事項に2つ以上の決定）
4. 本文中の 未確定(Q-xx) 参照が questions.md に実在するか
報告: REQ 総数 / 対象外 <n> / DEC <n> / ×の件数と個票
```

## C2. items ⇄ requirements（項目台帳の衛生）

```markdown
items.md を requirements.md と突合せよ。読むだけ。
1. 各 ITEM の req: [REQ-xx] 参照が実在するか（幽霊 REQ）
2. source と req の両方を持たない ITEM（台帳衛生違反）
3. entry: input かつ型未確定の ITEM の残数
報告: ITEM 総数（input/display 内訳）/ 幽霊 REQ <n> / 衛生違反 <n> /
型未確定 <n> / ×の個票
```

## C3. db-design ⇄ requirements（順トレース＋削除審問）

```markdown
db-design.yaml を requirements.md と双方向に突合せよ。読むだけ。
1. 順トレース: スコープ宣言の対象外を除く各 REQ を満たすテーブル・列が
   存在するか。既存テーブルで満たすものは covered(external)。
   「おそらく」は missing。missing には「既存テーブルで満たせない理由」
   1行必須。
2. 削除審問: 各テーブル・列の削除を試み、削除で満たせなくなる REQ-ID を
   挙げよ。REQ が無い要素は structural 連鎖・external の実在で判定。
   どの語彙でも根拠を示せない要素のみ削除提案。
報告: REQ 検分 <n> / missing <n> / 全行検分 <行数> / 削除提案 <n> / 個票
```

## C4. db-design ⇄ items（項目レベルトレース）

```markdown
db-design.yaml を items.md と突合せよ。読むだけ。
1. items.md の entry: input・型確定済みの全 ITEM が、いずれかの列に
   item: ITEM-xx として現れるか（missing(item)）
2. 列の item: 参照が items.md に実在するか（幽霊 ITEM）
3. 列の型・required が items.md の記載と一致するか
報告: ITEM 検分 <n> / missing(item) <n> / 幽霊 <n> / 型不一致 <n> / 個票
```

## C5. db-design ⇄ existing-tables（external 参照）

```markdown
db-design.yaml の external 参照を existing-tables.md と突合せよ。読むだけ。
1. evidence: {external: X} の X がカタログに実在するか（幽霊）
2. カタログに無いテーブル名への言及が無いか（カタログ外参照）
3. 逆向き: カタログの各テーブルが設計から参照されているか
   （未参照は事実として報告 — 削除提案はするな）
報告: external 参照 <n> / 幽霊 <n> / カタログ外 <n> / 未参照 <n> / 個票
```

## C6. process-design ⇄ requirements（カバレッジ）

```markdown
process-design.yaml を requirements.md と突合せよ。読むだけ。
スコープ宣言の対象外を除く各 REQ が、いずれかの process で実現されるか。
「おそらく」は missing。対象外にできるのはスコープ宣言に列挙された REQ
のみ — 自前判断の対象外発行を禁ずる。
rule が要件原文から引用できているかも抜き取りで5件検分せよ。
報告: REQ 検分 <n> / covered / missing <n> / 引用検分 5件の判定 / 個票
```

## C7. process-design ⇄ db-design（使用審問）

```markdown
process-design.yaml と db-design.yaml を突合せよ。読むだけ。
1. db-design の全テーブル・全列が、いずれかの process の reads/writes に
   現れるか（未使用列）
2. reads/writes の参照先が db-design か existing-tables.md に実在するか
   （幽霊参照）
報告: 列検分 <n> / 未使用 <n> / 幽霊参照 <n> / 個票
```

## C8. meta-sync ⇄ 各台帳（同期台帳の検証）

```markdown
meta-sync.yaml を検証せよ。読むだけ。行数を必ず報告 — 行数0の○は無効。
1. source が existing-tables.md / db-design.yaml に実在するか
2. field の着地先（Pleasanter 項目）が site-spec / constraints に実在するか
   （実体設計前なら「論理名のみ・実体未設計」と報告してよい）
3. 単一の正: 同じ事実に source が2つ以上・direction の矛盾
4. sync の process が process-design.yaml に実在するか
報告: 行数 <n> / 幽霊 source <n> / 着地未定 <n> / 二重の正 <n> /
sync 未整備 <n> / 個票
```

## C9. migration ⇄ db-design（移行の全数）

```markdown
migration.yaml を db-design.yaml と突合せよ。読むだけ。
1. store: 独自 の全列が migration.yaml に現れるか（全数）
2. source（Excel シート.列 / 既存テーブル.列）の実在（幽霊）
3. required: true の列の on_blank が補完/除外で確定しているか
   （「エラーにする」は未確定扱い）
報告: 対象列 <n> / 欠落 <n> / 幽霊 <n> / required 未確定 <n> / 個票
```

## C10. scenario ⇄ 全台帳（導出物の鮮度と実行）

```markdown
scenario/*.sql を検証せよ。
1. 各 scenario が参照するテーブル・列が db-design / existing-tables に
   実在するか（幽霊 = 台帳が動いた後の再生成漏れ）
2. 未確定を含む scenario の数と、その Q-ID の questions.md 実在
3. DDL を SQLite で実行し、全 scenario を実行せよ（実行のみ可、
   台帳修正は不可）
報告: scenario <n> / 幽霊参照 <n> / 未確定入り <n> / 実行 <成功>/<n> / 個票
```

## C11. acceptance ⇄ requirements（受け入れテストのカバレッジ）

```markdown
acceptance.md を requirements.md と突合せよ。読むだけ。
1. in-scope の全 REQ がいずれかの TEST に現れるか
2. TEST の参照（画面・テーブル・scenario）の実在
3. 期待動作未定義の残数と、要件に明記のない異常系 TEST の混入
   （発明された異常系は×）
報告: TEST <n> / REQ カバー <n>/<in-scope> / 幽霊 <n> / 未定義 <n> /
発明異常系 <n> / 個票
```

## C12. backlog ⇄ process-design（運用整合）

```markdown
backlog.md を process-design.yaml と突合せよ。読むだけ。
1. impl: 独自|バッチ の全 PROC が backlog に1行ずつ存在するか
   （欠落 / 重複 / 幽霊 = backlog にのみ存在）
2. 各行の name・impl の一致
3. 「完了」行に完了証拠（scenario 一致の記録）があるか
報告: PROC 検分 <n> / 欠落 <n> / 重複 <n> / 幽霊 <n> / 不一致 <n> /
証拠なし完了 <n> / 個票
```

## C13. docs/design ⇄ 台帳（設計書の件数突合）

```markdown
docs/design/ の各設計書の冒頭件数検査を検証せよ。読むだけ。
1. 各文書の件数（テーブル・列・処理・REQ）を現行台帳と突合
2. 生成日が直近の台帳更新より古い文書を「再生成待ち」として列挙
報告: 文書 <n> / 件数不一致 <n> / 再生成待ち <n>
```
