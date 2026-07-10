---
type: Consultation
title: サブエージェント役割別のティア×effort 最適化 — luna/terra × low〜xhigh の120ラン実測
description: 実装・テスト作成・レビュー・計画・設計書の5役割で gpt-5.6-luna/terra × reasoning effort 4段階を実測。品質は飽和し差はコスト・テールに出る。「low は medium より高くつく」逆転と役割別推奨構成表。
tags: [gpt-5.6, subagent, model-selection, reasoning-effort, eval, disposable]
timestamp: 2026-07-11T03:30:00+09:00
---

**この文書はモデル固有の使い捨て層**（[gpt-5.6 モデルプロファイル](/tech/gpt-56-model-profile.md)と同じ扱い）。
一次データ・ハーネス・全ログは `~/workspace/gpt56-eval/roles/`（README に設計、results.tsv に全120ラン）。

# 相談内容

実装 / 設計書作成 / 計画作成 / レビュー / テスト作成を担うサブエージェントに、
gpt-5.6-luna / gpt-5.6-terra × reasoning effort (low/medium/high/xhigh) のどの組が
トークンと出力のバランスで最適か。

# 方法

- 5役割 × 1タスク、全て **0〜1 の段階スコア**（二値だと effort 差が映らない）:
  実装=ホールドアウトテスト24件通過率 / テスト=ミュータント7体検出率 /
  レビュー=埋込バグ6個の recall（+FP 記録）/ 計画・設計書=述語チェックリスト。
- 2ティア × 4effort × 5役割 × N=3 = 120ラン。codex exec 0.144.0、プラグインなしの
  専用 CODEX_HOME（素の文脈 ≈2.1k トークン込みの "tokens used" を記録）。
- 判定器は目視較正済み（誤検知3種を修正: 否定文「Kafka は導入しない」を採用と誤判定 /
  小文字 `line` の見逃し / レビューの行内参照 `L6: …L15 の return` の不検出）。

# 結論: 役割別推奨構成

| 役割 | 推奨 | 根拠（score / tokens中央値 / wall中央値） |
|------|------|------|
| 実装 | **luna/medium** | 全構成満点。最安 10.0k・33s。テストで外部検証できる役割は luna で十分 |
| テスト作成 | **terra/medium** | 10.6k・33s で満点。luna は low/medium で仕様境界の取り逃しあり（後述） |
| レビュー | **terra/medium**（トークン最優先なら terra/xhigh） | recall は全構成 6/6 だが FP が luna 5/12ラン vs terra 0/12。terra/xhigh 11.3k が最小トークン、medium は最速 34s |
| 計画 | **terra/high**（または medium） | 11.3k・38s。luna は全 effort で terra より高コスト（17.7k〜27.0k） |
| 設計書 | **terra/medium**（薄くてよければ luna/low） | 述語は全構成満点。terra は 144〜214行で引き締まり、luna は effort↑で 162→373行に肥大化。luna/low 11.0k は最安だが最薄 |

**既定は terra/medium、実装だけ luna/medium** が運用の一行まとめ。
この規模のタスクでは high/xhigh に品質上の見返りがほぼない（唯一の例外は luna のテスト作成を
0.952→1.000 にする high）。xhigh は wall が最大 4 倍（設計書 66s→256s）。

# 横断的な発見

1. **品質は飽和していた**。仕様を明確に書いた小タスク（この実験の規模）では luna/low ですら
   ほぼ満点。ティア×effort の差は正答率ではなく**コスト・レイテンシ・テール**に現れる。
   モデル選定の議論は「どれが解けるか」ではなく「どの失敗の尻尾を許容するか」になる。
2. **「low = 安い」は agentic タスクでは偽**。検証ループのあるタスクでは low が medium より
   トークンを食う逆転が発生（実装: luna 17.1k vs 10.0k、terra 20.9k vs 13.9k）。
   low は一発で解けず試行錯誤が増えるため。一方、書くだけの設計書は effort に単調増加
   （luna 11k→36k）。**タスクに検証ループがあるかで effort とコストの関係が反転する**。
3. **luna のテールは「境界の書き漏らし」と「饒舌」**: (a) テスト作成で2回とも同じミュータント
   （記号除去仕様の境界 = アンダースコア残存）を検出できないテストを書いた（low/medium 各 1/3）。
   (b) レビューで投機的指摘の FP（CSV に id 列がない場合の KeyError 等。高 effort では自ら
   「低確信」とマークするので運用では書式で無害化可能）。(c) 設計書が effort↑で肥大化。
4. **terra の特徴は精密さ**: FP ゼロ・文書コンパクト・effort を上げてもトークンが暴れない
   （レビューは xhigh が最小トークンという逆転すらある）。
5. 無人運用のレビュー担当には既存知見も効く: [モデルプロファイル](/tech/gpt-56-model-profile.md)の
   ティア差（D4 正当化耐性 Terra 4/5 vs Luna 1/5）より、**説得に晒されるレビュー役は terra**。
   luna に任せるなら防御はプロンプト層でなく hook 層に置く。

# 限界

- 小規模・well-specified タスクでの結果。大規模・曖昧・長文脈タスクでは差が開く可能性が高い
  （そこでは既存のティア差知見 B2/D4 が参考になる）。N=3 なので 0.05 級の差はノイズ圏。
- tokens は codex の "tokens used"（reasoning・キャッシュ込み総計）。API 課金額とは別物。
- 判定器の較正3件はそのまま eval の教訓: **grep 述語は否定文・大文字小文字・参照形式で必ず割れる**。
  ヒューリスティック判定は実物との突き合わせ（[eval 入門](/tech/evals-for-practitioners.md)の判定器較正）を省略しない。

# 実験ノート

- 実行中にサブスク使用量上限に2回接触（51ラン喪失→リセット後に自動再開で完遂）。
  インフラエラー（usage limit / model at capacity）を品質 0 点と混同しない除外処理が必須だった。
- 関連: [モデル移行観測フロー](/tech/model-migration-observation-flow.md)（方法論）、
  [gpt-5.6 プロンプティングエッセンス](/tech/gpt-56-prompting-essence.md)（書き方の処方）。

# Citations

[1] 一次データ: ~/workspace/gpt56-eval/roles/ (README.md / results.tsv / runs/ 全120ラン)
