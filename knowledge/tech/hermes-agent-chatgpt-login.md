---
type: Reference
title: hermes-agent の ChatGPT サブスクログイン実装 — codex exec ではなく OAuth 模倣の直接 API 呼び出し
description: NousResearch/hermes-agent の ChatGPT サブスクリプションログインは codex exec のサブプロセス呼び出しではなく、Codex CLI の OAuth client_id を流用して自前でトークンを取得し chatgpt.com/backend-api/codex を直接叩く実装。
tags: [ai-agent, oauth, codex, reverse-engineering]
timestamp: 2026-07-25T00:00:00+09:00
---

# 質問

https://github.com/NousResearch/hermes-agent の ChatGPT サブスクリプションログイン機能は、内部で `codex exec` を呼んでいるのか？

# 調査結果

**呼んでいない。** プロバイダ `openai-codex` は「Codex CLI の OAuth フローを模倣して ChatGPT バックエンド API を直接叩く」実装。

## 実装方式（2026-07 時点のソース確認）

- **OAuth**: `hermes_cli/auth.py:102-103` に Codex CLI と同一の client_id `app_EMoamEEZ73f0CkXaXp7hrann` と `https://auth.openai.com/oauth/token` をハードコード。初回ログインは `auth.openai.com` のデバイスコードフローを Hermes 自身が実行（`_login_openai_codex()` → `_codex_device_code_login()`）。トークンリフレッシュも httpx で直接 POST（`refresh_codex_oauth_pure()`、auth.py:3638）。サブプロセス呼び出しなし。
- **API**: Bearer トークン + `ChatGPT-Account-Id` ヘッダ（OAuth JWT の `auth.chatgpt_account_id` クレームから抽出）を付けて `https://chatgpt.com/backend-api/codex` へ直接リクエスト（`hermes_cli/codex_models.py:127-145`、`agent/transports/codex.py` の ResponsesApiTransport）。
- **任意機能**: 既存の `~/.codex/auth.json` からのトークンインポートあり（`_import_codex_cli_tokens()`）。取得元であって実行経路ではない。

## 紛らわしい別経路

同リポジトリに `codex_app_server` ランタイムが別系統として存在し、こちらは Codex CLI をサブプロセス起動する。ただしコマンドは `codex app-server`（JSON-RPC over stdio）であって `codex exec` ではなく、「Codex CLI インストール自体をプロバイダに選んだ場合」用。ChatGPT サブスクログインの主経路（`codex_responses` api_mode）とは別物。

## 一般化できる知見

- サードパーティ製エージェントが「ChatGPT/Claude のサブスクで使える」を謳う場合、実装は大きく2択: (a) 公式 CLI をサブプロセスとしてラップ、(b) 公式 CLI の OAuth client_id を流用してバックエンド API を直接叩く。hermes-agent は (b)。
- (b) 方式は公式 CLI のアップデートに依存しない反面、非公開 API（`chatgpt.com/backend-api/codex`）と流用 client_id に依存するため、OpenAI 側の変更や規約執行で壊れる・BAN されるリスクを負う。

# Citations

[1] [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
