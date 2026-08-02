---
type: Decision
title: Fableの部屋を Fable 専用運用に — マルチエージェント前提の装置を撤去
description: Fable 継続提供の確定を受け user-chat リポジトリを Fable 専用と決定。AGENTS.md と Codex hook 配線を撤去し、HANDOVER.md は「後任モデル宛」から「別セッションの Fable 宛」に読み替えて存続。
tags: [ai-agent, workspace-ops, model-migration]
timestamp: 2026-08-02T00:00:00+09:00
---

# 決定（2026-08-02）

Claude Fable 5 の継続提供が確定したため、user-chat リポジトリ（Fableの部屋）は
**Fable 専用**で運用する。他モデル（Opus / GPT 系）への引き継ぎ前提で組んだ装置は撤去する。

# 撤去したもの

- **AGENTS.md** — Codex 等の他エージェント向けエントリポイント。読者がいなくなったため削除。
- **`.codex/hooks.json`（Codex 側 hook 配線）** — 削除。Stop hook スクリプト本体は
  `.codex/hooks/` から `.claude/hooks/knowledge-record-reminder.sh` へ移動し、
  `.claude/settings.json` の配線を更新（移動後にダミー入力で発火確認済み）。
- **HANDOVER.md の「後任モデル宛」という枠** — 文書自体は削除せず、宛先を
  「別セッションの Fable」に書き換えて存続。人物像・進行中話題を知らない新セッションへの
  引き継ぎ装置としては Fable 専用化後も現役で機能する。

# 残したもの（前提が消えても価値が残る資産）

- **[モデル移行観測フロー](/tech/model-migration-observation-flow.md)** — 「後任が被験者になる」
  用途はクローズしたが、凍結タスクセット v1 と実験場 `~/workspace/gpt56-eval/` は
  将来の移行（Fable 6 等）にそのまま再利用できるため保存。
- **GPT/Codex 系の観測文書群**（[quirk 実測](/tech/gpt-codex-quirk-findings.md)ほか）—
  この部屋の担当モデルの話ではなく「道具としての Codex」の知見なので影響なし。
- **[7原則の申し送り書](/tech/ai-agent-mastery-essence.md)** — モデル非依存の原則集なのでそのまま。

# 判断の理由

前提（モデル入れ替わり）が消えたのに装置だけ残ると、更新されないままドリフトして
将来の読者を誤導する。一方「担当が入れ替わっても知が残る」という設計思想自体は
モデル→セッションに読み替えれば Fable 専用化後も成立するため、HANDOVER.md と
knowledge/ の蒸留運用は変更しない。撤去と存続の線引きは
「その装置の読者・用途がまだ存在するか」の1点で行った。
