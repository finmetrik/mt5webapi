# MT5 WebAPI Service - API Documentation

## Overview
Production-ready MT5 WebAPI integration service with persistent connections, automatic keep-alive, and caching support.

## Base URL
```
http://your-domain.com
```

## Authentication
All API endpoints (except `/health`) require an API key in the request headers:

```
X-API-Key: your-api-key-here
```

---

## Endpoints

### 1. Health Check
Check service health and status.

**Endpoint:** `GET /health`
**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-24T12:00:00",
  "checks": {
    "api": "ok",
    "redis": "unavailable",
    "mt5_auth": "ok"
  }
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

---

### 2. Root Endpoint
Get basic service information.

**Endpoint:** `GET /`
**Authentication:** Not required

**Response:**
```json
{
  "service": "MT5 WebAPI Service",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

---

### 3. Force Authentication
Force re-authentication with MT5 server.

**Endpoint:** `POST /api/auth`
**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "timestamp": "2025-01-24T12:00:00"
}
```

**Status Codes:**
- `200 OK`: Authentication successful
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Authentication failed

---

### 4. Get User Information
Retrieve user details from MT5.

**Endpoint:** `GET /api/user/{login}`
**Authentication:** Required

**Parameters:**
- `login` (path): User login ID (e.g., 46108)

**Response:**
```json
{
  "success": true,
  "data": {
    "login": 46108,
    "name": "John Doe",
    "group": "demo",
    "leverage": 100,
    "balance": 10000.00,
    "credit": 0.00,
    "margin": 0.00,
    "margin_free": 10000.00,
    "margin_level": 0.00,
    "equity": 10000.00
  },
  "cached": false
}
```

**Status Codes:**
- `200 OK`: User found
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

---

### 5. Execute Custom Command
Execute any MT5 API command.

**Endpoint:** `POST /api/execute`
**Authentication:** Required
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "endpoint": "user/get",
  "params": {
    "login": "47325"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    // Response from MT5 API
  },
  "timestamp": "2025-01-24T12:00:00"
}
```

**Available Endpoints:**
- `user/get` - Get user information
- `user/list` - List users
- `tick/last` - Get last tick
- `position/list` - List positions
- `order/list` - List orders
- `deal/list` - List deals
- And more MT5 WebAPI endpoints...

**Status Codes:**
- `200 OK`: Command executed successfully
- `401 Unauthorized`: Invalid API key
- `400 Bad Request`: Invalid request format
- `500 Internal Server Error`: Execution failed

---

### 6. Get Positions by Login
Get open positions for a specific login.

**Endpoint:** `GET /api/positions/by-login/{login}`
**Authentication:** Required

**Parameters:**
- `login` (path): User login ID
- `symbol` (query, optional): Filter by symbol

**Example:**
```
GET /api/positions/by-login/47325
GET /api/positions/by-login/47325?symbol=EURUSD
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": [
      {
        "ticket": 1012,
        "login": 47325,
        "symbol": "EURUSD",
        "volume": 10000,
        "price_open": 1.0850,
        "price_current": 1.0855,
        "profit": 5.00
      }
    ],
    "retcode": "0"
  },
  "cached": false,
  "timestamp": "2025-01-24T12:00:00"
}
```

---

### 7. Get Positions by Group
Get open positions for users in specific group(s).

**Endpoint:** `GET /api/positions/by-group/{group}`
**Authentication:** Required

**Parameters:**
- `group` (path): Group name or pattern (supports wildcards: `*` for any, `!` for exclude)
- `symbol` (query, optional): Filter by symbol

**Examples:**
```
GET /api/positions/by-group/demoforex
GET /api/positions/by-group/demo*
GET /api/positions/by-group/demo*,!demoforex
GET /api/positions/by-group/demoforex?symbol=GBPUSD
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": [
      {
        "ticket": 1012,
        "login": 47325,
        "group": "demoforex",
        "symbol": "GBPUSD",
        "volume": 5000,
        "profit": -12.50
      }
    ],
    "retcode": "0"
  },
  "cached": false,
  "timestamp": "2025-01-24T12:00:00"
}
```

---

### 8. Get Positions by Symbol
Get all open positions for a specific symbol across all users.

**Endpoint:** `GET /api/positions/by-symbol/{symbol}`
**Authentication:** Required

**Parameters:**
- `symbol` (path): Trading symbol (e.g., EURUSD, GBPUSD)

**Example:**
```
GET /api/positions/by-symbol/EURUSD
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": [
      {
        "ticket": 1012,
        "login": 47325,
        "symbol": "EURUSD",
        "volume": 10000,
        "type": "buy",
        "profit": 25.00
      },
      {
        "ticket": 1013,
        "login": 46108,
        "symbol": "EURUSD",
        "volume": 5000,
        "type": "sell",
        "profit": -10.00
      }
    ],
    "retcode": "0"
  },
  "cached": false,
  "timestamp": "2025-01-24T12:00:00"
}
```

**Note:** Positions are cached for 30 seconds due to their frequently changing nature.

---

### 9. Test Connection
Test MT5 connection with a known user.

**Endpoint:** `GET /api/test`
**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "MT5 connection working",
  "test_user": {
    "login": 46108,
    "name": "Test User"
  },
  "timestamp": "2025-01-24T12:00:00"
}
```

**Status Codes:**
- `200 OK`: Connection successful
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Connection failed

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error description",
  "status_code": 400,
  "timestamp": "2025-01-24T12:00:00"
}
```

---

## Rate Limiting
Currently, there are no rate limits. However, please be mindful of:
- MT5 server connection limits
- Keep-alive pings occur every 20 seconds automatically
- Sessions timeout after 5 minutes of inactivity

---

## Caching
- User data is cached for 60 seconds
- Cache can be Redis (if configured) or in-memory
- Cache status is indicated in the response with `"cached": true/false`

---

## WebSocket Support
Not currently available. All communication is via REST API.

---

## Swagger Documentation
When running locally, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Note: Swagger UI may not be accessible through some proxy configurations.

---

## Examples

### cURL Example
```bash
# Get user information
curl -X GET "http://your-domain.com/api/user/46108" \
  -H "X-API-Key: your-api-key"

# Execute custom command
curl -X POST "http://your-domain.com/api/execute" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"endpoint":"user/get","params":{"login":"47325"}}'
```

### Python Example
```python
import requests

# Configuration
base_url = "http://your-domain.com"
api_key = "your-api-key"
headers = {"X-API-Key": api_key}

# Get user information
response = requests.get(
    f"{base_url}/api/user/46108",
    headers=headers
)
user_data = response.json()
print(user_data)

# Execute custom command
response = requests.post(
    f"{base_url}/api/execute",
    headers=headers,
    json={
        "endpoint": "user/get",
        "params": {"login": "47325"}
    }
)
result = response.json()
print(result)
```

### JavaScript Example
```javascript
const baseUrl = 'http://your-domain.com';
const apiKey = 'your-api-key';

// Get user information
fetch(`${baseUrl}/api/user/46108`, {
    headers: {
        'X-API-Key': apiKey
    }
})
.then(response => response.json())
.then(data => console.log(data));

// Execute custom command
fetch(`${baseUrl}/api/execute`, {
    method: 'POST',
    headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        endpoint: 'user/get',
        params: { login: '47325' }
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Environment Variables

Required environment variables for deployment:

| Variable | Description | Example |
|----------|-------------|---------|
| `MT5_SERVER` | MT5 server URL | `https://92.204.169.182:443` |
| `MT5_LOGIN` | MT5 login ID | `47325` |
| `MT5_PASSWORD` | MT5 password | `your-password` |
| `API_KEY` | API key for authentication | `your-secure-api-key` |
| `MT5_AGENT` | MT5 agent name (optional) | `WebManager` |
| `MT5_VERSION` | MT5 version (optional) | `1290` |
| `REDIS_URL` | Redis URL (optional) | `redis://localhost:6379` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` or `https://your-app.com` |

---

## Session Management
- The service maintains a persistent connection to MT5
- Automatic keep-alive pings every 20 seconds
- Session re-authentication on expiry
- Connection pooling for optimal performance

---

## Security Considerations
1. Always use HTTPS in production
2. Keep your API key secure
3. Use environment variables for sensitive data
4. Configure CORS appropriately for your use case
5. Monitor access logs regularly

---

## Support
For issues or questions, please refer to the GitHub repository or contact support.