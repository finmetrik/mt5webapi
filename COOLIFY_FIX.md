# Fixing Coolify Deployment Error

## The Problem
Coolify is using Nixpacks instead of your Dockerfile, and Nixpacks doesn't have pip installed properly.

## Solution: Force Dockerfile Usage

### In Coolify Dashboard:

1. **Go to your Application Settings**

2. **Change Build Pack Settings:**
   - Find "Build Pack" setting
   - Change from: `Nixpacks`
   - Change to: `Dockerfile`
   - Or select: `Docker Image` if Dockerfile option isn't visible

3. **Advanced Build Settings:**
   ```
   Build Pack: Dockerfile
   Base Directory: /
   Dockerfile Location: ./Dockerfile
   Docker Build Arguments: (leave empty)
   ```

4. **Alternative Settings to Try:**
   - Look for "Build Method" or "Builder"
   - Select "Dockerfile" or "Docker"
   - Disable "Auto-detect" if enabled

5. **Save and Redeploy**

## Alternative Solutions

### Option 1: Delete nixpacks.toml
If Coolify auto-detects nixpacks.toml, remove it:
```bash
git rm nixpacks.toml
git commit -m "Remove nixpacks, use Dockerfile"
git push
```

### Option 2: Use Docker Compose
In Coolify, you can also deploy using docker-compose:
1. Select "Docker Compose" as deployment type
2. Point to your docker-compose.yml file

### Option 3: Pre-built Docker Image
1. Build locally:
```bash
docker build -t yourusername/mt5-api:latest .
docker push yourusername/mt5-api:latest
```

2. In Coolify:
   - Select "Docker Image" deployment
   - Image: `yourusername/mt5-api:latest`

## Quick Test Locally
Before redeploying, test locally:
```bash
# Build
docker build -t mt5-api .

# Run
docker run -p 8000:8000 mt5-api

# Test
curl http://localhost:8000/health
```

## Coolify Settings That Work

### Confirmed Working Configuration:
```yaml
Build Pack: Dockerfile
Port: 8000
Health Check Path: /health
Health Check Interval: 30
```

### Environment Variables:
```
MT5_SERVER=https://92.204.169.182:443
MT5_LOGIN=47325
MT5_PASSWORD=ApiDubai@2025
API_KEY=your-secure-key
REDIS_URL=redis://localhost:6379
```

## If Still Having Issues

1. **Check Coolify Logs:**
   - Go to Deployments → Show Debug Logs
   - Look for "Building docker image" section

2. **Clear Build Cache:**
   - In Coolify settings, find "Clear Build Cache"
   - Or add a dummy file to force rebuild

3. **Check GitHub Integration:**
   - Ensure Coolify has access to your repo
   - Try "Refresh Repository" button

4. **Manual Override:**
   In Coolify's "Custom Docker Command":
   ```
   docker build -t app . && docker run -p 8000:8000 app
   ```

## Working Deployment Checklist

- [ ] Dockerfile is in root directory
- [ ] Build Pack set to "Dockerfile" not "Nixpacks"
- [ ] Port 8000 is configured
- [ ] Health check path is /health
- [ ] Environment variables are set
- [ ] Redis service is optional (app works without it)

## The Key Fix

**In Coolify Application Settings:**
1. Click on your application
2. Go to "Build" or "Configuration"
3. Find "Build Pack" or "Builder Type"
4. **Change from "Nixpacks" to "Dockerfile"**
5. Save and Deploy

This forces Coolify to use your Dockerfile instead of auto-generating with Nixpacks.