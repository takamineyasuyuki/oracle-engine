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
                "攻め型",
                "新しいことにすぐ飛び込む行動力があります。「まずやってみる」精神で先行者利益を掴みましょう。ただし、最低限のリサーチは忘れずに。"
            ),
            "balanced": (
                "バランス型",
                "計画と行動のバランスが取れています。状況に応じて慎重にも大胆にもなれる柔軟性が最大の強みです。"
            ),
            "cautious": (
                "慎重型",
                "慎重に計画を立ててから行動するタイプ。石橋を叩いて渡る姿勢で失敗リスクを最小化できます。準備ができたら思い切って踏み出しましょう。"
            ),
        }

        work_map = {
            "team": (
                "チーム型",
                "チームで協力することで力を発揮します。早い段階から外注やパートナーを見つけてスケールを目指しましょう。一人で抱え込まないことが成功のカギ。"
            ),
            "flexible": (
                "柔軟型",
                "状況に応じて一人でもチームでも対応できる柔軟性があります。最初はソロで始め、軌道に乗ったらチーム化がおすすめ。"
            ),
            "solo": (
                "ソロ型",
                "一人で集中して作業するのが得意なタイプ。自動化ツールを最大限活用し、一人でも大きく稼げる仕組みを構築しましょう。"
            ),
        }

        revenue_map = {
            "ambitious": (
                "挑戦型",
                "大きなリターンを狙う意欲があります。高単価戦略やスケーラブルなビジネスモデルに最適。リスクを取る分、リターンも大きくなります。"
            ),
            "balanced": (
                "バランス型",
                "安定と成長のバランスを重視するタイプ。基盤を固めつつ、チャンスが来たら攻めに転じる戦略が最適です。"
            ),
            "stable": (
                "安定型",
                "安定した収入を重視する堅実タイプ。サブスク型や継続案件を中心に、予測可能な収益基盤を構築しましょう。"
            ),
        }

        a_label, a_desc = action_map[action]
        w_label, w_desc = work_map[work]
        r_label, r_desc = revenue_map[revenue]

        return (
            f"📊 あなたのビジネス特性分析:\n\n"
            f"【行動スタイル：{a_label}】\n{a_desc}\n\n"
            f"【ワークスタイル：{w_label}】\n{w_desc}\n\n"
            f"【収益志向：{r_label}】\n{r_desc}"
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
                        "💨 まずは即行動！完璧を待たず最小限の準備で今日から始めましょう。"
                    )
                    append_steps.append(
                        "【即行動】初日で出品完了を目標に。完璧でなくてOK、まず市場に出してフィードバックを得る → 改善は走りながら"
                    )
                elif is_mid:
                    desc_additions.append(
                        "💨 スピードを維持して複数チャネルに同時展開。先行者利益を取りに行きます。"
                    )
                    append_steps.append(
                        "【高速展開】成功パターンを3プラットフォーム以上に横展開 → ココナラ+クラウドワークス+ランサーズを同時運用"
                    )
                else:
                    desc_additions.append(
                        "💨 攻めの姿勢で一気にスケール。競合が追いつけない速度で市場を押さえます。"
                    )
                    append_steps.append(
                        "【先行者利益】新しいAIツールが出たら即サービス化 → 市場が成熟する前にポジションを確立"
                    )
            elif action == "cautious":
                if is_early:
                    desc_additions.append(
                        "🛡️ 焦らず確実に。リサーチと準備を徹底してから最初の一歩を踏み出しましょう。"
                    )
                    prepend_steps.append(
                        "【事前準備】競合サービスを最低10件リサーチ → 価格帯・レビュー・差別化ポイントをスプレッドシートに整理してから出品"
                    )
                    extra_tools.append("Googleスプレッドシート（競合分析用）")
                elif is_mid:
                    desc_additions.append(
                        "🛡️ 一つのチャネルで確実に成果を出してから次へ。品質と信頼を最優先に。"
                    )
                    append_steps.append(
                        "【品質管理】納品前の3段階チェックリスト作成 → ①AI生成 ②内容確認 ③フォーマット整形 → 品質を武器にリピート率80%を目指す"
                    )
                else:
                    desc_additions.append(
                        "🛡️ 着実に積み上げた信頼と実績を基盤に、リスクを抑えながら確実にスケール。"
                    )
                    append_steps.append(
                        "【リスク分散】収入源を3つ以上に分散 → 1つが不調でも他でカバーできる安全設計"
                    )

            # ── ワークスタイル ──
            if work == "team":
                if is_early:
                    desc_additions.append(
                        "👥 早い段階からパートナーや外注を活用し、自分は得意なことに集中。"
                    )
                    append_steps.append(
                        "【チーム構築】ココナラ/クラウドワークスで外注パートナーを2〜3人テスト採用 → 小さな案件で品質とスピードを確認"
                    )
                    extra_tools.extend(["Chatwork", "Googleドライブ（共有用）"])
                elif is_mid:
                    append_steps.append(
                        "【分業体制】作業を「企画→制作→チェック→納品」に分解 → 制作は外注チーム、自分はクライアント対応と品質管理に特化"
                    )
                else:
                    append_steps.append(
                        "【組織化】チームを5名体制に拡大 → マニュアルとテンプレートで品質標準化 → 自分は経営と営業に専念"
                    )
                    extra_tools.append("Notion（チームWiki）")
            elif work == "solo":
                if is_early:
                    desc_additions.append(
                        "🔧 すべて一人で完結する仕組みを設計。自動化ツールがあなたの最強のパートナー。"
                    )
                    append_steps.append(
                        "【自動化設計】受注→作業→納品の全工程でテンプレートを用意 → 1件あたりの手作業を最小限に"
                    )
                elif is_mid:
                    append_steps.append(
                        "【仕組み化】Notion + Zapierで受注通知→作業テンプレート自動展開→納品リマインダーの一気通貫フローを構築"
                    )
                    extra_tools.append("Zapier")
                else:
                    append_steps.append(
                        "【一人帝国】AI + 自動化ツールで全工程を無人化 → 一人で月100万円を回せるシステム完成"
                    )

            # ── 収益志向 ──
            if revenue == "ambitious":
                if is_early:
                    desc_additions.append(
                        "🎯 最初から高単価で勝負。安売りせず、価値で選ばれるサービスを提供。"
                    )
                    append_steps.append(
                        "【高単価戦略】1万円以上で出品 → サービス説明に「なぜこの価格なのか」の価値を明記 → 品質重視の顧客を引き寄せる"
                    )
                elif is_mid:
                    append_steps.append(
                        "【収益最大化】松竹梅の3段階価格 → ライト(5,000円)/スタンダード(15,000円)/プレミアム(30,000円) → プレミアムを主力に育てる"
                    )
                else:
                    outcome_addition = "高単価×スケールで月収100万円超えを現実のものに。"
                    append_steps.append(
                        "【スケール戦略】法人向けパッケージ（月額10万円〜）を開発 → 個人から法人へとクライアント単価を10倍に引き上げ"
                    )
            elif revenue == "stable":
                if is_early:
                    desc_additions.append(
                        "📈 まずは確実な小さな収入を作ることに集中。成功体験を積み重ねましょう。"
                    )
                    append_steps.append(
                        "【堅実スタート】相場より少し安めの価格で出品 → まず実績10件とレビュー★5を最優先で獲得 → 信頼資産を構築"
                    )
                elif is_mid:
                    append_steps.append(
                        "【継続収入】月額制サービスを設計 → 単発の波をなくし毎月安定したキャッシュフローを確保"
                    )
                    extra_tools.append("Stripe（サブスク決済）")
                else:
                    outcome_addition = "予測可能な継続収入の基盤を確立。安定したキャッシュフローで安心経営。"
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
                    prompt_extras.append("- 私はスピード重視の行動派です。最短ルートを教えて")
                elif action == "cautious":
                    prompt_extras.append("- 私は慎重派です。リスクを最小限にする方法も含めて")
                if work == "team":
                    prompt_extras.append("- チームや外注を活用したいです。分業の方法も教えて")
                elif work == "solo":
                    prompt_extras.append("- 一人で完結したいです。自動化の方法を優先して")
                if revenue == "ambitious":
                    prompt_extras.append("- 高単価・高収益を狙いたいです")
                elif revenue == "stable":
                    prompt_extras.append("- 安定した継続収入を重視します")
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
            f"- 私は完全な初心者です。専門用語は使わず、小学生でもわかるように説明してください\n"
            f"- 「何を」「どこで」「どうやって」を1ステップずつ教えてください\n"
            f"- 各ステップは「○○を開く → △△をクリック → □□と入力」のレベルで具体的に\n\n"
            f"以下について教えてください：\n{ask_lines}\n\n"
            f"条件：\n"
            f"- コピペでそのまま使える文章・テンプレートを必ず含めて\n"
            f"- 無料で始められる方法を優先して\n"
            f"- 「今日中にここまでやる」というゴールを各ステップに設定して"
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
                    phase=f"🌱 覚醒フェーズ（1〜2週目）【{mbti_str}特別戦略】",
                    title="ChatGPT（無料版）で最初のAIサービスを構築、月5万円を手に入れる",
                    description="あなたの論理的思考を活かして、ChatGPT（無料版）でAIコンテンツ生成を開始。まずは無料版で十分始められます。ココナラで「AIコンテンツ生成サービス」を出品し、まず最初の1件を獲得することを目指します。",
                    tools=["ChatGPT（無料版）", "VS Code", "ココナラ"],
                    expected_outcome="目標: 初月でレビュー5件獲得。実績を作って値上げの土台を築く。",
                    detailed_steps=[
                        "chat.openai.comをブラウザで開く → Googleアカウントで無料登録 → すぐにChatGPTが使える状態になる",
                        "ChatGPTに「キャッチコピーを100個考えて」「ブログ記事を書いて」など指示を出す練習 → プロンプトのコツを掴む",
                        "VS Codeをダウンロード → ChatGPTで生成したコンテンツをコピペして整形 → 納品用ファイルを作成",
                        "ココナラで出品：タイトル『AIで100個のコンテンツを一括生成します』→ まず1,500円で出品 → 納期1日 → 最初の5件のレビュー★5獲得が最優先",
                        "依頼が来たらChatGPTでコンテンツ生成 → 結果をExcelにコピペ → 納品 → 作業時間30分で1万円！",
                        "レビュー5件獲得後 → 5,000円に値上げ → レビュー20件超で10,000円に → 実績が増えるほど高単価で売れる",
                        "💡 慣れてきたらPlus（月額約3,400円）に課金すると効率UP"
                    ],
                    ai_prompt=self._prompt("AI副業の専門コンサルタント", "完全な初心者です。ChatGPT（無料版）を使って、ココナラで「AIコンテンツ生成サービス」をまず1,500円で出品して最初のレビュー★5を5件集めたいです。", ["ココナラの出品タイトルと説明文をコピペで使えるレベルで書いて。1,500円でも買いたくなる内容にして", "ChatGPT（無料版）に送るプロンプトのテンプレートを3種類作って（キャッチコピー/ブログ記事/商品説明）", "最初の1件目の注文を取るためにやるべきことを、今日やること・明日やること・1週間以内にやることで分けて教えて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"⚡ 加速フェーズ（3〜6週目）【{mbti_str}特別戦略】",
                    title="データ分析で需要を可視化、月30万円の自動販売機を構築",
                    description="Google Trendsで需要が高いキーワードを特定し、専用自動化ツールを作成。SaaSとして月額課金で販売します。",
                    tools=["Google Trends", "Streamlit", "Stripe"],
                    expected_outcome="目標: 月30〜50万円の収益。データ駆動型で無駄を減らす。",
                    detailed_steps=[
                        "trends.google.comで「AI 副業」「ChatGPT 使い方」などを検索 → 上昇トレンドのキーワードをExcelに記録",
                        "需要1位のテーマで専用ツール作成 → Streamlit（Python製Webフレームワーク）でブラウザから使えるWebアプリ化",
                        "stripe.comでアカウント作成 → 商品「月額2,980円」を設定 → APIキーを取得してアプリに組み込み",
                        "Streamlit Community Cloud（完全無料）でデプロイ → 専用URL発行 → これがあなたの自動販売機！",
                        "月100人契約で 2,980円×100 = 298,000円の自動継続収入達成"
                    ],
                    ai_prompt=self._prompt("SaaSビジネスの専門家", "ココナラでレビュー5件獲得して値上げも済みました。次はStreamlitで月額課金のWebアプリを作りたいです。プログラミングは初心者です。", ["Streamlit + ChatGPT APIで簡単なWebアプリを作る手順をゼロから教えて。環境構築から1つずつ", "月額2,980円で売れるAIツールのアイデアを5つ、それぞれの想定ユーザーと一緒に教えて", "Streamlit Community Cloud（無料）にデプロイする手順を画面の操作レベルで教えて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"🚀 支配フェーズ（7〜12週目）【{mbti_str}特別戦略】",
                    title="マルチAIエージェントで月100万円の完全自動収益マシン",
                    description="複数のAI APIを組み合わせたエージェントシステムを構築。案件獲得→制作→納品まで全自動化し、月100万円の不労所得を実現します。",
                    tools=["LangChain 1.2", "Manus AI", "Claude API（Sonnet 4.5: $3/$15 per 1M tokens）", "GitHub Actions", "Stripe API"],
                    expected_outcome="目標: 月100万円の収益。AIで作業時間を最小化。",
                    detailed_steps=[
                        "LangChain 1.2でマルチステップAIエージェントを構築 → 入力テーマから自動で記事・画像・動画台本を一括生成",
                        "GitHub Actionsで毎日定時実行スケジュールを設定 → トレンドキーワード自動収集 → コンテンツ自動生成",
                        "Stripe Webhookで決済→納品を完全自動化 → 顧客管理もAPI連携で手間ゼロ",
                        "BrainやTipsで高単価コンテンツ（9,800円〜29,800円）を販売 → 月間100件で月100万円達成",
                        "自動化ノウハウをUdemy講座として販売 → 追加の不労所得ストリームを構築"
                    ],
                    ai_prompt=self._prompt("AIエージェント開発の専門家", "SaaSで月30万円稼いでいます。次はLangChainやManus AIで自動化システムを作りたいです。", ["LangChainで「テーマ入力→記事自動生成→投稿」の自動化を作る手順をゼロから教えて", "GitHub Actionsで毎日自動実行するワークフローの作り方を初心者向けに教えて", "Brain/noteで高単価コンテンツ（1〜3万円）を売るための販売ページの書き方テンプレート"], mbti_str),
                ),
            ]

        if tribe == "ANALYSTS" and not is_pc:
            return [
                RoadmapStep(
                    phase=f"🌱 覚醒フェーズ（1〜2週目）【{mbti_str}特別戦略】",
                    title="スマホ×クラウドAIで論理的に月5万円を構築",
                    description="あなたの分析力を活かし、ChatGPTアプリとNotion連携でクラウド完結の自動化フローを作成。データに基づく戦略で最短ルートを攻めます。",
                    tools=["ChatGPT（無料版）アプリ", "Notion", "ココナラアプリ", "Googleスプレッドシート"],
                    expected_outcome="目標: 初月でレビュー5件獲得。スマホだけでも始められることを体感。",
                    detailed_steps=[
                        "App StoreからChatGPTアプリをダウンロード（無料版でOK）→ アカウント作成 → すぐに使い始められる",
                        "Notionアプリをインストール → 「AI副業管理DB」を作成 → テンプレート：案件名/単価/ステータス/納期",
                        "ChatGPTに「ビジネス文書作成の専門家として振る舞って」と指示 → プロンプトテンプレートを5種類作成しNotionに保存",
                        "ココナラアプリで出品：『AIで企画書・提案書を作成します』→ まず1,500円で出品 → 納期2日 → レビュー★5を最優先で集める",
                        "受注→ChatGPTで生成→Googleドキュメントで整形→PDF納品。全工程スマホ完結。",
                        "レビュー5件獲得後 → 5,000円に値上げ → レビュー20件超で8,000円に → 実績が価格を上げてくれる",
                        "💡 慣れてきたらChatGPT Plus（月額約3,400円）に課金するとGPT-5が使えて品質・速度UP"
                    ],
                    ai_prompt=self._prompt("スマホ副業の専門コンサルタント", "完全な初心者です。スマホしかありません。ChatGPTアプリ（無料版）を使ってココナラで企画書作成サービスをまず1,500円で出品して最初のレビュー★5を5件集めたいです。", ["ココナラアプリでの出品手順を画面の操作レベルで教えて。タイトルと説明文もコピペで使えるように書いて", "ChatGPTアプリに送るプロンプトのテンプレートを3種類作って（企画書/提案書/報告書）。コピペするだけで使えるように", "スマホだけで受注→ChatGPTで作成→Googleドキュメントで整形→PDF納品する手順を1つずつ教えて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"⚡ 加速フェーズ（3〜6週目）【{mbti_str}特別戦略】",
                    title="No-CodeツールでAIサービスを自動化、月20万円達成",
                    description="MakeやZapierを使ってノーコードで自動化フローを構築。分析力で最適なワークフローを設計し、手作業をゼロに。",
                    tools=["Make (Integromat)", "Zapier", "Manus AI", "Notion API", "LINE公式"],
                    expected_outcome="目標: 月15〜20万円の収益。自動化で効率を高める。",
                    detailed_steps=[
                        "make.comでアカウント作成 → 無料プラン（月1,000クレジット）で自動化シナリオを作成開始",
                        "シナリオ：Googleフォーム受付 → ChatGPT API自動処理 → 結果をメール自動送信",
                        "LINE公式アカウントを開設（無料プラン月200通・ライトプラン月5,000円で5,000通）→ 自動応答でAIサービスの受付を24時間化",
                        "ココナラで実績ができたら、クラウドワークスにも同じサービスを出品 → 2つのプラットフォームで集客力を倍増",
                        "サービスを3段階に分ける：ライト(3,000円)/スタンダード(8,000円)/プレミアム(15,000円)",
                        "月間30件受注の自動フロー完成 → 平均単価7,000円 × 30 = 月21万円達成"
                    ],
                    ai_prompt=self._prompt("No-Code自動化の専門家", "スマホでココナラのレビュー5件獲得しました。MakeやZapierで受注→AI処理→納品を自動化したいです。初心者なので基礎から教えてください。", ["Make(Integromat)の無料アカウント作成から最初の自動化シナリオを作るまでの手順を1つずつ教えて", "LINE公式アカウントの開設手順と、自動応答でサービス受付を24時間化する設定方法", "月額制サービス（3,000円/8,000円/15,000円）のそれぞれの内容を具体的に設計して"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"🚀 支配フェーズ（7〜12週目）【{mbti_str}特別戦略】",
                    title="クラウドSaaS型サービスで月50万円の仕組み化",
                    description="No-Codeで構築した自動化フローをサブスク型サービスとして提供。スマホ管理だけで月50万円の継続収入を実現。",
                    tools=["Bubble", "Stripe", "Make", "Manus AI", "ChatGPT API"],
                    expected_outcome="目標: 月50万円の収益。クラウド運用でどこでも作業可能に。",
                    detailed_steps=[
                        "Bubble（Starterプラン月$29〜）でシンプルなWebアプリを構築 → AIコンテンツ生成ツールをSaaS化",
                        "月額制プラン設定：個人(2,980円)/ビジネス(9,800円) → Stripe決済を連携",
                        "Makeで新規登録→オンボーディング→利用開始を完全自動化",
                        "SNSで無料トライアルを訴求 → 月間200人登録 → 有料転換率25%で50人",
                        "50人 × 平均5,000円 = 月25万円 + 既存ココナラ25万円 = 月50万円達成"
                    ],
                    ai_prompt=self._prompt("No-Code SaaSの専門家", "No-Codeツールで月20万円稼いでいます。BubbleでAIツールをSaaS化したいです。初心者向けに教えてください。", ["Bubbleの無料プランでAIコンテンツ生成ツールを作る手順をゼロから教えて", "月額2,980円と9,800円の2プランで差をつけるサービス設計", "無料トライアルから有料に転換してもらうための仕組みを具体的に教えて"], mbti_str),
                ),
            ]

        # =============================================
        # DIPLOMATS（INFJ, INFP, ENFJ, ENFP）
        # 共感力・ストーリーテリング・人を動かす力が強み
        # =============================================
        if tribe == "DIPLOMATS" and is_pc:
            return [
                RoadmapStep(
                    phase=f"🌱 覚醒フェーズ（1〜2週目）【{mbti_str}特別戦略】",
                    title="共感力×AIで心に刺さるコンテンツを量産、月5万円を達成",
                    description="あなたの深い共感力を武器に、AIと組み合わせて感情に響くコンテンツを作成。人の悩みに寄り添うサービスで高単価を実現します。",
                    tools=["ChatGPT（無料版）", "Notion", "Canva（無料版）", "ココナラ"],
                    expected_outcome="目標: 初月でレビュー5件獲得。共感力で高評価を集める。",
                    detailed_steps=[
                        "ChatGPT（無料版）にアクセス → 「あなたは共感力の高いライターです。読者の感情に寄り添った文章を書いてください」というシステムプロンプトを作成",
                        "ココナラで出品：『心に響く自己紹介文・プロフィールを作成します』→ まず1,000円で出品 → 納期2日 → 丁寧な対応でレビュー★5を最優先",
                        "Canva（無料版）でプロフィール用のビジュアルテンプレートを5種類作成 → セットで差別化",
                        "Notionに「感情別テンプレートDB」を構築 → 喜び/悲しみ/期待/不安の4パターン × シーン別",
                        "SNSプロフィール添削サービスも追加出品（1,000円）→ レビュー5件獲得後に5,000円→10,000円と段階的に値上げ",
                        "お客様の声を丁寧にヒアリング → 期待以上の納品で★5評価を積み上げ → レビューが増えれば自然に高単価で売れる",
                        "💡 慣れてきたらChatGPT Plus（月額約3,400円）やCanva Pro（月額1,180円）に課金すると効率UP"
                    ],
                    ai_prompt=self._prompt("AI副業の専門コンサルタント", "完全な初心者です。ChatGPT（無料版）とCanva（無料版）を使って、ココナラで自己紹介文作成サービスをまず1,000円で出品して最初のレビュー★5を5件集めたいです。", ["ココナラの出品タイトルと説明文をコピペで使えるレベルで書いて。1,000円でも「この人に頼みたい」と思わせる内容にして", "ChatGPT（無料版）で心に響く自己紹介文を作るプロンプトを5パターン書いて。コピペしてそのまま使えるように", "初めての購入者に感動してもらい★5レビューをもらうための対応術を教えて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"⚡ 加速フェーズ（3〜6週目）【{mbti_str}特別戦略】",
                    title="AI×コーチング型コンテンツで月30万円のファンビジネス",
                    description="あなたのビジョンと影響力を活かし、AIサポート付きのオンラインコーチングやコミュニティ運営で安定収益を構築します。",
                    tools=["Zoom", "ChatGPT API", "Notion", "Stripe", "LINE公式"],
                    expected_outcome="目標: 月25〜30万円の収益。ファンを増やす好循環を目指す。",
                    detailed_steps=[
                        "LINE公式アカウントを開設（無料プラン月200通・ライト月5,000円で5,000通）→ ステップ配信で「AI活用術」を7日間無料講座として配信",
                        "ChatGPTで個別相談用のアドバイステンプレートを作成 → カスタマイズして1人30分のZoom相談を提供",
                        "個別コーチング（月額19,800円）を設計 → 週1回30分Zoom + LINEで無制限質問対応",
                        "Notionで受講生管理DB → 進捗トラッキング → AIで個別アドバイスを自動生成",
                        "無料講座200人集客 → 有料転換率5% = 10人 × 19,800円 = 月198,000円",
                        "ココナラ収益10万円 + コーチング20万円 = 月30万円達成"
                    ],
                    ai_prompt=self._prompt("オンラインコーチングの専門家", "ココナラでレビュー5件獲得して値上げも済みました。LINE公式とZoomでAI活用コーチング（月額19,800円）を始めたいです。集客方法がわかりません。", ["LINE公式アカウントの開設から友だち集めまでの手順を初心者向けにゼロから教えて", "7日間のステップ配信の内容を1日ずつ具体的に書いて（コピペで設定できるレベルで）", "無料講座から有料コーチングに申し込んでもらうためのトーク例を書いて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"🚀 支配フェーズ（7〜12週目）【{mbti_str}特別戦略】",
                    title="オンラインスクール×AIで月80万円の教育ビジネス",
                    description="あなたのビジョンを体系化したオンライン講座を開設。AI活用で運営を効率化し、影響力と収益を同時に最大化します。",
                    tools=["Udemy", "Teachable", "ChatGPT", "Canva", "OBS Studio"],
                    expected_outcome="目標: 月80万円の収益。コミュニティリーダーを目指す。",
                    detailed_steps=[
                        "OBS Studioで画面録画環境を構築 → 「AI×副業 完全ロードマップ」全10回の講座を収録",
                        "Udemyで講座を公開（2,400円）→ セール時に大量集客 → 自己集客なら売上の97%が収益（Udemy集客は37%）",
                        "Teachable（Builderプラン月$89〜・取引手数料0%）で上位コース（49,800円）を開設 → Udemy受講者に案内",
                        "卒業生コミュニティ（月額3,980円）をDiscordで運営 → AIボットで24時間サポート",
                        "Udemy48万円 + 上位コース月5人25万円 + コミュニティ20人8万円 = 月81万円達成"
                    ],
                    ai_prompt=self._prompt("オンライン講座ビジネスの専門家", "コーチングで月30万円稼いでいます。UdemyとTeachableでオンライン講座を作りたいです。動画撮影も初めてです。", ["Udemyの講座を作る手順をゼロから教えて。アカウント作成→撮影→編集→公開まで", "スマホだけで講座動画を撮影・編集する方法を具体的に教えて", "Udemy受講者を49,800円の上位コースに誘導するメール文面をコピペで使えるように書いて"], mbti_str),
                ),
            ]

        if tribe == "DIPLOMATS" and not is_pc:
            return [
                RoadmapStep(
                    phase=f"🌱 覚醒フェーズ（1〜2週目）【{mbti_str}特別戦略】",
                    title="スマホ×共感力で心を動かすSNS発信、月3万円を達成",
                    description="あなたの共感力をSNSで発揮。AIで文章を磨き上げ、フォロワーの心に刺さるコンテンツでアフィリエイト収益を獲得します。",
                    tools=["ChatGPTアプリ", "Instagram", "Canvaアプリ", "A8.net"],
                    expected_outcome="目標: 初月でフォロワー500人獲得。共感力で人を引きつける。",
                    detailed_steps=[
                        "Instagramのビジネスアカウントを開設 → プロフィールに「AI×自分らしい生き方」を明記",
                        "ChatGPTアプリで「フォロワーの悩みに寄り添う投稿文」を毎日3パターン生成",
                        "Canvaアプリでカルーセル投稿（10枚スライド）のテンプレートを作成 → 毎日1投稿",
                        "A8.netでAIツール系（画像生成AI・ライティングAI等）のアフィリエイト案件に登録 → 投稿内で自然に紹介",
                        "30日連続投稿でフォロワー500人 → ストーリーでアフィリエイトリンク → 月3万円達成",
                        "💡 慣れてきたらChatGPT Plus（月額約3,400円）やCanva Pro（月額1,180円）に課金すると効率UP"
                    ],
                    ai_prompt=self._prompt("Instagram運用の専門家", "完全な初心者です。スマホだけでInstagramを使ってAI副業の発信を始めたいです。フォロワー0人からのスタートです。", ["Instagramのビジネスアカウント開設手順と、プロフィールの書き方をコピペで使えるように教えて", "最初の30日間の投稿テーマを1日ずつ具体的に書いて。ChatGPTアプリに送るプロンプトも一緒に", "フォロワー0人から500人まで最速で増やすための毎日やるべきアクション（いいね/コメント/ハッシュタグ）を教えて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"⚡ 加速フェーズ（3〜6週目）【{mbti_str}特別戦略】",
                    title="LINE×AI相談サービスで月15万円の信頼ビジネス",
                    description="SNSで集めたファンをLINE公式に誘導。AIサポート付きの相談サービスで深い信頼関係を構築し収益化します。",
                    tools=["LINE公式", "ChatGPTアプリ", "ココナラアプリ", "PayPay"],
                    expected_outcome="目標: 月12〜15万円の収益。感謝されるサービスを構築。",
                    detailed_steps=[
                        "LINE公式アカウントを開設（無料プラン月200通・ライト月5,000円で5,000通）→ Instagramのプロフィールにリンク → 友だち登録特典「AI活用チェックリスト」を配布",
                        "ChatGPTで悩み別の回答テンプレートを20種類作成 → すぐに返信できる体制を構築",
                        "ココナラで『AIを使ったキャリア相談30分』を出品（8,000円）→ スマホZoomで対応",
                        "LINE友だち300人 → 相談サービス月15件 × 8,000円 = 月12万円",
                        "アフィリエイト月3万円 + 相談12万円 = 月15万円達成"
                    ],
                    ai_prompt=self._prompt("LINE公式×相談ビジネスの専門家", "Instagramでフォロワー500人集めました。LINE公式に誘導してAI活用の相談サービスを始めたいです。LINE公式は初めてです。", ["LINE公式アカウントの開設からInstagramのプロフィールにリンクを貼るまでの手順を教えて", "友だち登録特典「AI活用チェックリスト」の内容を10項目、そのまま使えるレベルで作って", "相談サービスの受付から実施までの流れを、初心者でもできるように1ステップずつ教えて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"🚀 支配フェーズ（7〜12週目）【{mbti_str}特別戦略】",
                    title="コミュニティ×デジタルコンテンツで月40万円",
                    description="ファンコミュニティを収益化。デジタルコンテンツ販売とメンバーシップで安定的な月40万円を実現します。",
                    tools=["note", "Brain", "LINE公式", "Canvaアプリ", "STORES"],
                    expected_outcome="目標: 月40万円の収益。スマホ1台でコミュニティを運営。",
                    detailed_steps=[
                        "noteで有料記事「AI副業の始め方 完全ガイド」を執筆（1,480円・手数料約14.5%）→ SNSで告知",
                        "Brainで上位教材「AI×共感マーケティング実践編」を販売（9,800円・手数料12%+決済4%）→ アフィリエイト機能で拡散",
                        "LINE公式でメンバーシップ（月額1,980円）を開始 → 限定コンテンツ毎週配信",
                        "note月50部7.4万円 + Brain月20部19.6万円 + メンバー60人11.9万円 = 月38.9万円",
                        "ファン同士の交流を促進 → 口コミで新規流入 → 月40万円安定化"
                    ],
                    ai_prompt=self._prompt("デジタルコンテンツ販売の専門家", "LINE相談で月15万円稼いでいます。noteとBrainで有料コンテンツを販売したいです。文章を書くのは初めてです。", ["noteで有料記事を公開する手順をゼロから教えて。アカウント作成から公開まで", "1,480円で売れる有料記事「AI副業の始め方 完全ガイド」の目次と各章の内容を具体的に書いて", "Brainで9,800円の教材を売るための販売ページの文章をコピペで使えるレベルで書いて"], mbti_str),
                ),
            ]

        # =============================================
        # SENTINELS（ISTJ, ISFJ, ESTJ, ESFJ）
        # 責任感・計画性・継続力・正確さが強み
        # =============================================
        if tribe == "SENTINELS" and is_pc:
            return [
                RoadmapStep(
                    phase=f"🌱 覚醒フェーズ（1〜2週目）【{mbti_str}特別戦略】",
                    title="AIで正確・高品質なビジネス文書サービス、月5万円を達成",
                    description="あなたの正確さと責任感を活かし、AIで品質管理された文書作成サービスを提供。「ミスゼロ」を武器に高単価案件を獲得します。",
                    tools=["ChatGPT（無料版）", "Googleドキュメント", "ココナラ", "Googleスプレッドシート"],
                    expected_outcome="目標: 初月でレビュー5件獲得。正確さで★5評価を狙う。",
                    detailed_steps=[
                        "ChatGPT（無料版）にアクセス → 「ビジネス文書の校正・品質チェック専門家として振る舞ってください」とプロンプトを入力",
                        "ココナラで出品：『AIで完璧なビジネス文書を作成します（議事録/報告書/企画書）』→ まず2,000円で出品 → 納期2日 → 正確さでレビュー★5を最優先",
                        "Googleスプレッドシートで品質チェックリストを作成 → 誤字脱字/論理構成/フォーマットの3段階チェック",
                        "AI生成 → 手動チェック → 修正 → 再チェック → 納品。ダブルチェック体制で品質保証",
                        "クラウドワークスにも同時出品 → 両プラットフォームでレビューを集める → 5件獲得後に5,000円→12,000円と段階値上げ",
                        "納品時に「無料修正1回付き」をアピール → 期待以上の品質で★5レビューを確実に獲得",
                        "💡 慣れてきたらChatGPT Plus（月額約3,400円）に課金するとカスタムGPT作成や高速応答が可能に"
                    ],
                    ai_prompt=self._prompt("AI副業の専門コンサルタント", "完全な初心者です。ChatGPT（無料版）を使って、ココナラで高品質なビジネス文書作成サービスをまず2,000円で出品して最初のレビュー★5を5件集めたいです。", ["ココナラの出品タイトルと説明文をコピペで使えるレベルで書いて。2,000円でも「この人は丁寧そう」と思わせる内容にして", "ChatGPT（無料版）で議事録/報告書/企画書を作るプロンプトをそれぞれ1つずつ書いて。コピペで使えるように", "納品前のチェックリスト（誤字脱字/論理構成/フォーマット）を作って。これで品質を保証できるように"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"⚡ 加速フェーズ（3〜6週目）【{mbti_str}特別戦略】",
                    title="AI×業務効率化コンサルで月25万円の堅実ビジネス",
                    description="Excelマクロ+AI自動化で中小企業の業務効率化を支援。あなたの計画性で確実に成果を出し、継続契約を獲得します。",
                    tools=["Excel VBA", "Python", "ChatGPT API", "Notion"],
                    expected_outcome="目標: 月20〜25万円の収益。継続契約で安定を目指す。",
                    detailed_steps=[
                        "ChatGPTに「Excel VBAコードを書いて」と依頼 → 日報自動集計/請求書自動生成のテンプレートを作成",
                        "ココナラで『Excel業務をAIで自動化します』を出品（20,000円〜）→ 見積もり対応",
                        "初回は割引価格（15,000円）で受注 → 完璧な成果物で信頼獲得 → 継続契約を提案",
                        "月次レポート自動化パッケージ（月額15,000円）を設計 → 一度構築すれば毎月自動",
                        "新規5件 × 2万円 = 10万円 + 継続10社 × 1.5万円 = 15万円 → 月25万円達成"
                    ],
                    ai_prompt=self._prompt("Excel業務自動化の専門家", "ココナラでレビュー5件獲得して値上げも済みました。次にChatGPTを使ってExcel業務の自動化サービスを始めたいです。VBAは初心者です。", ["ChatGPTに「Excel VBAコードを書いて」と頼むプロンプトを5種類書いて（日報集計/請求書/経費管理/顧客リスト/在庫管理）", "ココナラで「Excel業務をAIで自動化します」の出品テンプレートと見積もり対応の例文", "初回15,000円→月額15,000円の継続契約を提案する際のメッセージテンプレート"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"🚀 支配フェーズ（7〜12週目）【{mbti_str}特別戦略】",
                    title="AI業務改善パッケージで月60万円の安定経営",
                    description="標準化されたAI業務改善パッケージを開発。堅実な営業と確実な成果で法人契約を拡大し、月60万円を達成します。",
                    tools=["Python", "Streamlit", "Manus AI", "Notion", "Zoom", "freee"],
                    expected_outcome="目標: 月60万円の収益。法人クライアントとの長期契約を目指す。",
                    detailed_steps=[
                        "業種別AI改善パッケージを3種類作成：飲食店/小売/士業 → それぞれの業務フローを分析",
                        "Streamlitでデモアプリを構築 → 「こんなに効率化できます」を可視化して営業ツールに",
                        "商工会議所のセミナーに登壇申し込み → 「中小企業のAI活用術」で集客",
                        "法人契約（月額5万円/初期費用10万円）を設計 → 継続10社で月50万円の安定基盤",
                        "個人向けココナラ10万円 + 法人10社50万円 = 月60万円達成"
                    ],
                    ai_prompt=self._prompt("中小企業向けAIコンサルの専門家", "業務効率化コンサルで月25万円稼いでいます。法人向けAI業務改善パッケージを作りたいです。法人営業は初めてです。", ["飲食店/小売/士業の3業種それぞれの「AIで改善できる業務」と具体的な改善内容を教えて", "法人に送る提案書をコピペで使えるレベルで書いて。月額5万円の価値が伝わるように", "商工会議所のセミナーに登壇するための申込み手順と企画書テンプレートを作って"], mbti_str),
                ),
            ]

        if tribe == "SENTINELS" and not is_pc:
            return [
                RoadmapStep(
                    phase=f"🌱 覚醒フェーズ（1〜2週目）【{mbti_str}特別戦略】",
                    title="スマホ×AIで正確なデータ入力・整理サービス、月3万円を達成",
                    description="あなたの正確さと几帳面さを活かし、AIサポート付きのデータ整理・入力代行サービスをスマホだけで提供します。",
                    tools=["ChatGPTアプリ", "Googleスプレッドシート", "ココナラアプリ", "CamScanner"],
                    expected_outcome="目標: 初月でレビュー5件獲得。正確さを武器にする。",
                    detailed_steps=[
                        "ChatGPTアプリをインストール（無料版でOK）→ 「データ整理の専門家として正確に作業してください」とプロンプトを入力",
                        "Googleスプレッドシートアプリで作業用テンプレートを3種類作成（顧客リスト/在庫管理/経費管理）",
                        "ココナラで出品：『名刺・レシートのデータ化、正確に入力します』→ まず1,000円（100件）で出品 → 納期3日 → レビュー★5を最優先",
                        "CamScannerで画像をテキスト変換 → ChatGPTで整形 → スプレッドシートに入力 → 最終チェック",
                        "レビュー5件獲得後 → 3,000円に値上げ → レビュー20件超で5,000円に → 実績が信頼を生む",
                        "💡 慣れてきたらChatGPT Plus（月額約3,400円）に課金すると精度・速度が大幅UP"
                    ],
                    ai_prompt=self._prompt("スマホ副業の専門コンサルタント", "完全な初心者です。スマホしかありません。ChatGPTアプリ（無料版）を使ってココナラでデータ入力サービスをまず1,000円で出品して最初のレビュー★5を5件集めたいです。", ["ココナラアプリでの出品手順をスクショ撮る感覚で1つずつ教えて。タイトルと説明文もコピペで使えるように", "スマホでCamScanner→ChatGPT→Googleスプレッドシートのデータ入力フローを手順書レベルで教えて", "最初のお客さんに★5レビューをもらうための対応のコツを具体的に教えて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"⚡ 加速フェーズ（3〜6週目）【{mbti_str}特別戦略】",
                    title="AI×事務代行で月15万円の信頼ビジネス",
                    description="オンライン事務代行として企業のバックオフィスをサポート。計画的な作業管理と正確さで継続契約を積み上げます。",
                    tools=["Googleワークスペース", "ChatGPTアプリ", "Notion", "Chatwork"],
                    expected_outcome="目標: 月12〜15万円の収益。継続契約で安定を目指す。",
                    detailed_steps=[
                        "「オンライン事務代行」としてサービスを再設計 → メール対応/スケジュール管理/資料作成をパッケージ化（ココナラ手数料22%を考慮した価格設定）",
                        "ココナラで実績ができたら、クラウドワークスにも事務代行サービスを出品 → 法人案件はクラウドワークスの方が多い",
                        "Chatworkアプリをインストール → クライアントとの連絡ツールとして提案",
                        "月額制プラン：ライト(20,000円/月10時間) / スタンダード(40,000円/月20時間)を設計",
                        "ChatGPTでメール返信テンプレート/議事録テンプレートを事前作成 → 作業時間を半減",
                        "継続クライアント5社 × 平均3万円 = 月15万円達成"
                    ],
                    ai_prompt=self._prompt("オンライン事務代行の専門家", "ココナラでレビュー5件獲得しました。オンライン事務代行サービスとして月額制で提供したいです。事務代行は初めてです。", ["オンライン事務代行の月額制プラン（ライト2万円/スタンダード4万円）のサービス内容を具体的に設計して", "ChatGPTで作るメール返信テンプレート10種類をコピペで使えるレベルで書いて", "クライアントに「月額制に切り替えませんか？」と提案するメッセージテンプレートを書いて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"🚀 支配フェーズ（7〜12週目）【{mbti_str}特別戦略】",
                    title="事務代行チーム化で月35万円の安定経営",
                    description="信頼と実績を基に事務代行をチーム化。あなたが管理者となり、スマホ1台で複数クライアントを運営します。",
                    tools=["Notion", "Chatwork", "ココナラ", "freeeアプリ", "Zoom"],
                    expected_outcome="目標: 月35万円の収益。管理者として効率的に運営。",
                    detailed_steps=[
                        "ココナラで事務代行スタッフを2名募集 → マニュアル（Notion）で教育",
                        "品質管理チェックリストを作成 → 全納品物をあなたが最終チェック",
                        "クライアント10社体制を構築 → スタッフ2名に作業分配 → あなたは管理に専念",
                        "売上50万円 - 外注費15万円 = 粗利35万円 → スマホ管理だけで月35万円達成",
                        "freeeアプリで経費・売上管理 → 確定申告もスムーズに"
                    ],
                    ai_prompt=self._prompt("事務代行チーム運営の専門家", "事務代行で月15万円稼いでいます。スタッフを2名雇ってチーム化したいです。人を雇うのは初めてです。", ["ココナラで事務代行スタッフを募集する文面をコピペで使えるレベルで書いて", "スタッフ向けの業務マニュアルの目次と主要な項目をNotionに作れるレベルで教えて", "10社のクライアントを2名のスタッフに振り分ける管理シートの作り方を教えて"], mbti_str),
                ),
            ]

        # =============================================
        # EXPLORERS（ISTP, ISFP, ESTP, ESFP）
        # 実践力・行動力・センス・エンタメ力が強み
        # =============================================
        if tribe == "EXPLORERS" and is_pc:
            return [
                RoadmapStep(
                    phase=f"🌱 覚醒フェーズ（1〜2週目）【{mbti_str}特別戦略】",
                    title="AI×動画・デザインで即行動、月5万円を手に入れる",
                    description="あなたの行動力とセンスを活かし、AIで動画編集やデザイン制作を爆速化。トレンドを掴んで即収益化します。",
                    tools=["CapCut（無料版）", "Canva（無料版）", "ChatGPT（無料版）", "ココナラ"],
                    expected_outcome="目標: 初月でレビュー5件獲得。制作スキルを収益化。",
                    detailed_steps=[
                        "CapCutをダウンロード（無料版あり・Pro版は月額約1,350円で全機能解放）→ AI自動字幕/AI背景除去/AIエフェクト機能を全て試す",
                        "Canva（無料版）でSNS投稿用テンプレートを10種類作成",
                        "ココナラで出品：『AIでSNS用ショート動画を編集します』→ まず1,500円で出品 → 納期1日 → ポートフォリオ兼ねてレビュー★5を集める",
                        "同時出品：『AIでロゴ・バナーをデザインします』→ まず1,000円で出品 → 納期1日",
                        "レビュー5件獲得後 → 動画5,000円/デザイン3,000円に値上げ → レビュー20件超で8,000円に",
                        "制作実績をInstagramに投稿 → ポートフォリオとして活用 → 直接依頼も獲得",
                        "💡 慣れてきたらCanva Pro（月額1,180円）やCapCut Pro（月額約1,350円）に課金すると素材・機能が無制限に"
                    ],
                    ai_prompt=self._prompt("AI副業の専門コンサルタント", "完全な初心者です。CapCut（無料版）とCanva（無料版）を使って、ココナラでショート動画編集サービスをまず1,500円で出品して最初のレビュー★5を5件集めたいです。", ["ココナラの出品タイトルと説明文をコピペで使えるレベルで書いて。1,500円でも「この人センスいい」と思わせる内容にして", "CapCut（無料版）のAI自動字幕・BGM追加を使った編集フローを初心者向けにゼロから教えて", "ポートフォリオ用のサンプル動画を作る手順を教えて。どんな内容の動画を何本作ればいいかも含めて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"⚡ 加速フェーズ（3〜6週目）【{mbti_str}特別戦略】",
                    title="ショート動画量産×AI編集で月30万円のコンテンツファクトリー",
                    description="TikTok/YouTube Shortsのトレンドを分析し、AI編集で量産体制を構築。バズるコンテンツを科学的に生み出します。",
                    tools=["CapCut Pro", "Runway ML（Standardプラン月$12〜）", "TikTok", "YouTube Studio"],
                    expected_outcome="目標: 月25〜30万円の収益。バズから収益につなげる仕組みを構築。",
                    detailed_steps=[
                        "TikTokのトレンドハッシュタグを毎日チェック → ChatGPTで台本を5本/日生成",
                        "Runway ML（Gen-4.5でテキストから動画生成）→ CapCut Proで編集 → 1本あたり制作時間15分に短縮",
                        "自分のTikTokアカウントで毎日3投稿 → 30日で90本 → 収益化条件（フォロワー1万人）達成",
                        "企業案件の動画制作受注：1本30,000円 → 月5件で15万円",
                        "TikTok収益5万円 + ココナラ10万円 + 企業案件15万円 = 月30万円達成"
                    ],
                    ai_prompt=self._prompt("TikTok/YouTube Shortsの専門家", "ココナラでレビュー5件獲得して値上げも済みました。自分のTikTokアカウントも育ててショート動画で稼ぎたいです。TikTokは初めてです。", ["TikTokアカウントの開設から最初の投稿までの手順をゼロから教えて", "今バズりやすいジャンルTOP5と、それぞれの台本テンプレートをコピペで使えるように書いて", "ChatGPTで毎日の台本を効率的に作るプロンプトを書いて"], mbti_str),
                ),
                RoadmapStep(
                    phase=f"🚀 支配フェーズ（7〜12週目）【{mbti_str}特別戦略】",
                    title="マルチプラットフォーム展開で月80万円のクリエイター経済",
                    description="動画・デザインスキルを複数プラットフォームで展開。AI活用の制作ノウハウ自体を商品化し、収益源を多角化します。",
                    tools=["Adobe Premiere Pro", "Midjourney", "Teachable", "Instagram", "YouTube"],
                    expected_outcome="目標: 月80万円の収益。クリエイターとしての多角化を目指す。",
                    detailed_steps=[
                        "YouTubeチャンネル開設 → 「AI動画編集テクニック」を週2本投稿 → 3ヶ月で登録者5,000人",
                        "Midjourneyで生成したAIアート作品をSUZURI/REDBUBBLEでグッズ販売 → 不労所得化",
                        "「AI動画編集マスター講座」をTeachable（Builderプラン月$89〜・取引手数料0%）で販売（19,800円）→ 月20人で39.6万円",
                        "企業のSNS運用代行（月額10万円）を3社契約 → 月30万円の安定収入",
                        "動画制作10万円 + 講座40万円 + SNS運用30万円 = 月80万円達成"
                    ],
                    ai_prompt=self._prompt("クリエイターエコノミーの専門家", "TikTokで月30万円稼いでいます。マルチプラットフォーム展開と講座販売で収益を増やしたいです。講座を作るのは初めてです。", ["同じ動画素材をYouTube/Instagram/TikTokに効率的に展開する具体的な手順", "「AI動画編集マスター講座」のカリキュラムを全8回分、各回のタイトルと内容を書いて", "企業のSNS運用代行（月額10万円）の提案書をコピペで使えるレベルで書いて"], mbti_str),
                ),
            ]

        # EXPLORERS × MOBILE
        return [
            RoadmapStep(
                phase=f"🌱 覚醒フェーズ（1〜2週目）【{mbti_str}特別戦略】",
                title="スマホ1台でショート動画クリエイター、月3万円を達成",
                description="あなたの行動力とセンスをスマホで全開に。CapCutアプリとAIで魅力的なショート動画を量産し、即収益化します。",
                tools=["CapCutアプリ", "ChatGPTアプリ", "TikTok", "Instagram Reels"],
                expected_outcome="目標: 初月でフォロワー1,000人獲得。スマホ1台でクリエイターデビュー。",
                detailed_steps=[
                    "TikTokアカウントを開設 → ジャンル決定（AI活用術/ライフハック/面白動画から1つ選択）",
                    "ChatGPTアプリで「バズるTikTok台本を5本考えて。ジャンルは〇〇」→ 毎日の台本を自動生成",
                    "CapCutアプリ（無料版でも基本編集可・Pro版月額約1,350円で全機能）で撮影→AI自動字幕→BGM追加→エフェクト → 1本10分で完成",
                    "毎日2〜3本投稿を30日継続 → フォロワー1,000人 → TikTok Creator Fund申請",
                    "同じ動画をInstagram Reelsにも投稿（クロスポスト）→ 収益源を2倍に",
                    "💡 慣れてきたらCapCut Pro（月額約1,350円）に課金すると全機能解放で編集効率UP"
                ],
                ai_prompt=self._prompt("スマホ動画クリエイターの専門家", "完全な初心者です。スマホ1台でTikTokとInstagram Reelsのショート動画を始めたいです。動画を作ったことがありません。", ["TikTokアカウントの開設からジャンル選びまでの手順を初心者向けに教えて。おすすめジャンルTOP3も", "ChatGPTアプリで「バズる台本」を作るプロンプトを5パターン書いて。コピペするだけで使えるように", "CapCutアプリで撮影→字幕→BGM→投稿までの手順を初めての人向けにゼロから教えて"], mbti_str),
            ),
            RoadmapStep(
                phase=f"⚡ 加速フェーズ（3〜6週目）【{mbti_str}特別戦略】",
                title="動画編集受注×ライブ配信で月15万円のエンタメビジネス",
                description="動画スキルを収益化しながら、ライブ配信で投げ銭収入も獲得。複数の収入源でリスク分散します。",
                tools=["CapCutアプリ", "ココナラアプリ", "TikTok LIVE", "17LIVE"],
                expected_outcome="目標: 月12〜15万円の収益。エンタメ力を活かす。",
                detailed_steps=[
                    "ココナラで『スマホで撮った動画をプロ品質に編集します』→ まず1,000円で出品 → 納期1日 → レビュー★5を集める",
                    "ココナラで実績ができたら、クラウドワークスにも動画編集サービスを出品 → 企業案件が多く単価アップを狙える",
                    "TikTokフォロワー3,000人達成 → LIVE配信を週3回開始 → 投げ銭収入を獲得",
                    "LIVE配信テーマ：「AI使ってリアルタイムで○○作ってみた」→ エンタメ性で差別化",
                    "ココナラ月10件5万円 + TikTok収益3万円 + LIVE投げ銭5万円 + アフィリエイト2万円 = 月15万円",
                    "人気動画のパターンを分析 → ChatGPTで台本を最適化 → 再現性のあるバズを狙う"
                ],
                ai_prompt=self._prompt("スマホ動画収益化の専門家", "TikTokでフォロワー1,000人達成しました。動画編集の受注とライブ配信で稼ぎたいです。ココナラもライブ配信も初めてです。", ["ココナラで「スマホで動画をプロ品質に編集します」の出品テンプレートをコピペで使えるように書いて", "TikTok LIVEの始め方をゼロから教えて。投げ銭をもらうコツも", "「AIで○○作ってみた」のライブ配信企画を5つ、台本付きで書いて"], mbti_str),
            ),
            RoadmapStep(
                phase=f"🚀 支配フェーズ（7〜12週目）【{mbti_str}特別戦略】",
                title="インフルエンサー×プロデュースで月40万円",
                description="フォロワー1万人を達成し、企業案件とプロデュース業で大きく稼ぐ。あなたのエンタメ力で人を巻き込みます。",
                tools=["TikTok", "Instagram", "LINE公式", "Brain", "STORES"],
                expected_outcome="目標: 月40万円の収益。影響力を収益につなげる。",
                detailed_steps=[
                    "TikTokフォロワー1万人達成 → 企業PR案件の受注開始（1件3〜5万円）",
                    "「スマホ動画編集術」のBrain教材を販売（4,980円）→ アフィリエイト機能で拡散",
                    "動画編集初心者向けのLINEグループコンサル（月額2,980円）を開始",
                    "企業案件月3件15万円 + Brain月30部15万円 + コンサル20人6万円 + その他4万円 = 月40万円",
                    "コンテンツの型をテンプレート化 → 新ジャンルにも即展開できる体制を構築"
                ],
                ai_prompt=self._prompt("インフルエンサービジネスの専門家", "TikTokフォロワー1万人で月15万円稼いでいます。企業案件と教材販売を始めたいです。どちらも初めてです。", ["企業にPR案件を提案するDMテンプレートをコピペで使えるレベルで書いて", "Brain教材「スマホ動画編集術」の目次と販売ページの文章をそのまま使えるレベルで書いて", "ファンコミュニティ（月額2,980円）の設計と集客方法を初心者向けに教えて"], mbti_str),
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
                tool_name="Oracle Engine Phase 2 - AI副業自動化ツール",
                progress_percentage=75,
                time_saved="月40時間の作業を自動化し、収益を3倍に",
                key_features=[
                    "ChatGPT API自動連携",
                    "ココナラ案件自動取得・納品",
                    "トレンド自動分析",
                    "収益レポート自動生成"
                ],
                availability="2026年4月リリース予定 | 先行予約受付中"
            ),
            disclaimer="""【重要な免責事項】

本診断結果は教育・情報提供を目的としたものであり、投資助言や確実な収益を保証するものではありません。

・AI副業の収益は個人の努力、スキル、市場状況により大きく異なります
・提示された金額は目標値であり、達成を保証するものではありません
・実際の取り組みにあたっては、ご自身の判断と責任で行ってください
・税務・法務に関する相談は専門家にご確認ください

Created by 高嶺泰志""",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
