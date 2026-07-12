---
type: Consultation
title: Codex App の Pet 選び — 「役割の同型性」で選ぶ候補とプロンプト集
description: Codex Pet（/hatch で自由生成できるデスクトップコンパニオン）を「可愛さ」でなく「Pet の実機能（観測・通知）と役割が同型な存在」という軸で選んだ候補リスト。日本文化編を含む /hatch プロンプト集付き。
tags: [codex, ai-agent, fun]
timestamp: 2026-07-12T00:00:00+09:00
---

# 相談内容

Codex App の Pet 機能で何を Pet にするか。名前は Pet だが「一緒に働く同僚」なので動物に限らない提案が欲しい。追加要望: 日本のアニメ文化を参考にした案。

# 検討・調査

## Pet 機能の仕様（2026-05 リリース）

- `/pet` で召喚/解除。デスクトップ最前面に浮かぶピクセルアートのコンパニオン。
- 実機能は**状態通知**: 吹き出しで作業内容を表示、承認待ちは赤い時計、完了は緑チェック。
- 組み込み8種のほか、`/hatch <プロンプト>` で自由生成できる。Windows/macOS 対応。

## 選定軸

Pet の実機能は「ユーザーのエージェントの状態を観測して知らせる」こと。よって「何が可愛いか」ではなく**「その役割（観測・通知・使役される存在）と意味が同型な存在は何か」**で選ぶ。

# 結論（候補リスト）

## 西洋・概念編

| 候補 | 同型性 |
|---|---|
| 炭鉱のカナリア | 異常・要承認をいち早く知らせる番人。失敗観測駆動と同型 |
| マクスウェルの悪魔 | 観測して仕分けるだけの存在。「観測が仕事の同僚」 |
| ゴーレム | 額の文字（=プロンプト）で動く。指示書駆動エージェントの自己言及 |
| 灯台守 | 状態を光で知らせる寡黙な通知係 |
| Unix デーモン | 背景で待機しシグナルで起きる。Codex 自身の写し鏡 |
| 現場監督 | 「同僚」の直球解釈。承認待ちで渋い顔 |

ラバーダックはベタすぎて儀式的なので除外。

## 日本文化編（追加要望分）

| 候補 | 同型性 |
|---|---|
| タチコマ風思考戦車 | AI 同僚の理想像。並列動作・経験同期=マルチエージェントの化身 |
| 式神 | 呪符（=プロンプト）で動く紙の使い魔。軽量サブエージェント感 |
| ターミナルの付喪神 | 使い込んだ道具に神が宿る。「自分のハーネスに宿った神」の自己言及 |
| コダマ | 観測して首をカタカタ鳴らすだけ。通知機能の最ミニマル形 |
| からくり茶運び人形 | ゼンマイ→運搬→戻る。タスク委譲→完了→帰還と機構レベルで同型 |

最終推奨: 賑やかな同僚なら**タチコマ風**、寡黙な同僚なら**からくり人形**。（本人の最終選択は未記録）

# Examples

`/hatch` にそのまま渡せるプロンプト例:

- カナリア: `a small pixel-art canary wearing a tiny mining helmet with a headlamp, perched on a lantern, alert and watchful`
- タチコマ風: `a tiny cheerful blue spider-tank robot with a round body and curious camera eyes, chattering happily, inspired by classic anime think-tanks`
- 式神: `a shikigami: a small white paper doll spirit with ink brush markings, folded like origami, fluttering and awaiting orders`
- 付喪神: `a tsukumogami: an old CRT terminal come to life as a small spirit, with a glowing green cursor face and tiny arms, blinking sleepily`
- コダマ: `a small white forest spirit with a rattling head, translucent and quiet, appearing when something changes`
- からくり人形: `a karakuri tea-serving doll: a small Edo-period clockwork automaton in a kimono, carrying a tiny cup of tea, moving with gentle mechanical steps`

# Citations

[1] [Engadget: OpenAI introduces AI-generated pets for its Codex app](https://www.engadget.com/2162796/openai-introduces-ai-generated-pets-for-its-codex-app/)
[2] [PCWorld: I love my new Codex AI pet](https://www.pcworld.com/article/3131011/i-love-my-new-codex-ai-pet-and-now-i-want-one-in-every-app.html)
[3] [Technobezz: OpenAI Launches Codex Pets with Pixel Art Companions and Custom Creator Tool](https://www.technobezz.com/news/openai-launches-codex-pets-with-pixel-art-companions-and-custom-creator-tool)
