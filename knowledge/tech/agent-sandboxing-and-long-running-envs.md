---
type: Consultation
title: AIエージェントのサンドボックス — 隔離の層構造と長時間自律の交換関係
description: サンドボックスは「失敗と乗っ取りを可逆にする装置」であり、隔離の強さと自律時間は交換関係にある。隔離技術の5層構造、lethal trifecta と egress 制御が本丸である理由、長時間運用に載せる4要素、2026年前半の勢力図。
tags: [ai-agent, sandbox, security, infrastructure, long-running]
timestamp: 2026-07-11T00:00:00+09:00
---

# 相談内容

AIエージェント文脈でのサンドボックスとは何か、AIエージェントが長時間動くための環境づくりをどう考えるかを知りたい。

# 検討・調査

## 核心機構: 承認モデルの転換

- サンドボックスの本質は「この範囲内なら何が起きても構わない」という境界の機械的強制。
- 人間の承認を「行為の毎回審査」から「境界の事前設定」へ転換する装置。境界内は無承認で走らせられるため、**隔離の強さと自律時間は交換関係**になる。これが「サンドボックス」と「長時間自律」が同じ話題である理由。
- [skill をハーネス化する強制点の設計](/tech/skill-to-harness-enforcement.md) の延長: サンドボックスは最強の強制点。「〜するな」という指示（確率的遵守）を「能力の消去」（物理的不可能）に置き換える。[プロンプト力の階段](/tech/prompting-mastery-ladder.md) のレベル6「消去」の実装形。

## エージェント特有の脅威モデル

従来のサンドボックス（ブラウザ等）は「悪意あるコード」前提。エージェントの脅威は2種:

1. **正当な権限での事故** — rm -rf の対象間違い、force push。悪意ゼロでも起きる。
2. **prompt injection による乗っ取り** — 読んだ Web ページ/issue に埋め込まれた指示で行動が変わる。

Simon Willison の **lethal trifecta**: ①非公開データへのアクセス ②信頼できないコンテンツの読取 ③外部への送信チャネル — 3つ揃うと漏洩は防げない。エージェントは①②を手放せないので、実務の主戦場は **③ネットワーク egress 制御**（許可ドメインリスト + プロキシ）。FS 隔離より地味だがここが本丸。

## 隔離技術の5層構造（軽→重）

| 層 | 技術 | 特徴 | 使用例 |
|---|---|---|---|
| OSプリミティブ | seccomp / Landlock / bubblewrap (Linux)、Seatbelt (macOS) | 起動コストゼロ、カーネル共有 | Claude Code sandbox、Codex CLI |
| コンテナ | Docker / Podman | 配布・再現に優秀、**隔離としては弱い** | 開発環境の土台 |
| ユーザ空間カーネル | gVisor | syscall を横取り | claude.ai、Modal、GKE Agent Sandbox |
| microVM | Firecracker | 起動 ~100ms でVM級隔離 | E2B、Daytona、AWS Lambda |
| フルVM | 通常のVM | 最強・最重 | Devin、Anthropic Cowork |

直近18ヶ月で「コンテナはサンドボックスではない」がコンセンサス化し、エージェント実行基盤は microVM か gVisor にほぼ収束。Anthropic は製品別多層戦略（ローカル Claude Code = Seatbelt/bubblewrap、claude.ai = gVisor、Cowork = フルVM）。

## 長時間自律のためにサンドボックスの上に載せる4要素

1. **可逆性の機械化**: git as checkpoint（worktree + こまめなコミット）が最軽量。基盤レベルではスナップショット/チェックポイントが2026年に主要サービスの標準装備化。研究側にはターン境界で巻き戻し粒度を選ぶセマンティクス対応チェックポイント（Crab, arXiv）。
2. **承認境界の設計**: 二値（全部聞く/全部許す）ではなく「境界内は自由、境界越え（push・外部送信・課金・削除）だけ人間」。[git push 権限の設計](/tech/claude-code-push-permission-design.md) はこの一例。
3. **観測と割り込み**: 放置≠盲目。ログ・完了通知・トークン/時間バジェット・異常時のみ発火する監視。失敗観測駆動の運用ループ（[AIエージェント使いこなしのエッセンス](/tech/ai-agent-mastery-essence.md)）がそのまま適用できる。
4. **環境の再現性**: devcontainer/イメージで宣言的に持ち、壊れたら直さず捨てて再構築。長時間運用の保険は修復能力ではなく再構築の安さ。

## 2026年前半の勢力図（サブエージェント調査、2026-07-11 時点）

- **Anthropic sandbox-runtime (srt)**: 2025-10 OSS 公開、継続開発中（Beta、v0.0.65）。Windows 対応（WFP で egress 制御）で3プラットフォーム体制。2026-03 にサンドボックスバイパス脆弱性を修正 — サンドボックス自体も攻撃対象になる実例。
- **OpenAI Codex CLI**: デフォルト有効。Linux は bubblewrap 主軸 + Landlock/seccomp 補助、Windows ネイティブサンドボックス（restricted tokens + ACL + FW + 専用ユーザー）追加。
- **クラウドサンドボックス**: 専業2強 = E2B（Firecracker、テンプレート最大）と Daytona（コールドスタート最速級）、GPU は Modal（gVisor）。大手（Vercel/Cloudflare/AWS/Google）参入が2026年最大のトレンド。アイドル課金モデル（sleep-to-zero vs 秒課金）が長時間セッションのコスト論点。
- **Kubernetes 圏**: Google が gVisor ベース Agent Sandbox を OSS 公開（KubeCon NA 2025）。

# 結論

自前環境の設計判断はこの順:

1. **脅威が先、技術は後** — 何が漏れたら/壊れたら困るかを列挙してから隔離レベルを選ぶ。
2. ローカルで足りるなら **Claude Code / Codex のネイティブサンドボックス + git worktree** から。追加インフラゼロで FS 制限・egress 制限・可逆性が揃う。
3. 並列度・時間・危険度が上がったら **microVM 系クラウドサンドボックス**（E2B/Daytona 等）へ。チェックポイントと使い捨て環境が手に入る。
4. どの段階でも **egress 制御と承認境界の設計が本体**。隔離技術の選定は手段。

# Citations

[1] [Anthropic sandbox-runtime (GitHub)](https://github.com/anthropic-experimental/sandbox-runtime)
[2] [Anthropic engineering: Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
[3] [Simon Willison: How we contain Claude (2026-05-30)](https://simonwillison.net/2026/May/30/how-we-contain-claude/)
[4] [OpenAI Codex: approvals & security](https://developers.openai.com/codex/agent-approvals-security)
[5] [Superagent: AI code sandbox benchmark 2026](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026)
[6] [Northflank: Kata vs Firecracker vs gVisor](https://northflank.com/blog/kata-containers-vs-firecracker-vs-gvisor)
[7] [Crab: semantics-aware checkpointing (arXiv)](https://arxiv.org/html/2604.28138v1)
