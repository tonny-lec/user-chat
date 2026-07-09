---
type: Consultation
title: AIにUIを自己検証させるツールと仕組み（表示崩れ・操作性のフィードバックループ）
description: 「AIは利用者視点を持てない」の正体は観測手段と合否信号の欠落。ブラウザMCPで目を与え、VRT・axe-core・ウォークスルー実行で合否を機械化し、Storybook/デザインシステムで自由度を縛る4層構成。2026年時点のツール名込み。
tags: [llm, ui-design, testing, mcp, playwright, storybook, accessibility, feedback-loop]
timestamp: 2026-07-10T12:00:00+09:00
---

# 相談内容

業務システムのWebデザイン（目線の動き・操作性重視、派手さ不要）をAIに作らせているが、
AIには人間の利用者視点がないため表示崩れや意図と違うデザインになる。
解決するための**AI用のツールや仕組み**はあるか。

[業務システムUIのプロンプト処方](/tech/business-system-ui-prompting.md)の続きにあたる相談。
前回が「仕様の渡し方」なら、今回は「検証ループの組み方」。

# 診断

「AIが利用者視点を持てない」は2つの別問題の混合で、どちらも道具で潰せる:

1. **目がない**: AIは自分が書いたHTML/CSSのレンダリング結果を見ていない。
   表示崩れは能力不足ではなく、コンパイルせずにコードを納品しているのと同じ構造。
2. **合否信号がない**:「使いやすいか」を主観のまま渡しているので、AIは自己採点できない。
   [ウォークスルー述語](/tech/business-system-ui-prompting.md)を書いても、実行環境がなければ机上の答え合わせで終わる。

つまり買うべきは「利用者視点を持つAI」ではなく**フィードバックループ**。

# 結論: 4層で組む（2026年時点の実務標準）

## 層1: 目を与える — ブラウザ操作MCP（表示崩れの直接治療）

エージェントが実装→実ブラウザでレンダリング→スクリーンショットとアクセシビリティツリーを
自分で読んで修正、のループを回せるようにする。

- **Playwright MCP**（Microsoft製、事実上の標準）: スクショ・クリック・入力に加え、
  **a11yツリーのテキスト表現**をLLMに渡せるのが要。ピクセルよりセマンティック情報が
  トークン効率・判定精度とも良い。
- **Chrome DevTools MCP**（Google公式）: コンソール・ネットワーク・パフォーマンス
  トレースまで読める。「崩れている＋遅い」系のデバッグに強い。
- **Claude in Chrome**（Anthropic）: ログイン済みの実Chromeで検証できる。
  社内システムなど認証の裏の画面向き。

使い分けの定石: **その場の検証はMCP（書き捨て）、恒久チェックはPlaywrightテストコードに落とす**。

## 層2: 合否を機械化する — VRT + axe-core（「使いやすい」を述語に）

- **ビジュアルリグレッション**: Playwright `toHaveScreenshot()` が無料・ローカル完結で
  エージェントループに最も組みやすい。diff画像をエージェントに読ませて修正→再実行。
  Storybookがあるなら Chromatic、スクショを社外に出せないなら Lost Pixel / reg-suit / BackstopJS。
- **操作性の機械判定**: `@axe-core/playwright` をテストに入れれば、キーボード到達性・
  フォーカス順・コントラスト等のWCAG系判定が普通のテスト実行で返る。
  Deque公式の **Axe MCP Server**（analyze + remediate）もある。
  自動判定できるのはWCAG系の3〜4割で、残りはLLM＋a11yツリーで補う構図。
- **ウォークスルー述語の実行化**: 「経理担当が200件照合、1件15操作以内・キーボード完結」を
  Playwrightのテストとして書かせる。前回のプロンプト処方3が机上採点から実測に変わる。
  Tabキー巡回でフォーカス順を辿らせれば「目線の動き」の代理指標にもなる。

## 層3: 自由度を縛る — Storybook + デザインシステム（毎回のデザインガチャを止める）

- コンポーネントをStorybookで分離し、AIには**ページ全体を自由に描かせず、
  既存部品の組み合わせだけをやらせる**。表示崩れの発生源自体を減らす構造対策。
- **Storybook MCP**（公式アドオン、React先行）: エージェントが既存コンポーネント一覧と
  使用規約をランタイム照会し、再利用でUIを生成、ストーリー自動生成→インタラクション
  テスト・a11yチェックまで回せる。
- hover/error/empty等の状態がストーリーとして固定されるため、VRTの単位としても機能する。
  [デザインテンプレ固定](/tech/llm-md-to-html-design.md)・前回処方5の恒久化と同じ思想。

## 層4: 運用に埋める — 検証をskill/ワークフロー化 + 判定の分離

- 「フロント変更後は dev server 起動→該当ページ操作→前後スクショ比較→a11yチェック」を
  skill（手順書）として固定し、毎回頼まなくても走るようにする。
- **書いた本人に合否判定させない**: 生成したエージェントと別のエージェント（または別モデル）に
  スクショとdiffをレビューさせるのが定石。自己採点は甘くなる。

## 最小構成の始め方

いきなり全部は不要。効果順:

1. Playwright MCP（または Claude in Chrome）を入れ、「実装後は必ずスクショを撮って
   自分で確認してから完了報告せよ」をCLAUDE.mdに書く — これだけで表示崩れの大半が消える。
2. `@axe-core/playwright` 入りのテストを1本書かせる（キーボード操作の述語込み）。
3. 画面が増えてきたらStorybook分離とVRTを足す。

# 補足: 自律QA系の新顔（2025-2026）

Momentic / QA.tech / Octomind（自然言語E2E・自律巡回のCI組み込みSaaS）、
Stagehand / browser-use（自作ハーネス用のAIブラウザ操作OSS）。
まず層1-2を自前で組み、回帰保護をSaaSに外注したくなったら検討で足りる。

# Citations

[1] [Playwright MCP](https://github.com/microsoft/playwright-mcp)
[2] [Chrome DevTools MCP 公式ブログ](https://developer.chrome.com/blog/chrome-devtools-mcp)
[3] [Storybook MCP docs](https://storybook.js.org/docs/ai/mcp/overview)
[4] [Deque Axe MCP Server](https://www.deque.com/axe/mcp-server/)
[5] [Agentic Coding Handbook: Visual Feedback Loop](https://tweag.github.io/agentic-coding-handbook/WORKFLOW_VISUAL_FEEDBACK/)
[6] [Autonoma: VRT tools compared](https://getautonoma.com/blog/visual-regression-testing-tools)
