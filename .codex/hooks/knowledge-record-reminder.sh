#!/usr/bin/env bash
# Claude Code / Codex 共用 Stop hook: 会話が一定量あるのに knowledge/ が未更新ならターン終了をブロックする。
# 配線は2箇所: .claude/settings.json（Claude Code）と .codex/hooks.json（Codex）。スクリプト本体はこの1本のみ。
# CLAUDE.md の「記録は義務」ルール（レベル1: 善意頼み）をレベル3（機械強制）に配線したもの。
# 入力: stdin に hook の JSON。出力: 発火時のみ decision:block の JSON。
set -euo pipefail

command -v jq >/dev/null 2>&1 || exit 0   # jq がない環境では黙って無効化

input="$(cat)"
jq -e . >/dev/null 2>&1 <<<"$input" || exit 0   # 不正な JSON は黙って無効化
session_id="$(jq -r '.session_id // empty' <<<"$input")"
transcript="$(jq -r '.transcript_path // empty' <<<"$input")"
active="$(jq -r '.stop_hook_active // false' <<<"$input")"

[[ "$active" == "true" ]] && exit 0       # hook 起因の継続で再発火しない
[[ -n "$session_id" && -f "$transcript" ]] || exit 0

state_dir="${XDG_CACHE_HOME:-$HOME/.cache}/knowledge-record"
mkdir -p "$state_dir"
marker="$state_dir/reminded-$session_id"
[[ -e "$marker" ]] && exit 0              # セッションにつき 1 回だけ

lines=$(wc -l < "$transcript")
(( lines >= 30 )) || exit 0               # 雑談程度の短いセッションは対象外

# セッション開始時刻 = transcript 冒頭のタイムスタンプ。取れなければ黙って無効化
start_iso="$(head -10 "$transcript" | jq -r 'select(.timestamp != null) | .timestamp' 2>/dev/null | head -1)"
[[ -n "$start_iso" ]] || exit 0
start_epoch="$(date -d "$start_iso" +%s 2>/dev/null)" || exit 0

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
log_file="$repo_dir/knowledge/log.md"
if [[ -f "$log_file" ]]; then
  log_epoch="$(stat -c %Y "$log_file")"
  (( log_epoch >= start_epoch )) && exit 0   # このセッション中に記録済み
fi

reason="[knowledge-record] このセッションでは knowledge/ がまだ更新されていない。CLAUDE.md の記録義務に従い、相談から得られた再利用価値のある知見があれば OKF v0.1 でコンセプト文書を作成/更新し、所属 index.md と knowledge/log.md も更新すること。既存文書があれば新規作成ではなく更新する。記録価値のない雑談のみのセッションであれば『記録価値なし』と報告して終了してよい。"
jq -cn --arg r "$reason" '{decision:"block", reason:$r}'
touch "$marker"
