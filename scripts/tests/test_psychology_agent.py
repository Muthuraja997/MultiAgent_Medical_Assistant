"""
Test script for Psychology Assistant Agent
Tests the MentalBERT integration and response generation
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from agents.psychology_agent import PsychologyAssistant

def test_psychology_agent():
    """Test the Psychology Assistant with various queries."""
    
    print("="*80)
    print("PSYCHOLOGY ASSISTANT AGENT - TEST SUITE")
    print("="*80)
    print()
    
    # Initialize the assistant
    print("Initializing Psychology Assistant...")
    assistant = PsychologyAssistant()
    print("✅ Assistant initialized successfully!")
    print()
    
    # Test queries covering different mental health categories
    test_queries = [
        {
            "query": "I've been feeling really anxious lately and can't sleep well",
            "expected_category": "anxiety"
        },
        {
            "query": "I feel so sad all the time, nothing makes me happy anymore",
            "expected_category": "depression"
        },
        {
            "query": "I'm so stressed with work deadlines and family responsibilities",
            "expected_category": "stress"
        },
        {
            "query": "Can you help me understand PTSD symptoms?",
            "expected_category": "ptsd"
        },
        {
            "query": "I just want to talk to someone about my mental health",
            "expected_category": "general_mental_health"
        }
    ]
    
    # Run tests
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}")
        print(f"{'='*80}")
        print(f"\n📝 User Query: {test['query']}")
        print(f"🎯 Expected Category: {test['expected_category']}")
        print("\n" + "-"*80)
        
        try:
            # Process the query
            result = assistant.process_query(test['query'])
            
            # Display analysis
            print(f"\n🧠 Mental State Analysis:")
            mental_state = result.get('mental_state_analysis', {})
            for category, score in sorted(mental_state.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"   - {category:25s}: {score:.2%}")
            
            print(f"\n🎯 Primary Concern: {result.get('primary_concern', 'N/A')} "
                  f"(confidence: {result.get('concern_confidence', 0):.2%})")
            
            # Crisis assessment
            crisis = result.get('crisis_assessment', {})
            if crisis.get('is_crisis', False):
                print(f"\n⚠️  CRISIS DETECTED - Suicide Risk Score: {crisis.get('suicide_risk_score', 0):.2%}")
            else:
                print(f"\n✅ No crisis detected")
            
            # Display response (truncated)
            response = result.get('response', '')
            print(f"\n💬 Agent Response:")
            print("-"*80)
            response_preview = response[:300] + "..." if len(response) > 300 else response
            print(response_preview)
            print("-"*80)
            
            print(f"\n✅ Test {i} completed successfully")
            
        except Exception as e:
            print(f"\n❌ Test {i} failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Crisis detection test
    print(f"\n\n{'='*80}")
    print("CRISIS DETECTION TEST")
    print(f"{'='*80}")
    crisis_query = "I don't want to live anymore, I can't take this"
    print(f"\n📝 Crisis Query: {crisis_query}")
    
    try:
        result = assistant.process_query(crisis_query)
        crisis = result.get('crisis_assessment', {})
        
        print(f"\n⚠️  Crisis Assessment:")
        print(f"   - Is Crisis: {crisis.get('is_crisis', False)}")
        print(f"   - Suicide Risk: {crisis.get('suicide_risk_score', 0):.2%}")
        print(f"   - Recommendation: {crisis.get('recommendation', 'N/A')}")
        
        print(f"\n💬 Emergency Response:")
        print("-"*80)
        print(result.get('response', '')[:400] + "...")
        print("-"*80)
        
        if crisis.get('is_crisis', False):
            print(f"\n✅ Crisis correctly detected!")
        else:
            print(f"\n⚠️  Warning: Crisis not detected!")
            
    except Exception as e:
        print(f"\n❌ Crisis test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n\n{'='*80}")
    print("TEST SUITE COMPLETED")
    print(f"{'='*80}")
    print("\n✅ All tests finished. Check results above.")
    print("\n💡 Note: MentalBERT model downloads on first run (may take time)")
    print("💡 Fallback responses are used if model loading fails")
    print()

if __name__ == "__main__":
    test_psychology_agent()
