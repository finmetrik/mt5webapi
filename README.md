# MT5 WebAPI Service

Production-ready MT5 WebAPI integration service with persistent connections, Redis caching, and automatic deployment via Coolify.

## 🚀 Quick Start

### Local Development
```bash
# Clone repository
git clone https://github.com/yourusername/mt5webapi.git
cd mt5webapi

# Copy environment variables
cp .env.example .env

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Test the API
curl http://localhost:8000/health
```

### API Documentation
Once running, access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📦 Features

- ✅ Persistent MT5 connections
- ✅ Redis session caching
- ✅ Auto-reconnection logic
- ✅ RESTful API endpoints
- ✅ Health checks & monitoring
- ✅ Docker containerized
- ✅ Coolify ready
- ✅ Production optimized

## 🔧 Configuration

Edit `.env` file or set environment variables:

```env
MT5_SERVER=https://92.204.169.182:443
MT5_LOGIN=47325
MT5_PASSWORD=ApiDubai@2025
API_KEY=your-secure-api-key
REDIS_URL=redis://redis:6379
```

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/auth` | POST | Force re-authentication |
| `/api/user/{login}` | GET | Get user information |
| `/api/execute` | POST | Execute MT5 command |
| `/api/test` | GET | Test MT5 connection |

## 🚢 Deployment

See [Coolify Deployment Guide](docs/COOLIFY_MT5_DEPLOYMENT_GUIDE.md) for one-click deployment instructions.

## 📝 License

MIT
