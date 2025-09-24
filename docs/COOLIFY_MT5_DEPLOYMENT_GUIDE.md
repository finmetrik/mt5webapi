# MT5 WebAPI Deployment with Coolify - Ultimate Simple Solution

## 🎯 Why Coolify is PERFECT for MT5 Integration

Coolify gives you **Heroku-like simplicity** with **full control** over your infrastructure. One server, one dashboard, unlimited apps.

---

## ✅ Coolify Advantages for MT5

| Feature | Benefit for MT5 |
|---------|-----------------|
| **One-Click Deploy** | Push code → Auto deploy |
| **Persistent Containers** | MT5 sessions stay alive |
| **Built-in Redis** | Session management included |
| **Auto SSL** | Secure API automatically |
| **Git Integration** | Deploy from GitHub/GitLab |
| **Monitoring** | Real-time logs & metrics |
| **Backups** | Automated S3 backups |
| **Cost** | FREE (just pay for server) |
| **Scaling** | Multi-server support |
| **No Vendor Lock-in** | Move anytime |

---

## 🏗️ Architecture with Coolify

```
┌────────────────────────────────────────────────────┐
│                  COOLIFY SERVER                    │
├────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  MT5 Python │  │    Redis    │  │  Laravel   │ │
│  │     API     │──│   Session   │──│    CRM     │ │
│  │  Container  │  │    Cache    │  │     App    │ │
│  └─────────────┘  └─────────────┘  └────────────┘ │
│         │                                  │       │
│  ┌─────────────────────────────────────────┘       │
│  │              Coolify Dashboard                  │
│  │  • Monitoring  • Logs  • Backups  • SSL         │
│  └──────────────────────────────────────────────── │
└────────────────────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │   MT5   │
                    │ Server  │
                    └─────────┘
```

---

## 🚀 Complete Setup Guide (20 Minutes)

### Step 1: Get a Server (5 min)

#### Recommended Specs:
- **Minimum**: 4GB RAM, 2 vCPU, 50GB SSD
- **Recommended**: 8GB RAM, 4 vCPU, 100GB SSD
- **Cost**: $40-60/month (runs everything)

#### Best Providers:
1. **Hetzner** (Best value): €20/month for CPX31 (4 vCPU, 8GB)
2. **DigitalOcean**: $48/month (4 vCPU, 8GB)
3. **Vultr**: $48/month High Frequency

### Step 2: Install Coolify (5 min)

SSH into your server:

```bash
# One-command installation
curl -fsSL https://get.coolify.io | bash

# Installation will:
# - Install Docker
# - Setup Coolify
# - Configure firewall
# - Start services
```

After installation, access Coolify at:
```
http://your-server-ip:8000
```

### Step 3: Initial Coolify Setup (5 min)

1. **Create Admin Account**
   - Email: your-email@domain.com
   - Password: (strong password)

2. **Configure Server**
   - Coolify auto-configures your localhost server
   - No additional setup needed

3. **Add Domain (Optional)**
   - Settings → Domains
   - Add your domain for automatic SSL

### Step 4: Deploy MT5 Python API (5 min)

#### A. Create GitHub Repository

Create repository with these files:

**📁 `Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**📁 `requirements.txt`**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.1
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

**📁 `main.py`**
```python
import os
import time
import hashlib
import httpx
import redis
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

app = FastAPI(title="MT5 WebAPI Service")

# Configuration from environment
MT5_SERVER = os.getenv('MT5_SERVER', 'https://92.204.169.182:443')
MT5_LOGIN = os.getenv('MT5_LOGIN', '47325')
MT5_PASSWORD = os.getenv('MT5_PASSWORD', 'ApiDubai@2025')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
API_KEY = os.getenv('API_KEY', 'your-secure-api-key')

# Redis connection
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Global session storage
class MT5SessionManager:
    def __init__(self):
        self.sessions = {}
        self.last_auth = None

    async def get_session(self, force_new=False):
        """Get or create MT5 session"""
        session_key = f"mt5_session_{MT5_LOGIN}"

        if not force_new:
            # Check Redis cache
            cached = redis_client.get(session_key)
            if cached:
                return cached

        # Create new session
        session = await self.authenticate()

        # Cache for 5 minutes
        redis_client.setex(session_key, 300, session)

        return session

    async def authenticate(self):
        """Authenticate with MT5 server"""
        async with httpx.AsyncClient(verify=False) as client:
            # Step 1: Auth start
            start_resp = await client.get(
                f"{MT5_SERVER}/api/auth/start",
                params={
                    'version': 1290,
                    'agent': 'WebManager',
                    'login': MT5_LOGIN,
                    'type': 'manager'
                }
            )
            start_data = start_resp.json()
            srv_rand = start_data['srv_rand']

            # Step 2: Create auth hash
            pwd_bytes = MT5_PASSWORD.encode('utf-16le')
            pwd_md5 = hashlib.md5(pwd_bytes).digest()
            password_hash = hashlib.md5(pwd_md5 + b'WebAPI').digest()
            srv_rand_bytes = bytes.fromhex(srv_rand)
            srv_rand_answer = hashlib.md5(password_hash + srv_rand_bytes).hexdigest()

            import secrets
            cli_rand = secrets.token_hex(16)

            # Step 3: Auth answer
            answer_resp = await client.get(
                f"{MT5_SERVER}/api/auth/answer",
                params={
                    'srv_rand_answer': srv_rand_answer,
                    'cli_rand': cli_rand
                }
            )

            result = answer_resp.json()
            if not result.get('retcode', '').startswith('0'):
                raise HTTPException(status_code=401, detail="MT5 authentication failed")

            return "authenticated"

# Create session manager
session_manager = MT5SessionManager()

# API key validation
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

@app.get("/")
async def root():
    return {"service": "MT5 WebAPI", "status": "running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis_client.ping()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "redis": "connected"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/api/auth", dependencies=[Depends(verify_api_key)])
async def authenticate():
    """Force re-authentication"""
    try:
        session = await session_manager.get_session(force_new=True)
        return {"success": True, "message": "Authentication successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{login}", dependencies=[Depends(verify_api_key)])
async def get_user(login: str):
    """Get user information from MT5"""
    try:
        # Get session
        session = await session_manager.get_session()

        # Check cache
        cache_key = f"user:{login}"
        cached = redis_client.get(cache_key)
        if cached:
            import json
            return json.loads(cached)

        # Fetch from MT5
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.get(
                f"{MT5_SERVER}/api/user/get",
                params={'login': login}
            )

            data = resp.json()

            # Cache for 60 seconds
            redis_client.setex(cache_key, 60, resp.text)

            return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute", dependencies=[Depends(verify_api_key)])
async def execute_command(request: Dict[str, Any]):
    """Execute MT5 command"""
    try:
        session = await session_manager.get_session()

        endpoint = request.get('endpoint')
        params = request.get('params', {})

        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.get(
                f"{MT5_SERVER}/api/{endpoint}",
                params=params
            )

            return {
                "success": resp.status_code == 200,
                "data": resp.json() if resp.status_code == 200 else None,
                "status_code": resp.status_code
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**📁 `.env`**
```bash
MT5_SERVER=https://92.204.169.182:443
MT5_LOGIN=47325
MT5_PASSWORD=ApiDubai@2025
API_KEY=your-very-secure-api-key-here
REDIS_URL=redis://redis:6379
```

#### B. Deploy in Coolify

1. **Create New Project**
   - Click "New Project"
   - Name: "MT5 Integration"

2. **Add New Service**
   - Click "New Service"
   - Choose "GitHub" (connect your account)
   - Select your MT5 repository

3. **Configure Service**
   ```yaml
   Service Name: mt5-api
   Port: 8000
   Health Check Path: /health

   Environment Variables:
   - MT5_SERVER: https://92.204.169.182:443
   - MT5_LOGIN: 47325
   - MT5_PASSWORD: ApiDubai@2025
   - API_KEY: generate-secure-key-here
   - REDIS_URL: redis://redis:6379
   ```

4. **Add Redis Service**
   - Click "New Service"
   - Choose "Redis"
   - Name: redis
   - Deploy

5. **Deploy MT5 API**
   - Click "Deploy"
   - Watch real-time logs
   - Auto-builds on git push

### Step 5: Deploy Laravel App (Optional)

If you want Laravel on same server:

1. **Add Laravel Service**
   - New Service → GitHub
   - Select Laravel repository

2. **Configure Laravel**
   ```yaml
   Build Command: composer install && npm install && npm run build
   Start Command: php artisan serve --host=0.0.0.0 --port=8000

   Environment Variables:
   - APP_ENV: production
   - MT5_API_URL: http://mt5-api:8000
   - MT5_API_KEY: your-api-key
   ```

3. **Add MySQL**
   - New Service → MySQL
   - Auto-generates credentials
   - Auto-connects to Laravel

---

## 🔥 Coolify Super Powers

### 1. Automatic SSL Certificates
```yaml
# In service settings
Domain: api.yourdomain.com
SSL: Enabled (automatic Let's Encrypt)
```

### 2. One-Click Backups
```yaml
# Database backups
Backup Schedule: Daily
Backup Destination: S3/Local
Retention: 7 days
```

### 3. Real-Time Monitoring
- CPU/Memory graphs
- Request logs
- Error tracking
- Health checks

### 4. Git Push Deploy
```bash
# Make changes
git add .
git commit -m "Update MT5 config"
git push

# Coolify auto-deploys!
```

### 5. Environment Management
- Dev/Staging/Production environments
- Environment-specific variables
- Secrets management

---

## 💰 Cost Comparison

| Solution | Monthly Cost | Setup Time | Complexity |
|----------|-------------|------------|------------|
| **Coolify** | $40-60 | 20 min | Simple |
| Manual Docker | $20-40 | 1 hour | Medium |
| Kubernetes | $200+ | 1 week | Complex |
| Heroku | $50-100 | 30 min | Simple |
| AWS ECS | $100+ | 2 hours | Complex |

**Coolify wins**: Best balance of simplicity and control

---

## 📈 Scaling with Coolify

### Single Server (0-5000 users)
- Current setup
- Vertical scaling (upgrade server)
- Cost: $40-60/month

### Multi-Server (5000+ users)
```bash
# Add new server in Coolify
Servers → Add Server → Enter IP

# Deploy services across servers
Service Settings → Server: server-2
```

### Docker Swarm Mode
```bash
# Enable Swarm in Coolify
Settings → Docker Swarm → Enable

# Auto-orchestration across servers
```

---

## 🛡️ Production Checklist

### Security
- [x] Change default passwords
- [x] Enable firewall (Coolify does this)
- [x] Setup SSL certificates
- [x] Use environment variables for secrets
- [x] Enable 2FA on Coolify

### Monitoring
- [x] Health checks configured
- [x] Resource alerts set
- [x] Log aggregation enabled
- [x] Uptime monitoring

### Backup
- [x] Database backups scheduled
- [x] S3 backup destination
- [x] Test restore procedure
- [x] Document recovery steps

---

## 🔧 Maintenance

### Daily (Automated)
- Health checks (every 30s)
- Log rotation
- Resource monitoring

### Weekly
```bash
# Check Coolify dashboard
- Review metrics
- Check disk space
- Review error logs
```

### Monthly
```bash
# Update Coolify
cd /data/coolify
docker compose pull
docker compose up -d

# Update system
apt update && apt upgrade -y
```

---

## 🚨 Troubleshooting

### Service Won't Start
1. Check logs in Coolify dashboard
2. Verify environment variables
3. Check port conflicts

### High Memory Usage
1. Set resource limits in service settings
2. Enable swap on server
3. Upgrade server RAM

### Connection Issues
1. Check firewall rules
2. Verify Redis connection
3. Test MT5 credentials

---

## 🎯 Why This is the BEST Solution

### For You:
✅ **Simplest setup** - 20 minutes total
✅ **Visual dashboard** - No terminal needed
✅ **Auto-everything** - SSL, deploys, backups
✅ **Git integration** - Push to deploy
✅ **Free software** - Just pay for server
✅ **No lock-in** - Export and leave anytime

### For MT5:
✅ **Persistent connections** - Containers stay alive
✅ **Redis included** - Session management built-in
✅ **Health checks** - Auto-restart on failure
✅ **Monitoring** - Real-time metrics
✅ **Scalable** - Add servers as needed

### vs Other Options:
| Feature | Coolify | Manual | Cloudflare | Heroku |
|---------|---------|---------|------------|--------|
| Setup Time | 20 min | 1 hour | 2 days | 30 min |
| Complexity | Low | Medium | High | Low |
| Control | Full | Full | Limited | Limited |
| Cost | $40 | $20 | $30 | $50+ |
| Persistence | ✅ | ✅ | ❌ | ⚠️ |
| Auto-SSL | ✅ | ❌ | ✅ | ✅ |
| Monitoring | ✅ | ❌ | ⚠️ | ✅ |

---

## 🚀 Next Steps

1. **Get Hetzner/DigitalOcean server** (5 min)
2. **Install Coolify** (5 min)
3. **Push code to GitHub** (5 min)
4. **Deploy in Coolify** (5 min)
5. **Test API** ✅

**Total time: 20 minutes to production!**

---

## 📞 Support Resources

- **Coolify Docs**: https://coolify.io/docs
- **Discord**: https://discord.gg/coolify
- **GitHub**: https://github.com/coollabsio/coolify

---

**This is it. The simplest, most powerful solution for your MT5 integration.**