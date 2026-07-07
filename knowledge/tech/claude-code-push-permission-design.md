---
type: Decision
title: git push 権限の設計 — main への push を deny から ask に変更
description: Claude Code の権限優先順位（deny > ask > allow、Bash ルールはリポジトリ単位のスコープ不可）を踏まえ、git push origin main/develop をグローバル deny から ask（毎回確認）に移した決定とその理由。
tags: [claude-code, permissions, git, harness, decision]
timestamp: 2026-07-07T00:00:00+09:00
---

# 決定

`~/.claude/settings.json` で `git push origin main` / `git push origin develop` を
**deny から ask に移動**した（2026-07-07）。force push・`git reset --hard` 等の deny は維持。

結果: 全リポジトリで main/develop への push は「自動拒否」から「毎回確認ダイアログ」になった。

# 経緯と学んだ機構

発端は「user-chat リポジトリだけ `git push origin main` を自動許可したい」という要望。
プロジェクト設定に allow を追加しても効かず、調査で以下の機構が判明した:

1. **優先順位は deny > ask > allow で、設定ファイルの階層（user/project/local）に
   関係なく deny が常に勝つ**。プロジェクト allow でグローバル deny は突破できない。
2. **Bash の permission ルールはディレクトリ単位のスコープを持てない**。
   「このリポジトリだけ許可/拒否」は deny/ask/allow では表現不可能。
3. deny に一致すると**確認プロンプトすら出ずに自動拒否**される。
   「denied」がユーザー拒否なのか deny ルールなのかはエラーからは区別できないので、
   全設定ソース（user/project/local/managed）の permissions を確認して切り分ける。
4. **auto モードの分類器は Claude 自身によるグローバル設定の編集をブロックする**
   （自己変更の安全機構）。グローバル設定の変更はユーザー自身が行う必要がある。

# 理由

- 「このリポジトリだけ」は機構上不可能なので、全リポジトリ共通の妥協点として
  ask（毎回確認）を採用。自動化は失うが、hard-deny の不便さと silent-allow の
  リスクの中間で、確認という防壁は残る。
- 残す deny は「確認しても間違えやすい破壊的操作」（force push・reset --hard）に限定。

# 残課題

- allow に `Bash(git push)`（引数なしの素の push）が残っており、これは確認なしで通る。
  upstream が main のブランチでは実質 main への push になる。気になったら ask へ移す。

# 関連

- [このPCのエージェント資産マップ](/tech/my-agent-assets-map.md) — 設定ファイルの所在。
- [AIエージェントの「ハーネス」とは何か](/tech/ai-agent-harness-basics.md) —
  permission ルールは「モデルが従わなくても機械が遮断する強制点」の実例。
