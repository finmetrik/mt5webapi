import os
import time
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import httpx
# Redis import - optional
from fastapi import FastAPI, HTTPException, Depends, Header, Request
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

# Configuration
MT5_SERVER = os.getenv('MT5_SERVER', 'https://92.204.169.182:443')
MT5_LOGIN = os.getenv('MT5_LOGIN', '47325')
MT5_PASSWORD = os.getenv('MT5_PASSWORD', 'ApiDubai@2025')
MT5_AGENT = os.getenv('MT5_AGENT', 'WebManager')
MT5_VERSION = int(os.getenv('MT5_VERSION', '1290'))
API_KEY = os.getenv('API_KEY', 'your-secure-api-key-change-this')
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

# MT5 Session Management
class MT5SessionManager:
    def __init__(self):
        self.session = None
        self.cookies = {}
        self.last_auth_time = None
        self.auth_lock = False

    def is_session_valid(self) -> bool:
        """Check if current session is still valid (5 minute timeout)"""
        if not self.last_auth_time:
            return False
        return (time.time() - self.last_auth_time) < 300

    async def authenticate(self) -> bool:
        """Authenticate with MT5 server"""
        if self.auth_lock:
            # Prevent concurrent authentication attempts
            for _ in range(30):  # Wait up to 3 seconds
                await asyncio.sleep(0.1)
                if not self.auth_lock:
                    break

        self.auth_lock = True
        try:
            async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
                # Store cookies between requests
                if self.cookies:
                    client.cookies = self.cookies

                # Step 1: Auth start
                print(f"Authenticating with MT5 server at {MT5_SERVER}")
                start_url = f"{MT5_SERVER}/api/auth/start"
                params = {
                    'version': MT5_VERSION,
                    'agent': MT5_AGENT,
                    'login': MT5_LOGIN,
                    'type': 'manager'
                }

                start_resp = await client.get(start_url, params=params)
                if start_resp.status_code != 200:
                    raise Exception(f"Auth start failed: {start_resp.status_code}")

                start_data = start_resp.json()
                srv_rand = start_data.get('srv_rand')
                if not srv_rand:
                    raise Exception("No srv_rand in response")

                # Step 2: Create auth hash
                pwd_bytes = MT5_PASSWORD.encode('utf-16le')
                pwd_md5 = hashlib.md5(pwd_bytes).digest()
                password_hash = hashlib.md5(pwd_md5 + b'WebAPI').digest()
                srv_rand_bytes = bytes.fromhex(srv_rand)
                srv_rand_answer = hashlib.md5(password_hash + srv_rand_bytes).hexdigest()
                cli_rand = secrets.token_hex(16)

                # Step 3: Auth answer
                answer_url = f"{MT5_SERVER}/api/auth/answer"
                answer_params = {
                    'srv_rand_answer': srv_rand_answer,
                    'cli_rand': cli_rand
                }

                answer_resp = await client.get(answer_url, params=answer_params)
                if answer_resp.status_code != 200:
                    raise Exception(f"Auth answer failed: {answer_resp.status_code}")

                result = answer_resp.json()
                retcode = result.get('retcode', '')

                if not retcode.startswith('0'):
                    raise Exception(f"MT5 authentication failed: {retcode}")

                # Save session info
                self.session = client
                self.cookies = dict(client.cookies)
                self.last_auth_time = time.time()

                # Cache authentication status
                cache_set('mt5:auth:status', 'authenticated', 300)

                print("MT5 authentication successful")
                return True

        except Exception as e:
            print(f"Authentication error: {e}")
            return False
        finally:
            self.auth_lock = False

    async def get_session(self):
        """Get authenticated session, create new if needed"""
        if not self.is_session_valid():
            success = await self.authenticate()
            if not success:
                raise HTTPException(status_code=500, detail="MT5 authentication failed")
        return self.session

# Global session manager
import asyncio
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

        # Get authenticated session
        await session_manager.get_session()

        # Fetch from MT5
        async with httpx.AsyncClient(verify=False, timeout=30.0, cookies=session_manager.cookies) as client:
            url = f"{MT5_SERVER}/api/user/get"
            resp = await client.get(url, params={'login': login})

            if resp.status_code != 200:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"MT5 API error: {resp.text}"
                )

            data = resp.json()

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
        # Get authenticated session
        await session_manager.get_session()

        # Build URL
        endpoint = request.endpoint.lstrip('/')
        url = f"{MT5_SERVER}/api/{endpoint}"

        # Execute request
        async with httpx.AsyncClient(verify=False, timeout=30.0, cookies=session_manager.cookies) as client:
            resp = await client.get(url, params=request.params)

            return {
                "success": resp.status_code == 200,
                "status_code": resp.status_code,
                "data": resp.json() if resp.status_code == 200 else None,
                "error": resp.text if resp.status_code != 200 else None
            }

    except Exception as e:
        print(f"Error executing command {request.endpoint}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test_endpoint(api_key: bool = Depends(verify_api_key)):
    """Test endpoint to verify MT5 connection"""
    try:
        # Test with a known user
        result = await get_user("46108", api_key)
        return {
            "success": True,
            "message": "MT5 connection working",
            "test_user": result.data,
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
    print(f"Redis: {'Connected' if REDIS_AVAILABLE else 'Not available'}")

    # Try initial authentication
    try:
        await session_manager.authenticate()
        print("Initial MT5 authentication successful")
    except Exception as e:
        print(f"Initial authentication failed (will retry on first request): {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)