#!/usr/bin/env python3
"""
Oracle Engine - Test Script
Quick test to verify the system works correctly
"""
import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("1. Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_get_questions():
    """Test psychometric questions endpoint"""
    print_section("2. Get Psychometric Questions (ENTP)")
    
    response = requests.get(f"{BASE_URL}/questions/ENTP")
    print(f"Status: {response.status_code}")
    
    data = response.json()
    print(f"\nMBTI: {data['mbti']}")
    print(f"Questions ({len(data['questions'])}):")
    
    for i, q in enumerate(data['questions'], 1):
        print(f"\n  Q{i}: {q['question']}")
        print(f"      Low (1-2): {q['scale_low']}")
        print(f"      High (4-5): {q['scale_high']}")


def test_full_diagnosis(mbti: str = "ENTP", device: str = "PC_MAC"):
    """Test full diagnosis endpoint"""
    print_section(f"3. Full Diagnosis ({mbti} + {device})")
    
    payload = {
        "mbti": mbti,
        "device": device,
        "psychometric_responses": [
            {"question_id": 1, "score": 5},
            {"question_id": 2, "score": 4},
            {"question_id": 3, "score": 5},
            {"question_id": 4, "score": 4},
            {"question_id": 5, "score": 3}
        ]
    }
    
    print("Sending diagnosis request...")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    response = requests.post(
        f"{BASE_URL}/diagnose",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"🎯 Archetype: {result['archetype']}")
        print(f"📝 Description: {result['archetype_description'][:100]}...")
        
        print(f"\n✅ Strengths ({len(result['strengths'])}):")
        for s in result['strengths'][:3]:
            print(f"   • {s}")
        
        print(f"\n⚠️  Weaknesses ({len(result['weaknesses'])}):")
        for w in result['weaknesses'][:3]:
            print(f"   • {w}")
        
        if result.get('psychometric_insight'):
            print(f"\n🧠 Psychometric Insight:")
            print(f"   {result['psychometric_insight'][:150]}...")
        
        print(f"\n📰 Latest Trends ({len(result['latest_trends'])}):")
        for trend in result['latest_trends'][:3]:
            print(f"   • [{trend['relevance_score']:.2f}] {trend['title'][:60]}...")
        
        print(f"\n🗺️  Strategic Roadmap ({len(result['strategic_roadmap'])} steps):")
        for step in result['strategic_roadmap']:
            print(f"\n   {step['phase']}: {step['title']}")
            print(f"   Tools: {', '.join(step['tools'][:3])}...")
            print(f"   Outcome: {step['expected_outcome'][:80]}...")
        
        print(f"\n🛠️  Automation Teaser:")
        teaser = result['automation_teaser']
        print(f"   Tool: {teaser['tool_name']}")
        print(f"   Progress: {teaser['progress_percentage']}%")
        print(f"   Time Saved: {teaser['time_saved']}")
        print(f"   Availability: {teaser['availability']}")
        print(f"   Features ({len(teaser['key_features'])}):")
        for feature in teaser['key_features'][:3]:
            print(f"      • {feature}")
        
        print(f"\n⚖️  Disclaimer:")
        print(f"   {result['disclaimer'][:200]}...")
        
        print(f"\n⏰ Timestamp: {result['timestamp']}")
        
    else:
        print(f"Error: {response.text}")


def test_archetypes():
    """Test archetypes endpoint"""
    print_section("4. Get All Archetypes")
    
    response = requests.get(f"{BASE_URL}/archetypes")
    print(f"Status: {response.status_code}")
    
    archetypes = response.json()
    print(f"\nTotal Archetypes: {len(archetypes)}\n")
    
    for name, data in list(archetypes.items())[:3]:
        print(f"  {name}:")
        print(f"    {data['description'][:80]}...")
        print(f"    Strengths: {len(data['strengths'])}")
        print(f"    Weaknesses: {len(data['weaknesses'])}")
        print()


def test_mbti_mapping():
    """Test MBTI mapping endpoint"""
    print_section("5. MBTI to Archetype Mapping")
    
    response = requests.get(f"{BASE_URL}/mbti-mapping")
    print(f"Status: {response.status_code}\n")
    
    mapping = response.json()
    
    # Group by archetype
    by_archetype = {}
    for mbti, archetype in mapping.items():
        if archetype not in by_archetype:
            by_archetype[archetype] = []
        by_archetype[archetype].append(mbti)
    
    for archetype, mbtis in by_archetype.items():
        print(f"  {archetype}: {', '.join(mbtis)}")


def main():
    """Run all tests"""
    print("\n" + "🚀" * 40)
    print("  ORACLE ENGINE - PHASE 1 - TEST SUITE")
    print("  Created by: 高嶺泰志 (Target: 年収10億円)")
    print("🚀" * 40)
    
    try:
        test_health_check()
        test_get_questions()
        test_archetypes()
        test_mbti_mapping()
        test_full_diagnosis(mbti="ENTP", device="PC_MAC")
        
        print_section("✅ ALL TESTS COMPLETED")
        print("The Oracle Engine is fully operational!")
        print("\nNext: Start server with 'uvicorn app.main:app --reload'")
        print("Then access http://localhost:8000/docs for interactive API docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("\nPlease start the server first:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
