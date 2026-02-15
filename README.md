# The Oracle Engine - Phase 1

**年収10億円を目指す起業家・高嶺泰志専属のLead AI Architect**

MBTI診断をフックに、ユーザーの性格と環境（PC/スマホ）に合わせた「最新の稼ぎ方」を提示し、将来の自動化ツールへの渇望感を作る【Phase 1】エンジン。

---

## 🎯 Business Logic

1. **Entrance**: 16タイプからユーザーのMBTIを選択
2. **The Filter**: PC（Mac/Win）所有の確認
3. **Psychometric Audit**: MBTIに基づく5問のビジネス特性診断（1-5スケール）
4. **Real-Time Trend Search**: DuckDuckGoで2026年2月の最新AI副業トレンドを取得
5. **Strategic Roadmap**: 
   - **PCユーザー**: Python等を使った仕組み化ロードマップ
   - **スマホユーザー**: ブラウザ/アプリ駆使のクラウド完結型ロードマップ
6. **Candid Disclaimer & The Tease**: 
   - 情報鮮度の短さと責任の透明性開示
   - 専用自動化ツール（開発進捗80%〜）の予告

---

## 🚀 Quick Start (MacBook Air M1)

### 1. 環境構築

```bash
# プロジェクトディレクトリに移動
cd oracle_engine

# 仮想環境作成（推奨）
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. サーバー起動

```bash
# FastAPIサーバーを起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

サーバーが起動したら、以下のURLにアクセス:
- **API ドキュメント**: http://localhost:8000/docs
- **Root**: http://localhost:8000/

### 3. API使用例

#### 3.1 心理測定質問の取得

```bash
curl http://localhost:8000/questions/ENTP
```

#### 3.2 完全診断の実行

```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "mbti": "ENTP",
    "device": "PC_MAC",
    "psychometric_responses": [
      {"question_id": 1, "score": 5},
      {"question_id": 2, "score": 4},
      {"question_id": 3, "score": 5},
      {"question_id": 4, "score": 4},
      {"question_id": 5, "score": 3}
    ]
  }'
```

---

## 📊 8つのビジネスアーキタイプ

| MBTI | Archetype | 特徴 |
|------|-----------|------|
| INTJ, INTP | **ARCHITECT** | システム設計者 - 論理的思考と長期戦略 |
| ENTJ, ESTJ | **COMMANDER** | 統率者 - リーダーシップと決断力 |
| ENTP, ESTP | **HACKER** | 実験的破壊者 - グロースハックと革新 |
| INFJ, ENFJ | **VISIONARY** | 理想主義者 - 社会的インパクト重視 |
| INFP, ENFP | **CREATOR** | クリエイター - オリジナルコンテンツ創造 |
| ISTJ, ISFJ | **GUARDIAN** | 堅実な実行者 - 計画的で着実 |
| ESFP, ESFJ | **PERFORMER** | エンターテイナー - カリスマとエンゲージメント |
| ISTP, ISFP | **CRAFTSMAN** | 職人 - 技術追求と品質重視 |

---

## 🛠️ API Endpoints

### GET `/`
Root endpoint - システム情報

### GET `/health`
ヘルスチェック

### GET `/questions/{mbti}`
指定されたMBTIタイプの心理測定質問5問を取得

**Parameters:**
- `mbti`: MBTI type (e.g., ENTP, INTJ, ENFP)

**Response:**
```json
{
  "mbti": "ENTP",
  "questions": [
    {
      "question": "既存のルールや常識を破ることに、どの程度の抵抗感がありますか?",
      "scale_low": "慎重に従う",
      "scale_high": "積極的に破壊する"
    },
    ...
  ]
}
```

### POST `/diagnose`
完全なビジネス診断を実行

**Request Body:**
```json
{
  "mbti": "ENTP",
  "device": "PC_MAC",
  "psychometric_responses": [
    {"question_id": 1, "score": 5},
    {"question_id": 2, "score": 4},
    {"question_id": 3, "score": 5},
    {"question_id": 4, "score": 4},
    {"question_id": 5, "score": 3}
  ]
}
```

**Device Options:**
- `PC_MAC`: Mac所有
- `PC_WINDOWS`: Windows所有
- `MOBILE_ONLY`: スマホのみ

**Response:**
```json
{
  "archetype": "HACKER",
  "archetype_description": "【The Hacker - 実験的破壊者】...",
  "strengths": ["革新的なアイデアの創出", ...],
  "weaknesses": ["持続性と一貫性の欠如", ...],
  "psychometric_insight": "典型的なハッカーマインド...",
  "latest_trends": [
    {
      "title": "AI副業 2026年最新トレンド",
      "snippet": "...",
      "relevance_score": 0.85
    },
    ...
  ],
  "strategic_roadmap": [
    {
      "phase": "Week 1-2: ハックツール構築",
      "title": "グロースハック自動化システム",
      "description": "Selenium/Playwrightで...",
      "tools": ["Selenium", "Playwright", ...],
      "expected_outcome": "1週間でTwitterフォロワー1000人増加"
    },
    ...
  ],
  "automation_teaser": {
    "tool_name": "Factory5.py - HACKER Edition",
    "progress_percentage": 85,
    "key_features": ["ワンクリックでAI APIを統合", ...],
    "time_saved": "現在のロードマップの90%の作業時間を削減",
    "availability": "2026年3月中旬リリース予定"
  },
  "disclaimer": "【重要な免責事項と行動の緊急性】...",
  "timestamp": "2026-02-13T10:30:00Z"
}
```

### GET `/archetypes`
全アーキタイプのプロフィールを取得

### GET `/mbti-mapping`
MBTI → Archetype のマッピングを取得

---

## 📁 Project Structure

```
oracle_engine/
├── app/
│   ├── __init__.py       # Package initialization
│   ├── main.py           # FastAPI application
│   ├── engine.py         # Core business logic
│   ├── schemas.py        # Pydantic models
│   └── tools.py          # DuckDuckGo search integration
├── requirements.txt      # Dependencies
└── README.md            # This file
```

---

## 🔍 Key Features

### ✅ 完全実装済み（省略なし）

1. **16 MBTI → 8 Archetype マッピング**: 全タイプに対応
2. **心理測定質問**: 各アーキタイプごとに5問のカスタマイズ質問
3. **リアルタイムトレンド検索**: DuckDuckGoで最新AI副業情報を取得
4. **デバイス別ロードマップ**: PC（Python重視）とスマホ（ノーコード重視）
5. **自動化ツール予告**: 開発中ツールの具体的な機能と進捗
6. **透明な免責事項**: 情報鮮度の短さとアクションの緊急性を明示

### 🎯 ビジネス目標との整合性

- **Phase 1の目的**: ユーザーに「最新の稼ぎ方」を提示し、自動化ツールへの渇望感を作る
- **収益化へのパス**: 診断で興味を引き → ロードマップで信頼を得る → 自動化ツール販売へ誘導
- **スケーラビリティ**: API化により、Webアプリ、モバイルアプリ、チャットボット等に展開可能

---

## 🧪 Testing

### サーバーログの確認

サーバーを起動すると、以下のようなログが出力されます:

```
2026-02-13 10:30:00 - INFO - 🚀 Oracle Engine - Phase 1 starting up...
2026-02-13 10:30:00 - INFO - ============================================================
2026-02-13 10:30:00 - INFO - System initialized by: 高嶺泰志 (Target: 年収10億円)
2026-02-13 10:30:00 - INFO - Mission: MBTI-based AI business strategy engine
2026-02-13 10:30:00 - INFO - ============================================================
```

診断リクエストが来ると:

```
2026-02-13 10:31:00 - INFO - ================================================================================
2026-02-13 10:31:00 - INFO - 📊 NEW DIAGNOSIS REQUEST
2026-02-13 10:31:00 - INFO -    MBTI: ENTP
2026-02-13 10:31:00 - INFO -    Device: PC_MAC
2026-02-13 10:31:00 - INFO -    Archetype: HACKER
2026-02-13 10:31:00 - INFO -    Psychometric: Completed
2026-02-13 10:31:00 - INFO - ================================================================================
```

---

## 🚨 Important Notes

### DuckDuckGo Search について

`duckduckgo-search` は外部API不要で、リアルタイムにWeb検索を実行します。ただし:

- **レート制限**: 短時間に大量のリクエストを送るとブロックされる可能性
- **結果の変動**: 検索結果は時間とともに変化
- **ネットワーク必須**: インターネット接続が必要

### プロダクション運用時の推奨事項

1. **キャッシング**: 検索結果をRedisやMemcachedでキャッシュ
2. **レート制限**: ユーザーごとの診断回数制限
3. **非同期処理**: Celeryなどでバックグラウンドジョブ化
4. **モニタリング**: Sentry、DataDog等でエラー追跡

---

## 🎬 Next Steps (Phase 2以降)

1. **フロントエンド構築**: React/Vue.jsでユーザーインターフェース
2. **認証システム**: JWTベースのユーザー管理
3. **決済統合**: Stripe連携で自動化ツールの販売
4. **メール自動化**: 診断結果をメールで送信、リマーケティング
5. **Factory5.pyの実装**: 予告していた自動化ツールの実装

---

## 📝 License

Proprietary - 高嶺泰志 (All Rights Reserved)

---

## 👤 Contact

**Creator**: 高嶺泰志  
**Mission**: 年収10億円への道筋を示す  
**Role**: Lead AI Architect

---

**🔥 今すぐ行動を開始してください。情報の価値は時間とともに減少します。**
