---
type: Reference
title: Claude と YouTube 動画 — リンク共有で何が見えるか
description: Claude は動画・音声を直接処理できない。YouTube リンクで取得できるのはページテキストのみ。内容把握には yt-dlp で字幕を渡すのが確実。
tags: [claude, capabilities, youtube, video, workaround]
timestamp: 2026-07-11T00:00:00+09:00
---

# Claude と YouTube 動画 — リンク共有で何が見えるか

2026年7月時点の公式ドキュメントに基づく整理。

## できないこと

- Claude（claude.ai / Claude Code / API 共通）は**動画・音声フォーマットを直接処理できない**。
- Vision が対応するのは画像のみ: JPEG / PNG / GIF / WebP。GIF もアニメーション非対応で最初の 1 フレームのみ。

## YouTube リンクを渡すと実際に起こること

- WebFetch は HTML を Markdown 化してテキスト抽出する。動画プレーヤー（`<iframe>`/`<video>`）は変換時に失われる。
- 取得できるのは**タイトル・チャンネル名・概要欄・コメント等のページテキストだけ**。字幕（トランスクリプト）はページ HTML に埋め込まれていないため取れない。
- 注意: モデルはタイトルと概要欄から内容を「推測」して答えることがある。「動画を見た」回答ではない。

## 内容を把握させる現実的な方法

1. **字幕を渡す（推奨）**:
   ```bash
   yt-dlp --write-subs --write-auto-subs --skip-download --sub-lang ja,en "<URL>"
   ```
   出力 `.vtt` を Read させれば全内容ベースで要約・質疑応答が可能。字幕がない動画は不可。
2. **キーフレームのスクリーンショット**: Chrome 連携ツールで動画ページを開き特定場面を静止画でキャプチャ。図・グラフ確認向き。全体把握には不向き。
3. **概要欄で足りる質問**: リンクだけで WebFetch でも回答可能。

要約: 「リンク共有 = 概要欄が読める」「字幕を渡す = 内容が分かる」。

# Citations

[1] [Claude Vision (対応フォーマット)](https://platform.claude.com/docs/en/build-with-claude/vision)
[2] [Claude Code tools — WebFetch の挙動](https://code.claude.com/docs/en/tools)
