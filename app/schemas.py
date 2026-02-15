"""
Oracle Engine - Phase 1: Data Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Optional
from enum import Enum


class MBTIType(str, Enum):
    """16 MBTI Personality Types"""
    INTJ = "INTJ"
    INTP = "INTP"
    ENTJ = "ENTJ"
    ENTP = "ENTP"
    INFJ = "INFJ"
    INFP = "INFP"
    ENFJ = "ENFJ"
    ENFP = "ENFP"
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    ESTP = "ESTP"
    ESFP = "ESFP"


class DeviceType(str, Enum):
    """User's primary device"""
    PC_MAC = "PC_MAC"
    PC_WINDOWS = "PC_WINDOWS"
    MOBILE_ONLY = "MOBILE_ONLY"


class ArchetypeType(str, Enum):
    """8 Business Archetypes"""
    ARCHITECT = "ARCHITECT"  # INTJ, INTP - システム設計者
    COMMANDER = "COMMANDER"  # ENTJ, ESTJ - 統率者
    HACKER = "HACKER"  # ENTP, ESTP - 実験的破壊者
    VISIONARY = "VISIONARY"  # INFJ, ENFJ - 理想主義者
    CREATOR = "CREATOR"  # INFP, ENFP - クリエイター
    GUARDIAN = "GUARDIAN"  # ISTJ, ISFJ - 堅実な実行者
    PERFORMER = "PERFORMER"  # ESFP, ESFJ - エンターテイナー
    CRAFTSMAN = "CRAFTSMAN"  # ISTP, ISFP - 職人


class PsychometricQuestion(BaseModel):
    """Single psychometric assessment question"""
    id: int = Field(..., description="質問ID")
    text: str = Field(..., description="質問文")
    scale_low: str = Field(..., description="1-2の場合の意味")
    scale_high: str = Field(..., description="4-5の場合の意味")


class PsychometricResponse(BaseModel):
    """User's response to psychometric questions"""
    question_id: int = Field(..., ge=1, le=5)
    score: int = Field(..., ge=1, le=5)


class DiagnosisRequest(BaseModel):
    """Initial diagnosis request"""
    mbti: MBTIType = Field(..., description="ユーザーのMBTIタイプ")
    device: DeviceType = Field(..., description="使用デバイス")
    psychometric_responses: Optional[List[PsychometricResponse]] = Field(
        default=None,
        description="心理測定の回答（5問）"
    )


class TrendData(BaseModel):
    """Latest AI business trend"""
    title: str
    snippet: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class RoadmapStep(BaseModel):
    """Single step in the strategic roadmap with concrete action items"""
    phase: str = Field(..., description="Phase名（例: Week 1-2）")
    title: str = Field(..., description="ステップのタイトル")
    description: str = Field(..., description="具体的な行動内容")
    tools: List[str] = Field(..., description="使用ツール・技術")
    expected_outcome: str = Field(..., description="期待される成果")
    detailed_steps: List[str] = Field(
        default_factory=lambda: [
            "ステップ1: 必要なツールをインストールまたは登録する",
            "ステップ2: 基本的な設定を完了させる",
            "ステップ3: 最初のコンテンツを作成する"
        ],
        description="超具体的な作業手順（最低3〜7ステップ、必ず生成すること）"
    )
    ai_prompt: str = Field(
        default="",
        description="このステップを進めるためにAIに送る推奨プロンプト"
    )


class AutomationTeaser(BaseModel):
    """Future automation tool teaser"""
    tool_name: str = Field(..., description="開発中ツールの名称")
    progress_percentage: int = Field(..., ge=0, le=100)
    key_features: List[str] = Field(..., description="主要機能")
    time_saved: str = Field(..., description="節約できる時間（例: 90%の作業を自動化）")
    availability: str = Field(..., description="リリース予定時期")


class DiagnosisResult(BaseModel):
    """Complete diagnosis result"""
    archetype: ArchetypeType = Field(..., description="割り当てられたビジネスアーキタイプ")
    archetype_description: str = Field(..., description="アーキタイプの詳細説明")
    
    strengths: List[str] = Field(..., description="ビジネス上の強み（3-5項目）")
    weaknesses: List[str] = Field(..., description="ビジネス上の弱み（3-5項目）")
    
    psychometric_insight: Optional[str] = Field(
        default=None,
        description="心理測定結果に基づく洞察"
    )
    
    latest_trends: List[TrendData] = Field(..., description="2026年2月時点の最新トレンド")
    
    strategic_roadmap: List[RoadmapStep] = Field(
        ...,
        description="デバイスに最適化された3ヶ月ロードマップ"
    )
    
    automation_teaser: AutomationTeaser = Field(
        ...,
        description="開発中の自動化ツール情報"
    )
    
    disclaimer: str = Field(
        ...,
        description="透明性の高い免責事項とアクションの緊急性"
    )
    
    timestamp: str = Field(..., description="診断実行時刻（ISO 8601）")


class PsychometricQuestionsResponse(BaseModel):
    """Response containing psychometric questions for a specific MBTI"""
    mbti: MBTIType
    questions: List[PsychometricQuestion]
