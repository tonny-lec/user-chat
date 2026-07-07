---
type: Consultation
title: AIエージェントの「ハーネス」とは何か・どう育てるか
description: ハーネスの定義と層構造、「開示されない」という誤解の正体、失敗観測駆動でハーネスを育てる実践手順。
tags: [ai-agent, claude-code, harness, claude-md]
timestamp: 2026-07-06T00:00:00+09:00
---

# 相談内容

AIエージェントを活用しきれない。「ハーネス」という言葉の意味がわからず、
CLAUDE.md / AGENTS.md などの中身は「開示すると他人が同レベルで仕事できてしまうから」
あまり共有されていないように感じる、という相談。

# 検討・調査

## ハーネスの定義

モデル（LLM）本体の周りに巻き付けて実際に仕事をさせる仕組み一式。語源は馬具・テストハーネス。
Claude Code というツール自体が一つのハーネス。層構造で捉えると:

| 層 | 役割 | Claude Code での実体 |
|---|---|---|
| エージェントループ | 考える→ツール実行→結果を見る→次を判断 | Claude Code 本体 |
| ツール | ファイル編集・コマンド実行・検索・ブラウザ | Edit / Bash / MCP |
| コンテキスト注入 | プロジェクト前提知識の毎回読み込み | CLAUDE.md / メモリ |
| ルール強制 | 「気をつけます」に頼らず機械的に強制 | hooks |
| 手順知識 | 必要なときだけロードするノウハウ | skills |
| 分業 | 探索・検証を別コンテキストへ切り出し | サブエージェント |
| 権限 | 何を勝手にやってよいか | permissions / サンドボックス |

同じモデルでもハーネスの出来で成果が段違いになる。

## 「開示されない」の誤解

1. 実際はかなり公開されている: Anthropic 公式ベストプラクティス、obra/superpowers(MIT)、
   公開 CLAUDE.md 多数。詳細は [superpowers の解剖](/tech/superpowers-plugin-anatomy.md)。
2. 他人のハーネスをコピーしても効きにくい。良いハーネスは「その人・そのプロジェクトで
   観測した失敗の蓄積」であり、レシピではなく筋トレ記録に近い。価値は成果物ではなく
   運用ループにある。

# 結論

ハーネスは秘密の魔法ではない。始め方は「立派な CLAUDE.md を書く」ことではなく:

1. CLAUDE.md は短く保つ(100行以内目安)。「この行を消すと間違えるか? No なら消す」
2. 一般論は書かない(モデルは既に知っている)。検証可能な固有ルールのみ
3. 機械的に強制できるルールは hooks へ移す
4. 手順・ノウハウは skills へ(毎回コンテキストに載せない)
5. 失敗を観測してからルール追加、定期的に削除。2回同じ修正指示をしたらルール化

数週間この運用ループを回せば「自分専用のハーネス」が育つ。

# Citations

[1] [Claude Code Best Practices (Anthropic)](https://www.anthropic.com/engineering/claude-code-best-practices)
[2] [obra/superpowers (GitHub, MIT)](https://github.com/obra/superpowers)
