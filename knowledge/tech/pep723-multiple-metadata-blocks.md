---
type: Consultation
title: PEP 723「multiple metadata blocks」エラーの機構と対処
description: uv の「The script contains multiple PEP 723 metadata blocks」は行単位の正規表現検出が原因で、文字列リテラルやコメント内のブロック例も本物としてカウントされる。SSSF の make_adw.py が実例。
tags: [python, uv, pep723, troubleshooting]
timestamp: 2026-08-07T00:00:00+09:00
---

# PEP 723「multiple metadata blocks」エラー

# 相談内容

`uv run` 実行時に `error: The script contains multiple PEP 723 metadata blocks` が出た。原因と、disler/super-simple-software-factory リポジトリ内の該当箇所を特定したい。

# 検討・調査

- PEP 723 はスクリプト先頭に `# /// script` 〜 `# ///` のコメントブロックで依存関係を埋め込む仕様。1 ファイルに 1 ブロックのみ許される。
- 検出は **Python 構文を解釈しない行単位の正規表現マッチ**。仕様自体が「複数マッチしたらエラーにせよ」と定めており、uv はそれに従う。
- したがって**トリプルクォート文字列やコメントの中にあるブロック例も本物としてカウントされる**。これが非自明な落とし穴。
- リポジトリを clone して `grep -rn "/// script" --include="*.py"` でファイルごとの出現数を数えたところ、`.claude/skills/sssf/scripts/make_adw.py` のみ 2 箇所:
  - 2–4 行目: スクリプト自身の本物のブロック
  - 24–26 行目: 生成先スクリプトのヘッダーを持つ `HEADER` テンプレート文字列内のブロック（誤検知源）

# 結論

- エラーの原因は `make_adw.py` の `HEADER` 文字列内に生成用 PEP 723 ブロックがそのまま書かれていること。`uv run make_adw.py` のときだけ発火する（templates/ 配下は各 1 ブロックで正常）。
- 対処の定石は、テンプレート内のブロックを正規表現に一致しない形に崩し、書き出し時に組み立てる:
  - `# {slashes} script` と書いて `format(slashes="///")` で置換する（既に format を使うテンプレートなら自然）
  - または `"# //" + "/ script"` のような文字列連結
- 一般則: **PEP 723 ブロックを文字列やドキュメントの「例」としてスクリプト内に書くときは、必ずパターンを崩す**。診断は `grep -n "/// script" <file>` で出現数を数えれば一発。

関連: [SSSF cookbooks 読解](/tech/sssf-cookbooks.md)（このリポジトリの設計全体の記録）

# Citations

[1] [PEP 723 – Inline script metadata](https://peps.python.org/pep-0723/)
[2] [disler/super-simple-software-factory](https://github.com/disler/super-simple-software-factory)
