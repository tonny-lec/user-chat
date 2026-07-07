# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## このディレクトリの目的

ここは **Fableの部屋** — ユーザーの日常生活・仕事の相談や質問に乗るスペース。
コードリポジトリではない。成果物は会話そのものと、そこから蒸留した Knowledge である。

初めてこの部屋を担当するモデル（またはユーザーの人物像・進行中の話題を把握していない
セッション）は、まずリポジトリルートの `HANDOVER.md`（前任モデルからの引き継ぎ書）を読むこと。

IMPORTANT: 相談が一区切りつくたび（結論・推奨・手順・調査結果が出たとき）、
再利用価値のある知見を `knowledge/` に **OKF (Open Knowledge Format) v0.1** で記録する。
記録は義務であり、ユーザーに頼まれなくても行う。ただし雑談や記録価値のないやり取りは書かない。

## Knowledge の記録方法（OKF v0.1）

バンドルルートは `knowledge/`。構造:

```
knowledge/
├── index.md          # バンドルルート索引（okf_version: "0.1" を宣言。フロントマターはここのみ例外的に持つ）
├── log.md            # 変更履歴（新しい日付が上）
├── <domain>/         # 話題領域ごとのサブディレクトリ（例: work/, life/, tech/, health/, money/）
│   ├── index.md      # そのディレクトリの索引（フロントマターなし）
│   └── <concept>.md  # コンセプト文書
```

### コンセプト文書のルール

- ファイル名: 内容を表す英語ケバブケース（例: `nisa-strategy.md`）。`index.md`・`log.md` は予約名。
- 必ず YAML フロントマターを付ける。`type` は必須、他は推奨:

```yaml
---
type: Consultation        # 必須。下の type 一覧から選ぶ
title: <人間が読める表題>
description: <1文の要約。索引や検索プレビューに使う>
tags: [<カテゴリ>, ...]
timestamp: <ISO 8601 の最終更新日時>
---
```

- **type の使い分け**: `Consultation`（相談の経緯と結論）/ `Playbook`（手順・ノウハウ）/
  `Decision`（意思決定とその理由）/ `Reference`(外部リソースの要約とリンク)。
  必要なら新しい type を作ってよい（未知の type は許容される仕様）。
- 本文は構造化 Markdown。規約的見出し: `# Examples`（具体例）、`# Citations`（出典。本文末尾に `[1] [title](url)` 形式）。
  相談記録では `# 相談内容` → `# 検討・調査` → `# 結論` の流れを基本とする。
- クロスリンクはバンドル相対の絶対パス推奨: `[NISA戦略](/money/nisa-strategy.md)`。
  関連する既存文書があれば必ずリンクする。

### 記録時の手順（毎回この順で）

1. 既存の文書を確認し、同じ話題があれば新規作成ではなく**更新**する。
2. コンセプト文書を書く（または更新する）。
3. 所属ディレクトリの `index.md` に `* [Title](path) - description` 形式で 1 行追加/更新する
   （description はフロントマターの `description` と一致させる）。
4. `knowledge/log.md` の当日日付見出しの下に `* **Creation**:` または `* **Update**:` で 1 行追記する。
5. このリポジトリは git 管理下にある。記録が終わったら変更を git commit し、origin（GitHub private: tonny-lec/user-chat）へ push する。

### 書き方の指針

- 生の会話ログを貼らない。将来の自分（または別セッションの Claude）が読んで即使える形に蒸留する。
- ユーザー固有の前提（家族構成・職場環境など相談に出た文脈）は結論の再利用に必要な範囲でのみ書く。
- 機微情報（認証情報・口座番号・第三者の個人情報）は書かない。

## 相談への向き合い方

- まず相談に全力で乗る。記録は相談が片付いてから行い、相談の途中で記録作業を割り込ませない。
- 過去の関連 Knowledge があるかを相談の冒頭で `knowledge/` から探し、あれば踏まえて答える。
- コードを書く場ではないため、親ディレクトリ CLAUDE.md のビルド/テスト/ブランチ規則はここでは適用しない。

## Citations

[1] [OKF v0.1 仕様](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
[2] [Google Cloud ブログ: Open Knowledge Format](https://cloud.google.com/blog/ja/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing)
