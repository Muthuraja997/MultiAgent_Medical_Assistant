# Ngrok Port Forwarding Setup Guide

## Problem
When using ngrok to expose the frontend, API calls fail with network errors because:
- Ngrok only forwards the frontend (port 3000)
- Frontend tries to call `localhost:8000` (backend)
- External users can't access `localhost:8000`

## Solution
Use **Vite's built-in proxy** to route all `/api` requests through the frontend server to the backend.

---

## Configuration Applied

### 1. Updated Frontend API Configuration
**File:** `frontend/src/services/api.ts`

**Changed from:**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

**Changed to:**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
```

### 2. Vite Proxy Configuration (Already Configured)
**File:** `frontend/vite.config.ts`

```typescript
export default defineConfig({
  server: {
    port: 3000,
    host: true, // Allow external access
    allowedHosts: [
      'unhumidifying-relational-drema.ngrok-free.dev',
      '.ngrok-free.app',
      '.ngrok.io',
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

**How it works:**
- Frontend makes request to: `https://your-ngrok-url.ngrok-free.dev/api/doctors`
- Vite proxy forwards to: `http://localhost:8000/api/doctors`
- Backend responds through the proxy

---

## Usage Instructions

### Step 1: Start Backend
```bash
cd backend
../venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Start Frontend (with proxy)
```bash
cd frontend
npm run dev
```

Frontend should start on: `http://localhost:3000`

### Step 3: Start Ngrok Tunnel
```bash
cd frontend
ngrok http 3000
```

**Ngrok Output:**
```
Forwarding: https://unhumidifying-relational-drema.ngrok-free.dev -> http://localhost:3000
```

### Step 4: Access via Ngrok URL
Visit: `https://unhumidifying-relational-drema.ngrok-free.dev`

**All API calls will work!** 🎉

---

## How It Works

### Request Flow:
```
User Browser (External)
    ↓
https://your-app.ngrok-free.dev/api/doctors
    ↓
Ngrok Tunnel (Internet → Your Machine)
    ↓
Vite Dev Server (localhost:3000)
    ↓
Vite Proxy (/api → http://localhost:8000/api)
    ↓
FastAPI Backend (localhost:8000)
    ↓
MongoDB Atlas (Cloud)
```

### Key Points:
✅ Frontend is accessible via ngrok URL
✅ API requests go through Vite proxy
✅ Backend stays on localhost (doesn't need ngrok)
✅ Works with all API endpoints
✅ No CORS issues

---

## Alternative: Separate Ngrok Tunnels (Not Recommended)

If you want to expose both frontend and backend separately:

### Terminal 1: Backend Ngrok
```bash
ngrok http 8000
```
Output: `https://abc123.ngrok-free.dev → localhost:8000`

### Terminal 2: Frontend Ngrok
```bash
ngrok http 3000
```
Output: `https://xyz789.ngrok-free.dev → localhost:3000`

### Create `.env` file
```bash
cd frontend
echo "VITE_API_URL=https://abc123.ngrok-free.dev/api" > .env
```

### Restart Frontend
```bash
npm run dev
```

**Downsides:**
- ⚠️ Need to update `.env` every time ngrok URL changes
- ⚠️ Requires two ngrok tunnels (free tier limits)
- ⚠️ More complex configuration

---

## Testing

### 1. Test Local Access
```bash
curl http://localhost:3000/api/health
```

### 2. Test Ngrok Access
```bash
curl https://your-ngrok-url.ngrok-free.dev/api/health
```

### 3. Test Frontend Features via Ngrok
1. Open: `https://your-ngrok-url.ngrok-free.dev`
2. Login as user
3. Click "Find Nearby Hospitals" ✅ Should work!
4. Request appointment ✅ Should work!
5. Login as doctor
6. Accept appointment ✅ Should work!
7. Join meeting ✅ Should work!

---

## Troubleshooting

### Issue 1: Still getting network errors
**Solution:** Make sure frontend is using the proxy:
```bash
# Check the API calls in browser DevTools
# URL should be: /api/something
# NOT: http://localhost:8000/api/something
```

### Issue 2: Ngrok shows "Host header is not allowed"
**Solution:** Already fixed in `vite.config.ts` with `allowedHosts`

### Issue 3: CORS errors
**Solution:** Vite proxy handles CORS automatically. Make sure:
- Backend has CORS enabled (already done in `main.py`)
- Using relative URLs (`/api`) not absolute URLs

### Issue 4: Backend not responding
**Solution:** Check backend is running:
```bash
curl http://localhost:8000/api/health
```

---

## Production Deployment

For production, you'll need to:

1. **Deploy Backend** (e.g., Railway, Render, AWS)
   - Get backend URL: `https://api.yourdomain.com`

2. **Build Frontend** with backend URL:
   ```bash
   cd frontend
   echo "VITE_API_URL=https://api.yourdomain.com/api" > .env.production
   npm run build
   ```

3. **Deploy Frontend** (e.g., Vercel, Netlify, AWS S3)

4. **Update CORS** in backend to allow frontend domain

---

## Current Configuration Summary

✅ **Frontend API:** Uses `/api` (relative URL)
✅ **Vite Proxy:** Routes `/api` → `http://localhost:8000`
✅ **Ngrok Allowed:** Multiple ngrok domains whitelisted
✅ **Backend CORS:** Allows frontend requests
✅ **Ready to Use:** Just start ngrok and share the URL!

---

## Quick Start Commands

### Terminal 1: Backend
```bash
cd /Users/muthuraja/Documents/EE/MultiAgent_Medical_Assistant/backend
../venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend
```bash
cd /Users/muthuraja/Documents/EE/MultiAgent_Medical_Assistant/frontend
npm run dev
```

### Terminal 3: Ngrok
```bash
cd /Users/muthuraja/Documents/EE/MultiAgent_Medical_Assistant/frontend
ngrok http 3000
```

**Share the ngrok URL and everything will work!** 🚀

---

## Status
✅ Configuration updated
✅ Vite proxy enabled
✅ Ngrok hosts whitelisted
✅ Ready for testing

Try clicking "Find Nearby Hospitals" now - it should work via ngrok!
