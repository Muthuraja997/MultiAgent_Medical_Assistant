# 🔑 How to Get a New ElevenLabs API Key with Correct Permissions

## 📍 Current Status
- **API Key Location**: `.env` file
- **Current Key**: `sk_0b39e3ad7e55f6bc17c42fef0da034c2f8574dadad26a2e9`
- **Problem**: Missing `text_to_speech` permission
- **Error**: 401 Unauthorized

---

## ✅ Step-by-Step Fix

### Step 1: Access ElevenLabs API Keys Page
1. Open browser: https://elevenlabs.io/
2. Login with your account (or create one)
3. Go to: **https://elevenlabs.io/app/keys**

### Step 2: View Current Key Details
1. Look for your current API key in the list
2. Click on it to see permissions
3. Check if `text_to_speech` is listed ✅
   - If **NOT checked**: ❌ This is the problem

### Step 3: Create a NEW API Key (Recommended)
**Option A: Best - Create Fresh with Correct Permissions**

1. Click **"Create New API Key"** button
2. Enter name: `Medical Assistant Voice`
3. Select permissions - **ENABLE AT LEAST**:
   - ✅ `text_to_speech` (REQUIRED for voice)
   - ✅ `read_subscription` (recommended)
4. Click **"Create"**
5. **COPY THE KEY IMMEDIATELY** - ElevenLabs shows it only once!

**Option B: Fix Existing Key (If Regenerate is Available)**

1. Click on your current key
2. If you see "Regenerate" option, click it
3. Ensure all permissions are enabled
4. Copy the regenerated key

---

## 🔧 Update Your .env File

### Current Content:
```properties
ELEVEN_LABS_API_KEY=sk_0b39e3ad7e55f6bc17c42fef0da034c2f8574dadad26a2e9
```

### Replace With Your New Key:
```properties
ELEVEN_LABS_API_KEY=sk_YOUR_NEW_KEY_HERE
```

**Example (after getting new key)**:
```properties
ELEVEN_LABS_API_KEY=sk_1234567890abcdefghijklmnopqrstuv
```

### How to Update:
1. **Option 1 - Use Terminal**:
   ```bash
   # Edit the .env file
   nano .env
   
   # Find line with ELEVEN_LABS_API_KEY
   # Delete old key, paste new key
   # Save: Ctrl+X, then Y, then Enter
   ```

2. **Option 2 - Use VS Code**:
   - Open `.env` file
   - Find: `ELEVEN_LABS_API_KEY=sk_0b39e3ad...`
   - Replace with: `ELEVEN_LABS_API_KEY=sk_your_new_key`
   - Save: Ctrl+S

---

## ✔️ Verify the Fix

### Test 1: Run Diagnostic Script
```bash
python3 test_elevenlabs.py
```

**Expected Output (SUCCESS)**:
```
[1/5] ✅ Checking if ElevenLabs API key is configured...
[2/5] ✅ Loading configuration...
[3/5] ✅ Checking SpeechConfig...
[4/5] ✅ Testing ElevenLabs API connection...
[5/5] ✅ All tests passed! Voice feature is working!
```

**If still showing ❌**: The new key also doesn't have permissions - try again!

### Test 2: Run the Application
```bash
python3 app.py
```

### Test 3: Test Voice in Web UI
1. Open: http://localhost:8000
2. Ask a medical question
3. Click **🔊 Play Audio** button
4. Listen for voice output

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Still getting 401 error | New key doesn't have `text_to_speech` - check ElevenLabs permission settings |
| Key page won't load | Check you're logged into ElevenLabs account |
| Can't create new key | You might be on free tier - check subscription |
| App won't start | Make sure you saved .env file correctly |

---

## 📋 Permissions Checklist

When creating/checking your API key, ensure these are enabled ✅:

- [ ] `text_to_speech` - **REQUIRED** for voice feature
- [ ] `read_subscription` - Optional but recommended
- [ ] Any other available permissions

---

## 🚀 Quick Summary

1. **Go to**: https://elevenlabs.io/app/keys
2. **Create NEW key** with `text_to_speech` permission ✅
3. **Copy the key**
4. **Update .env**: Replace old key with new key
5. **Test**: `python3 test_elevenlabs.py`
6. **Run**: `python3 app.py`
7. **Use**: Click 🔊 Play Audio on responses

---

## 💬 What Each Permission Does

| Permission | Purpose |
|------------|---------|
| `text_to_speech` | Allows converting text to speech (REQUIRED) |
| `text_to_speech_v2` | Access to newer TTS models |
| `read_subscription` | Check subscription details |
| `write_subscription` | Modify subscription (not needed) |

---

## 🆘 Still Not Working?

After getting new key and updating .env:

1. **Verify key is in .env**: `grep ELEVEN_LABS .env`
2. **Check key format**: Should start with `sk_`
3. **Restart app**: `python3 app.py`
4. **Clear browser cache**: Ctrl+Shift+Delete
5. **Test again**: `python3 test_elevenlabs.py`

If still issues, the problem is in ElevenLabs account settings, not our code!
