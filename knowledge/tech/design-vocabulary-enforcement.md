---
type: Consultation
title: パーツを用意してもデザインが統一されない問題 — 語彙の閉包と強制点
description: テンプレ的な web パーツを用意しても codex の推測が混入して統一されない相談。原因は能力でなく自由度 — パーツ提供は知識層にすぎず強制点がない。処方は語彙の閉包(lint で生値・生マークアップを機械的に遮断)・在庫切れプロトコル(推測の代わりの逃げ道)・ユニーク値数の監視の3段。
tags: [llm, ui-design, design-system, codex, lint, harness, enforcement]
timestamp: 2026-07-16T12:00:00+09:00
---

# 相談内容

codex に web デザインの修正をさせるのが難しい。テンプレートみたいに web パーツを
用意しても、推測が入ってしまいデザインが統一されない。

[業務システムUIのプロンプト処方](/tech/business-system-ui-prompting.md)の処方5
「テンプレ固定・逸脱禁止」と[UI自己検証ループ](/tech/ai-ui-verification-loop.md)の
層3「部品の組み合わせだけやらせる」を実践した、その一段先の症状。

# 診断: パーツの「用意」は知識層であり、強制点がない

推測の混入はモデルの能力問題ではなく**自由度が閉じていない**問題。
[skill-to-harness-enforcement](/tech/skill-to-harness-enforcement.md) の診断がそのまま当てはまる。
穴は2つ:

## 穴1: 語彙が閉じていない（逸脱が物理的に可能でコストゼロ）

テンプレートを渡してもモデルは生の HTML/CSS を書ける。「これを使え」は証拠であって
強制ではない。文書層の遵守は確率的（[GPT/Codex ハーネス癖の実測](/tech/gpt-codex-quirk-findings.md):
AGENTS.md 遵守 2/3）であり、**統一性は AND 条件**なので遵守率 90% でも
画面 10 枚でほぼ確実に崩れる。単発タスクなら 90% で十分だが、統一性は全生成の
連言なので確率遵守では原理的に達成できない。

## 穴2: パーツの在庫切れ地帯で推測が湧く

パーツ集はアトム（ボタン・カード・フォーム）を覆うが、画面の大半は**パーツの間**
— ページレイアウト・余白・並べ方・空/エラー状態 — でできている。部品がない次元は
黙って推測で埋まる。推測の発生地点はランダムではなく**語彙の穴の位置**で決まる。

# 結論: 「用意する」から「それしか書けなくする」へ（強度順3段）

## 1. 語彙の閉包 — 値とマークアップの供給源を1つにし、lint で強制

- 色・サイズ・余白は**デザイントークン以外から調達禁止**を機械で強制:
  stylelint `declaration-property-value-allowed-list` で生の hex/px リテラルを
  CI/commit hook で落とす。Tailwind なら arbitrary value (`w-[137px]`) を lint 禁止。
- コンポーネントは**コピペ改変でなく import のみ**（`@ui/*` からだけ）:
  ESLint `no-restricted-syntax` / `react/forbid-elements` で生の `<button>` や
  inline style を落とす。コピペは世代ごとに劣化するが import は劣化しない。

ポイントは「守らせる」でなく「破ると赤くなる」。モデルの遵守率と無関係に統一性が
担保される。最初に入れる1本はこれ（設定数十行、codex に書かせられる）。

## 2. 在庫切れプロトコル — 推測の代わりの逃げ道

述語+停止条件+**逃げ道**の3点セット（[gpt-5.6 プロファイル](/tech/gpt-56-model-profile.md)）の適用。
逸脱を禁止するだけだと部品がない場面で詰み、こっそり推測に戻る。逃げ道を明示する:

> 該当する部品・トークンが存在しない場合は実装するな。`MISSING_PARTS.md` に
> 「必要だった部品・用途・暫定案」を追記して報告せよ。

新パーツ追加は人間レビュー付きの別レーン。推測が「黙った混入」から「観測可能な
在庫切れ報告」に変わり、パーツ集は失敗観測駆動で育つ。lint（処方1）が落ち始めた
とき＝穴が観測されたときに導入すれば十分。

## 3. 統一性の数値監視 — ユニーク値数は統一性の検出器

トークン運用が守られていればビルド後 CSS の**ユニーク値の個数**（distinct な色・
font-size・spacing の数）は一定のはず。wallace-cli / cssstats 系で集計し
「ユニーク色数が増えたら fail」をテスト1本に。閾値は現状凍結
（[閾値調達4番](/tech/ai-ui-verification-loop.md)）でよい。

# 未解決の分岐

強制点の置き方はスタック依存。React 等コンポーネントがあるなら上記そのまま。
**素の HTML/CSS の場合**「import しか許さない」が使えないため、テンプレートエンジンの
partial 化、または CSS をクラス語彙だけに固定して HTML 側を lint する等に変形が必要
（相談時点でスタック未確認）。

# Citations

[1] [stylelint declaration-property-value-allowed-list](https://stylelint.io/user-guide/rules/declaration-property-value-allowed-list/)
[2] [ESLint no-restricted-syntax](https://eslint.org/docs/latest/rules/no-restricted-syntax)
[3] [wallace-cli](https://github.com/projectwallace/wallace-cli)
