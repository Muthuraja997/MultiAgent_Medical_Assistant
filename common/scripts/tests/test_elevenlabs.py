#!/usr/bin/env python3
"""
Test ElevenLabs API Integration

This script verifies that:
1. API key is loaded from .env
2. ElevenLabs client is properly initialized
3. Text-to-speech endpoint works
"""

import os
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from config import Config

# Load environment variables
load_dotenv()

print("=" * 70)
print("🔊 ELEVENLABS API INTEGRATION TEST")
print("=" * 70)

# Test 1: Check if API key is loaded
print("\n[1/5] Checking if ElevenLabs API key is configured...")
api_key = os.getenv("ELEVEN_LABS_API_KEY")

if not api_key:
    print("❌ ERROR: ELEVEN_LABS_API_KEY not found in .env file!")
    print("   Make sure you added: ELEVEN_LABS_API_KEY=sk_...")
    sys.exit(1)
else:
    # Mask the key for security
    masked_key = api_key[:10] + "..." + api_key[-10:]
    print(f"✅ API Key found: {masked_key}")

# Test 2: Load configuration
print("\n[2/5] Loading configuration...")
try:
    config = Config()
    print(f"✅ Config loaded successfully")
except Exception as e:
    print(f"❌ ERROR loading config: {e}")
    sys.exit(1)

# Test 3: Check SpeechConfig
print("\n[3/5] Checking SpeechConfig...")
try:
    speech_config = config.speech
    print(f"✅ SpeechConfig initialized")
    print(f"   - API Key: {speech_config.eleven_labs_api_key[:10]}...{speech_config.eleven_labs_api_key[-10:] if speech_config.eleven_labs_api_key else 'None'}")
    print(f"   - Voice ID: {speech_config.eleven_labs_voice_id}")
    
    if not speech_config.eleven_labs_api_key:
        print("❌ ERROR: eleven_labs_api_key is None!")
        sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Test 4: Test ElevenLabs API connection
print("\n[4/5] Testing ElevenLabs API connection...")
try:
    import requests
    
    elevenlabs_url = f"https://api.elevenlabs.io/v1/text-to-speech/{speech_config.eleven_labs_voice_id}/stream"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": speech_config.eleven_labs_api_key
    }
    payload = {
        "text": "Hello, this is a test of the ElevenLabs API.",
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    response = requests.post(elevenlabs_url, headers=headers, json=payload, timeout=10)
    
    if response.status_code == 200:
        print(f"✅ ElevenLabs API responded successfully (HTTP {response.status_code})")
        print(f"   - Audio file size: {len(response.content)} bytes")
        
        # Try to save the audio for manual testing
        os.makedirs("./uploads/speech", exist_ok=True)
        with open("./uploads/speech/test_audio.mp3", "wb") as f:
            f.write(response.content)
        print(f"   - Test audio saved to: ./uploads/speech/test_audio.mp3")
    else:
        print(f"❌ ERROR: ElevenLabs API returned status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR connecting to ElevenLabs API: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Summary
print("\n[5/5] Test Summary")
print("=" * 70)
print("✅ All tests passed!")
print("\nWhat's working:")
print("  ✓ ElevenLabs API key is configured")
print("  ✓ SpeechConfig is loaded correctly")
print("  ✓ ElevenLabs API connection is working")
print("  ✓ Text-to-speech generation is successful")
print("\nYour voice feature is ready to use!")
print("=" * 70)
