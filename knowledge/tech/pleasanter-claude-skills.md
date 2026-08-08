---
type: Reference
title: Pleasanter 向け Claude Code skills の調査 — 公開 skill は plsnt のみ、主流は MCP
description: Pleasanter 開発に使える Claude Code skills の公開状況調査（2026-08）。SKILL.md 形式の公開物は immmmmmmu/plsnt（11スキル同梱、Star 0）が事実上唯一で、エコシステムの主流は公式 MCP サーバー（本体 v1.5.2.0 で実装）。自作するなら plsnt の目次を設計参考に。
tags: [pleasanter, claude-code, skills, mcp, survey]
timestamp: 2026-08-08T00:00:00+09:00
---

# Pleasanter 向け Claude Code skills の調査

「Pleasanter を利用した開発に使える Claude Code skills を知りたい」への調査結果（2026-08-08 時点）。

# 結論

- **Pleasanter 専用の公開 skill（SKILL.md 形式）は事実上 1 件のみ**: [immmmmmmu/plsnt](https://github.com/immmmmmmu/plsnt)。
- エコシステムの主流は skill ではなく **MCP サーバー**。Pleasanter 本体 v1.5.2.0（2026-03 頃）で MCP サーバー機能が公式実装された。
- skills.sh・awesome-claude-skills 系集約リポジトリ・GitHub `.claude/skills` 検索・日本語圏（Qiita/Zenn/Implem ブログ）のいずれにも、plsnt 以外の Pleasanter skill 公開物は無い。記事はすべて MCP 活用の文脈。

# 唯一の skill 該当: plsnt

- Go 製の Pleasanter REST API 用 CLI（AGPL-3.0）。「エージェントファースト」を謳い、`internal/bootstrap/assets/skills/` に **Core 11 スキル**を同梱:
  `plsnt-guide` / `column-design` / `relational-modeling` / `data-migration` / `bulk-operations` / `search-and-report` / `display-views` / `setup-issues` / `multi-environment` / `mcp-setup` / `troubleshooting`
- `plsnt init` で Claude Code / Codex / Gemini の各エージェントに展開するクロスエージェント設計。YAML バッチによる複数テーブル一括構築、SitePackage の意味的 diff、docs に「Pleasanter MCP vs plsnt CLI」比較 ADR あり。
- **注意**: 2026-05 作成・Star 0 の個人リポジトリ。そのまま依存するより、SKILL.md の中身を読んで自リポジトリの `.claude/skills/` に取り込む（AGPL-3.0 に留意）か、構成だけ参考に自作するのが現実的。

# MCP サーバー（skill の代替・主流）

- **公式**: Pleasanter 本体 v1.5.2.0 で MCP サーバー機能を実装。レコード検索・取得・更新、ビュー CRUD、サイト・ユーザー情報取得、メール送信。Claude Desktop へは `.mcpb` 拡張（URL + API キー）で導入。自己署名証明書対応のため TLS 検証を無効化する既知のセキュリティ注意あり。[マニュアル](https://pleasanter.org/manual/api-mcp-server)
- **サードパーティ**: [Takashi-Matsumura/pleasanter-mcp-server](https://github.com/Takashi-Matsumura/pleasanter-mcp-server)（TypeScript、複合フィルタ検索・傾向分析・一括操作、Star 7、2026-03 更新）。mcpflow 版は 2025-04 で停滞。

# 自案件への含意

閉域 Pleasanter 案件（[接続できない検証環境とエージェント開発](/tech/closed-network-agent-dev-loop.md)）で蓄積済みの呼び出しカタログ・列マッピング・[台帳プロンプト集](/tech/db-design-flow-prompts.md)は、plsnt が skill 化しているのと同種の知見。公開物を待つより、**plsnt の 11 スキルの目次を設計参考に、自分のプロンプト集を SKILL.md 形式へ切り出す**のが最も実りが大きい。

# Citations

[1] [immmmmmmu/plsnt](https://github.com/immmmmmmu/plsnt)
[2] [Implem/Pleasanter-MCP](https://github.com/Implem/Pleasanter-MCP)
[3] [Pleasanter 公式マニュアル: API MCP サーバー](https://pleasanter.org/manual/api-mcp-server)
[4] [Takashi-Matsumura/pleasanter-mcp-server](https://github.com/Takashi-Matsumura/pleasanter-mcp-server)
[5] [Qiita: プリザンターの MCP サーバの実装を詳しくみてみる](https://qiita.com/pmc-ko/items/95a914a96f59bf6ef2ed)
[6] [Zenn: Pleasanter MCP サーバーを Codex で設定する方法](https://zenn.dev/atoy0m0/articles/cff728079095c7)
