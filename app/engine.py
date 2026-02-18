"""
Oracle Engine - Business Strategy Engine
完全日本語版
"""
from datetime import datetime, timezone
from typing import List, Dict, Tuple
from app.schemas import (
    MBTIType, ArchetypeType, DeviceType,
    RoadmapStep, PsychometricQuestion, PsychometricResponse,
    DiagnosisResult, AutomationTeaser, TrendData
)
from app.tools import TrendSearchEngine, calculate_trend_relevance


class OracleEngine:
    """Core diagnosis engine"""
    
    MBTI_TO_ARCHETYPE = {
        MBTIType.INTJ: ArchetypeType.ARCHITECT,
        MBTIType.INTP: ArchetypeType.ARCHITECT,
        MBTIType.ENTJ: ArchetypeType.COMMANDER,
        MBTIType.ESTJ: ArchetypeType.COMMANDER,
        MBTIType.ENTP: ArchetypeType.HACKER,
        MBTIType.ESTP: ArchetypeType.HACKER,
        MBTIType.INFJ: ArchetypeType.VISIONARY,
        MBTIType.ENFJ: ArchetypeType.VISIONARY,
        MBTIType.INFP: ArchetypeType.CREATOR,
        MBTIType.ENFP: ArchetypeType.CREATOR,
        MBTIType.ISTJ: ArchetypeType.GUARDIAN,
        MBTIType.ISFJ: ArchetypeType.GUARDIAN,
        MBTIType.ESFP: ArchetypeType.PERFORMER,
        MBTIType.ESFJ: ArchetypeType.PERFORMER,
        MBTIType.ISTP: ArchetypeType.CRAFTSMAN,
        MBTIType.ISFP: ArchetypeType.CRAFTSMAN,
    }
    
    TRIBE_ANALYSTS = [MBTIType.INTJ, MBTIType.INTP, MBTIType.ENTJ, MBTIType.ENTP]
    TRIBE_DIPLOMATS = [MBTIType.INFJ, MBTIType.INFP, MBTIType.ENFJ, MBTIType.ENFP]
    TRIBE_SENTINELS = [MBTIType.ISTJ, MBTIType.ISFJ, MBTIType.ESTJ, MBTIType.ESFJ]
    TRIBE_EXPLORERS = [MBTIType.ISTP, MBTIType.ISFP, MBTIType.ESTP, MBTIType.ESFP]
    
    def __init__(self):
        self.search_engine = TrendSearchEngine()
    
    def get_tribe_group(self, mbti: MBTIType) -> str:
        if mbti in self.TRIBE_ANALYSTS:
            return "ANALYSTS"
        elif mbti in self.TRIBE_DIPLOMATS:
            return "DIPLOMATS"
        elif mbti in self.TRIBE_SENTINELS:
            return "SENTINELS"
        elif mbti in self.TRIBE_EXPLORERS:
            return "EXPLORERS"
        return "ANALYSTS"
    
    def get_archetype(self, mbti: MBTIType) -> ArchetypeType:
        return self.MBTI_TO_ARCHETYPE[mbti]
    
    def get_psychometric_questions(self, mbti: MBTIType) -> List[PsychometricQuestion]:
        """5つのビジネス特性診断質問を生成"""
        questions = [
            PsychometricQuestion(
                id=1,
                text="新しいビジネスアイデアを実行する際、まず何を重視しますか？",
                scale_low="慎重な計画と準備",
                scale_high="即座の行動と実験"
            ),
            PsychometricQuestion(
                id=2,
                text="ビジネスにおいて、あなたはどちらのタイプですか？",
                scale_low="一人で集中して作業",
                scale_high="チームで協力"
            ),
            PsychometricQuestion(
                id=3,
                text="収益化において、どちらを優先しますか？",
                scale_low="安定した継続収入",
                scale_high="大きなリターン"
            ),
            PsychometricQuestion(
                id=4,
                text="新しいツールや技術に対してどう感じますか？",
                scale_low="慎重に検討してから導入",
                scale_high="すぐに試してみる"
            ),
            PsychometricQuestion(
                id=5,
                text="ビジネスの成功をどう測りますか？",
                scale_low="明確な数値目標の達成",
                scale_high="自己実現と影響力"
            ),
        ]
        return questions

    def analyze_psychometric(self, responses: List[PsychometricResponse]) -> Dict:
        """5問の回答を3つの軸に集約して心理プロファイルを生成"""
        scores = {r.question_id: r.score for r in responses}

        # 行動スタイル: Q1(計画vs行動) + Q4(慎重vs即試す)
        action_avg = (scores.get(1, 3) + scores.get(4, 3)) / 2
        if action_avg >= 3.5:
            action_style = "aggressive"
        elif action_avg <= 2.5:
            action_style = "cautious"
        else:
            action_style = "balanced"

        # ワークスタイル: Q2(個人vsチーム)
        work_score = scores.get(2, 3)
        if work_score >= 4:
            work_style = "team"
        elif work_score <= 2:
            work_style = "solo"
        else:
            work_style = "flexible"

        # 収益志向: Q3(安定vs高リスク) + Q5(数値vs自己実現)
        revenue_avg = (scores.get(3, 3) + scores.get(5, 3)) / 2
        if revenue_avg >= 3.5:
            revenue_style = "ambitious"
        elif revenue_avg <= 2.5:
            revenue_style = "stable"
        else:
            revenue_style = "balanced"

        return {
            "action_style": action_style,
            "work_style": work_style,
            "revenue_style": revenue_style,
            "scores": scores,
        }

    def generate_psychometric_insight(self, profile: Dict) -> str:
        """心理プロファイルから詳細なインサイトテキストを生成"""
        action = profile["action_style"]
        work = profile["work_style"]
        revenue = profile["revenue_style"]

        action_map = {
            "aggressive": (
                "攻撃型",
                "即座に実行へ移行する行動特性を持つ。MVP（最小限の実行可能プロダクト）を素早く市場投入し、フィードバックループで改善する戦略が最適。先行者利益の獲得に優位性がある。"
            ),
            "balanced": (
                "バランス型",
                "計画と実行のバランスが取れた特性。状況に応じて慎重にも大胆にもなれる柔軟性が最大の資本。適応型戦略で環境変化に強い。"
            ),
            "cautious": (
                "分析型",
                "綿密な計画を立ててから実行に移行する特性。リサーチと準備の徹底でリスクを最小化する。準備が整った段階で一気に展開する戦略が有効。"
            ),
        }

        work_map = {
            "team": (
                "チーム型",
                "チームでの協働により力を最大化する特性。早期段階からパートナーや外注を活用し、スケーラブルな体制を構築する。分業による効率化が成功の鍵。"
            ),
            "flexible": (
                "柔軟型",
                "状況に応じてソロとチームを使い分ける柔軟性がある。初期はソロで検証し、軌道に乗った段階でチーム化する段階的拡大が最適。"
            ),
            "solo": (
                "独立型",
                "集中した個人作業で高い成果を出す特性。自動化ツールを最大限活用し、一人で高収益を生む仕組みを構築する戦略が最適。"
            ),
        }

        revenue_map = {
            "ambitious": (
                "高収益志向",
                "大きなリターンを追求する意欲がある。高単価戦略やスケーラブルなビジネスモデルとの親和性が高い。リスクテイクの見返りとして高い収益ポテンシャルを持つ。"
            ),
            "balanced": (
                "バランス型",
                "安定と成長のバランスを重視する特性。基盤を固めつつ、機会を捉えて攻勢に転じる段階的成長戦略が最適。"
            ),
            "stable": (
                "安定型",
                "予測可能な収益を重視する堅実な特性。サブスクリプション型や継続案件を中心に、安定したキャッシュフロー基盤を構築する戦略が有効。"
            ),
        }

        a_label, a_desc = action_map[action]
        w_label, w_desc = work_map[work]
        r_label, r_desc = revenue_map[revenue]

        return (
            f"ポテンシャル特性分析:\n\n"
            f"【行動スタイル: {a_label}】\n{a_desc}\n\n"
            f"【ワークスタイル: {w_label}】\n{w_desc}\n\n"
            f"【収益志向: {r_label}】\n{r_desc}"
        )

    def customize_roadmap(
        self, roadmap: List[RoadmapStep], profile: Dict
    ) -> List[RoadmapStep]:
        """心理プロファイルに基づいてロードマップの各フェーズをカスタマイズ"""
        action = profile["action_style"]
        work = profile["work_style"]
        revenue = profile["revenue_style"]

        customized = []
        for i, step in enumerate(roadmap):
            desc_additions: List[str] = []
            extra_tools: List[str] = []
            prepend_steps: List[str] = []
            append_steps: List[str] = []
            outcome_addition = ""

            is_early = (i == 0)
            is_mid = (i == 1)
            is_late = (i >= 2)

            # ── 行動スタイル ──
            if action == "aggressive":
                if is_early:
                    desc_additions.append(
                        "速度優先戦略: 最小限の準備で即座に市場投入し、実行しながら改善するアプローチを推奨。"
                    )
                    append_steps.append(
                        "【即時実行】初日で出品完了を目標に設定。MVPを市場に投入しフィードバックを取得 → 改善は実行と並行して進める"
                    )
                elif is_mid:
                    desc_additions.append(
                        "速度維持戦略: 複数チャネルへの同時展開で先行者利益を確保する。"
                    )
                    append_steps.append(
                        "【高速展開】成功パターンを3プラットフォーム以上に横展開 → ココナラ+クラウドワークス+ランサーズを同時運用"
                    )
                else:
                    desc_additions.append(
                        "攻勢戦略: 一気にスケールし、競合が追随できない速度で市場ポジションを確立する。"
                    )
                    append_steps.append(
                        "【先行者利益】新規AIツールのリリースと同時にサービス化 → 市場成熟前にポジションを確立"
                    )
            elif action == "cautious":
                if is_early:
                    desc_additions.append(
                        "分析先行戦略: リサーチと準備を徹底し、確実性の高い状態で市場参入する。"
                    )
                    prepend_steps.append(
                        "【事前分析】競合サービスを最低10件リサーチ → 価格帯・レビュー・差別化ポイントをスプレッドシートに整理してから出品"
                    )
                    extra_tools.append("Googleスプレッドシート（競合分析用）")
                elif is_mid:
                    desc_additions.append(
                        "品質優先戦略: 一つのチャネルで確実に成果を出してから次へ展開。品質と信頼を最優先にする。"
                    )
                    append_steps.append(
                        "【品質管理】納品前の3段階チェックリスト作成 → (1)AI生成 (2)内容確認 (3)フォーマット整形 → 品質を武器にリピート率80%を目指す"
                    )
                else:
                    desc_additions.append(
                        "堅実拡大戦略: 着実に積み上げた信頼と実績を基盤に、リスクを抑えながら確実にスケールする。"
                    )
                    append_steps.append(
                        "【リスク分散】収入源を3つ以上に分散 → 1つが不調でも他でカバーできるポートフォリオ設計"
                    )

            # ── ワークスタイル ──
            if work == "team":
                if is_early:
                    desc_additions.append(
                        "チーム構築戦略: 早期段階からパートナーや外注を活用し、コア業務に集中する。"
                    )
                    append_steps.append(
                        "【チーム構築】ココナラ/クラウドワークスで外注パートナーを2〜3人テスト採用 → 小規模案件で品質とスピードを検証"
                    )
                    extra_tools.extend(["Chatwork", "Googleドライブ（共有用）"])
                elif is_mid:
                    append_steps.append(
                        "【分業体制】作業を「企画→制作→チェック→納品」に分解 → 制作は外注チーム、自身はクライアント対応と品質管理に特化"
                    )
                else:
                    append_steps.append(
                        "【組織化】チームを5名体制に拡大 → マニュアルとテンプレートで品質を標準化 → 経営と営業に専念する体制を構築"
                    )
                    extra_tools.append("Notion（チームWiki）")
            elif work == "solo":
                if is_early:
                    desc_additions.append(
                        "独立運用戦略: 全工程を一人で完結する仕組みを設計。自動化ツールを最大の資本とする。"
                    )
                    append_steps.append(
                        "【自動化設計】受注→作業→納品の全工程でテンプレートを準備 → 1件あたりの手作業を最小化"
                    )
                elif is_mid:
                    append_steps.append(
                        "【仕組み化】Notion + Zapierで受注通知→作業テンプレート自動展開→納品リマインダーの一気通貫フローを構築"
                    )
                    extra_tools.append("Zapier")
                else:
                    append_steps.append(
                        "【完全自動化】AI + 自動化ツールで全工程を無人化 → 一人で月次収益100万円を運用するシステムを完成"
                    )

            # ── 収益志向 ──
            if revenue == "ambitious":
                if is_early:
                    desc_additions.append(
                        "高単価戦略: 初期段階から価値ベースの価格設定で参入。品質重視の顧客層を獲得する。"
                    )
                    append_steps.append(
                        "【高単価戦略】1万円以上で出品 → サービス説明に価値の根拠を明記 → 品質重視の顧客を獲得"
                    )
                elif is_mid:
                    append_steps.append(
                        "【収益最大化】3段階価格設計 → ライト(5,000円)/スタンダード(15,000円)/プレミアム(30,000円) → プレミアムを主力に育成"
                    )
                else:
                    outcome_addition = "高単価×スケールで月次収益100万円超の達成。"
                    append_steps.append(
                        "【スケール戦略】法人向けパッケージ（月額10万円〜）を開発 → 個人から法人へクライアント単価を10倍に引き上げ"
                    )
            elif revenue == "stable":
                if is_early:
                    desc_additions.append(
                        "堅実参入戦略: 確実な初期収益を確保し、信頼資産を積み上げることに集中する。"
                    )
                    append_steps.append(
                        "【堅実スタート】相場より少し安めの価格で出品 → まず実績10件とレビュー高評価を最優先で獲得 → 信頼資産を構築"
                    )
                elif is_mid:
                    append_steps.append(
                        "【継続収入】月額制サービスを設計 → 単発の波動を排除し毎月安定したキャッシュフローを確保"
                    )
                    extra_tools.append("Stripe（サブスク決済）")
                else:
                    outcome_addition = "予測可能な継続収入基盤を確立。安定したキャッシュフローによる持続的経営。"
                    append_steps.append(
                        "【安定基盤】継続クライアント数を毎月純増 → 解約率を5%以下に抑える仕組み（定期フォロー/改善提案）を構築"
                    )

            # --- 組み立て ---
            new_desc = step.description
            if desc_additions:
                new_desc += "\n\n" + " ".join(desc_additions)

            new_tools = list(step.tools)
            for t in extra_tools:
                if t not in new_tools:
                    new_tools.append(t)

            new_steps = prepend_steps + list(step.detailed_steps) + append_steps

            new_outcome = step.expected_outcome
            if outcome_addition:
                new_outcome += " " + outcome_addition

            # プロンプトに心理プロファイルの補足を追加
            new_prompt = step.ai_prompt
            if new_prompt:
                prompt_extras = []
                if action == "aggressive":
                    prompt_extras.append("- 速度重視の実行スタイルです。最短ルートを提示してください")
                elif action == "cautious":
                    prompt_extras.append("- 分析重視のスタイルです。リスク最小化の方法も含めてください")
                if work == "team":
                    prompt_extras.append("- チームや外注を活用する方針です。分業設計も含めてください")
                elif work == "solo":
                    prompt_extras.append("- 独立運用の方針です。自動化の方法を優先してください")
                if revenue == "ambitious":
                    prompt_extras.append("- 高単価・高収益を志向しています")
                elif revenue == "stable":
                    prompt_extras.append("- 安定した継続収入を重視しています")
                if prompt_extras:
                    new_prompt += "\n" + "\n".join(prompt_extras)

            customized.append(RoadmapStep(
                phase=step.phase,
                title=step.title,
                description=new_desc,
                tools=new_tools,
                expected_outcome=new_outcome,
                detailed_steps=new_steps,
                ai_prompt=new_prompt,
            ))

        return customized

    def get_archetype_profile(self, archetype: ArchetypeType) -> Tuple[str, List[str], List[str]]:
        """アーキタイプの説明、強み、弱みを取得"""
        profiles = {
            ArchetypeType.ARCHITECT: (
                "システム思考と自動化のエキスパート",
                ["論理的思考力と問題解決能力", "システム設計と自動化の追求", "効率化への強いこだわり", "長期的視点での戦略立案", "技術的な深い理解"],
                ["マーケティングや営業への苦手意識", "完璧主義による行動の遅延", "人間関係構築の軽視", "感情よりも論理重視", "柔軟性の欠如"]
            ),
            ArchetypeType.COMMANDER: (
                "統率力とビジョンを持つリーダー",
                ["強力な統率力と決断力", "明確なビジョンの提示", "効率的な組織運営", "目標達成への執念", "戦略的思考"],
                ["他者の意見を聞かない傾向", "感情的配慮の不足", "柔軟性の欠如", "細部への注意散漫"],
            ),
            ArchetypeType.HACKER: (
                "破壊的イノベーションと成長ハック",
                ["創造的な問題解決能力", "迅速な実行力と行動力", "トレンド察知と先読み", "リスクを取る勇気", "新しい手法の開拓"],
                ["一貫性の欠如と飽きやすさ", "計画性の不足", "細部の見落とし", "長期的コミットメントの困難"],
            ),
            ArchetypeType.VISIONARY: (
                "理想と共感を形にする先導者",
                ["深い共感力と洞察力", "理想を語る情熱", "人を動かす影響力", "長期的ビジョンの構築"],
                ["現実的な実行力の不足", "理想と現実のギャップ", "批判への過敏さ"],
            ),
            ArchetypeType.CREATOR: (
                "独自性と表現を追求する芸術家",
                ["独創的なアイデア創出", "感性豊かな表現力", "オリジナリティの追求", "美的センス"],
                ["ビジネス的視点の欠如", "継続性の困難", "マネタイズへの抵抗感"],
            ),
            ArchetypeType.GUARDIAN: (
                "安定と信頼を守る管理者",
                ["責任感の強さ", "計画的な実行力", "リスク管理能力", "継続性と忍耐力"],
                ["変化への抵抗", "革新性の不足", "柔軟性の欠如"],
            ),
            ArchetypeType.PERFORMER: (
                "人を魅了するエンターテイナー",
                ["人を引きつける魅力", "コミュニケーション能力", "柔軟な対応力", "ポジティブな雰囲気"],
                ["計画性の不足", "深い専門性の欠如", "継続力の弱さ"],
            ),
            ArchetypeType.CRAFTSMAN: (
                "実践と技術を極める職人",
                ["実践的なスキル", "技術的な深さ", "現実的な問題解決", "手を動かす実行力"],
                ["マーケティングの苦手", "抽象的思考の困難", "ビジネス拡大への消極性"],
            ),
        }
        return profiles.get(archetype, ("ビジネスプロフェッショナル", ["適応力"], ["要改善"]))
    
    def _prompt(self, role: str, situation: str, asks: List[str], mbti_str: str) -> str:
        """AIプロンプトを組み立てるヘルパー"""
        ask_lines = "\n".join(f"{i+1}. {a}" for i, a in enumerate(asks))
        return (
            f"あなたは{role}です。\n"
            f"私のMBTIは{mbti_str}です。{situation}\n\n"
            f"重要な前提：\n"
            f"- 効率的な実行手順を、具体的なアクションレベルで示してください\n"
            f"- 「何を」「どこで」「どうやって」を1ステップずつ明示してください\n"
            f"- 各ステップは具体的な操作手順レベルで記述してください\n\n"
            f"以下について教えてください：\n{ask_lines}\n\n"
            f"条件：\n"
            f"- そのまま使えるテンプレートを必ず含めてください\n"
            f"- 最小のリソースで最大価値を抽出する方法を優先してください\n"
            f"- 各ステップに明確な完了基準を設定してください"
        )

    def generate_roadmap(
        self,
        archetype: ArchetypeType,
        device: DeviceType,
        trends: List[Dict[str, str]],
        mbti: MBTIType
    ) -> List[RoadmapStep]:
        """デバイス最適化された3ヶ月ロードマップを生成"""
        is_pc = device in [DeviceType.PC_MAC, DeviceType.PC_WINDOWS]
        tribe = self.get_tribe_group(mbti)
        mbti_str = mbti.value

        # =============================================
        # ANALYSTS（INTJ, INTP, ENTJ, ENTP）
        # 論理的思考・システム設計・データ分析が強み
        # =============================================
        if tribe == "ANALYSTS" and is_pc:
            return [
                RoadmapStep(
                    phase=f"覚醒フェーズ（1〜2週目）【{mbti_str}】",
                    title="ChatGPT（無料版）で初期AIサービスを構築し、月次収益5万円の基盤を確立する",
                    description="論理的思考力を活用し、ChatGPT（無料版）によるAIコンテンツ生成サービスを設計。ココナラで市場投入し、初期の実績基盤を構築する。",
                    tools=["ChatGPT（無料版）", "VS Code", "ココナラ"],
                    expected_outcome="目標: 初月でレビュー5件獲得。実績を構築し価格改定の基盤を確立。",
                    detailed_steps=[
                        "chat.openai.comにアクセス → Googleアカウントで無料登録 → ChatGPTの操作環境を構築",
                        "ChatGPTへの指示出し（キャッチコピー生成/ブログ記事作成等）を実施 → プロンプト設計のパターンを習得",
                        "VS Codeをインストール → ChatGPTで生成したコンテンツを整形 → 納品用ファイルのフォーマットを標準化",
                        "ココナラで出品: タイトル『AIで100個のコンテンツを一括生成します』→ 1,500円で出品 → 納期1日 → レビュー高評価5件の獲得を最優先",
                        "受注後はChatGPTでコンテンツ生成 → Excelに整形 → 納品。1件あたり作業時間30分の効率運用を確立",
                        "レビュー5件獲得後 → 5,000円に価格改定 → 20件超で10,000円に → 実績蓄積に比例した段階的値上げ",
                        "効率化オプション: ChatGPT Plus（月額約3,400円）の導入で処理速度と品質が向上"
                    ],
                    ai_prompt=self._prompt("AI事業戦略アドバイザー", "ChatGPT（無料版）を使って、ココナラで「AIコンテンツ生成サービス」を1,500円で出品し、レビュー高評価5件を獲得したいです。", ["ココナラの出品タイトルと説明文を実用レベルで作成してください。1,500円でも価値が伝わる内容に", "ChatGPT（無料版）に送るプロンプトのテンプレートを3種類作成してください（キャッチコピー/ブログ記事/商品説明）", "最初の受注を獲得するためのアクションを、今日/明日/1週間以内で分類して提示してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"加速フェーズ（3〜6週目）【{mbti_str}】",
                    title="データ駆動型分析で需要を可視化し、月次収益30万円のSaaS基盤を構築する",
                    description="Google Trendsで高需要キーワードを特定し、専用自動化ツールをSaaSとして構築。月額課金モデルで継続収益を確立する。",
                    tools=["Google Trends", "Streamlit", "Stripe"],
                    expected_outcome="目標: 月次収益30〜50万円の達成。データ駆動型の効率的収益構造を確立。",
                    detailed_steps=[
                        "trends.google.comで需要の高いキーワードを調査 → 上昇トレンドのキーワードをExcelに記録・分析",
                        "需要1位のテーマで専用ツールを作成 → Streamlit（Python製Webフレームワーク）でWebアプリ化",
                        "stripe.comでアカウント作成 → 商品「月額2,980円」を設定 → APIキーを取得しアプリに統合",
                        "Streamlit Community Cloud（無料）でデプロイ → 専用URLを発行し自動課金の仕組みを構築",
                        "月間100契約で 2,980円 x 100 = 298,000円の自動継続収入を達成"
                    ],
                    ai_prompt=self._prompt("SaaS事業戦略アドバイザー", "ココナラでレビュー5件獲得し価格改定も完了しました。次はStreamlitで月額課金のWebアプリを構築したいです。", ["Streamlit + ChatGPT APIでWebアプリを構築する手順を環境構築から段階的に提示してください", "月額2,980円で需要のあるAIツールのアイデアを5つ、想定ユーザーと共に提示してください", "Streamlit Community Cloud（無料）へのデプロイ手順を具体的な操作レベルで提示してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"支配フェーズ（7〜12週目）【{mbti_str}】",
                    title="マルチAIエージェントシステムで月次収益100万円の自動化基盤を構築する",
                    description="複数のAI APIを統合したエージェントシステムを構築。案件獲得→制作→納品の全工程を自動化し、スケーラブルな収益基盤を確立する。",
                    tools=["LangChain 1.2", "Manus AI", "Claude API（Sonnet 4.5: $3/$15 per 1M tokens）", "GitHub Actions", "Stripe API"],
                    expected_outcome="目標: 月次収益100万円の達成。AIによる作業時間の最小化。",
                    detailed_steps=[
                        "LangChain 1.2でマルチステップAIエージェントを構築 → 入力テーマから記事・画像・動画台本を一括自動生成",
                        "GitHub Actionsで定時実行スケジュールを設定 → トレンドキーワード自動収集 → コンテンツ自動生成パイプラインを構築",
                        "Stripe Webhookで決済→納品を完全自動化 → 顧客管理もAPI連携で運用コストをゼロに",
                        "BrainやTipsで高単価コンテンツ（9,800円〜29,800円）を販売 → 月間100件で月次収益100万円を達成",
                        "自動化ノウハウをUdemy講座として販売 → 追加の継続収益ストリームを構築"
                    ],
                    ai_prompt=self._prompt("AIエージェント開発アドバイザー", "SaaSで月次収益30万円を達成しています。次はLangChainやManus AIで自動化システムを構築したいです。", ["LangChainで「テーマ入力→記事自動生成→投稿」の自動化パイプラインを構築する手順を提示してください", "GitHub Actionsで毎日自動実行するワークフローの構築方法を提示してください", "Brain/noteで高単価コンテンツ（1〜3万円）の販売ページテンプレートを作成してください"], mbti_str),
                ),
            ]

        if tribe == "ANALYSTS" and not is_pc:
            return [
                RoadmapStep(
                    phase=f"覚醒フェーズ（1〜2週目）【{mbti_str}】",
                    title="モバイル×クラウドAIで月次収益5万円の基盤を構築する",
                    description="分析力を活用し、ChatGPTアプリとNotion連携でクラウド完結の自動化フローを設計。データに基づく戦略で効率的に収益化する。",
                    tools=["ChatGPT（無料版）アプリ", "Notion", "ココナラアプリ", "Googleスプレッドシート"],
                    expected_outcome="目標: 初月でレビュー5件獲得。モバイル完結の収益モデルを実証。",
                    detailed_steps=[
                        "App StoreからChatGPTアプリをダウンロード（無料版） → アカウント作成 → 操作環境を構築",
                        "Notionアプリをインストール → 「事業管理DB」を作成 → テンプレート: 案件名/単価/ステータス/納期",
                        "ChatGPTに「ビジネス文書作成の専門家として振る舞って」と指示 → プロンプトテンプレートを5種類作成しNotionに保存",
                        "ココナラアプリで出品:『AIで企画書・提案書を作成します』→ 1,500円で出品 → 納期2日 → レビュー高評価を最優先で獲得",
                        "受注→ChatGPTで生成→Googleドキュメントで整形→PDF納品。全工程モバイル完結。",
                        "レビュー5件獲得後 → 5,000円に価格改定 → 20件超で8,000円に → 実績蓄積に比例した段階的値上げ",
                        "効率化オプション: ChatGPT Plus（月額約3,400円）の導入で品質・速度が向上"
                    ],
                    ai_prompt=self._prompt("AI事業戦略アドバイザー", "モバイル環境のみです。ChatGPTアプリ（無料版）を使ってココナラで企画書作成サービスを1,500円で出品し、レビュー高評価5件を獲得したいです。", ["ココナラアプリでの出品手順を操作レベルで提示してください。タイトルと説明文も実用レベルで作成", "ChatGPTアプリに送るプロンプトのテンプレートを3種類作成してください（企画書/提案書/報告書）", "モバイルで受注→ChatGPT作成→Googleドキュメント整形→PDF納品する手順を段階的に提示してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"加速フェーズ（3〜6週目）【{mbti_str}】",
                    title="No-Codeツールでサービスを自動化し、月次収益20万円を達成する",
                    description="MakeやZapierでノーコード自動化フローを構築。分析力で最適なワークフローを設計し、手作業を最小化する。",
                    tools=["Make (Integromat)", "Zapier", "Manus AI", "Notion API", "LINE公式"],
                    expected_outcome="目標: 月次収益15〜20万円の達成。自動化による効率最大化。",
                    detailed_steps=[
                        "make.comでアカウント作成 → 無料プラン（月1,000クレジット）で自動化シナリオを作成",
                        "シナリオ: Googleフォーム受付 → ChatGPT API自動処理 → 結果をメール自動送信",
                        "LINE公式アカウントを開設（無料プラン月200通・ライトプラン月5,000円で5,000通）→ 自動応答で24時間受付体制を構築",
                        "ココナラで実績確立後、クラウドワークスにも同サービスを出品 → 2プラットフォームで集客力を倍増",
                        "サービスを3段階に設計: ライト(3,000円)/スタンダード(8,000円)/プレミアム(15,000円)",
                        "月間30件受注の自動フロー完成 → 平均単価7,000円 x 30 = 月次収益21万円を達成"
                    ],
                    ai_prompt=self._prompt("No-Code自動化アドバイザー", "ココナラでレビュー5件獲得しました。MakeやZapierで受注→AI処理→納品を自動化したいです。", ["Make(Integromat)の無料アカウント作成から最初の自動化シナリオ構築までの手順を段階的に提示してください", "LINE公式アカウントの開設手順と、自動応答でサービス受付を24時間化する設定方法を提示してください", "月額制サービス（3,000円/8,000円/15,000円）のサービス設計を具体的に提示してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"支配フェーズ（7〜12週目）【{mbti_str}】",
                    title="クラウドSaaS型サービスで月次収益50万円の継続収入を確立する",
                    description="No-Codeで構築した自動化フローをサブスクリプション型サービスとして展開。モバイル管理のみで月次収益50万円の継続収入を実現する。",
                    tools=["Bubble", "Stripe", "Make", "Manus AI", "ChatGPT API"],
                    expected_outcome="目標: 月次収益50万円の達成。クラウド運用による場所に依存しない収益構造。",
                    detailed_steps=[
                        "Bubble（Starterプラン月$29〜）でWebアプリを構築 → AIコンテンツ生成ツールをSaaS化",
                        "月額制プラン設定: 個人(2,980円)/ビジネス(9,800円) → Stripe決済を連携",
                        "Makeで新規登録→オンボーディング→利用開始を完全自動化",
                        "SNSで無料トライアルを展開 → 月間200人登録 → 有料転換率25%で50人獲得",
                        "50人 x 平均5,000円 = 月25万円 + 既存ココナラ25万円 = 月次収益50万円を達成"
                    ],
                    ai_prompt=self._prompt("No-Code SaaS事業アドバイザー", "No-Codeツールで月次収益20万円を達成しています。BubbleでAIツールをSaaS化したいです。", ["BubbleでAIコンテンツ生成ツールを構築する手順を段階的に提示してください", "月額2,980円と9,800円の2プランで差別化するサービス設計を提示してください", "無料トライアルから有料転換を促進する仕組みを具体的に提示してください"], mbti_str),
                ),
            ]

        # =============================================
        # DIPLOMATS（INFJ, INFP, ENFJ, ENFP）
        # 共感力・ストーリーテリング・人を動かす力が強み
        # =============================================
        if tribe == "DIPLOMATS" and is_pc:
            return [
                RoadmapStep(
                    phase=f"覚醒フェーズ（1〜2週目）【{mbti_str}】",
                    title="共感力×AIで高訴求コンテンツを構築し、月次収益5万円を達成する",
                    description="深い共感力を資本化し、AIと組み合わせて感情に響くコンテンツを設計。顧客の課題に寄り添うサービスで高評価基盤を構築する。",
                    tools=["ChatGPT（無料版）", "Notion", "Canva（無料版）", "ココナラ"],
                    expected_outcome="目標: 初月でレビュー5件獲得。共感力による高評価基盤の構築。",
                    detailed_steps=[
                        "ChatGPT（無料版）にアクセス → 「共感力の高いライターとして、読者の感情に寄り添った文章を書いてください」というシステムプロンプトを設計",
                        "ココナラで出品:『心に響く自己紹介文・プロフィールを作成します』→ 1,000円で出品 → 納期2日 → 丁寧な対応でレビュー高評価を獲得",
                        "Canva（無料版）でプロフィール用のビジュアルテンプレートを5種類作成 → セットで差別化",
                        "Notionに「感情別テンプレートDB」を構築 → 喜び/悲しみ/期待/不安の4パターン x シーン別",
                        "SNSプロフィール添削サービスも追加出品（1,000円）→ レビュー5件獲得後に5,000円→10,000円と段階的に価格改定",
                        "顧客の要望を丁寧にヒアリング → 期待を超える納品で高評価を蓄積 → 実績に比例して単価が向上",
                        "効率化オプション: ChatGPT Plus（月額約3,400円）やCanva Pro（月額1,180円）の導入で生産性が向上"
                    ],
                    ai_prompt=self._prompt("AI事業戦略アドバイザー", "ChatGPT（無料版）とCanva（無料版）を使って、ココナラで自己紹介文作成サービスを1,000円で出品しレビュー高評価5件を獲得したいです。", ["ココナラの出品タイトルと説明文を実用レベルで作成してください。1,000円でも依頼したくなる訴求力のある内容に", "ChatGPT（無料版）で心に響く自己紹介文を作るプロンプトを5パターン作成してください", "購入者から高評価レビューを獲得するための対応プロセスを提示してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"加速フェーズ（3〜6週目）【{mbti_str}】",
                    title="AI×コーチング型コンテンツで月次収益30万円のファンビジネスを構築する",
                    description="ビジョンと影響力を資本化し、AIサポート付きのオンラインコーチングで安定した収益構造を確立する。",
                    tools=["Zoom", "ChatGPT API", "Notion", "Stripe", "LINE公式"],
                    expected_outcome="目標: 月次収益25〜30万円の達成。ファン基盤の好循環を確立。",
                    detailed_steps=[
                        "LINE公式アカウントを開設（無料プラン月200通・ライト月5,000円で5,000通）→ ステップ配信で「AI活用術」7日間無料講座を展開",
                        "ChatGPTで個別相談用のアドバイステンプレートを作成 → カスタマイズして1人30分のZoom相談を提供",
                        "個別コーチング（月額19,800円）を設計 → 週1回30分Zoom + LINEでの質問対応",
                        "Notionで受講生管理DB → 進捗トラッキング → AIで個別アドバイスを自動生成",
                        "無料講座200人集客 → 有料転換率5% = 10人 x 19,800円 = 月198,000円",
                        "ココナラ収益10万円 + コーチング20万円 = 月次収益30万円を達成"
                    ],
                    ai_prompt=self._prompt("オンラインコーチング事業アドバイザー", "ココナラでレビュー5件獲得し価格改定も完了しました。LINE公式とZoomでAI活用コーチング（月額19,800円）を展開したいです。", ["LINE公式アカウントの開設から友だち獲得までの手順を段階的に提示してください", "7日間のステップ配信の内容を1日ずつ具体的に設計してください", "無料講座から有料コーチングへの転換を促進するトークスクリプトを作成してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"支配フェーズ（7〜12週目）【{mbti_str}】",
                    title="オンラインスクール×AIで月次収益80万円の教育事業を確立する",
                    description="ビジョンを体系化したオンライン講座を開設。AI活用で運営を効率化し、影響力と収益を同時に最大化する。",
                    tools=["Udemy", "Teachable", "ChatGPT", "Canva", "OBS Studio"],
                    expected_outcome="目標: 月次収益80万円の達成。教育事業リーダーとしてのポジション確立。",
                    detailed_steps=[
                        "OBS Studioで画面録画環境を構築 → 「AI×事業戦略 完全ロードマップ」全10回の講座を収録",
                        "Udemyで講座を公開（2,400円）→ セール時に大量集客 → 自己集客なら売上の97%が収益（Udemy集客は37%）",
                        "Teachable（Builderプラン月$89〜・取引手数料0%）で上位コース（49,800円）を開設 → Udemy受講者に案内",
                        "卒業生コミュニティ（月額3,980円）をDiscordで運営 → AIボットで24時間サポート体制を構築",
                        "Udemy48万円 + 上位コース月5人25万円 + コミュニティ20人8万円 = 月次収益81万円を達成"
                    ],
                    ai_prompt=self._prompt("オンライン教育事業アドバイザー", "コーチングで月次収益30万円を達成しています。UdemyとTeachableでオンライン講座を構築したいです。", ["Udemyの講座構築手順を段階的に提示してください。アカウント作成→撮影→編集→公開まで", "モバイルで講座動画を撮影・編集する具体的な方法を提示してください", "Udemy受講者を49,800円の上位コースに誘導するメールテンプレートを作成してください"], mbti_str),
                ),
            ]

        if tribe == "DIPLOMATS" and not is_pc:
            return [
                RoadmapStep(
                    phase=f"覚醒フェーズ（1〜2週目）【{mbti_str}】",
                    title="モバイル×共感力で高訴求SNS発信を構築し、月次収益3万円を達成する",
                    description="共感力をSNSで資本化。AIで文章を最適化し、フォロワーに響くコンテンツでアフィリエイト収益を獲得する。",
                    tools=["ChatGPTアプリ", "Instagram", "Canvaアプリ", "A8.net"],
                    expected_outcome="目標: 初月でフォロワー500人獲得。共感力による集客基盤の構築。",
                    detailed_steps=[
                        "Instagramのビジネスアカウントを開設 → プロフィールに「AI×自分らしい生き方」を明記",
                        "ChatGPTアプリで「フォロワーの課題に寄り添う投稿文」を毎日3パターン生成",
                        "Canvaアプリでカルーセル投稿（10枚スライド）のテンプレートを作成 → 毎日1投稿",
                        "A8.netでAIツール系（画像生成AI・ライティングAI等）のアフィリエイト案件に登録 → 投稿内で自然に紹介",
                        "30日連続投稿でフォロワー500人を獲得 → ストーリーでアフィリエイトリンク → 月次収益3万円を達成",
                        "効率化オプション: ChatGPT Plus（月額約3,400円）やCanva Pro（月額1,180円）の導入で生産性が向上"
                    ],
                    ai_prompt=self._prompt("Instagram運用アドバイザー", "モバイルのみでInstagramを使ったAI事業の発信を開始したいです。フォロワー0人からのスタートです。", ["Instagramのビジネスアカウント開設手順とプロフィールの設計を実用レベルで提示してください", "最初の30日間の投稿テーマを1日ずつ具体的に設計してください。ChatGPTアプリに送るプロンプトも含めて", "フォロワー0人から500人まで効率的に増やすための日次アクション（いいね/コメント/ハッシュタグ）を提示してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"加速フェーズ（3〜6週目）【{mbti_str}】",
                    title="LINE×AI相談サービスで月次収益15万円の信頼ビジネスを構築する",
                    description="SNSで獲得したファンをLINE公式に誘導。AIサポート付きの相談サービスで深い信頼関係を構築し収益化する。",
                    tools=["LINE公式", "ChatGPTアプリ", "ココナラアプリ", "PayPay"],
                    expected_outcome="目標: 月次収益12〜15万円の達成。信頼ベースのサービス構築。",
                    detailed_steps=[
                        "LINE公式アカウントを開設（無料プラン月200通・ライト月5,000円で5,000通）→ Instagramのプロフィールにリンク → 友だち登録特典「AI活用チェックリスト」を配布",
                        "ChatGPTで課題別の回答テンプレートを20種類作成 → 即時返信体制を構築",
                        "ココナラで『AIを活用したキャリア相談30分』を出品（8,000円）→ モバイルZoomで対応",
                        "LINE友だち300人 → 相談サービス月15件 x 8,000円 = 月12万円",
                        "アフィリエイト月3万円 + 相談12万円 = 月次収益15万円を達成"
                    ],
                    ai_prompt=self._prompt("LINE公式×相談事業アドバイザー", "Instagramでフォロワー500人を獲得しました。LINE公式に誘導してAI活用の相談サービスを展開したいです。", ["LINE公式アカウントの開設からInstagramプロフィールへのリンク設置までの手順を提示してください", "友だち登録特典「AI活用チェックリスト」の内容を10項目、実用レベルで作成してください", "相談サービスの受付から実施までのフローを段階的に提示してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"支配フェーズ（7〜12週目）【{mbti_str}】",
                    title="コミュニティ×デジタルコンテンツで月次収益40万円を達成する",
                    description="ファンコミュニティを収益化。デジタルコンテンツ販売とメンバーシップで安定した月次収益40万円を実現する。",
                    tools=["note", "Brain", "LINE公式", "Canvaアプリ", "STORES"],
                    expected_outcome="目標: 月次収益40万円の達成。モバイル1台でのコミュニティ運営体制を確立。",
                    detailed_steps=[
                        "noteで有料記事「AI事業の始め方 完全ガイド」を執筆（1,480円・手数料約14.5%）→ SNSで告知",
                        "Brainで上位教材「AI×共感マーケティング実践編」を販売（9,800円・手数料12%+決済4%）→ アフィリエイト機能で拡散",
                        "LINE公式でメンバーシップ（月額1,980円）を開始 → 限定コンテンツを毎週配信",
                        "note月50部7.4万円 + Brain月20部19.6万円 + メンバー60人11.9万円 = 月38.9万円",
                        "ファン同士の交流を促進 → 口コミによる新規流入 → 月次収益40万円を安定化"
                    ],
                    ai_prompt=self._prompt("デジタルコンテンツ事業アドバイザー", "LINE相談で月次収益15万円を達成しています。noteとBrainで有料コンテンツを販売したいです。", ["noteで有料記事を公開する手順を段階的に提示してください。アカウント作成から公開まで", "1,480円で需要のある有料記事「AI事業の始め方 完全ガイド」の目次と各章の内容を具体的に設計してください", "Brainで9,800円の教材を販売するための販売ページテンプレートを作成してください"], mbti_str),
                ),
            ]

        # =============================================
        # SENTINELS（ISTJ, ISFJ, ESTJ, ESFJ）
        # 責任感・計画性・継続力・正確さが強み
        # =============================================
        if tribe == "SENTINELS" and is_pc:
            return [
                RoadmapStep(
                    phase=f"覚醒フェーズ（1〜2週目）【{mbti_str}】",
                    title="AIで高品質ビジネス文書サービスを構築し、月次収益5万円を達成する",
                    description="正確さと責任感を資本化し、AIで品質管理されたビジネス文書作成サービスを提供。品質保証を武器に高評価基盤を構築する。",
                    tools=["ChatGPT（無料版）", "Googleドキュメント", "ココナラ", "Googleスプレッドシート"],
                    expected_outcome="目標: 初月でレビュー5件獲得。正確さによる高評価基盤の構築。",
                    detailed_steps=[
                        "ChatGPT（無料版）にアクセス → 「ビジネス文書の校正・品質チェック専門家として振る舞ってください」とプロンプトを設計",
                        "ココナラで出品:『AIで高品質なビジネス文書を作成します（議事録/報告書/企画書）』→ 2,000円で出品 → 納期2日 → 正確さでレビュー高評価を獲得",
                        "Googleスプレッドシートで品質チェックリストを作成 → 誤字脱字/論理構成/フォーマットの3段階チェック体制",
                        "AI生成 → 手動チェック → 修正 → 再チェック → 納品。ダブルチェック体制で品質を保証",
                        "クラウドワークスにも同時出品 → 両プラットフォームでレビューを蓄積 → 5件獲得後に5,000円→12,000円と段階的価格改定",
                        "納品時に「無料修正1回付き」を提示 → 期待を超える品質でレビュー高評価を確実に獲得",
                        "効率化オプション: ChatGPT Plus（月額約3,400円）の導入でカスタムGPT作成や高速応答が可能"
                    ],
                    ai_prompt=self._prompt("AI事業戦略アドバイザー", "ChatGPT（無料版）を使って、ココナラで高品質ビジネス文書作成サービスを2,000円で出品しレビュー高評価5件を獲得したいです。", ["ココナラの出品タイトルと説明文を実用レベルで作成してください。2,000円でも信頼感が伝わる内容に", "ChatGPT（無料版）で議事録/報告書/企画書を作成するプロンプトをそれぞれ1つずつ作成してください", "納品前の品質チェックリスト（誤字脱字/論理構成/フォーマット）を設計してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"加速フェーズ（3〜6週目）【{mbti_str}】",
                    title="AI×業務効率化コンサルティングで月次収益25万円の堅実な事業を構築する",
                    description="Excelマクロ+AI自動化で中小企業の業務効率化を支援。計画性を活かした確実な成果提供で継続契約を獲得する。",
                    tools=["Excel VBA", "Python", "ChatGPT API", "Notion"],
                    expected_outcome="目標: 月次収益20〜25万円の達成。継続契約による安定収益基盤の構築。",
                    detailed_steps=[
                        "ChatGPTに「Excel VBAコードを書いて」と依頼 → 日報自動集計/請求書自動生成のテンプレートを作成",
                        "ココナラで『Excel業務をAIで自動化します』を出品（20,000円〜）→ 見積もり対応",
                        "初回は導入価格（15,000円）で受注 → 高品質な成果物で信頼獲得 → 継続契約を提案",
                        "月次レポート自動化パッケージ（月額15,000円）を設計 → 構築後は毎月自動で価値を提供",
                        "新規5件 x 2万円 = 10万円 + 継続10社 x 1.5万円 = 15万円 → 月次収益25万円を達成"
                    ],
                    ai_prompt=self._prompt("Excel業務自動化アドバイザー", "ココナラでレビュー5件獲得し価格改定も完了しました。ChatGPTを使ったExcel業務の自動化サービスを展開したいです。", ["ChatGPTにExcel VBAコード生成を依頼するプロンプトを5種類作成してください（日報集計/請求書/経費管理/顧客リスト/在庫管理）", "ココナラで「Excel業務をAIで自動化します」の出品テンプレートと見積もり対応の例文を作成してください", "初回15,000円→月額15,000円の継続契約を提案するメッセージテンプレートを作成してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"支配フェーズ（7〜12週目）【{mbti_str}】",
                    title="AI業務改善パッケージで月次収益60万円の安定経営を確立する",
                    description="標準化されたAI業務改善パッケージを開発。堅実な営業と確実な成果で法人契約を拡大し、安定した収益基盤を構築する。",
                    tools=["Python", "Streamlit", "Manus AI", "Notion", "Zoom", "freee"],
                    expected_outcome="目標: 月次収益60万円の達成。法人クライアントとの長期契約による安定基盤。",
                    detailed_steps=[
                        "業種別AI改善パッケージを3種類作成: 飲食店/小売/士業 → それぞれの業務フローを分析・設計",
                        "Streamlitでデモアプリを構築 → 効率化効果を可視化し営業ツールとして活用",
                        "商工会議所のセミナーに登壇申し込み → 「中小企業のAI活用術」で集客",
                        "法人契約（月額5万円/初期費用10万円）を設計 → 継続10社で月50万円の安定基盤",
                        "個人向けココナラ10万円 + 法人10社50万円 = 月次収益60万円を達成"
                    ],
                    ai_prompt=self._prompt("中小企業向けAIコンサルティングアドバイザー", "業務効率化コンサルで月次収益25万円を達成しています。法人向けAI業務改善パッケージを構築したいです。", ["飲食店/小売/士業の3業種それぞれの「AIで改善できる業務」と具体的な改善内容を提示してください", "法人向け提案書を実用レベルで作成してください。月額5万円の価値が明確に伝わるように", "商工会議所のセミナー登壇のための申込み手順と企画書テンプレートを作成してください"], mbti_str),
                ),
            ]

        if tribe == "SENTINELS" and not is_pc:
            return [
                RoadmapStep(
                    phase=f"覚醒フェーズ（1〜2週目）【{mbti_str}】",
                    title="モバイル×AIで高精度データ入力・整理サービスを構築し、月次収益3万円を達成する",
                    description="正確さと几帳面さを資本化し、AIサポート付きのデータ整理・入力代行サービスをモバイル環境で提供する。",
                    tools=["ChatGPTアプリ", "Googleスプレッドシート", "ココナラアプリ", "CamScanner"],
                    expected_outcome="目標: 初月でレビュー5件獲得。正確さを差別化要因として確立。",
                    detailed_steps=[
                        "ChatGPTアプリをインストール（無料版）→ 「データ整理の専門家として正確に作業してください」とプロンプトを設計",
                        "Googleスプレッドシートアプリで作業用テンプレートを3種類作成（顧客リスト/在庫管理/経費管理）",
                        "ココナラで出品:『名刺・レシートのデータ化、正確に入力します』→ 1,000円（100件）で出品 → 納期3日 → レビュー高評価を最優先",
                        "CamScannerで画像をテキスト変換 → ChatGPTで整形 → スプレッドシートに入力 → 最終チェック",
                        "レビュー5件獲得後 → 3,000円に価格改定 → 20件超で5,000円に → 実績蓄積に比例した段階的値上げ",
                        "効率化オプション: ChatGPT Plus（月額約3,400円）の導入で精度・速度が大幅に向上"
                    ],
                    ai_prompt=self._prompt("AI事業戦略アドバイザー", "モバイル環境のみです。ChatGPTアプリ（無料版）を使ってココナラでデータ入力サービスを1,000円で出品しレビュー高評価5件を獲得したいです。", ["ココナラアプリでの出品手順を操作レベルで段階的に提示してください。タイトルと説明文も実用レベルで作成", "モバイルでCamScanner→ChatGPT→Googleスプレッドシートのデータ入力フローを手順書レベルで提示してください", "購入者から高評価レビューを獲得するための対応プロセスを具体的に提示してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"加速フェーズ（3〜6週目）【{mbti_str}】",
                    title="AI×事務代行で月次収益15万円の信頼ビジネスを構築する",
                    description="オンライン事務代行として企業のバックオフィスを支援。計画的な作業管理と正確さで継続契約を積み上げる。",
                    tools=["Googleワークスペース", "ChatGPTアプリ", "Notion", "Chatwork"],
                    expected_outcome="目標: 月次収益12〜15万円の達成。継続契約による安定収益。",
                    detailed_steps=[
                        "「オンライン事務代行」としてサービスを再設計 → メール対応/スケジュール管理/資料作成をパッケージ化（ココナラ手数料22%を考慮した価格設定）",
                        "ココナラで実績確立後、クラウドワークスにも事務代行サービスを出品 → 法人案件はクラウドワークスが多く単価向上が見込める",
                        "Chatworkアプリをインストール → クライアントとの連絡ツールとして提案",
                        "月額制プラン: ライト(20,000円/月10時間) / スタンダード(40,000円/月20時間)を設計",
                        "ChatGPTでメール返信テンプレート/議事録テンプレートを事前作成 → 作業時間を半減",
                        "継続クライアント5社 x 平均3万円 = 月次収益15万円を達成"
                    ],
                    ai_prompt=self._prompt("オンライン事務代行アドバイザー", "ココナラでレビュー5件獲得しました。オンライン事務代行サービスを月額制で提供したいです。", ["オンライン事務代行の月額制プラン（ライト2万円/スタンダード4万円）のサービス内容を具体的に設計してください", "ChatGPTで作成するメール返信テンプレート10種類を実用レベルで作成してください", "クライアントに月額制への切り替えを提案するメッセージテンプレートを作成してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"支配フェーズ（7〜12週目）【{mbti_str}】",
                    title="事務代行チーム化で月次収益35万円の安定経営を確立する",
                    description="信頼と実績を基盤に事務代行をチーム化。管理者としてモバイル1台で複数クライアントを運営する体制を構築する。",
                    tools=["Notion", "Chatwork", "ココナラ", "freeeアプリ", "Zoom"],
                    expected_outcome="目標: 月次収益35万円の達成。管理者としての効率的運営体制の確立。",
                    detailed_steps=[
                        "ココナラで事務代行スタッフを2名募集 → マニュアル（Notion）で教育・品質標準化",
                        "品質管理チェックリストを作成 → 全納品物の最終チェック体制を構築",
                        "クライアント10社体制を構築 → スタッフ2名に作業分配 → 管理業務に専念",
                        "売上50万円 - 外注費15万円 = 粗利35万円 → モバイル管理のみで月次収益35万円を達成",
                        "freeeアプリで経費・売上管理 → 確定申告への備えも効率化"
                    ],
                    ai_prompt=self._prompt("事務代行チーム運営アドバイザー", "事務代行で月次収益15万円を達成しています。スタッフを2名採用してチーム化したいです。", ["ココナラで事務代行スタッフを募集する文面を実用レベルで作成してください", "スタッフ向けの業務マニュアルの目次と主要項目をNotion構築レベルで設計してください", "10社のクライアントを2名のスタッフに振り分ける管理シートの設計を提示してください"], mbti_str),
                ),
            ]

        # =============================================
        # EXPLORERS（ISTP, ISFP, ESTP, ESFP）
        # 実践力・行動力・センス・エンタメ力が強み
        # =============================================
        if tribe == "EXPLORERS" and is_pc:
            return [
                RoadmapStep(
                    phase=f"覚醒フェーズ（1〜2週目）【{mbti_str}】",
                    title="AI×動画・デザインで即座にサービスを構築し、月次収益5万円を達成する",
                    description="行動力とセンスを資本化し、AIで動画編集・デザイン制作を高速化。トレンドを捉えた即時収益化を実現する。",
                    tools=["CapCut（無料版）", "Canva（無料版）", "ChatGPT（無料版）", "ココナラ"],
                    expected_outcome="目標: 初月でレビュー5件獲得。制作スキルの収益化基盤を構築。",
                    detailed_steps=[
                        "CapCutをダウンロード（無料版あり・Pro版は月額約1,350円で全機能解放）→ AI自動字幕/AI背景除去/AIエフェクト機能を検証",
                        "Canva（無料版）でSNS投稿用テンプレートを10種類作成",
                        "ココナラで出品:『AIでSNS用ショート動画を編集します』→ 1,500円で出品 → 納期1日 → ポートフォリオ兼用でレビュー高評価を獲得",
                        "同時出品:『AIでロゴ・バナーをデザインします』→ 1,000円で出品 → 納期1日",
                        "レビュー5件獲得後 → 動画5,000円/デザイン3,000円に価格改定 → 20件超で8,000円に",
                        "制作実績をInstagramに投稿 → ポートフォリオとして活用 → 直接依頼も獲得",
                        "効率化オプション: Canva Pro（月額1,180円）やCapCut Pro（月額約1,350円）の導入で素材・機能が無制限に"
                    ],
                    ai_prompt=self._prompt("AI事業戦略アドバイザー", "CapCut（無料版）とCanva（無料版）を使って、ココナラでショート動画編集サービスを1,500円で出品しレビュー高評価5件を獲得したいです。", ["ココナラの出品タイトルと説明文を実用レベルで作成してください。センスの良さが伝わる内容に", "CapCut（無料版）のAI自動字幕・BGM追加を使った編集フローを段階的に提示してください", "ポートフォリオ用のサンプル動画の制作手順を提示してください。内容と本数の設計も含めて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"加速フェーズ（3〜6週目）【{mbti_str}】",
                    title="ショート動画量産×AI編集で月次収益30万円のコンテンツ制作基盤を構築する",
                    description="TikTok/YouTube Shortsのトレンドを分析し、AI編集で量産体制を構築。データに基づくバズコンテンツ生成を確立する。",
                    tools=["CapCut Pro", "Runway ML（Standardプラン月$12〜）", "TikTok", "YouTube Studio"],
                    expected_outcome="目標: 月次収益25〜30万円の達成。バズから収益への変換構造を確立。",
                    detailed_steps=[
                        "TikTokのトレンドハッシュタグを毎日チェック → ChatGPTで台本を5本/日生成",
                        "Runway ML（Gen-4.5でテキストから動画生成）→ CapCut Proで編集 → 1本あたり制作時間15分に短縮",
                        "TikTokアカウントで毎日3投稿 → 30日で90本 → 収益化条件（フォロワー1万人）達成",
                        "企業案件の動画制作受注: 1本30,000円 → 月5件で15万円",
                        "TikTok収益5万円 + ココナラ10万円 + 企業案件15万円 = 月次収益30万円を達成"
                    ],
                    ai_prompt=self._prompt("ショート動画事業アドバイザー", "ココナラでレビュー5件獲得し価格改定も完了しました。TikTokアカウントを成長させショート動画で収益化したいです。", ["TikTokアカウントの開設から最初の投稿までの手順を段階的に提示してください", "バズりやすいジャンルTOP5と、それぞれの台本テンプレートを作成してください", "ChatGPTで毎日の台本を効率的に生成するプロンプトを設計してください"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"支配フェーズ（7〜12週目）【{mbti_str}】",
                    title="マルチプラットフォーム展開で月次収益80万円のクリエイター経済を確立する",
                    description="動画・デザインスキルを複数プラットフォームで展開。AI活用の制作ノウハウ自体を商品化し、収益源を多角化する。",
                    tools=["Adobe Premiere Pro", "Midjourney", "Teachable", "Instagram", "YouTube"],
                    expected_outcome="目標: 月次収益80万円の達成。クリエイターとしての多角的収益構造を確立。",
                    detailed_steps=[
                        "YouTubeチャンネル開設 →「AI動画編集テクニック」を週2本投稿 → 3ヶ月で登録者5,000人を達成",
                        "Midjourneyで生成したAIアート作品をSUZURI/REDBUBBLEでグッズ販売 → 不労所得化",
                        "「AI動画編集マスター講座」をTeachable（Builderプラン月$89〜・取引手数料0%）で販売（19,800円）→ 月20人で39.6万円",
                        "企業のSNS運用代行（月額10万円）を3社契約 → 月30万円の安定収入",
                        "動画制作10万円 + 講座40万円 + SNS運用30万円 = 月次収益80万円を達成"
                    ],
                    ai_prompt=self._prompt("クリエイターエコノミーアドバイザー", "TikTokで月次収益30万円を達成しています。マルチプラットフォーム展開と講座販売で収益を拡大したいです。", ["同じ動画素材をYouTube/Instagram/TikTokに効率的に展開する手順を提示してください", "「AI動画編集マスター講座」のカリキュラムを全8回分、各回のタイトルと内容を設計してください", "企業のSNS運用代行（月額10万円）の提案書テンプレートを作成してください"], mbti_str),
                ),
            ]

        # EXPLORERS x MOBILE
        return [
            RoadmapStep(
                phase=f"覚醒フェーズ（1〜2週目）【{mbti_str}】",
                title="モバイル1台でショート動画クリエイターとして月次収益3万円を達成する",
                description="行動力とセンスをモバイル環境で最大化。CapCutアプリとAIで魅力的なショート動画を量産し、即時収益化する。",
                tools=["CapCutアプリ", "ChatGPTアプリ", "TikTok", "Instagram Reels"],
                expected_outcome="目標: 初月でフォロワー1,000人獲得。モバイル1台でのクリエイター基盤を構築。",
                detailed_steps=[
                    "TikTokアカウントを開設 → ジャンル決定（AI活用術/ライフハック/エンタメから1つ選択）",
                    "ChatGPTアプリで「バズるTikTok台本を5本考えて。ジャンルは○○」→ 毎日の台本を自動生成",
                    "CapCutアプリ（無料版でも基本編集可・Pro版月額約1,350円で全機能）で撮影→AI自動字幕→BGM追加→エフェクト → 1本10分で完成",
                    "毎日2〜3本投稿を30日継続 → フォロワー1,000人 → TikTok Creator Fund申請",
                    "同一動画をInstagram Reelsにもクロスポスト → 収益チャネルを2倍に拡大",
                    "効率化オプション: CapCut Pro（月額約1,350円）の導入で全機能解放・編集効率が向上"
                ],
                ai_prompt=self._prompt("モバイル動画クリエイターアドバイザー", "モバイル1台でTikTokとInstagram Reelsのショート動画を開始したいです。", ["TikTokアカウントの開設からジャンル選定までの手順を提示してください。推奨ジャンルTOP3も", "ChatGPTアプリで「バズる台本」を生成するプロンプトを5パターン作成してください", "CapCutアプリで撮影→字幕→BGM→投稿までの手順を段階的に提示してください"], mbti_str),
            ),
            RoadmapStep(
                phase=f"加速フェーズ（3〜6週目）【{mbti_str}】",
                title="動画編集受注×ライブ配信で月次収益15万円のエンタメ事業を構築する",
                description="動画スキルを収益化しながら、ライブ配信で投げ銭収入も獲得。複数の収入源でポートフォリオを構築する。",
                tools=["CapCutアプリ", "ココナラアプリ", "TikTok LIVE", "17LIVE"],
                expected_outcome="目標: 月次収益12〜15万円の達成。エンタメ力の収益化。",
                detailed_steps=[
                    "ココナラで『モバイルで撮った動画をプロ品質に編集します』→ 1,000円で出品 → 納期1日 → レビュー高評価を獲得",
                    "ココナラで実績確立後、クラウドワークスにも動画編集サービスを出品 → 企業案件が多く単価向上が見込める",
                    "TikTokフォロワー3,000人達成 → LIVE配信を週3回開始 → 投げ銭収入を獲得",
                    "LIVE配信テーマ:「AIでリアルタイムに○○を制作」→ エンタメ性で差別化",
                    "ココナラ月10件5万円 + TikTok収益3万円 + LIVE投げ銭5万円 + アフィリエイト2万円 = 月次収益15万円",
                    "人気動画のパターンを分析 → ChatGPTで台本を最適化 → 再現性のあるバズ戦略を構築"
                ],
                ai_prompt=self._prompt("モバイル動画収益化アドバイザー", "TikTokでフォロワー1,000人を達成しました。動画編集の受注とライブ配信で収益化したいです。", ["ココナラで「モバイルで動画をプロ品質に編集します」の出品テンプレートを作成してください", "TikTok LIVEの開始手順を段階的に提示してください。投げ銭を獲得するための戦略も", "「AIで○○を制作」のライブ配信企画を5つ、台本付きで設計してください"], mbti_str),
            ),
            RoadmapStep(
                phase=f"支配フェーズ（7〜12週目）【{mbti_str}】",
                title="インフルエンサー×プロデュースで月次収益40万円を達成する",
                description="フォロワー1万人を達成し、企業案件とプロデュース事業で収益を最大化。影響力を多角的に収益化する。",
                tools=["TikTok", "Instagram", "LINE公式", "Brain", "STORES"],
                expected_outcome="目標: 月次収益40万円の達成。影響力の収益変換構造を確立。",
                detailed_steps=[
                    "TikTokフォロワー1万人達成 → 企業PR案件の受注開始（1件3〜5万円）",
                    "「モバイル動画編集術」のBrain教材を販売（4,980円）→ アフィリエイト機能で拡散",
                    "動画編集向けのLINEグループコンサル（月額2,980円）を開始",
                    "企業案件月3件15万円 + Brain月30部15万円 + コンサル20人6万円 + その他4万円 = 月次収益40万円",
                    "コンテンツの型をテンプレート化 → 新ジャンルにも即展開できる体制を構築"
                ],
                ai_prompt=self._prompt("インフルエンサー事業アドバイザー", "TikTokフォロワー1万人で月次収益15万円を達成しています。企業案件と教材販売を展開したいです。", ["企業にPR案件を提案するDMテンプレートを実用レベルで作成してください", "Brain教材「モバイル動画編集術」の目次と販売ページテンプレートを作成してください", "ファンコミュニティ（月額2,980円）の設計と集客方法を提示してください"], mbti_str),
            ),
        ]
    
    async def generate_diagnosis(
        self,
        mbti: MBTIType,
        device: DeviceType,
        psychometric_responses: List[PsychometricResponse] = None
    ) -> DiagnosisResult:
        """完全な診断結果を生成"""
        
        archetype = self.get_archetype(mbti)
        description, strengths, weaknesses = self.get_archetype_profile(archetype)
        
        # トレンド検索
        raw_trends = self.search_engine.search_latest_ai_business_trends()

        # Dict -> TrendData に変換
        trends = [
            TrendData(
                title=t.get('title', ''),
                snippet=t.get('snippet', ''),
                relevance_score=calculate_trend_relevance(t, archetype.value, device.value)
            )
            for t in raw_trends
        ]

        # ロードマップ生成（ベース）
        roadmap = self.generate_roadmap(archetype, device, raw_trends, mbti)

        # 心理測定インサイト & ロードマップカスタマイズ
        insight = None
        if psychometric_responses:
            profile = self.analyze_psychometric(psychometric_responses)
            insight = self.generate_psychometric_insight(profile)
            roadmap = self.customize_roadmap(roadmap, profile)
        
        return DiagnosisResult(
            archetype=archetype.value,
            archetype_description=description,
            strengths=strengths,
            weaknesses=weaknesses,
            psychometric_insight=insight,
            latest_trends=trends,
            strategic_roadmap=roadmap,
            automation_teaser=AutomationTeaser(
                tool_name="Oracle Engine Phase 2 - AI事業戦略自動化エンジン",
                progress_percentage=75,
                time_saved="月40時間の戦略実行を自動化し、成果を3倍に",
                key_features=[
                    "ChatGPT API自動連携",
                    "ココナラ案件自動取得・納品",
                    "トレンド自動分析",
                    "収益レポート自動生成"
                ],
                availability="2026年4月リリース予定 | 先行予約受付中"
            ),
            disclaimer="""【免責事項】

本診断結果は教育・情報提供を目的としたものであり、投資助言や確実な収益を保証するものではありません。

・AI事業の収益は個人の努力、スキル、市場状況により大きく異なります
・提示された金額は目標値であり、達成を保証するものではありません
・実際の取り組みにあたっては、ご自身の判断と責任で行ってください
・税務・法務に関する相談は専門家にご確認ください

Powered by SUMI X""",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
