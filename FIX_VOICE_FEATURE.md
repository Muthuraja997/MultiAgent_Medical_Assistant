## 🔊 Voice Feature Fix Guide - Permission Error

### ❌ Problem Found

**Error**: The ElevenLabs API key is missing the `text_to_speech` permission

**Status Code**: 401 Unauthorized

**Response**: 
```json
{
  "detail": {
    "status": "missing_permissions",
    "message": "The API key you used is missing the permission text_to_speech to execute this operation."
  }
}
```

---

## ✅ Solution: Get a Proper ElevenLabs API Key

### Option 1: Create a New API Key with Correct Permissions (Recommended)

1. **Go to ElevenLabs**: https://elevenlabs.io/
2. **Sign Up or Login**
3. **Go to API Settings**: https://elevenlabs.io/app/keys
4. **Create a New API Key**:
   - Click "Create New API Key"
   - Select **ALL permissions** (especially `text_to_speech`)
   - Give it a name like "Medical Assistant"
   - Copy the key

5. **Update .env file**:
   ```bash
   # Replace the old key with the new one
   ELEVEN_LABS_API_KEY=sk_new_key_here
   ```

6. **Restart the app**:
   ```bash
   python3 app.py
   ```

### Option 2: Check Existing API Key Permissions

If you have a key that used to work:

1. Visit: https://elevenlabs.io/app/keys
2. Click on your API key
3. Check if these permissions are enabled:
   - ✅ `text_to_speech` (REQUIRED for voice feature)
   - ✅ `text_to_speech_v2` (optional, for newer models)
   - ✅ `read_subscription` (optional)

If not enabled, regenerate the key with full permissions.

---

## 🔧 Troubleshooting Checklist

| Check | Status | Action |
|-------|--------|--------|
| API key exists in .env | ✅ | ✓ Configured |
| API key loaded to config | ✅ | ✓ Working |
| API connection | ✅ | ✓ Responding |
| API permissions | ❌ | 🔧 **NEEDS FIX** |
| text_to_speech enabled | ❌ | 🔧 **Regenerate key** |

---

## 📋 Steps to Fix

1. **Delete current API key** from ElevenLabs dashboard
   - Go to: https://elevenlabs.io/app/keys
   - Find your key
   - Click delete (or disable)

2. **Create new key with full permissions**
   - Click "Create New API Key"
   - Name: `Medical Assistant`
   - Select: "All Permissions" or manually check:
     - ✅ `text_to_speech` 
     - ✅ `read_subscription`
     - ✅ Any others available

3. **Copy the new key**
   - ElevenLabs will show it once - copy immediately

4. **Update .env file**:
   ```bash
   # Open .env in editor
   nano .env
   
   # Find this line:
   ELEVEN_LABS_API_KEY=sk_0b39e3ad7e55f6bc17c42fef0da034c2f8574dadad26a2e9
   
   # Replace with your NEW key:
   ELEVEN_LABS_API_KEY=sk_your_new_key_here
   
   # Save (Ctrl+X, Y, Enter if using nano)
   ```

5. **Test the fix**:
   ```bash
   # Test connection
   python3 test_elevenlabs.py
   
   # Should see ✅ All tests passed!
   ```

6. **Restart the app**:
   ```bash
   python3 app.py
   # Visit http://localhost:8000
   # Try asking a question and clicking 🔊 Play Audio
   ```

---

## 🚀 After Getting New Key

Once you have a key WITH `text_to_speech` permission:

1. **Update .env**: Replace the old key
2. **Run test**: `python3 test_elevenlabs.py`
3. **Check output**: Should show all ✅ passed
4. **Use the app**: `python3 app.py`
5. **Test voice**: Ask a medical question and click 🔊

---

## 💡 Alternative: Use Free Local Text-to-Speech

If you don't want to use ElevenLabs, you can use **pyttsx3** (free, local):

1. **Comment out the ElevenLabs key** in .env:
   ```bash
   # ELEVEN_LABS_API_KEY=sk_...
   ```

2. **The app will automatically use pyttsx3** (local TTS engine)

3. **Restart**: `python3 app.py`

The voice feature will still work, just with a computer-generated voice instead of natural-sounding ElevenLabs voices.

---

## 📞 Need Help?

- **ElevenLabs Docs**: https://elevenlabs.io/docs
- **API Keys**: https://elevenlabs.io/app/keys
- **Troubleshoot**: Check your subscription plan has API access

Your API key is missing permissions. Get a new one with `text_to_speech` enabled!
