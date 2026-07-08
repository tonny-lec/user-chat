# Directory Update Log

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
