---
type: Consultation
title: コードエントロピーをエージェントの修正範囲選択に使う — 種類の整理と層1(履歴エントロピーマップ)の実測
description: エントロピーは必ず「何の分布か」を特定して使う。修正範囲の自律選択に効く3系統のうち、git履歴から作る層1（change entropy + co-change）を実リポジトリ2つで試作。co-changeだけが強制点(述語)になる、が最重要の発見。
tags: [entropy, agent, risk-map, git, harness]
timestamp: 2026-07-11T00:00:00+09:00
---

# 相談内容

CS のエントロピー概念（種類・用途）を整理したい。動機: エントロピーのコンテキストを
エージェントに与えることで、コード修正時の**修正範囲・規模を自律的に選択**させられないか。

# 検討・調査

## 大原則: エントロピーは「何の分布か」を特定しないと使えない

エントロピー H(X) = −Σ p log p は常に**ある確率分布に対する量**。「コードのエントロピー」と
分布を特定せずに言うと比喩に堕ちて測れなくなる（「ソフトウェアエントロピー」「技術的負債」
系の議論が測れないのはこれが理由）。設計の最初の分岐は常に「p は何の分布か」。

## CS のエントロピーのカタログ（分布を添えて）

| 種類 | 分布 | 用途 |
|---|---|---|
| Shannon エントロピー | 記号の出現確率 | 圧縮限界。派生のクロスエントロピー(モデルの驚き)・KL(分布のズレ)・パープレキシティ(実質何択か)が実務の本体 |
| 決定木の情報利得 | ラベル分布 | 「どの質問で不確実性が最も下がるか」— 探索と行動の切り替え判定の祖先 |
| 暗号のエントロピー | 攻撃者から見た秘密の候補 | 予測不能性の在庫量（パスワード強度・乱数プール） |
| コルモゴロフ複雑性 | （個別データの最短記述長） | 計算不能。gzip圧縮率が粗い近似 |
| ソフトウェアエントロピー | **未特定（比喩）** | Lehman法則・割れ窓。測れないのでここで止まる議論が多い |

## 修正範囲選択に直結する3系統（測れる形にした研究）

- **A. change entropy（変更履歴）** — 分布: 期間内コミットのファイル散布。
  Hassan (ICSE 2009): 変更が散らばる期間ほど後の欠陥が多い。git log から計算可能。
- **B. naturalness（コード自体）** — 分布: 言語モデルのトークン予測。
  Hindle+ (ICSE 2012): コードは低エントロピー(定型的)。Ray+ (ICSE 2016): バグ行は
  クロスエントロピーが高い(LMが驚く箇所は怪しい)。
- **C. モデル自身の出力エントロピー** — 分布: 生成時トークン分布 / N回試行の意味的割れ
  (semantic entropy, Farquhar+ Nature 2024)。「今書く」vs「先に調べてエントロピーを下げる」
  の切り替え判定に使える。ただし logprobs は校正問題があり相対比較に留める。

全体設計は2層: **層1=事前計算の静的マップ（A系）** + 層2=実行時のモデルの迷い観測（C系）。
今回の相談は層1を深掘り（層2の観測は別テーマで扱う予定）。

# 層1の深掘り: エントロピーマップの設計

## HCM (History Complexity Metric) の実用形

1. 履歴を period に分割（**period 幅が最重要ハイパーパラメータ**。若いリポジトリ7日、長寿4週目安）
2. 各 period でファイル変更分布の正規化エントロピー H_norm = H / log2(n) を計算
3. ファイルへの配分は **HCM2+3: 寄与 = (変更シェア p_i) × H_norm × decay^経過期間**
   - HCM1（period 内の全ファイルに H を均等配分）は識別力がなく使えない
4. **一括コミット除外（>30ファイル等）が必須**。一括 import/リフォーマットが分母を膨張させ
   実コードのスコアを希釈する

## マップの列 — それぞれ別の分布のエントロピー

| 列 | 分布 | エージェントへの行動翻訳 |
|---|---|---|
| HCM | 期間内コミットのファイル散布 | 高→変更が散らばる領域。最小diff・blast radius を疑う |
| co-change confidence | Aと同時に変更されたファイル | conf≥0.8 の相方は修正範囲候補に自動追加 |
| ownership entropy | ファイルを触った著者 | 高→単一の設計意図なし。既存パターン踏襲。**ソロリポジトリでは常に0（死ぬ列）** |
| recency/churn | （補助列） | 古×低churn=安定帯、大胆な変更の許可帯 |
| テストカバレッジ | （補助列） | HCM高×カバレッジ低=最危険象限、テスト先行強制 |

## 注入設計: 静的テーブルより「照会 + 強制点」

全ファイルのテーブル常時注入はコンテキストの無駄＋陳腐化。3段構え:

- **a. 照会型 CLI** (`entropy-map query <path>`) + skill で「修正計画前に対象ディレクトリを照会」
- **b. PreToolUse hook**: Edit 対象が高リスク上位20%なら additionalContext で注意を受動注入
- **c. co-change 検証 hook（本命）**: diff に A があり conf(A→B)≥0.8 の B がなければ警告。
  **HCM は助言にしかならないが、co-change は述語になる** — 修正範囲の妥当性をモデルの
  自覚ではなく機械の検証に変える強制点（[skill のハーネス化](/tech/skill-to-harness-enforcement.md)と同型）

## 導入前の検証（ゼロ件禁止）

1. HCM×欠陥相関: `git log --grep='fix\|bug' --name-only` の対象ファイルと HCM 上位20%の
   重なり(lift)。重ならないリポジトリでは HCM 列を捨てる
2. co-change 予測力: 履歴を前半/後半に分割、前半学習のペア(conf≥0.8)が後半でも共変更されるか

# 実測結果（codex-os 137コミット / lets-langgraph 127コミット）

- **co-change が即戦力**: `README.md↔README.ja.md` conf 1.0/0.93（翻訳ペア）、
  `artifacts.ts↔artifacts.test.ts` 1.0/1.0、`install.sh↔test_install_idempotent.sh` 0.86。
  「実装だけ直して翻訳/テストを忘れる」失敗クラスを潰す情報が git log に眠っていた
- HCM 上位 = 変更の重心。ドキュメント駆動リポジトリでは plan/spec 文書が上位に来る
- 実装時に踏んだ罠3つ（period幅・HCM1の無識別力・一括コミット希釈）は上記設計に反映済み

計算のコア（stdlib のみ、約100行の要点）:

```python
# git log --name-only --no-merges --pretty=format:@@@%H|%at|%an|%s をパース
# period 分割 → 各 period の Counter(file→変更数) から
h = -sum((c/total)*log2(c/total) for c in ctr.values()) / log2(len(ctr))  # H_norm
hcm[f] += (cnt/total) * h * DECAY**(n_periods-1-p)                        # HCM2+3
# co-change: 同一コミット(≤30ファイル)内の全ペアを Counter、support≥3 で
# conf(a→b) = support / churn[a]
```

# 結論

- エントロピーを使う議論は「何の分布か」の特定から始める。比喩のままでは設計に落ちない
- 層1は git log から数十行で作れて既存研究の裏付けがあり、即日試せる。**優先順位は
  co-change > HCM**: co-change は修正範囲の検証述語（hook で強制可能）になり、HCM は
  リスク予算の配分表（助言）に留まる
- 高エントロピー≠常に危険（設定・生成コード・ロックファイルは構造的に高い）。除外リスト必須
- 相関は元研究の対象プロジェクトでの実証にすぎない。自分のリポジトリで欠陥履歴との
  重なりを1回測ってから採用する

# Citations

[1] [Hassan, "Predicting Faults Using the Complexity of Code Changes" (ICSE 2009)](https://dl.acm.org/doi/10.1109/ICSE.2009.5070510)
[2] [Hindle et al., "On the Naturalness of Software" (ICSE 2012)](https://dl.acm.org/doi/10.1109/ICSE.2012.6227135)
[3] [Ray et al., "On the 'Naturalness' of Buggy Code" (ICSE 2016)](https://dl.acm.org/doi/10.1145/2884781.2884848)
[4] [Farquhar et al., "Detecting hallucinations in large language models using semantic entropy" (Nature 2024)](https://www.nature.com/articles/s41586-024-07421-0)
