# 🚀 Quick Deploy to Coolify (5 Minutes)

## Step 1: Push to GitHub

```bash
git add .
git commit -m "Ready for Coolify deployment"
git push origin main
```

Make your repo public temporarily for easy testing (you can make it private later).

## Step 2: In Coolify Dashboard

### Add New Resource:

1. Click **"+ New"**
2. Select **"Public Repository"** (if your repo is public)
   - OR select **"Private Repository (with GitHub App)"** if private
3. Enter your repository URL:
   ```
   https://github.com/yourusername/mt5webapi
   ```

### Configure Application:

**Basic Settings:**
```
Name: mt5-api
Port: 8000
Build Pack: Docker (it will auto-detect Dockerfile)
```

**Environment Variables (click "Environment Variables" tab):**
```
MT5_SERVER=https://92.204.169.182:443
MT5_LOGIN=47325
MT5_PASSWORD=ApiDubai@2025
API_KEY=change-this-to-secure-key
REDIS_URL=redis://localhost:6379
```

**Health Check (in "Health Check" tab):**
```
Path: /health
```

### Deploy:

1. Click **"Deploy"**
2. Watch the build logs
3. Wait for "Running" status (2-3 minutes)

## Step 3: Test

```bash
# Test health endpoint
curl http://[your-server-ip]:[assigned-port]/health

# Should return:
{
  "status": "healthy",
  "timestamp": "...",
  "checks": {
    "api": "ok",
    "redis": "ok" or "unavailable",
    "mt5_auth": "ok" or "expired"
  }
}
```

## That's it! 🎉

Your MT5 API is now running on Coolify.

### Optional: Add Redis

If you want Redis caching:
1. Add New Resource → Docker → Redis
2. Update `REDIS_URL` to `redis://redis:6379`
3. Make sure both are on same network

### Auto-Deploy on Git Push

Coolify automatically deploys when you push to GitHub:
```bash
git push → Coolify builds → Deploys new version
```

---

**Total time: 5 minutes** ⚡