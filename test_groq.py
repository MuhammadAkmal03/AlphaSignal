"""
Test script to verify Groq API connectivity
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    print(f"✓ GROQ_API_KEY found (length: {len(groq_key)})")
    print(f"  First 10 chars: {groq_key[:10]}...")
    
    # Test Groq API
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'Hello, AlphaSignal!' in one sentence."}
            ],
            max_tokens=50
        )
        
        print("\n✓ Groq API Test Successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\n✗ Groq API Test Failed: {e}")
else:
    print("✗ GROQ_API_KEY not found in environment")
    print("  Make sure .env file exists with GROQ_API_KEY=your_key")
