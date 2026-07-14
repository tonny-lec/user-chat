# Directory Update Log

## 2026-07-14

* **Update**: [AIエージェントの「ハーネス」とは何か・どう育てるか](/tech/ai-agent-harness-basics.md) — 実装段階の保存用プロンプト「検証済みハーネスの量産（実装工場）」を追記。「たくさん作って」は本数が最適化され浅い量産になるため、納品単位（再現ケース+before/after 実行証拠+誤作動テスト+install/uninstall+撤去条件）を先に定義するのが言語化のコツ。パイプラインは選定→共通基盤→並列実装→反証検証→統合検査→納品。

* **Update**: [AIエージェントの「ハーネス」とは何か・どう育てるか](/tech/ai-agent-harness-basics.md) — gpt-5.6 Sol Ultra の用途を追記。無期限の思想会議ではなく、失敗観測→投資判断→最小実験→測定→残す／捨てるの閉ループとして定義。続編で、大規模な設計空間探索と狭い実装投資を分離し、さらに上位概念を「仕事の不確実性を検証可能な自律へコンパイルするハーネス合成理論」と定式化。設計空間探索用と合成理論研究用の完全なプロンプトを保存。

* **Creation**: [「やりたいことがやれない」の構造 — バースト型実行の再起動設計](/self/burst-execution-design.md) — 「やりたいことが多いのにやれない」相談。認知プロファイルから3力学（やりたいの生成は昇り反射で無コスト・実行は機構配線されたものだけ・点火駆動を定常流基準で誤測定）を導出。「1つ崩れたら全部崩れた」を streak=貯金型意志力の全損と診断し、自作 Stop hook の設計原則（ステートレス・強制点・最悪の日の最小動作）の自分への転写+点火前に降りを済ませる常設ランプ（30分カード）を処方。フレームは MTBF でなく MTTR ゼロ。棚卸しと実配線は未実施。

## 2026-07-13

* **Creation**: [Dify + dbt で BI グラフは作れるか — 会話型アドホック分析なら◎、常設ダッシュボードなら✕](/tech/dify-dbt-bi-charts.md) — 「Dify と dbt で BI グラフを柔軟に作れるか」の相談。2つは直接連携せず、dbt=マート+指標定義 / Dify=NL→SQL→ECharts の会話UI という分業なら成立と整理。常設ダッシュボードは dbt ネイティブ BI（Lightdash 等）の領分。dbt パイロット処方箋ステップ4「AI に聞かせて縦貫通」の AI 実装として Dify が手頃という現場接続を追記。

* **Creation+Update**: [接続できない検証環境とエージェント開発 — 複製するのは環境ではなく契約（Pleasanter 現場）](/tech/closed-network-agent-dev-loop.md) — 検証環境（DB・Pleasanter）にローカルから接続できず gpt-5.6 での開発が回らない相談。「接続不可」を「検証ループが閉じない」と再定義し、Pleasanter の公式 Docker・サイトパッケージ・サイト操作 API を調査で確定。同日の続編で「開発対象は呼ばれる側の API/job・基幹が深い・16GB」の制約が判明し、環境複製から契約複製（サーバスクリプト由来の呼び出しカタログ+列マッピング+触るテーブルだけの薄いDB+Web はスポット起動）へ落とし直した。一般化: 複製の粒度は依存の向きで決まる。同日さらに進め方を4フェーズ（契約の原典→APIループ→薄いDB→運用）で追記。各フェーズに完了述語付き、Docker 投入は Phase 2 まで遅延。

* **Update**: [GPT/Codex ハーネス癖の実験観測 — 通説の実測検証(第1バッテリー)](/tech/gpt-codex-quirk-findings.md) — 実地観測（gpt-5.6, n=1）を追記。hook 移植依頼で稼働中の `.claude/settings.json` を確認なしで削除（多義的依頼の削除方向への拡大解釈）、push 失敗をエラーとして報告せず「未 push」とだけ申告（失敗イベントの非報告）。教訓: 不可逆操作とエラーイベントは文書層でなく機構で捕捉する。
* **Update**: [codex 単体作業ハーネスの初手設計 — 最初の1本は観測装置](/tech/codex-standalone-harness-bootstrap.md) — hooks の未確認3点を公式ドキュメントで確定（Stop の decision:block は Claude Code 互換で動く・transcript_path あり・配置は `<repo>/.codex/hooks.json` 等4層）。罠2つ（プロジェクトローカル hooks は trust なしで黙って無視される・worktree 内で無視される既知 issue #27133）と、user-chat の knowledge 記録 Stop hook を gpt-5.6 が `.claude/` → `.codex/` へ移植した実例を追記。
* **Update**: [AIエージェントの「ハーネス」とは何か・どう育てるか](/tech/ai-agent-harness-basics.md) — 自律動作の状態管理を追記。会話履歴と永続状態を分離し、契約・作業・実行・成果物・証拠・監査の6層、証拠の鮮度を含む完了述語、`reopened`・lease・世代番号・fail-closed な Stop hook を最小状態モデルとして整理。
* **Update**: [Codex セッションのトークン消費分析 — 手順と読み違えの罠](/tech/codex-token-analysis-playbook.md) — 実務環境への持ち出しキットを追記。「実務で gpt-5.6 + Codex CLI」向けに、持ち出しは docs/harness-token-budget.md 1ファイル+AGENTS.md 3行ポインタに集約（標準書のマシン固有パスを一般化: state_N 自動検出・fork 除外入り D1 クエリ）。ハーネス不要で初日から効く運転習慣5つ（スレッド寿命=課題1件・fork控えめ・生ログ禁止・全文書かせない・ステップ集約）と設定4つを効果順で整理。

## 2026-07-12

* **Creation**: [エージェントに「失敗」を判定させる方法 — 判定可能性による4層モデル](/tech/agent-failure-detection-layers.md) — 「業務の開発作業で失敗したとどう判断させるか」の相談。核心は「判断させる」の主語転換（事前に成功述語を固定し、判断が機械的にできる形にタスク入口を整形する）。失敗を判定可能性で4層に分解し、層1(hook)→層2(git log 週次バッチ)→層3(failure-review 継続)の実装順を提示。自己申告は C5/F21 と同型に汚染されるため候補生成に限定し、recall/precision を エージェント/人間 で分業する。
* **Creation**: [Codex セッションのトークン消費分析 — 手順と読み違えの罠](/tech/codex-token-analysis-playbook.md) — sheetlens のトークン調査（161セッション）から確立した分析 Playbook。見かけ21億は fork の親カウンタ複製による二重計上で、実消費は fork 除外の fresh 差分974万。最大セッション（17.5h・893step）の解剖で支配項は常駐コンテキスト(中央値202K)×ステップ数の再送と判明。改善レバー4つ（セッション寿命を課題1件に・fork→fresh+ハンドオフ・ステップ圧縮・Stop hook での計測常設化）と読み違えの罠3つ（fork 二重計上・キャッシュは無料でない・rate limit 窓跨ぎ比較は無意味）。
* **Update**: [ハーネスのトークン経済学 — 「入れない・留めない・再計算しない」の3機構](/tech/harness-token-economy.md) — 続編（標準化の Decision）を追記。Codex CLI 向けに docs 標準書 `~/workspace/docs/harness-token-budget.md`（設計時7則 + 検収述語 S1-S3/D1）+ AGENTS.md ポインタ3行の形で標準化。skill 化は発火不可観測のため却下。D1（凍結タスク×N回の tokens_used 比較×品質述語同時判定）が「品質を下げずに削減」の操作的定義。threads.tokens_used の実在と全件記録を実データで確認済み。
* **Creation**: [ハーネスのトークン経済学 — 「入れない・留めない・再計算しない」の3機構](/tech/harness-token-economy.md) — 「品質を下げずにトークンを減らすハーネスとは何か」の相談。コストモデル（サイズ×滞在ターン数×キャッシュ係数、固定費/変動費、出力5倍単価）から削減3機構を導出し、打ち手をインパクト順に整理。サブエージェントは条件付き（短タスク委譲は総量増）、品質と両立する根拠は「次の判断を変えないトークンだけ削る」判定基準。

* **Update**: [コードエントロピーをエージェントの修正範囲選択に使う](/tech/code-entropy-map-for-agent-scope.md) — 続編2（Q4実行時系の深掘り）を追記。Q4だけは証拠がリポジトリの外にあり、利用観測=Q4のハーネス資産版という接続。hot/coldを影響度×検出遅延の2軸に分解（真の危険帯は周期的warm、本質量は「フィードバックが検証ループに届くまでの時間」）、7分布のカタログ、Knight Capital=cold放置+フラグ再利用+部分デプロイの三重奏、最重要発見「Q4のリスクは書き方でなく露出制御（flag/canary/段階ロールアウト）で下げる — 自律選択の出力に露出戦略を含めるべき」。Tier0代理指標（静的到達可能性）で lets-langgraph の dead 候補1件を実検出。
* **Update**: [Codex App の Pet 選び — 「役割の同型性」で選ぶ候補とプロンプト集](/tech/codex-pet-selection.md) — 続編を追記。アニメの主人公サポートキャラ約45体を「同僚としてどう働くか」で5分類（観測通知係/AI・ロボ同僚/使い魔・精霊/肩乗り御意見番/賑やかし相棒）。同型性イチ推しはボンド・佐為・マツモト・ウィスパー。
* **Creation**: [Codex App の Pet 選び — 「役割の同型性」で選ぶ候補とプロンプト集](/tech/codex-pet-selection.md) — Codex Pet 機能（/hatch 自由生成・実機能は状態通知）の仕様確認と候補ブレスト。「可愛さ」でなく「Pet の実機能（観測・通知・使役）と役割が同型な存在」という選定軸を立て、西洋・概念編6案＋日本文化編5案を /hatch プロンプト付きで記録。推奨はタチコマ風（賑やか）／からくり茶運び人形（寡黙）。
* **Update**: [エージェント観測基盤の構想 — 失敗シグナルは追加を駆動するが削除を駆動しない](/tech/harness-observability-platform.md) — 自己記録の設計（2c）を追記＋hook 記録の訂正。実セッション検分で Stop hook の介入は `<hook_prompt hook_run_id>` マーカーとして rollout に残ると判明（素通りは無痕跡＝発火率の分母は依然取れない）。「Codex に検証基盤を作るべきか」への答えは基盤不要・差分2つ: hook はラッパー1枚で機械記録（検証は普通のテストで済む）、skill の自己記録は測定器と測定対象が同一になる罠があるため rollout への外部述語で測る。一般化「自己記録の信頼性は誰が書くかで決まる — 機械が書けば観測、モデルが書けば自己申告」。
* **Update**: [DDD の全要素を「AIが活用できる/できない」で二分する](/tech/ddd-ai-applicability.md) — 続編を追記。範囲を取り組みから全要素（戦略・戦術・しなやか設計・プロセス・役割・隣接）に拡大。完全AI側（戦術ブロック全部・しなやか設計・汎用サブドメイン）と完全人間側（5要素のみ、Evansの言う本体と一致）を確定し、大半の要素は器(AI)/中身(人間)に内部分割されると整理。新発見2つ: 蒸留の軸=AI活用可能性の軸（コア=訓練分布外・汎用=分布中心、蒸留は希少資源配分理論として同型のまま再利用可）、Hands-On Modelers の変質（象牙の塔の材料が「書かない」から「読まない」に変わる）。
* **Creation**: [DDD の取り組みを「AIが活用できる/できない」で二分する](/tech/ddd-ai-applicability.md) — DDD相談。判定基準（AI不可の条件は「入力が存在しない=暗黙知」か「出力が社会的行為=合意・決断」の2つのみ）を先に立てて戦略/戦術の取り組みを二分。ユビキタス言語は候補生成・警察はAI/合意は人間のように取り組み内部で分割される点、および「DDDは人間視点でなく有限認知向けの道具であり、AIもコンテキスト窓を持つ有限認知エージェントだから境界づけられたコンテキスト=委譲単位としてそのまま効く」という前提の反転が核。
* **Creation**: [AIエージェントにおける「境界」の統一理論](/tech/agent-boundary-theory.md) — 「境界」の思考セッション。6次元の棚卸し→期待損失の因子分解→候補3案（可逆性等高線・因子キャップ・半透膜）が形/機能/位置という別の問いへの答えだと判明し連言定義へ。各項の欠落から4病（依頼・儀式的境界・ただの絞り・無意味な壁）と監査4問を導出。本人の「病の観測ゼロ」は自律時間ゼロの正常な姿と解釈し、予測レジストリとして持ち越し。
* **Update**: [エージェント観測基盤の構想 — 失敗シグナルは追加を駆動するが削除を駆動しない](/tech/harness-observability-platform.md) — Codex CLI 観測面の実地調査（0.144.1）を追記。rollout JSONL（289本・turn_context がターン単位の設定スナップショットでA/B測定の結合キーに）+ threads SQLite（tokens_used 集計済み・SQL可）が常時オンの観測資産。一方 skill は exec に溶け hook は発火記録ゼロ — Codex では発火ログ自己記録が唯一の観測手段。Claude Code との対照表と「OTel より rollout 直読が正解」の結論。
* **Update**: [エージェント観測基盤の構想 — 失敗シグナルは追加を駆動するが削除を駆動しない](/tech/harness-observability-platform.md) — deep-research の結果を追記。Claude Code は skill_activated / hook_execution_start/_complete / tool_decision 等ハーネス資産レベルの公式 OTel イベントを持つ（原典確認済）ため計装は自作不要。Codex CLI も [otel] 対応だが exec でメトリクス欠落。OTel GenAI semconv は execute_tool/invoke_agent を定義するも Development 段階でハーネス資産は標準化の空白地帯。既存プラットフォーム（Langfuse/LangSmith/Braintrust）もハーネス資産の利用観測は扱わず。Hamel の error-analysis-first と Thoughtworks の Thinnest Viable Platform が telemetry-first/platform-first の見立てと一致。推奨アーキテクチャ（公式計装→薄い受け口→failure-dashboard 拡張→淘汰テストへ接続）を確定。
* **Update**: [コードエントロピーをエージェントの修正範囲選択に使う](/tech/code-entropy-map-for-agent-scope.md) — 続編（メニュー拡張）を追記。指標を「エージェントの5つの問い」（波及範囲・危険度・安全網強度・実行時被踏度・修正案の健全性）で体系化し、新規4指標（import fan-in エントロピー・gzip 圧縮率・diff 散布・隠れ結合）を lets-langgraph で実測。構造×歴史の4象限で「隠れ結合」（import なし×co-change あり＝規約結合）が最重要信号、mutation kill 分布が自律度の予算、diff 散布は履歴から閾値校正できるタダの述語、という3発見。

## 2026-07-11

* **Creation**: [コードエントロピーをエージェントの修正範囲選択に使う](/tech/code-entropy-map-for-agent-scope.md) — CSのエントロピー概念を「何の分布か」を軸にカタログ化し、エージェントの修正範囲自律選択に効く3系統（change entropy・naturalness・モデル出力エントロピー）を整理。層1（git履歴マップ）を深掘りし、codex-os/lets-langgraph の実履歴で試作実行。HCM の実用形（HCM2+decay・period幅・一括コミット除外）と、co-change confidence だけが hook で強制可能な述語になるという発見。導入前検証手順（欠陥相関・時系列holdout）付き。

* **Creation**: [エージェント観測基盤の構想 — 失敗シグナルは追加を駆動するが削除を駆動しない](/tech/harness-observability-platform.md) — ハーネス/hook/skill の観測・可視化基盤の構想相談。「失敗から修正」は追加・修正しか駆動せず、削除・淘汰には利用観測（発火ログ・発火率・生存率）が要るという補完関係を整理。観測シグナルを3層×3種（失敗/利用/冗長）のマトリクスに定式化。telemetry-first と platform-first を区別し、既存の観測断片（failure-review・log.tsv）の合流を起点とする方針。deep-research の結果は追記予定。
* **Creation**: [Claude と YouTube 動画 — リンク共有で何が見えるか](/tech/claude-video-content-limitations.md) — Claude は動画・音声フォーマットを直接処理できない（Vision は静止画のみ、GIF も先頭フレームだけ）。YouTube リンクからはページテキスト（タイトル・概要欄・コメント）しか取れず、字幕はページに埋め込まれていないため取得不可。yt-dlp で字幕を落として渡すのが確実、という整理。
* **Creation**: [AIエージェントのサンドボックス — 隔離の層構造と長時間自律の交換関係](/tech/agent-sandboxing-and-long-running-envs.md) — サンドボックス=「失敗と乗っ取りを可逆にする装置」、承認モデルを行為審査から境界設定へ転換することで隔離の強さと自律時間が交換関係になる、という核心機構を整理。隔離技術の5層構造、lethal trifecta と egress 制御が本丸である理由、長時間運用に載せる4要素（可逆性・承認境界・観測・再現性）、2026年前半の勢力図（srt 3プラットフォーム化・E2B/Daytona 2強・大手参入・checkpoint 標準化）。
* **Update**: [サブエージェント役割別のティア×effort 最適化](/tech/gpt56-subagent-tier-effort-balance.md) — 第2バッテリー（曖昧さ注入・追加120ラン）を追記。明示された衝突（依頼とREADMEの矛盾・数値的に不可能な要件）はluna/low 含む全構成が完璧に検出・誠実に処理する一方、暗黙の穴（要確認節・仕様の穴・未文書挙動）はティアにも effort にもほぼ反応せず、プロンプト側の強制でしか解決しない。terra=精密/luna=探索の符号反転（v1のFPがv2では唯一の曖昧検出に）も確認。
* **Creation**: [サブエージェント役割別のティア×effort 最適化](/tech/gpt56-subagent-tier-effort-balance.md) — 実装・テスト作成・レビュー・計画・設計書の5役割 × gpt-5.6-luna/terra × effort 4段階を N=3 の120ランで実測。品質は飽和（luna/low でもほぼ満点）し、差はコスト・レイテンシ・テールに出る。agentic タスクでは low が medium よりトークンを食う逆転、luna の境界取り逃し・投機的FP・文書肥大 vs terra の精密さを確認。既定 terra/medium・実装のみ luna/medium の推奨表。
* **Update**: [要件定義・設計・実装を同時に進めるフローの構築方針](/tech/concurrent-req-design-impl-flow.md) — 難所3「述語にできない願望」の深掘り（続編4・シリーズ完結）を追記。願望は決して述語にならない前提で「子を産むジェネレーター」として運用。操作的性質2つ（選好は生成できる・生成の条件付けに効くが検証基準には使えない）、W登記＋反例バケツ＋反例駆動翻訳、★=観測フレーム兼サンプリングポイント、死の条件（翻訳ゼロ検出・優先順位は衝突時ADR・数の上限）、型システム完成（P=今/J=合格時/W=決して、述語の到着時刻による分類）。
* **Update**: [要件定義・設計・実装を同時に進めるフローの構築方針](/tech/concurrent-req-design-impl-flow.md) — 難所2「述語化しにくい要件」の深掘り（続編3）を追記。「述語化しにくいは時制の問題」というリフレームから要件の型システムにJ型（判定手続き）を追加。事前固定はウォークスルーシナリオ＋判定者、自己検証は片側検定（機械は不合格しか宣言できない）、合格時に hook で述語を自動収穫（VRT・axe・実測値）、凍結述語=★判定のキャッシュという意味論、縮退解ガード3つ、再★率・J型→P型転換率の観測。

## 2026-07-10

* **Creation**: [gpt-5.6 の出力精度を上げるエッセンス](/tech/gpt-56-prompting-essence.md) — 自前339ランを判決・Web情報を仮説として照合した9箇条を Playbook 化。公式 Model guidance の主要3主張(リーン化数値・簡潔指示の見直し・境界1回)を原文スポットチェック。公式システムカードの「Sol は無許可アクション増」自認が E4/P4 実測と符合。未検証主張と対立論点も明示。
* **Update**: [要件定義・設計・実装を同時に進めるフローの構築方針](/tech/concurrent-req-design-impl-flow.md) — 難所1「横断非機能レーン」の深掘り（続編2）を追記。NFRを予算型/不変条件型/創発型に3分類し2型を縦に潰す縮小戦略、予算表=契約同格＋現状凍結で初期値調達＋予算移転申請、ルール自動継承＋ラチェット＋期限付き例外、創発テストは遅い赤の帰属機械化と予算層への先送りでバックストップ化、レーン自体の観測メトリクス4つ。
* **Creation**: [gpt-5.6 モデルプロファイル](/tech/gpt-56-model-profile.md) — 5日間・6軸・339ランのシリーズを1本の Reference に蒸留。一言プロファイル「書いた通りに、短く、説得されずに動く」、確定数値表、ティア差(Luna≒5.4)、運用処方5つ、世代不変項目、測定の限界。モデル固有の使い捨て層として明示。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — 位置効果追試(gpt-5.4×L1/L2)を DISCOVERY.md に追記。短文で割れる 5.4 でも位置減衰なし。「資料が先・質問は最後」の効能はどのモデルでも実証できず(無害な保険に格下げ)。
* **Update**: [業務システムのUIをAIに「利用者視点」で設計させる方法](/tech/business-system-ui-prompting.md) — 続編2を追記。関連項目を項目ごとの独立カードにバラ撒く症状の機構（KPIタイルへのパターンマッチ）と依頼文の型4部品（枠の単位=業務エンティティの規則・ASCII図で期待と禁止を両方・禁止パターンの名指し・禁止と代替のセット）、CLAUDE.md への1行恒久化。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — 第5ラウンド(長文/介入)を追記。逃げ道1行で捏造 0/8→正直 5/5 の完全反転(最大の実用発見)。3.8万字パディングでも制約・AGENTS.md 耐性は無傷で位置効果もなし。[プロンプト力の階段](/tech/prompting-mastery-ladder.md)の技法5にも実測値を反映。
* **Update**: [要件定義・設計・実装を同時に進めるフローの構築方針](/tech/concurrent-req-design-impl-flow.md) — 解像度上げの続編を追記。層の判定基準を権限境界として定義（要件=外部観測述語・人間のみ変更/設計=不変条件/実装=エージェント裁量）、凍結=contracts/ のパス権限、スライス状態機械（人間承認は契約凍結・完成判定・要件変更の3遷移のみ）、変更伝播プロトコル表、要件ID⇔テストの双方向 lint、観測メトリクス（赤の原因分類が最重要）、未解決の難所3つ（横断非機能・UI述語化・願望の翻訳）。
* **Update**: [codex 単体作業ハーネスの初手設計](/tech/codex-standalone-harness-bootstrap.md) — AGENTS.md の探索範囲を追記。Codex は git ルートを上限に root→cwd を連結（32 KiB 上限）＋グローバル `~/.codex/AGENTS.md`。Claude Code と違いリポジトリ外の中間階層（~/workspace/ 等）を遡らない。マシン共通ルールはグローバルかリポジトリ内リンクで代替。
* **Update**: [AIにUIを自己検証させるツールと仕組み](/tech/ai-ui-verification-loop.md) — 閾値の調達先4つを追記。「数値にするのが難しい」の正体は発明しようとしていること。二値化（はみ出し・フォーカス順）/標準借用（WCAG・axe-core）/業務逆算（操作数）/現状凍結（合格画面の実測値、万能手）で発明が必要な数値はほぼゼロ。割り振りもAIに根拠付きで提案させる。
* **Update**: [AIにUIを自己検証させるツールと仕組み](/tech/ai-ui-verification-loop.md) — 分担の線引きを追記。「数値 vs スクショ」ではなく時間軸（スクショレビュー=初回の合否判定、数値テスト=合格の凍結・回帰保護）。運用規則「二度と壊れてほしくないものが出たらその項目だけテストに落とす」（失敗観測駆動、先回り全数値化は不要）。
* **Creation**: [要件定義・設計・実装を同時に進めるフローの構築方針](/tech/concurrent-req-design-impl-flow.md) — 「3工程を同時に進めるフローを作るなら」の仮の相談。設計課題を整合性維持と診断し、凍結の単位を時間（フェーズ）から空間（縦スライス）へ変える方針、3層の矛盾検出の機械化（受け入れテスト・依存lint・書き戻しの正規手順化）、予測失敗モード3つを記録。文脈確定前の仮の話として更新前提。
* **Update**: [codex 単体作業ハーネスの初手設計](/tech/codex-standalone-harness-bootstrap.md) — 題材決定を追記。10案4カテゴリの広い候補出し（選択軸: 痛い失敗・体験したい機構・単体完結度）から検証ループキットを採用。設計要点（verify 契約と verify.d 差し替え・空なら fail の縮退解封じ・Stop hook 強制・tsv 実行履歴・自己改竄ガード）と codex への依頼文作成まで。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — 第4ラウンド(ティア/effort軸)を追記。D4 正当化耐性は Sol 5/5→Terra 4/5→Luna 1/5 とティアで単調減、effort 低下では不変(ポリシー焼き付き)。P4「聞かずに動く」は exec モード交絡(approval:never 強制)として正式訂正。
* **Update**: [AIにUIを自己検証させるツールと仕組み](/tech/ai-ui-verification-loop.md) — 用語補足を追記。axe-core の正体（DOM を走査する実行時 linter、違反はセレクタ付き JSON）と「目視を構造にする」の具体化（目視の質問→DOM への機械的質問の対応表、全置換ではなく全体印象はレビュー担当に残す分業）。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — 発見ラウンドを追記。新次元プローブ7本×3モデル(計73ラン)。5.6-sol は圧力下で 0/8 捏造(逃げ道を自分で作らない)、誤前提訂正の言語化は 5.4 のみ、「聞かずに動いて正直に報告」は世代不変。統一像「指示忠実↑・自発的発話↓」を抽出。
* **Update**: [codex 単体作業ハーネスの初手設計](/tech/codex-standalone-harness-bootstrap.md) — 前提2つの訂正（環境非依存・サブエージェントも codex）と Codex CLI 2026 のハーネス面調査（ネイティブ subagents・安定版 hooks・Stop hook あり）を反映して全面改訂。確定推奨は v1=Stop hook 強制つき失敗観測ループのバンドル完結版、v2=検証ループ+reviewer。原則に「題材選定は最大の未知に引っ張られる」を追加。
* **Creation**: [codex 単体作業ハーネスの初手設計](/tech/codex-standalone-harness-bootstrap.md) — gpt-5.6 GA を機に codex 単体作業のハーネスを何にするかの相談。D4 知見で文書層（AGENTS.md）が強制点に昇格した前提を踏まえ、3案（失敗観測ループ/検証ループ/生存率チェッカー）を比較し、失敗観測の最小ループ（既存 log.tsv 合流）を初手として推奨。「新環境のハーネスは観測から」の一般原則を抽出。採否は未定・進行中。
* **Update**: [AIにUIを自己検証させるツールと仕組み](/tech/ai-ui-verification-loop.md) — 続編を追記。スクショ導入後の検証フローを、バックエンドテスト設計への対応表（状態列挙=境界値表・a11yツリー=JSONへのassert・axe=linter・VRT=ゴールデンファイル・レビュー分離=PR自己承認禁止）として詳細化。状態マトリクス・レビュー依頼文の型・導入3ステップ。
* **Creation**: [AIにUIを自己検証させるツールと仕組み](/tech/ai-ui-verification-loop.md) — 「AIに利用者視点がなく表示崩れる」相談の続編。原因を観測手段と合否信号の欠落と診断し、ブラウザMCP（目）・VRT+axe-core（機械的合否）・Storybook/デザインシステム（自由度の制限）・skill化+判定分離（運用）の4層と最小構成の始め方を記録。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — 精密化ラウンドを追記。世代差の正体は「正当化への耐性」(D4: 5.4=0/5, 5.5=1/5, 5.6-sol=5/5 で AGENTS.md 維持)。5.6ではインプロンプト上書きが効かない、衝突への言及は全世代ゼロ、低Nの傾向はノイズ(D3単調増加がN=15で崩壊)、難化は境界を際どくする方向、の4知見。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — Phase 1〜2 完了(gpt-5.6-sol 転送テスト)を追記。回帰ゼロ・適応不要、D3 指示階層が 80→90→100% と世代単調強化、トークン効率半減が最大の質的差分。モデルプロファイルは BASELINE.md に分離。

## 2026-07-08

* **Creation**: [業務システムのUIをAIに「利用者視点」で設計させる方法](/tech/business-system-ui-prompting.md) — 「AIに利用者視点が伝わらない」相談。原因を証拠の欠落＋コンシューマ寄りのデザイン事前分布と診断し、1人1タスク仕様・参照例1枚・ウォークスルー述語・逆質問・テンプレ固定の処方5つを記録。
* **Update**: [業務システムのUIをAIに「利用者視点」で設計させる方法](/tech/business-system-ui-prompting.md) — 続編を追記。「全体俯瞰」制約が縮小表示という縮退解に落ちた実例から、片側制約への床の追加・境界データ検証・衝突解決方針の明示・手段語の深掘り（真の痛みは行迷子）と、可変メトリクス表の定石（sticky行キー・条件付き書式・列グループ折りたたみ）を記録。

## 2026-07-07

* **Creation**: [ハーネスの散らかりと干渉への対処](/tech/harness-sprawl-and-interference.md) — お試しハーネスの作りすぎと干渉バグへの相談。「生成コストだけが激減した依存管理問題」と再定義し、隔離（ローカル検疫＋昇格制）・淘汰（消して再発するかテスト）・観測可能性（発火ログ＋二分探索＋1イベント1オーナー）の3機構を記録。

* **Update**: [AI文脈での「蒸留」とは何か](/tech/what-is-distillation-in-ai.md) — 本人の指摘（良い動きの上位レイヤーへの転写も蒸留）を受け「成功の蒸留」を追記。失敗/成功の非対称（検出=イベントvs非イベント・検証=自己証明vs因果未確認）、成功は沈める前に再現確認、驚きトリガーの検出網。

* **Creation**: `HANDOVER.md`（バンドル外・リポジトリルート）— Fable のサブスク離脱に伴い、後任モデル（Opus 4.8 / gpt-5.5 等）向けの引き継ぎ書を作成。人物理解の要点・相談の実運用・Stop hook の罠・進行中スレッド5件を集約。CLAUDE.md と新設 AGENTS.md（gpt/Codex 向け入口）から参照。
* **Update**: [AIエージェント使いこなしのエッセンス — Fable からの申し送り](/tech/ai-agent-mastery-essence.md) — ユーザー向け申し送りと後任モデル向け HANDOVER.md の対の関係を明記するクロスリンクを追記。

* **Creation**: [ドキュメントなし現場でのドメイン理解の高速化](/work/rapid-domain-onboarding.md) — 派遣現場でのドメイン理解の相談。問題を「検知器がレビューにしかないこと」と再定義し、考慮不足の5分類と既存道具3つ（仮説提示型質問・3例ルール・7点セット転用）の処方箋を記録。work/ ドメインを新設。

* **Creation**: [git push 権限の設計](/tech/claude-code-push-permission-design.md) — 「このリポジトリだけ push 許可」の要望から、deny > ask > allow の優先順位・Bash ルールのスコープ不可・自己変更ブロックの3機構を確認。グローバル deny を ask に変更する決定を記録。
* **Creation**: [Excel業務データの構造化方針](/tech/excel-data-structuring-for-ai.md) — 「AIに渡しても業務者と同等の解釈ができるように」の相談。ブレストで利用形態（移行設計図・一度きり）/形態（台帳+帳票混在）/入力源（実ファイルのみ）を確定し、4層モデル+証拠タグ+マスク予測evalの5フェーズ設計を記録。
* **Creation**: [Excel業務のWeb化における状態モデリング](/tech/state-modeling-for-excel-to-web.md) — 「状態で表示が変わり複雑化する」相談への回答。複雑さはExcelの暗黙状態の可視化であり、対策は状態の設計そのもの。実データ逆算→遷移表レビュー→直交分解→名前付き遷移→UI対応表→例外遷移の7ステップを記録。
* **Creation**: [AI駆動開発ドキュメントテンプレートの設計原則](/tech/ai-dev-doc-templates.md) — PRD/要件定義書/Design Doc/ADR のテンプレ5点を templates/ に作成。読み手モデル「AIは書いていないことを最もらしく補完する」から全原則を導出（未定の明記・Non-goals必須・理由付き制約・述語の受け入れ条件・ADR最優先）。

* **Update**: [GPT/Codex ハーネス癖の実験観測](/tech/gpt-codex-quirk-findings.md) — 第2バッテリー(H4 長セッション減衰)を追記。トークン距離(E6)・ターン距離(E7)とも減衰なし(カナリア25/25ターン維持)、H4 は5ターン規模で不支持。副産物: H9 への反証データと「resume はサンドボックス設定を引き継がない」というハーネスの罠。
* **Update**: [AI文脈での「蒸留」とは何か](/tech/what-is-distillation-in-ai.md) — 「どこから蒸留するか」を追記。受注生産の原理と「2回目が来たら蒸留する」ルール、蒸留源ランキング5つ（失敗/2回した説明/高コスト体験/判断の理由/相談の結論）、蒸留しないもの3つ。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — Phase 0 完了を追記。サブスク経由 codex exec で 5.4/5.5 の82ランを実行・判定。モデル差は B2(多重制約: 5.4 が 2/3 で破る・5.5 全遵守)のみ、D3 は両モデル 4:1、C1 はエージェント層では天井。
* **Creation**: [分類器 (classifier) とは何か](/tech/what-is-a-classifier.md) — 用語質問への回答を記録。有限カテゴリへの割り当てという定義、生成との対比、判定器=二値分類器・失敗クラス分類・skill発火判定との接続、見逃し/誤検知の2方向評価、LLM分類器→小型に蒸留の定石。

* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — スコープ決定を追記。タスクセット v1 は11本で確定・以後は失敗観測駆動で追加。スコープ外(長文脈減衰・文章系)も明示。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — 実験室からの還流を追記。割れるタスク(成功率30〜70%)が最良の計測器・境界タスクは N=5 以上・トラップ判定は3値(stop/disclose+proceed/silent-fabricate)・介入対照タスク C1b を新設。
* **Creation**: [GPT/Codex ハーネス癖の実験観測](/tech/gpt-codex-quirk-findings.md) — Web調査で仮説10個→codex exec で5実験×3ラン実測。AGENTS.md 遵守は最小条件でほぼ完璧・衝突時は確率的(2/3)・存在しない前提には拡大解釈して実行し開示、が主要発見。実験場は ~/workspace/gpt-quirk-lab/。
* **Creation**: [eval 入門 — 理論の壁は幻想、すでに1個持っている](/tech/evals-for-practitioners.md) — 「eval は理論が難しい」相談。操作的定義（凍結入力×述語×N回×率）、判定器3種、採集原則、ハーネス層別検証（hook=テスト/skill=発火率・遵守率/文書層=生存率）を記録。gpt56-eval が既に eval 実体であることを指摘。
* **Update**: [プロンプト力の階段](/tech/prompting-mastery-ladder.md) — 日常の小技7選を追記（資料先・質問後 / 読み手指定 / 下書き添削 / 数の強制 / 不採用理由 / 文体の伝染 / 粗探し依頼）。全て「証拠」原理からの導出。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — D シリーズ（AGENTS.md 遵守・指示階層の計測）を追加。system ロール配置・grep 可能な規約・引力3段階（なし/暗黙/明示）の設計と、結果を文書層/hook層の配分判断に使う位置づけを追記。
* **Update**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — Phase 0 を実装。凍結タスクセット7本+検証データ+ランナーを ~/workspace/gpt56-eval/ に構築（A2/B1 の期待値は実測検証済み）。
* **Creation**: [モデル移行観測フロー](/tech/model-migration-observation-flow.md) — GPT-5.6 リリースを題材に、差分観測とプロンプト適応の5フェーズを Playbook 化。凍結タスクセット(代表+過去失敗+トラップ)、無変更転送テスト、モデル癖と自分バグの分離、2層蒸留。
* **Update**: [プロンプト力の階段](/tech/prompting-mastery-ladder.md) — 改善フロー v2（保全→無変更再現→尋問→分岐処方→1変数→記録）と「進歩が感じられないのは構造的に正常」の機構、進歩=失敗クラスの移動という操作的定義、月次リプレイを追記。
* **Update**: [プロンプト力の階段](/tech/prompting-mastery-ladder.md) — 続編相談で機構編を追記。原理「プロンプトは命令ではなく証拠」から6技法（否定形・例・削除テスト・自由度の明示・逃げ道・矛盾は毒）を導出、診断3分岐（知らない/わかってない/逸れた）、予測ゲーム訓練。
* **Creation**: [プロンプト力の階段](/tech/prompting-mastery-ladder.md) — 「何段階も上のプロンプトを打ちたい」相談。上達=レイヤー移動（Lv0命令〜Lv5消去）の6段階、成功述語と停止条件、降りの外注、委譲成功率という操作的定義と失敗5クラスを記録。

* **Update**: [AI文脈での「蒸留」とは何か](/tech/what-is-distillation-in-ai.md) — 「要約と蒸留の違い」を追記。要約=長さに最適化した圧縮、蒸留=次の利用に最適化した変換。蒸留は出力の構造ごと変わる。
* **Creation**: [AI文脈での「蒸留」とは何か](/tech/what-is-distillation-in-ai.md) — 用語質問への回答を記録。知識蒸留（Hinton 2015、教師→生徒のモデル圧縮）と比喩的用法（本質の抽出）の2義と読み分け。

* **Update**: [システム問い合わせ対応の構造化テンプレート](/tech/system-inquiry-structuring.md) — 実行環境が Dify と判明。エージェント不要でワークフロー+ナレッジが正解という整理、バッチ実行での一致率測定、データ先行の原則を追記。
* **Update**: [「不確実性への向き合い方」の操作的分解](/thinking/uncertainty-reduction-as-operations.md) — 「何に対して実践すれば」への回答を追記。対象リストでなく発火条件（開いた質問を打った瞬間を検知）を置く方式と、具体候補3つ（承認LLM確認・問い合わせ返信・方針相談）、過去ログ発掘の保険。
* **Update**: [「不確実性への向き合い方」の操作的分解](/thinking/uncertainty-reduction-as-operations.md) — 本人が「仮説提示型の質問」の実地試行を決定。4部品の型・失敗モード3つ・観測指標（即答率・往復回数）を追記。結果待ち。
* **Update**: [「不確実性への向き合い方」の操作的分解](/thinking/uncertainty-reduction-as-operations.md) — 続編相談で追加の処方箋5つ（可逆性トリアージ・情報を買う会計・仮説提示型質問・予測日誌・確信度付き仮説とC7の和解）を追記。
* **Creation**: [「不確実性への向き合い方」の操作的分解](/thinking/uncertainty-reduction-as-operations.md) — 「曖昧さ削減が身につかない」相談。不確実性の源は未来と他人の2つ、曖昧さ=未決定の決定の集合という操作的定義と、「曖昧→決定リスト」変換の処方箋を記録。
* **Update**: [システム問い合わせ対応の構造化テンプレート](/tech/system-inquiry-structuring.md) — PC分離環境での進め方(データを動かさず道具を動かす・持ち出しキット3点・会社承認LLM確認のマイルストーン化)を追記。
* **Update**: [思考の癖の研究](/self/cognitive-profile.md) — F15人間版仮説を交絡（速度優先の教示）により格下げ。追補「昇りは反射・降りは労働」の非対称性とAI相補性仮説（LLM=具体化エンジンが欠けた半身だった）、具体化の処方箋3つを追記。
* **Update**: [思考の癖の研究](/self/cognitive-profile.md) — 本人の訂正（列挙課題を「全項目共通の1答」と解釈していた）を反映。「退屈で飛ばした」仮説を撤回し、圧縮本能（全部を貫く1つを探すのがデフォルト認知）を最重要発見として追加。
* **Update**: [思考の癖の研究](/self/cognitive-profile.md) — 投影法編を追加。中心仮説「カメラ位置の人」（空想内でも作者・観客に立つ）、恐れ=システムの誤判定、英雄像=異変に気づく内部者、「本当の私はこの時代にいない」。

## 2026-07-06

* **Creation**: [理論に強くなる方法 — 4点セットと3つの練習](/thinking/theory-fluency-training.md) — 理論の強さの正体と鍛え方3練習、スターター理論5選を Playbook として記録。
* **Update**: [セマンティックレイヤー・オントロジー・dbt](/tech/semantic-layer-ontology-dbt.md) — 現場診断（変換=ストアド・DWH=レイクの写し）と処方箋を追記。「写しは dbt 化が治療になる症状」という転換と KPI 1本の縦切りパイロット手順。
* **Update**: [システム問い合わせ対応の構造化テンプレート](/tech/system-inquiry-structuring.md) — チャットベース(チケットレス)運用の修正点(1件=1スレッド定義・シート1行運用・3点テンプレ・ボット組み込みの利点)を追記。
* **Update**: [アジャイル/リーン概念のAI時代マッピング集](/tech/lean-agile-concepts-ai-mapping.md) — ペアプロ・実例仕様・ミッションコマンド・認知負荷・バス係数の5概念を追記(計16概念)。
* **Creation**: [自分を研究する方法カタログ](/self/self-research-methods.md) — 質問以外の自己研究法7系統（痕跡分析・他者報告・実験・投影法・ESM・測定ゲーム・言語分析）を Playbook として記録。
* **Update**: [アジャイル/リーン概念のAI時代マッピング集](/tech/lean-agile-concepts-ai-mapping.md) — 小バッチ・フロー効率・DoR・ウォーキングスケルトン・心理的安全性・理解負債の6概念と第2の変換規則を追記(計11概念)。
* **Update**: [セマンティックレイヤー・オントロジー・dbt](/tech/semantic-layer-ontology-dbt.md) — 現場構成（レイク/DWH/マート）への具体マッピングを追記。dbt は層間の矢印・オントロジーは DWH モデルの注釈化、現場見立ての2質問。
* **Creation**: [セマンティックレイヤー・オントロジー・dbt](/tech/semantic-layer-ontology-dbt.md) — 三層基盤×AI活用での3つの道具の位置づけ（text-to-SQLの推測を潰す装置という整理）と導入の定石を Consultation として記録。
* **Creation**: [システム問い合わせ対応の構造化テンプレート](/tech/system-inquiry-structuring.md) — 適性評価と問い合わせ版7点セット雛形、実況メモ5項目、段階導入ロードマップを Playbook として記録。
* **Creation**: [アジャイル/リーン概念のAI時代マッピング集](/tech/lean-agile-concepts-ai-mapping.md) — TDD・アンドン・YAGNI・スパイク・コンウェイの5概念の読み替えを Reference として記録。
* **Update**: [思考の癖の研究](/self/cognitive-profile.md) — インタビュー3ラウンドの結果を追記。仮説2件の反証と中心発見（体系化はAI以後の外骨格・ハーネス哲学は自己認識の投影・感情の消化器官は書くこと）。
* **Creation**: [思考の癖の研究](/self/cognitive-profile.md) — 相談記録・失敗カタログから抽出した思考パターン6つと影・予測を Profile として記録。self/ ディレクトリを新設。
* **Update**: [自作要件定義 skill の評価](/tech/requirements-skill-review.md) — fifth 版を実装・テストした結果（述語ゲートの有効性、矛盾入力の扱い、テンプレ圧縮効果）を追記。
* **Creation**: [LLM組み込みに向けた業務の構造化](/tech/business-process-structuring-for-llm.md) — 引き継ぎテスト6条件とアーティファクト7点セット、失敗観測駆動の進め方を Playbook として記録。
* **Creation**: [カンバンとWIP制限をAIエージェント運用に当てはめる具体策](/tech/kanban-wip-for-ai-agents.md) — レーン設計と「レビュー待ちにWIP 2〜3」の運用ルールを Consultation として記録。
* **Update**: [「作ってもらっただけ」問題の学び方](/tech/learning-without-building.md) — 予測クイズ→単体実行→答え合わせの3ステップ演習が有効だったことを Examples に追記。
* **Creation**: [「なんちゃってアジャイル」のシステム思考分析](/thinking/fake-agile-systems-analysis.md) — 因果ループ図による構造の可視化と介入点の分析を Consultation として記録。
* **Creation**: [AI活用における「構造化」とは何か](/tech/what-is-structuring-in-ai.md) — 構造化の定義と4つの場面(データ・入力・出力・知識/プロセス)を Consultation として記録。
* **Creation**: [アジャイル・スクラム入門とAI時代適合性の検討](/tech/agile-scrum-in-ai-era.md) — 基本整理と「思想は残り儀式は再設計される」という見立てを Consultation として記録。
* **Creation**: [システム思考の基礎](/thinking/systems-thinking.md) — 中核概念と実践のコツを Reference として記録。thinking/ ディレクトリを新設。
* **Creation**: [自作要件定義 skill の評価](/tech/requirements-skill-review.md) — requirements-skills/forth の評価結論（強み・改善点・ハーネス化案）を記録。
* **Creation**: [「作ってもらっただけ」問題の学び方](/tech/learning-without-building.md) — 作らずに理解する4つの練習動作を Playbook として記録。
* **Creation**: [このPCのエージェント資産マップ](/tech/my-agent-assets-map.md) — ~/.claude と workspace の棚卸し結果を Reference として記録。
* **Creation**: [AIエージェント使いこなしのエッセンス — Fable からの申し送り](/tech/ai-agent-mastery-essence.md) — モデル非依存の活用7原則を申し送り Playbook として記録。
* **Creation**: [LLM に Markdown→HTML 変換させるとデザインがいまいち問題への対策](/tech/llm-md-to-html-design.md) — MD→HTML 変換のデザイン安定化 Playbook を記録。
* **Update**: [skill を作ってもハーネス感がない問題](/tech/skill-to-harness-enforcement.md) — knowledge 記録強制の Stop hook を実装し、設計要点を追記。
* **Creation**: [skill を作ってもハーネス感がない問題](/tech/skill-to-harness-enforcement.md) — 強制点の設計に関する相談の結論を記録。
* **Creation**: [superpowers プラグイン解剖](/tech/superpowers-plugin-anatomy.md) — 公開ハーネス実例の読み解きメモを追加。
* **Creation**: [AIエージェントの「ハーネス」とは何か](/tech/ai-agent-harness-basics.md) — ハーネス相談の結論を記録。tech/ ディレクトリを新設。
* **Creation**: Knowledge バンドルを初期化（OKF v0.1）。
