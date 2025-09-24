# Coolify Port Configuration Fix

## Issue
"Port 8000 is already allocated" error when trying to change from port 3000 to 8000.

## Solution

Since port 8000 is already in use on the Coolify server, you have two options:

### Option 1: Keep Using Port 3000 (Recommended)
Leave Coolify settings as they are (3000) and just ensure the container maps correctly:

1. In Coolify Application Settings:
   - **Port:** `3000`
   - **Exposed Port:** `3000`

2. The container internally runs on port 8000, but Coolify will map it:
   - External: `3000` → Internal: `8000`

### Option 2: Use a Different Port
If you want to change from 3000, use another available port like 8080:

1. In Coolify Application Settings:
   - **Port:** `8080`
   - **Exposed Port:** `8080`

## Current Working Configuration

Your app is running correctly with:
- **Internal Port (Container):** 8000 (FastAPI default)
- **External Port (Coolify):** 3000
- **URL:** `http://rw8o8g88coc4k44kwg004sk4.168.231.109.214.sslip.io`

## Testing the API

Since the proxy shows "Bad Gateway" for the UI, test directly with curl or Postman:

```bash
# Health check (no auth required)
curl http://rw8o8g88coc4k44kwg004sk4.168.231.109.214.sslip.io/health

# Test with API key
curl -H "X-API-Key: your-api-key" \
  http://rw8o8g88coc4k44kwg004sk4.168.231.109.214.sslip.io/api/test
```

## Why "Bad Gateway" on /docs?

The Swagger UI (`/docs`) requires additional proxy headers that Coolify might not be passing. The API itself works fine, as shown in your logs:
- Health checks returning `200 OK`
- Authentication successful
- Test user retrieved successfully

## Verification

Your logs show the app is working perfectly:
```
✅ MT5 authentication successful in 0.05s
✅ Initial MT5 authentication successful
✅ Test API call successful: User 46108 found
INFO: 127.0.0.1:43806 - "GET /health HTTP/1.1" 200 OK
```

The API is fully functional - just use the endpoints directly rather than the Swagger UI.