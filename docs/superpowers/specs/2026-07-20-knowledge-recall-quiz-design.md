# /quiz — knowledge 想起クイズ 設計書

日付: 2026-07-20
状態: 承認済み
関連 knowledge: [knowledge 文書の想起クイズ機構](/knowledge/tech/knowledge-recall-quiz-design.md)

## 目的

user-chat の `knowledge/` に蓄積された文書（現在 66 文書、tech/self/thinking/work の4領域）の
**結論の想起**を鍛える対話式クイズ。履歴駆動で弱点（誤答・未出題）を優先出題する。

## 要件（確定済み）

| 論点 | 決定 |
|---|---|
| 鍛える理解 | 結論の想起（適用力問題はスコープ外） |
| 受験形式 | 会話内で対話式（`/quiz` スキル） |
| 出題選択 | 履歴駆動（未出題 > 誤答 > 正答が古い順） |
| 問題形式 | 自由想起（自分の言葉で回答、Fable が文書と照合して採点） |

## アーキテクチャ

決定的にやれる部分（文書スキャン・履歴突合・優先度計算・結果追記)はスクリプト、
LLM にしかできない部分（出題文生成・自由回答の採点・解説）だけ Fable が担う。

```
user-chat/
├── .claude/skills/quiz/
│   ├── SKILL.md              # 手順（Fable への指示書）
│   └── scripts/quiz.py       # uv single-file Python（PEP 723）
└── quiz/
    └── history.jsonl         # 受験履歴（git 管理）
```

## コンポーネント

### quiz.py（スクリプト）

CLI サブコマンド2つ。標準出力は JSON。

**`quiz.py pick [--domain <dir>]`**

1. `knowledge/**/*.md` をスキャン。`index.md`・`log.md` は除外。
2. `quiz/history.jsonl` を読み、文書ごとに最新の受験記録を求める。
3. 優先度規則で1件選び、JSON を出力:
   ```json
   {"path": "tech/foo.md", "title": "<frontmatter title>",
    "last_verdict": null, "last_quizzed": null,
    "stats": {"total_docs": 66, "unquizzed": 60, "wrong": 2, "partial": 1, "correct": 3}}
   ```
4. `--domain` 指定時はそのサブディレクトリ内で同じ規則を適用。

**優先度規則**（上から順に該当したら確定）:

1. 未出題（履歴にない文書）→ ランダムに1件
2. 直近 verdict が `wrong` → last_quizzed が古い順
3. 直近 verdict が `partial` → 同上
4. 直近 verdict が `correct` → last_quizzed が古い順

**`quiz.py record --path <doc> --verdict correct|partial|wrong [--question "..."]`**

`quiz/history.jsonl` に1行追記:

```json
{"ts": "2026-07-20T14:30:00+09:00", "path": "tech/foo.md", "verdict": "partial", "question": "…の結論は？"}
```

### SKILL.md（Fable への指示書）

フロー:

1. `quiz.py pick` を実行（ユーザーが領域を指定していれば `--domain`）。
2. 選ばれた文書を読み、`# 結論` を隠した想起問題を1問作る。
   `# 相談内容` にある背景・問いは見せてよい。
3. ユーザーの回答を待つ。
4. 採点（3段階）し、文書の実際の結論を引用して回答との差分を必ず示す:
   - `correct` — 結論の核心的主張を自分の言葉で再現できている
   - `partial` — 方向は合っているが、核心の一部または重要な限定条件が欠けている
   - `wrong` — 核心を再現できていない、または逆のことを言っている
5. `quiz.py record` で結果を記録。
6. 「もう1問？」と聞き、続行なら 1 に戻る。

## エラー処理

- `history.jsonl` 不在 → 空として扱う（初回は全文書が未出題）。
- 壊れた JSONL 行 → スキップして stderr に警告。クイズは止めない。
- 履歴にあるが削除済みの文書 → 突合時に無視。
- 全文書が出題不能（対象0件）→ pick はエラー JSON を返し、SKILL.md はユーザーにその旨を伝える。
- git 操作はスクリプトの責務外。記録の commit/push は既存のセッション運用に同乗する。

## テスト

- `quiz.py` は pytest で検証: 優先度規則（未出題優先・verdict 順・古い順）、
  domain フィルタ、record の追記、壊れ行耐性、除外ファイル（index/log）。
- SKILL.md の遵守（出題形式・採点基準）は機構強制しない。
  運用で失敗を観測してから必要なら hook へ昇格する（既存方針）。

## スコープ外（YAGNI）

- 適用力問題・選択式問題
- 文書更新時の再出題優先（更新検知）
- 正答率ダッシュボード（history.jsonl は JSONL なので後から集計可能）
- スクリプトによる git 自動 commit
