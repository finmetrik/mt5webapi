import os
import time
import hashlib
import secrets
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import httpx
from fastapi import FastAPI, HTTPException, Depends, Header, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(
    title="MT5 WebAPI Service",
    version="1.0.0",
    description="Production-ready MT5 WebAPI integration service"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Environment variables are REQUIRED in production
MT5_SERVER = os.getenv('MT5_SERVER')
MT5_LOGIN = os.getenv('MT5_LOGIN')
MT5_PASSWORD = os.getenv('MT5_PASSWORD')
MT5_AGENT = os.getenv('MT5_AGENT', 'WebManager')
MT5_VERSION = int(os.getenv('MT5_VERSION', '1290'))
API_KEY = os.getenv('API_KEY')

# Validate required environment variables
if not all([MT5_SERVER, MT5_LOGIN, MT5_PASSWORD, API_KEY]):
    print("⚠️ WARNING: Missing required environment variables!")
    print("Using development defaults - DO NOT use in production!")
    # Development defaults (remove these in production)
    MT5_SERVER = MT5_SERVER or 'https://92.204.169.182:443'
    MT5_LOGIN = MT5_LOGIN or '47325'
    MT5_PASSWORD = MT5_PASSWORD or 'ApiDubai@2025'
    API_KEY = API_KEY or 'development-key-change-this'

# Redis is optional - will use in-memory cache if not available
REDIS_URL = os.getenv('REDIS_URL', '')
REDIS_AVAILABLE = False
redis_client = None

# Try to import and connect to Redis if URL is provided
if REDIS_URL:
    try:
        import redis
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        REDIS_AVAILABLE = True
        print("Redis connected successfully")
    except ImportError:
        print("Redis library not installed, using in-memory cache")
    except Exception as e:
        print(f"Redis connection failed, using in-memory cache: {e}")
else:
    print("No Redis URL provided, using in-memory cache")

# Request/Response models
class ExecuteRequest(BaseModel):
    endpoint: str
    params: Dict[str, Any] = {}

class UserResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cached: bool = False

# In-memory cache fallback
memory_cache = {}

def cache_set(key: str, value: str, expire: int = 300):
    """Set cache with fallback to memory if Redis unavailable"""
    if REDIS_AVAILABLE and redis_client:
        redis_client.setex(key, expire, value)
    else:
        memory_cache[key] = {
            'value': value,
            'expires': time.time() + expire
        }

def cache_get(key: str) -> Optional[str]:
    """Get cache with fallback to memory if Redis unavailable"""
    if REDIS_AVAILABLE and redis_client:
        return redis_client.get(key)
    else:
        if key in memory_cache:
            if memory_cache[key]['expires'] > time.time():
                return memory_cache[key]['value']
            else:
                del memory_cache[key]
        return None

# MT5 Session Management with Keep-Alive
class MT5SessionManager:
    def __init__(self):
        self.client = None
        self.last_auth_time = None
        self.auth_lock = asyncio.Lock()
        self.keep_alive_task = None
        self.password_hash_bytes = None

    def is_session_valid(self) -> bool:
        """Check if current session is still valid"""
        if not self.last_auth_time or not self.client:
            return False
        # Consider session valid for 5 minutes (but we'll ping every 20 seconds)
        return (time.time() - self.last_auth_time) < 300

    async def keep_alive_ping(self):
        """Send keep-alive ping every 20 seconds"""
        while True:
            try:
                await asyncio.sleep(20)
                if self.client and self.is_session_valid():
                    # Send ping to keep session alive
                    try:
                        response = await self.client.get(f"{MT5_SERVER}/api/test/access")
                        if response.status_code == 200:
                            print(f"Keep-alive ping successful at {datetime.now().isoformat()}")
                        else:
                            print(f"Keep-alive ping returned status {response.status_code}")
                    except Exception as e:
                        print(f"Keep-alive ping failed: {e}")
                        # If ping fails, try to re-authenticate
                        await self.authenticate()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Keep-alive error: {e}")

    async def authenticate(self) -> bool:
        """Authenticate with MT5 server using persistent session"""
        async with self.auth_lock:
            try:
                # Create a new persistent client with keep-alive
                if self.client:
                    await self.client.aclose()

                self.client = httpx.AsyncClient(
                    verify=False,
                    timeout=30.0,
                    headers={"Connection": "keep-alive"}
                )

                print(f"Authenticating with MT5 server at {MT5_SERVER}")
                auth_start_time = time.time()

                # Step 1: Auth start
                start_url = f"{MT5_SERVER}/api/auth/start"
                params = {
                    'version': MT5_VERSION,
                    'agent': MT5_AGENT,
                    'login': MT5_LOGIN,
                    'type': 'manager'
                }

                start_resp = await self.client.get(start_url, params=params)
                if start_resp.status_code != 200:
                    raise Exception(f"Auth start failed: {start_resp.status_code}")

                start_data = start_resp.json()
                srv_rand = start_data.get('srv_rand')
                if not srv_rand:
                    raise Exception("No srv_rand in response")

                # Step 2: Create auth hash (same as hash.py)
                pwd_bytes = MT5_PASSWORD.encode('utf-16le')
                pwd_md5 = hashlib.md5(pwd_bytes).digest()
                self.password_hash_bytes = hashlib.md5(pwd_md5 + b'WebAPI').digest()
                srv_rand_bytes = bytes.fromhex(srv_rand)
                srv_rand_answer = hashlib.md5(self.password_hash_bytes + srv_rand_bytes).hexdigest()
                cli_rand = secrets.token_hex(16)

                # Check timing (must be within 10 seconds)
                elapsed_time = time.time() - auth_start_time
                if elapsed_time > 10:
                    print(f"⚠️ Warning: {elapsed_time:.2f}s elapsed, may exceed 10s window")

                # Step 3: Auth answer
                answer_url = f"{MT5_SERVER}/api/auth/answer"
                answer_params = {
                    'srv_rand_answer': srv_rand_answer,
                    'cli_rand': cli_rand
                }

                answer_resp = await self.client.get(answer_url, params=answer_params)
                if answer_resp.status_code != 200:
                    raise Exception(f"Auth answer failed: {answer_resp.status_code}")

                result = answer_resp.json()
                retcode = result.get('retcode', '')

                if not retcode.startswith('0'):
                    raise Exception(f"MT5 authentication failed: {retcode}")

                # Validate server auth (mutual authentication)
                if 'cli_rand_answer' in result:
                    expected_cli_rand_answer = hashlib.md5(
                        self.password_hash_bytes + bytes.fromhex(cli_rand)
                    ).hexdigest()
                    if result['cli_rand_answer'] != expected_cli_rand_answer:
                        print("⚠️ Warning: Server authentication validation failed")

                self.last_auth_time = time.time()

                # Start keep-alive task if not already running
                if self.keep_alive_task:
                    self.keep_alive_task.cancel()
                self.keep_alive_task = asyncio.create_task(self.keep_alive_ping())

                # Cache authentication status
                cache_set('mt5:auth:status', 'authenticated', 300)

                print(f"✅ MT5 authentication successful in {elapsed_time:.2f}s")
                return True

            except Exception as e:
                print(f"❌ Authentication error: {e}")
                if self.client:
                    await self.client.aclose()
                    self.client = None
                return False

    async def get_client(self) -> httpx.AsyncClient:
        """Get authenticated client, create new if needed"""
        if not self.is_session_valid():
            success = await self.authenticate()
            if not success:
                raise HTTPException(status_code=500, detail="MT5 authentication failed")
        return self.client

    async def execute_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MT5 API request using persistent session"""
        client = await self.get_client()
        url = f"{MT5_SERVER}/api/{endpoint.lstrip('/')}"

        try:
            response = await client.get(url, params=params or {})
            if response.status_code != 200:
                # If unauthorized, try to re-authenticate once
                if response.status_code in [401, 403]:
                    print("Session expired, re-authenticating...")
                    await self.authenticate()
                    client = await self.get_client()
                    response = await client.get(url, params=params or {})

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"MT5 API error: {response.text}"
                    )

            return response.json()
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def close(self):
        """Clean shutdown"""
        if self.keep_alive_task:
            self.keep_alive_task.cancel()
        if self.client:
            await self.client.aclose()

# Global session manager
session_manager = MT5SessionManager()

# API key validation
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Validate API key from header"""
    if API_KEY == 'your-secure-api-key-change-this':
        # Allow access without API key in development
        return True
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MT5 WebAPI Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "ok",
            "redis": "ok" if REDIS_AVAILABLE else "unavailable",
            "mt5_auth": "ok" if session_manager.is_session_valid() else "expired"
        }
    }

    # Test Redis if available
    if REDIS_AVAILABLE:
        try:
            redis_client.ping()
        except:
            health_status["checks"]["redis"] = "error"
            health_status["status"] = "degraded"

    return health_status

@app.post("/api/auth")
async def force_auth(api_key: bool = Depends(verify_api_key)):
    """Force re-authentication with MT5 server"""
    try:
        success = await session_manager.authenticate()
        if success:
            return {
                "success": True,
                "message": "Authentication successful",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Authentication failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{login}")
async def get_user(login: str, api_key: bool = Depends(verify_api_key)):
    """Get user information from MT5"""
    try:
        # Check cache first
        cache_key = f"user:{login}"
        cached_data = cache_get(cache_key)

        if cached_data:
            return UserResponse(
                success=True,
                data=json.loads(cached_data),
                cached=True
            )

        # Fetch from MT5
        data = await session_manager.execute_request("user/get", {"login": login})

        # Cache the result
        cache_set(cache_key, json.dumps(data), 60)

        return UserResponse(
            success=True,
            data=data,
            cached=False
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching user {login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
async def execute_command(
    request: ExecuteRequest,
    api_key: bool = Depends(verify_api_key)
):
    """Execute arbitrary MT5 API command"""
    try:
        data = await session_manager.execute_request(request.endpoint, request.params)

        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error executing command {request.endpoint}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions/by-login/{login}")
async def get_positions_by_login(
    login: str,
    symbol: Optional[str] = None,
    api_key: bool = Depends(verify_api_key)
):
    """Get positions by login ID, optionally filtered by symbol"""
    try:
        params = {"login": login}
        if symbol:
            params["symbol"] = symbol

        # Check cache
        cache_key = f"positions:login:{login}:{symbol or 'all'}"
        cached_data = cache_get(cache_key)

        if cached_data:
            return {
                "success": True,
                "data": json.loads(cached_data),
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }

        # Fetch from MT5
        data = await session_manager.execute_request("position/get_batch", params)

        # Cache for 30 seconds (positions change frequently)
        cache_set(cache_key, json.dumps(data), 30)

        return {
            "success": True,
            "data": data,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching positions for login {login}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions/by-group/{group}")
async def get_positions_by_group(
    group: str,
    symbol: Optional[str] = None,
    api_key: bool = Depends(verify_api_key)
):
    """Get positions by group, optionally filtered by symbol. Supports wildcards like 'demo*' or '!demoforex'"""
    try:
        params = {"group": group}
        if symbol:
            params["symbol"] = symbol

        # Check cache
        cache_key = f"positions:group:{group}:{symbol or 'all'}"
        cached_data = cache_get(cache_key)

        if cached_data:
            return {
                "success": True,
                "data": json.loads(cached_data),
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }

        # Fetch from MT5
        data = await session_manager.execute_request("position/get_batch", params)

        # Cache for 30 seconds
        cache_set(cache_key, json.dumps(data), 30)

        return {
            "success": True,
            "data": data,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching positions for group {group}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/positions/by-symbol/{symbol}")
async def get_positions_by_symbol(
    symbol: str,
    api_key: bool = Depends(verify_api_key)
):
    """Get all positions for a specific symbol across all users"""
    try:
        # For symbol-only queries, we need to specify all groups or logins
        # Using wildcard to get all groups
        params = {
            "group": "*",  # All groups
            "symbol": symbol
        }

        # Check cache
        cache_key = f"positions:symbol:{symbol}"
        cached_data = cache_get(cache_key)

        if cached_data:
            return {
                "success": True,
                "data": json.loads(cached_data),
                "cached": True,
                "timestamp": datetime.now().isoformat()
            }

        # Fetch from MT5
        data = await session_manager.execute_request("position/get_batch", params)

        # Cache for 30 seconds
        cache_set(cache_key, json.dumps(data), 30)

        return {
            "success": True,
            "data": data,
            "cached": False,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching positions for symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test_endpoint(api_key: bool = Depends(verify_api_key)):
    """Test endpoint to verify MT5 connection"""
    try:
        # Test with user 46108 as in hash.py
        data = await session_manager.execute_request("user/get", {"login": "46108"})

        return {
            "success": True,
            "message": "MT5 connection working",
            "test_user": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": "MT5 connection failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print(f"MT5 WebAPI Service starting...")
    print(f"MT5 Server: {MT5_SERVER}")
    print(f"MT5 Login: {MT5_LOGIN}")
    print(f"Redis: {'Connected' if REDIS_AVAILABLE else 'Not available - using in-memory cache'}")

    # Try initial authentication
    try:
        success = await session_manager.authenticate()
        if success:
            print("✅ Initial MT5 authentication successful")
            # Test the connection
            test_data = await session_manager.execute_request("user/get", {"login": "46108"})
            print(f"✅ Test API call successful: User 46108 found")
        else:
            print("❌ Initial authentication failed (will retry on first request)")
    except Exception as e:
        print(f"❌ Startup authentication failed: {e}")
        print("Will retry on first request...")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down MT5 WebAPI Service...")
    await session_manager.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)