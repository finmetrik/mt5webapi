import requests
import hashlib
import os
import time

# Create a session to maintain cookies/connection
session = requests.Session()
session.verify = False  # Disable SSL verification
session.headers.update({"Connection": "keep-alive"})

# =========================
# CONFIG
# =========================
SERVER = "https://92.204.169.182:443"
LOGIN = "47325"
PASSWORD = "ApiDubai@2025"
AGENT = "WebManager"
VERSION = 1290  # must be >= 484
ACCTYPE = "manager"

# =========================
# HELPERS
# =========================
def md5_bytes(data: bytes) -> bytes:
    return hashlib.md5(data).digest()

def md5_hex(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()

def make_auth_hashes(password: str, srv_rand: str):
    # Step 1: MD5(password in UTF-16LE)
    pwd_utf16le = password.encode('utf-16le')
    pwd_md5 = md5_bytes(pwd_utf16le)

    # Step 2: MD5( MD5(password) + "WebAPI" )
    password_hash_bytes = md5_bytes(pwd_md5 + b"WebAPI")

    # Step 3: MD5(password_hash_bytes + srv_rand_bytes)
    srv_rand_bytes = bytes.fromhex(srv_rand)
    combined = password_hash_bytes + srv_rand_bytes
    srv_rand_answer = md5_hex(combined)

    # Step 4: cli_rand (16 bytes hex string)
    cli_rand = os.urandom(16).hex()

    return srv_rand_answer, cli_rand, password_hash_bytes

def validate_server_auth(password_hash_bytes: bytes, cli_rand: str, cli_rand_answer: str) -> bool:
    """Validate server's authentication response"""
    expected_cli_rand_answer = md5_hex(password_hash_bytes + bytes.fromhex(cli_rand))
    return expected_cli_rand_answer == cli_rand_answer


# =========================
# STEP 1: AUTH START
# =========================
auth_start_time = time.time()  # Start timing here

start_url = f"{SERVER}/api/auth/start"
params = {
    "version": VERSION,
    "agent": AGENT,
    "login": LOGIN,
    "type": ACCTYPE
}

step1_start = time.time()
print(f"Step 1: Auth start...")
resp = session.get(start_url, params=params)
step1_time = time.time() - step1_start
print(f"Step 1 response ({step1_time:.3f}s): {resp.text}")

if resp.status_code != 200:
    raise Exception("Auth start failed")

data = resp.json()
if "srv_rand" not in data:
    raise Exception("No srv_rand in response")

srv_rand = data["srv_rand"]

# =========================
# STEP 2: AUTH ANSWER
# =========================
srv_rand_answer, cli_rand, password_hash_bytes = make_auth_hashes(PASSWORD, srv_rand)

# Check if we're still within the 10-second window
elapsed_time = time.time() - auth_start_time
if elapsed_time > 10:
    print("⚠️  Warning: More than 10 seconds have passed since auth start!")

step2_start = time.time()
print(f"Step 2: Auth answer...")
answer_url = f"{SERVER}/api/auth/answer"
full_url = f"{answer_url}?srv_rand_answer={srv_rand_answer}&cli_rand={cli_rand}"
resp = session.get(full_url)
step2_time = time.time() - step2_start
print(f"Step 2 response ({step2_time:.3f}s): {resp.text}")

if resp.status_code != 200:
    print(f"❌ HTTP Error {resp.status_code}: {resp.reason}")
    print(f"Response headers: {dict(resp.headers)}")
    raise Exception(f"Auth answer failed with status {resp.status_code}: {resp.text}")

# =========================
# STEP 3: VALIDATE SERVER AUTH
# =========================
try:
    final_data = resp.json()
    
    # Check if authentication was successful
    if "retcode" not in final_data or not final_data["retcode"].startswith("0"):
        raise Exception(f"Authentication failed: {final_data.get('retcode', 'Unknown error')}")
    
    # Validate server's authentication (mutual authentication)
    if "cli_rand_answer" in final_data:
        server_auth_valid = validate_server_auth(password_hash_bytes, cli_rand, final_data["cli_rand_answer"])
        if not server_auth_valid:
            print("⚠️  Warning: Server authentication validation failed")
    
    print(f"✅ Authentication successful! ({elapsed_time:.2f}s)")
    
    # Test API access
    step3_start = time.time()
    print(f"Step 3: Testing API access...")
    test_url = f"{SERVER}/api/user/get?login=46108"
    test_resp = session.get(test_url)
    step3_time = time.time() - step3_start
    print(f"Step 3 response ({step3_time:.3f}s): {test_resp.text}")
    
    # Summary
    total_time = time.time() - auth_start_time
    print(f"\n⏱️  Timing Summary:")
    print(f"   Step 1 (Auth Start): {step1_time:.3f}s")
    print(f"   Step 2 (Auth Answer): {step2_time:.3f}s") 
    print(f"   Step 3 (API Call): {step3_time:.3f}s")
    print(f"   Total Time: {total_time:.3f}s")
    
except Exception as e:
    print(f"❌ Error processing final authentication response: {e}")
    raise
