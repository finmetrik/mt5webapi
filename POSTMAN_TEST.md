# MT5 WebAPI - Postman Testing Guide

Your API is running successfully! Test it with these endpoints:

## Base URL
```
http://rw8o8g88coc4k44kwg004sk4.168.231.109.214.sslip.io
```

## 1. Health Check (No Auth)
**Method:** GET
**URL:** `/health`
**Headers:** None required

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-24T...",
  "checks": {
    "api": "ok",
    "redis": "unavailable",
    "mt5_auth": "ok"
  }
}
```

## 2. Test Connection
**Method:** GET
**URL:** `/api/test`
**Headers:**
```
X-API-Key: your-api-key-from-coolify-env
```

**Expected Response:**
```json
{
  "success": true,
  "message": "MT5 connection working",
  "test_user": {...},
  "timestamp": "2025-01-24T..."
}
```

## 3. Get User Info
**Method:** GET
**URL:** `/api/user/46108`
**Headers:**
```
X-API-Key: your-api-key-from-coolify-env
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "login": 46108,
    "name": "...",
    ...
  },
  "cached": false
}
```

## 4. Force Re-Authentication
**Method:** POST
**URL:** `/api/auth`
**Headers:**
```
X-API-Key: your-api-key-from-coolify-env
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "timestamp": "2025-01-24T..."
}
```

## 5. Execute Custom Command
**Method:** POST
**URL:** `/api/execute`
**Headers:**
```
X-API-Key: your-api-key-from-coolify-env
Content-Type: application/json
```

**Body:**
```json
{
  "endpoint": "user/get",
  "params": {
    "login": "47325"
  }
}
```

## Troubleshooting

### Bad Gateway on /docs
This is a Coolify proxy issue. The API works fine, just not the Swagger UI. Test using the endpoints above.

### 403 on Keep-Alive Ping
The `/api/test/access` endpoint returns 403 because your server IP isn't whitelisted on MT5. This is normal - your main API calls still work.

### Finding Your API Key
Check the environment variables you set in Coolify. The `API_KEY` value is what you need for the `X-API-Key` header.