---
type: Playbook
title: LLM に Markdown→HTML 変換させるとデザインがいまいち問題への対策
description: LLM に毎回デザインさせず、CSS テンプレートを固定して変換を機械化することで HTML の見た目を安定させる手順。
tags: [llm, codex, markdown, html, design, workflow]
timestamp: 2026-07-06T00:00:00+09:00
---

# 問題

Codex/GPT に Markdown を HTML に変換させると、毎回デザインがいまいち・毎回違う仕上がりになる。

原因: 「変換」と「デザイン」を両方 LLM に任せているため、デザインが毎回ガチャになる。
LLM は抽象的な指示（「きれいに」「見やすく」）に対して平凡な HTML を生成しがち。

# 結論（対策は 3 段階、上ほど根本的）

## 1. 変換を機械化する（推奨・決定版）

LLM を変換に使わず、pandoc + 気に入った CSS を一度だけ用意する。決定的なので毎回同じ品質。

```bash
pandoc input.md -o output.html --standalone --embed-resources \
  --css=style.css --metadata title="タイトル"
```

CSS を自作しなくても classless CSS（HTML にクラス不要、素のタグに当たる）を使えば即見栄えする:

- **sakura.css** — 軽量・和風の落ち着いた見た目
- **water.css** — ダークモード自動対応
- **pico.css** — ややリッチ、セマンティック HTML 前提
- **github-markdown-css** — GitHub README と同じ見た目

## 2. LLM を使い続けるなら、テンプレートを固定して渡す

一度だけ納得いくまで HTML スケルトン（CSS 込み）を作り、以後は
「このテンプレートの `<main>` に本文を流し込むだけ。CSS は変更禁止」と指示する。
デザイン判断を LLM から取り上げるのがポイント。

Codex なら `AGENTS.md` にこの指示とテンプレートの場所を書いておけば毎回指定不要。

## 3. 単発ならプロンプトを具体化する

抽象語（きれい・モダン・見やすい）ではなく測定可能な指定をする。例:

> 本文の最大幅 72ch・中央寄せ、line-height 1.7、システムフォントスタック、
> 余白は 8px グリッド、コードブロックは横スクロール可、
> `prefers-color-scheme` でダークモード対応。
> グラデーション・絵文字アイコン・カード UI・影は使わない。
> 参考: GitHub README のレンダリング風。

「〜しない」の禁止リスト（グラデ・カード乱用・紫系配色など LLM の癖）を入れると効果が大きい。

# Examples

sakura.css を使った最小テンプレート（LLM に渡す or pandoc の `--css` に指定）:

```html
<link rel="stylesheet" href="https://unpkg.com/sakura.css/css/sakura.css">
<main><!-- ここに変換した本文 --></main>
```

# Citations

[1] [pandoc](https://pandoc.org/)
[2] [sakura.css](https://github.com/oxalorg/sakura)
[3] [water.css](https://watercss.kognise.dev/)
[4] [github-markdown-css](https://github.com/sindresorhus/github-markdown-css)
