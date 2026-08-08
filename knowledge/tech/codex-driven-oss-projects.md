---
type: Reference
title: Codex をメイン開発エージェントとする OSS プロジェクト一覧
description: OpenAI Codex を主力コーディングエージェントとして開発されている OSS の調査結果（2026-08）。確実5件（openai/codex・openclaw・CodexBar・ossrs/srs・tc39-codex-wiki）と推定・境界例。ハーネス構成の観察点付き。
tags: [codex, oss, harness, agents-md, case-study]
timestamp: 2026-08-08T00:00:00+09:00
---

# 調査の趣旨

「Codex をメインエージェントとして開発している OSS プロジェクト」の実例探し。
ハーネス構成（AGENTS.md・.codex/・skills）の生きた見本を得るのが狙い。

判定基準: `.codex/` のコミット、`Co-authored-by: Codex` / `codex/*` ブランチ PR の量、メンテナの公言。

# 規模感（2026-08 時点）

- `.codex/config.toml` をコミットしているリポジトリ: 約 7,200 件
- `Co-authored-by: Codex` を含むコミット: 約 30 万件
- Codex cloud のブランチ規約 `codex/*` からの PR: 約 605 万件

# 確実（強い証拠）

| プロジェクト | 何か | 証拠 | ハーネス観察点 |
|---|---|---|---|
| [openai/codex](https://github.com/openai/codex) | Codex CLI 本体（Rust） | `codex/*` PR 1,897件。`.codex/`（environments/, skills/）と AGENTS.md をコミット。OpenAI「Harness engineering」ブログで dogfooding を公言（内部アプリでは3→7人・5ヶ月・約100万行・手打ちゼロ） | AGENTS.md が「エージェントの過去の失敗の規則化」の見本: サンドボックス環境変数の扱い、clippy 規約、引数コメント lint（Bazel 駆動） |
| [openclaw/openclaw](https://github.com/openclaw/openclaw) | パーソナル AI アシスタント（★385k） | `codex/*` PR 9,648件。作者 Peter Steinberger が「Just Talk To It」等で Codex 主体開発を公言→後に OpenAI 入社 | オーケストレーション技巧なしで「モデルと会話する」流儀の代表 |
| [steipete/CodexBar](https://github.com/steipete/CodexBar) | Codex/Claude Code 使用量の macOS メニューバー（★19.8k） | `codex/*` PR 421件。同じく Steinberger | — |
| [ossrs/srs](https://github.com/ossrs/srs) | メディアストリーミングサーバ（C++、★29k） | 直近コミットのほぼ全てが `Co-authored-by: chatgpt-codex-connector[bot]`。`.codex/` に CODEX/IDENTITY/MEMORY/SOUL/TOOLS/USER.md + skills/ をコミット（実在をスポットチェック済み） | OpenClaw 風ワークスペースファイル群を `.codex/` に置く独自ハーネス。**既存の大規模 C++ プロジェクトを Codex 駆動に移行した例**として最重要 |
| [dherman/tc39-codex-wiki](https://github.com/dherman/tc39-codex-wiki) | 新 TC39 wiki | リポジトリ説明自体が「built with codex」。作者は Dave Herman | 小規模 |

# 推定・境界例

- [ghostty-org/ghostty](https://github.com/ghostty-org/ghostty) — Mitchell Hashimoto のターミナル。6ヶ月未解決の GTK4 フリッカーバグを Codex が45分・$4.14 で特定した件が有名。「AGENTS.md の各行は過去のエージェントの失敗」というハーネス工学の実践者だが、Amp/Claude/Codex 併用で「Codex がメイン」とは断定できない。
- [openai/openai-agents-python](https://github.com/openai/openai-agents-python) — `codex/*` PR 109件。社内 dogfooding 方針から主力利用が濃厚だが公言なし。
- telepresenceio/telepresence・cuthbertLab/music21・hexlet-codebattle/codebattle — `.codex/config.toml` はあるが Codex 共著コミットの痕跡なし。「開発環境の一つとして設定済み」の段階。

# 補足

- OpenAI は「Codex for Open Source」プログラム（2026-03 発表、ChatGPT Pro 6ヶ月+最大 $25k API クレジット）で OSS メンテナの採用を推進中。この種のプロジェクトは今後増える見込み。
- README に「built with codex」を掲げるリポジトリは多数あるが大半は★100未満の小規模。上記は規模・著名性で選別。
- ハーネス見本として読むなら: 規律の書き方 → openai/codex の AGENTS.md、既存大規模プロジェクトへの後付け → ossrs/srs の `.codex/`。関連: [codex 単体作業ハーネスの初手設計](/tech/codex-standalone-harness-bootstrap.md)、[.claude/rules の Codex 再現](/tech/claude-rules-in-codex.md)

# Citations

[1] [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/)
[2] [Just Talk To It (steipete.me)](https://steipete.me/posts/just-talk-to-it)
[3] [Shipping at Inference-Speed (steipete.me)](https://steipete.me/posts/2025/shipping-at-inference-speed)
[4] [Simon Willison: agentic engineering](https://simonwillison.net/2025/Oct/14/agentic-engineering/)
[5] [Mitchell Hashimoto の AI ワークフロー (catalins.tech)](https://catalins.tech/how-experts-use-ai-mitchell-hashimoto/)
[6] [Codex for Open Source (OpenAI)](https://openai.com/form/codex-for-oss/)
