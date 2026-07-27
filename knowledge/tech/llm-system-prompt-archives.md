---
type: Reference
title: LLMシステムプロンプトの抽出アーカイブ — asgeirtj/system_prompts_leaks
description: 主要LLM（ChatGPT GPT-5.6 Sol・Claude・Gemini・Grok等）のコミュニティ抽出システムプロンプトを集めたGitHubリポジトリの案内と、GPT-5.6 Sol プロンプトの構造メモ。
tags: [llm, system-prompt, reference]
timestamp: 2026-07-27T00:00:00+09:00
---

# 何か

各社LLM製品のシステムプロンプトを抽出（プロンプトインジェクション等で引き出したもの）して集めている
コミュニティリポジトリ。公式公開ではない点に注意。

- リポジトリ: https://github.com/asgeirtj/system_prompts_leaks
- OpenAI / Anthropic / Google / xAI のほか Cursor・Copilot・Perplexity 等のツール系も収録。更新頻度が高い。

# GPT-5.6 系の収録状況（2026-07-27 時点）

- **Sol**: `OpenAI/gpt-5.6-sol-extra-high.md` あり（約2,660行・115KB）。
- **Luna / Terra**: 未収録。Luna が知りたい場合はこのリポジトリの更新を待つか、他の抽出元を探す。

# GPT-5.6 Sol プロンプトの構造メモ

- 冒頭は `You are ChatGPT, ...` + 日付。knowledge cutoff は 2025年12月。
- **Environment**: PDF/docx/slides/spreadsheets 用に `/home/oai/skills/*/SKILL.md` を読めと指示 —
  Claude の Skills と同型の「ファイルに外出しした手順書」方式を OpenAI も採用している。
- **Trustworthiness and Factuality**: カットオフ以降の可能性が少しでもあれば必ず web 検索、
  事実には citation 必須、という強い義務形。
- **広告の扱い**: 広告UIはモデルから見えない前提で、「広告を出していない」と断言するな、
  定型文で答えろという指示がある（Free/Go プランに広告が出る時代の対応）。
- **ツール群**: namespace 形式（python / genui / web / automations / bio(メモリ) / api_tool /
  image_gen / user_settings / artifact_handoff / file_search）。web には株価チャート・天気・
  カルーセル等の Rich UI エレメント指定がある。
- **チャンネル制**: `analysis, commentary, final, summary` の4チャンネル + `Juice: 112`
  （reasoning 予算とみられるパラメータ）。
- **Developer Instructions**: 「平均15秒か2-3ツールコールごとに 1-2文の進捗更新」など、
  長時間エージェント動作時のユーザー向け実況の細かい規定。

# 注意

- 抽出版は改変・欠落・幻覚の可能性がある。一次資料ではなく「おおよその実像」として扱う。
- 公式が出すのはプロンプト本体ではなく prompting guide（https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6）。

# Citations

[1] [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks)
[2] [OpenAI: Previewing GPT-5.6 Sol](https://openai.com/index/previewing-gpt-5-6-sol/)
