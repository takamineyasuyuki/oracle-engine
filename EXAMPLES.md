# Oracle Engine - API Usage Examples

## Quick Test Examples

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Get Questions for ENTP
```bash
curl http://localhost:8000/questions/ENTP
```

### 3. Full Diagnosis - ENTP + PC (Mac)
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

### 4. Full Diagnosis - INTJ + Mobile
```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "mbti": "INTJ",
    "device": "MOBILE_ONLY",
    "psychometric_responses": [
      {"question_id": 1, "score": 5},
      {"question_id": 2, "score": 5},
      {"question_id": 3, "score": 4},
      {"question_id": 4, "score": 5},
      {"question_id": 5, "score": 4}
    ]
  }'
```

### 5. Full Diagnosis - ENFP + PC (Windows)
```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "mbti": "ENFP",
    "device": "PC_WINDOWS",
    "psychometric_responses": [
      {"question_id": 1, "score": 4},
      {"question_id": 2, "score": 3},
      {"question_id": 3, "score": 2},
      {"question_id": 4, "score": 4},
      {"question_id": 5, "score": 3}
    ]
  }'
```

### 6. Get All Archetypes
```bash
curl http://localhost:8000/archetypes
```

### 7. Get MBTI Mapping
```bash
curl http://localhost:8000/mbti-mapping
```

---

## Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Step 1: Get questions
response = requests.get(f"{BASE_URL}/questions/ENTP")
questions = response.json()
print(json.dumps(questions, indent=2, ensure_ascii=False))

# Step 2: User answers questions (simulate)
psychometric_responses = [
    {"question_id": 1, "score": 5},
    {"question_id": 2, "score": 4},
    {"question_id": 3, "score": 5},
    {"question_id": 4, "score": 4},
    {"question_id": 5, "score": 3}
]

# Step 3: Get full diagnosis
diagnosis_request = {
    "mbti": "ENTP",
    "device": "PC_MAC",
    "psychometric_responses": psychometric_responses
}

response = requests.post(
    f"{BASE_URL}/diagnose",
    json=diagnosis_request
)

result = response.json()

print(f"\n🎯 Archetype: {result['archetype']}")
print(f"\n📰 Latest Trends:")
for trend in result['latest_trends']:
    print(f"  • {trend['title']}")

print(f"\n🛠️  Automation Tool: {result['automation_teaser']['tool_name']}")
print(f"   Progress: {result['automation_teaser']['progress_percentage']}%")
```

---

## JavaScript/TypeScript Client Example

```javascript
const BASE_URL = "http://localhost:8000";

async function getDiagnosis(mbti, device, responses) {
  const response = await fetch(`${BASE_URL}/diagnose`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      mbti: mbti,
      device: device,
      psychometric_responses: responses
    })
  });
  
  const result = await response.json();
  return result;
}

// Usage
const diagnosis = await getDiagnosis("ENTP", "PC_MAC", [
  {question_id: 1, score: 5},
  {question_id: 2, score: 4},
  {question_id: 3, score: 5},
  {question_id: 4, score: 4},
  {question_id: 5, score: 3}
]);

console.log("Archetype:", diagnosis.archetype);
console.log("Roadmap steps:", diagnosis.strategic_roadmap.length);
console.log("Automation tool:", diagnosis.automation_teaser.tool_name);
```

---

## Test All 16 MBTI Types

```bash
# Loop through all MBTI types
for mbti in INTJ INTP ENTJ ENTP INFJ INFP ENFJ ENFP ISTJ ISFJ ESTJ ESFJ ISTP ISFP ESTP ESFP
do
  echo "Testing $mbti..."
  curl -X POST http://localhost:8000/diagnose \
    -H "Content-Type: application/json" \
    -d "{
      \"mbti\": \"$mbti\",
      \"device\": \"PC_MAC\",
      \"psychometric_responses\": [
        {\"question_id\": 1, \"score\": 4},
        {\"question_id\": 2, \"score\": 4},
        {\"question_id\": 3, \"score\": 3},
        {\"question_id\": 4, \"score\": 4},
        {\"question_id\": 5, \"score\": 3}
      ]
    }" | jq '.archetype'
  echo ""
done
```

---

## Expected Server Logs

When you run a diagnosis, you should see logs like:

```
2026-02-13 10:30:00 - INFO - ================================================================================
2026-02-13 10:30:00 - INFO - 📊 NEW DIAGNOSIS REQUEST
2026-02-13 10:30:00 - INFO -    MBTI: ENTP
2026-02-13 10:30:00 - INFO -    Device: PC_MAC
2026-02-13 10:30:00 - INFO -    Archetype: HACKER
2026-02-13 10:30:00 - INFO -    Psychometric: Completed
2026-02-13 10:30:00 - INFO - ================================================================================
2026-02-13 10:30:01 - INFO - Searching latest AI business trends...
2026-02-13 10:30:05 - INFO - Found 8 unique trend results
2026-02-13 10:30:05 - INFO - Generating strategic roadmap...
2026-02-13 10:30:05 - INFO - ✅ Diagnosis completed successfully
2026-02-13 10:30:05 - INFO -    Trends found: 5
2026-02-13 10:30:05 - INFO -    Roadmap steps: 4
2026-02-13 10:30:05 - INFO -    Automation tool: Factory5.py - HACKER Edition (85%)
2026-02-13 10:30:05 - INFO - ================================================================================
```
