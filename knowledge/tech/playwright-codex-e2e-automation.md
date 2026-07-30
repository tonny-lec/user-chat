---
type: Consultation
title: Codex × Playwright MCP による E2E テスト自動化
description: Pleasanter 案件の acceptance TEST を Codex＋Playwright MCP で自動化する構成の調査。Playwright Test Agents（planner/generator/healer）が Codex を公式サポート。生成と修理だけエージェント、実行は決定的に。
tags: [playwright, mcp, codex, e2e, testing, pleasanter]
timestamp: 2026-07-30T00:00:00+09:00
---

# 相談内容

Pleasanter 案件のローカル検証（acceptance.md の TEST-xx を画面＋DB 状態で判定）
において、業務PC で Playwright MCP が使えるようになった。Codex app と組み合わせて
E2E テストを大幅に自動化できないか。

# 検討・調査

## 事実（2026-07-30 調査）

- **Playwright Test Agents が Codex を公式サポート**。`npx playwright init-agents
  --loop=codex` でエージェント定義を生成できる（他に vscode / claude / opencode）[1]。
- 3 エージェントの分担: **planner**（実アプリを触って Markdown テスト計画を生成）/
  **generator**（計画を Playwright spec に変換 — セレクタと assert を実ブラウザで
  検証しながら書く）/ **healer**（失敗テストを再生して locator や wait を修理）[1][2]。
- 成果物: `specs/`（Markdown 計画）、`tests/`（spec ファイル）、`tests/seed.spec.ts`
  （初期コンテキスト用シード）。Playwright 更新時はエージェント定義を再生成する [1]。
- MCP は accessibility tree スナップショットベースで実 DOM を観測して判断する
  （ソースからの推測ではない）[3]。
- Codex 側の設定: `config.toml` の `[mcp_servers.playwright]` に
  `command = "npx"` / `args = ["@playwright/mcp@latest"]`。または
  `codex mcp add playwright npx "@playwright/mcp@latest"` [4][5]。

## 設計判断（既存 knowledge との接続）

原則は [AI UI 検証ループ](/tech/ai-ui-verification-loop.md) の定石そのまま —
**「その場の検証は MCP（書き捨て）、恒久チェックは Playwright テストコードに落とす」**。
今回の案件文脈に当てはめると:

1. **planner は簡略化できる** — テスト計画は既に acceptance.md（TEST-xx）として
   存在する。ゼロから探索させず、acceptance.md を specs/ 形式に変換して generator に
   食わせるのが最短。抽出主義（作るのではなく既存資産から抽出する）とも一致。
2. **エージェントの仕事は生成と修理だけ**。日々の実行は `npx playwright test` の
   決定的実行（トークン 0・再現可能・件数で報告可能）。毎回エージェントに画面を
   触らせて「確認しました」と言わせる方式は再現性がなく高コストなので採らない。
3. **2 層 assert**: 画面（Playwright の expect）＋ DB 状態（scenario 突合 — 既存の
   API/SQL インターフェイスをテストコードから叩く）。TEST-xx の判定基準と同型。
4. **環境値の結線**: site id・base URL・認証は .env / playwright config / fixture
   経由。site id は環境値（インポート時採番・指定不可）という規律
   （[プロンプト集](/tech/db-design-flow-prompts.md) 共通規律）とそのまま噛み合う。
   ログインは storageState で 1 回だけ。
5. **healer への規律が必須**: healer は「テストを直して green にする」方向に
   バイアスがある。期待値の書き換え（＝チェックを通すためのエラー握りつぶし）を
   禁止し、「テストの修理か実装の欠陥かの裁定は acceptance/scenario（台帳）を正とし、
   台帳と食い違う修理は差分提案で○×待ち」を指示に含めること。

## リスク・要確認

- **ネットワーク**: `npx @playwright/mcp` とブラウザバイナリの取得に npm レジストリ
  アクセスが要る。業務PC が閉域なら事前にオフラインインストール経路を確認。
- **セレクタ安定性**: Pleasanter はサーバレンダリング＋jQuery で data-testid が無い。
  ラベル・ロールベースの locator を書かせる。拡張 HTML（独自部分）は自前なので
  必要なら data-testid を足せる。
- **拡張 HTML の描画タイミング**: script 実行後の描画待ちが flaky の温床。
  healer 頼みにせず、生成時から明示的な wait 条件を書かせる。

# 結論

- 「めちゃくちゃ自動化できる」は正しい。公式の Test Agents（--loop=codex）で
  **acceptance.md → Playwright spec の生成**と**失敗時の修理**をエージェント化し、
  **実行は決定的**にするのが推奨構成。
- 導入タイミング: 現在の不具合修正＋#4c 再実行が先。TEST 再実行が回った後、
  「TEST-xx の Playwright 化」を並行トラックとして 1 本立てる。
- 期待効果: 動作確認の反復（いま毎回手で回している job→画面→保存の類）が
  `npx playwright test` 1 コマンドになり、報告も 通過数/総数＋✗個票 の形式に
  そのまま乗る。回帰検査が事実上無料になるため、「修正のたびに全 TEST を回す」が
  現実的になる。

## 導入プロンプト案（キュー投入はユーザー指定後）

```markdown
E2E テストの恒久化を行え。エージェントによるその場の画面確認ではなく、
再実行可能な Playwright テストとして抽出する。

0. 準備: npx playwright init-agents --loop=codex を実行し、Playwright MCP
   が使えることを確認せよ（ブラウザバイナリ取得も含む）。失敗したら
   ネットワーク要因を報告して止まれ（回避策の発明禁止）。
1. 変換: acceptance.md の TEST-xx を specs/ の Markdown 計画に変換せよ。
   新しいテストを発明するな — 出所は acceptance.md のみ。
2. 生成: 計画から Playwright spec を生成せよ。制約:
   - site id・URL・認証情報はハードコード禁止 — 環境値（.env /
     playwright config）経由。ログインは storageState で 1 回。
   - assert は 2 層: 画面（expect）＋ DB 状態（既存インターフェイス経由で
     scenario の期待値と突合）。
   - 待ち条件は明示的に書く（拡張 HTML の描画完了を含む）。
3. 実行: npx playwright test で全件回せ。
4. 失敗の扱い: テストの欠陥（locator・wait）は修理してよい。期待値と
   実際の食い違いは修理禁止 — acceptance/scenario を正とし、実装欠陥の
   個票（操作/期待/実際/見立て1行）または台帳差分提案として報告せよ。

報告: 変換 <n>/<TEST 総数> / 生成 spec <n> / 実行 <通過>/<n> /
修理（テスト側）<n> / 実装欠陥の個票 <n> / 台帳差分提案 <n>
```

# Citations

[1] [Playwright Test Agents（公式）](https://playwright.dev/docs/test-agents)
[2] [Playwright Test Agents: Planner, Generator and Healer Guide](https://testdino.com/blog/playwright-test-agents)
[3] [Playwright AI Ecosystem 2026: MCP, Agents & Self-Healing Tests](https://testdino.com/blog/playwright-ai-ecosystem)
[4] [Codex CLI で MCP サーバを設定する方法](https://qiita.com/tomada/items/2eb8d5b5173a4d70b287)
[5] [Codex CLI で Playwright MCP を使う](https://www.oresamalabo.net/entry/2026/01/01/141147)
