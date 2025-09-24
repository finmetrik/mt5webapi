# Coolify Deployment Guide for MT5 WebAPI

Deploy your MT5 WebAPI to Coolify in under 10 minutes with this step-by-step guide.

## Prerequisites

✅ Coolify installed on your server
✅ GitHub repository connected to Coolify
✅ This repository cloned/forked to your GitHub

## 🚀 Deployment Steps

### Step 1: Create New Project in Coolify

1. Log into your Coolify dashboard
2. Click **"New Project"**
3. Name it: `MT5 Integration` (or your preference)

### Step 2: Add Redis Service First

1. In your project, click **"+ New"**
2. Select **"Services"** → **"Redis"**
3. Configure:
   ```
   Name: redis
   Version: 7-alpine
   ```
4. Click **"Save"** and **"Deploy"**
5. Wait for Redis to be running (green status)

### Step 3: Add MT5 API Application

1. Click **"+ New"** again
2. Select **"Applications"**
3. Choose **"GitHub"** (make sure your account is connected)
4. Select your repository: `mt5webapi`
5. Select branch: `main` (or your default branch)

### Step 4: Configure MT5 API Application

In the application settings, configure the following:

#### General Settings:
```
Name: mt5-api
Port: 8000
```

#### Build Settings:
```
Build Pack: Dockerfile
Dockerfile Location: ./Dockerfile (default)
```

#### Environment Variables:
Click "Environment Variables" and add:

```bash
MT5_SERVER=https://92.204.169.182:443
MT5_LOGIN=47325
MT5_PASSWORD=ApiDubai@2025
MT5_AGENT=WebManager
MT5_VERSION=1290
API_KEY=generate-a-secure-random-key-here
REDIS_URL=redis://redis:6379
CORS_ORIGINS=*
```

⚠️ **Important**: Generate a secure API_KEY using:
```bash
openssl rand -hex 32
```

#### Health Check:
```
Health Check Path: /health
Health Check Interval: 30
Health Check Timeout: 10
Health Check Retries: 3
```

#### Network Settings:
```
Network: Select the same network as Redis (usually project network)
```

### Step 5: Deploy

1. Click **"Save"** to save all settings
2. Click **"Deploy"** to start deployment
3. Watch the build logs in real-time
4. Wait for the application to show "Running" status

### Step 6: Configure Domain (Optional but Recommended)

1. In application settings, go to **"Domains"**
2. Add your domain:
   ```
   Domain: api.yourdomain.com
   Generate SSL: ✅ (automatic Let's Encrypt)
   ```
3. Update your DNS:
   - Add A record pointing to your server IP
   - Or CNAME to your server hostname

### Step 7: Test Your Deployment

#### Test Health Endpoint:
```bash
# If using domain
curl https://api.yourdomain.com/health

# If using server IP
curl http://your-server-ip:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00.000Z",
  "checks": {
    "api": "ok",
    "redis": "ok",
    "mt5_auth": "ok"
  }
}
```

#### Test API with API Key:
```bash
curl -H "X-API-Key: your-api-key" \
     https://api.yourdomain.com/api/test
```

## 📊 Monitoring in Coolify

### View Logs:
1. Go to your application
2. Click **"Logs"** tab
3. Select container: `mt5-api`
4. View real-time logs

### Monitor Resources:
1. Click **"Monitoring"** tab
2. View CPU, Memory, Network usage
3. Set up alerts if needed

### Check Health:
1. Click **"Health Checks"** tab
2. View health check history
3. See response times

## 🔧 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `MT5_SERVER` | MT5 WebAPI server URL | `https://92.204.169.182:443` |
| `MT5_LOGIN` | MT5 manager login | `47325` |
| `MT5_PASSWORD` | MT5 manager password | `ApiDubai@2025` |
| `API_KEY` | API authentication key | Generate with `openssl rand -hex 32` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` or `https://yourdomain.com` |

## 🔄 Continuous Deployment

Once deployed, Coolify will automatically:

1. **Watch** your GitHub repository
2. **Build** when you push to main branch
3. **Deploy** the new version
4. **Health check** before switching
5. **Rollback** if deployment fails

To trigger a deployment:
```bash
git add .
git commit -m "Update MT5 configuration"
git push origin main
```

## 🚨 Troubleshooting

### Application Won't Start

1. Check logs for errors:
   - Go to Logs → Look for error messages

2. Verify Redis is running:
   - Redis service should show "Running" status

3. Check environment variables:
   - Ensure all required variables are set
   - No typos in variable names

### Cannot Connect to MT5

1. Verify MT5 credentials:
   - Check `MT5_LOGIN` and `MT5_PASSWORD`

2. Check network connectivity:
   - Ensure your server can reach MT5 server
   - No firewall blocking outbound HTTPS

3. Test manually:
   ```bash
   docker exec -it mt5-api curl https://92.204.169.182:443
   ```

### High Memory Usage

In Coolify application settings:
1. Go to **"Resources"**
2. Set limits:
   ```
   Memory Limit: 1024 (MB)
   Memory Reservation: 512 (MB)
   ```

## 🎯 Production Checklist

- [ ] Generate secure `API_KEY`
- [ ] Configure custom domain with SSL
- [ ] Set appropriate CORS origins
- [ ] Enable monitoring alerts
- [ ] Configure backup for Redis
- [ ] Set resource limits
- [ ] Test all API endpoints
- [ ] Document API key for clients

## 🔐 Security Best Practices

1. **API Key**: Always use a strong, random API key
2. **CORS**: Restrict to specific domains in production
3. **SSL**: Always use HTTPS in production
4. **Firewall**: Restrict Redis port (6379) to internal network
5. **Updates**: Keep Docker images updated

## 📈 Scaling

When you need to scale:

1. **Vertical Scaling**:
   - Upgrade your server (more CPU/RAM)
   - Adjust resource limits in Coolify

2. **Horizontal Scaling**:
   - Add more servers to Coolify
   - Deploy multiple instances
   - Use Coolify's load balancing

## 🎉 Success!

Your MT5 WebAPI is now running on Coolify with:
- ✅ Automatic SSL certificates
- ✅ Continuous deployment from GitHub
- ✅ Redis caching
- ✅ Health monitoring
- ✅ Automatic restarts on failure
- ✅ Real-time logs

## Need Help?

- Check application logs in Coolify
- Review environment variables
- Ensure Redis is running
- Test with `/health` endpoint first

---

**Deployment Time: ~10 minutes** 🚀