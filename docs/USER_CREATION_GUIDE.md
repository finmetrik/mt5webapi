# MT5 User Creation API Guide

## Required Fields (MUST provide)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `group` | string | **MT5 group name** - Must be an existing group you have permission to | `"real\\std\\1"` or `"demoforex"` |
| `name` | string | **Full name of the user** | `"John Smith"` |
| `leverage` | integer | **Trading leverage** (1-500) | `100` |

## Password Fields (Highly Recommended)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `pass_main` | string | Master password (auto-generated if not provided) | `"Dubai@2025"` |
| `pass_investor` | string | Investor password (auto-generated if not provided) | `"Dubai@2025i"` |

**Password Requirements:**
- Minimum 8 characters, maximum 16 characters
- Must contain: lowercase, uppercase, numbers, special characters (#@!$%)
- Example: `"Pass@123!"` or `"Dubai@2025"`

## Optional Fields (Can skip or use real values)

### Important Optional Fields
| Field | Type | Description | Example | Default/Skip? |
|-------|------|-------------|---------|---------------|
| `email` | string | User's email address | `"user@example.com"` | Recommended to provide |
| `phone` | string | User's phone number | `"+971501234567"` | Recommended to provide |
| `country` | string | User's country | `"United Arab Emirates"` | Can skip |
| `city` | string | User's city | `"Dubai"` | Can skip |
| `company` | string | Company name | `"Individual"` | Default: "Individual" |

### Less Important Fields (Usually skip)
| Field | Type | Description | Skip? |
|-------|------|-------------|-------|
| `first_name` | string | First name (use `name` instead) | Skip |
| `last_name` | string | Last name (use `name` instead) | Skip |
| `middle_name` | string | Middle name | Skip |
| `language` | integer | Language ID (LANGID) | Skip (use 0) |
| `state` | string | State/Province | Skip |
| `zipcode` | string | Postal code | Skip |
| `address` | string | Street address | Skip |
| `id` | string | Identity document number | Skip |
| `status` | string | Account status | Skip |
| `comment` | string | Internal comment | Skip |
| `color` | integer | Display color in terminal | Skip (use 0) |
| `phone_password` | string | Phone password | Skip |
| `agent` | integer | Agent account number | Skip (use 0) |
| `mqid` | string | MetaQuotes ID | Skip |
| `login` | integer | User login (0 = auto-assign) | Skip (use 0) |
| `rights` | integer | Permission flags | Skip (default: 483) |

## Minimal Working Example

```json
{
  "group": "real\\std\\1",
  "name": "John Smith",
  "leverage": 100
}
```

## Recommended Example

```json
{
  "group": "real\\std\\1",
  "name": "John Smith",
  "leverage": 100,
  "pass_main": "SecurePass@123",
  "pass_investor": "InvestorPass@456",
  "email": "john.smith@example.com",
  "phone": "+971501234567",
  "country": "United Arab Emirates",
  "city": "Dubai",
  "company": "Individual"
}
```

## Common Errors and Solutions

### Error 403: Forbidden
**Causes:**
1. **Wrong group**: The group doesn't exist or you don't have permission
   - Solution: Use a group your manager account has access to
2. **IP not whitelisted**: Your server IP is not allowed
   - Solution: Add your Coolify server IP to MT5 whitelist
3. **No permission**: Manager account lacks user creation rights
   - Solution: Check manager permissions in MT5 Admin

### Error 3006: Invalid Password
**Cause:** Password doesn't meet complexity requirements
**Solution:** Use passwords with all 4 character types, 8-16 chars

### Error 3004: Account Already Exists
**Cause:** Login already exists
**Solution:** Use `login: 0` to auto-assign a new login

### Error 3002: No Available Login Range
**Cause:** No free login numbers in the group
**Solution:** Contact MT5 administrator to extend login range

## Testing Your Configuration

### Step 1: Test Authentication First
```bash
curl -X GET http://your-domain/api/test \
  -H "X-API-Key: your-api-key"
```

### Step 2: Try Minimal User Creation
```bash
curl -X POST http://your-domain/api/user/create \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "group": "demoforex",
    "name": "Test User",
    "leverage": 100
  }'
```

### Step 3: If Successful, Add More Fields
```bash
curl -X POST http://your-domain/api/user/create \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "group": "real\\std\\1",
    "name": "Real User",
    "leverage": 100,
    "email": "user@example.com",
    "phone": "+971501234567"
  }'
```

## Important Notes

1. **Group Names**: Must match exactly as configured in MT5 (case-sensitive)
   - Use double backslash in JSON: `"real\\std\\1"`

2. **Auto-Generated Passwords**: If you don't provide passwords, the system generates secure ones and returns them in the response

3. **Rights**: Default value (483) enables:
   - USER_RIGHT_ENABLED (can login)
   - USER_RIGHT_PASSWORD (can change password)
   - USER_RIGHT_TRAILING (can use trailing stop)
   - USER_RIGHT_EXPERT (can use Expert Advisors)
   - USER_RIGHT_REPORTS (receives daily reports)

4. **Login Assignment**: Use `login: 0` or omit it to auto-assign a login number

## Response Example

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "login": "2005",
    "group": "real\\std\\1",
    "name": "John Smith",
    "passwords": {
      "main": "SecurePass@123",
      "investor": "InvestorPass@456"
    },
    "user_details": {
      "Login": "2005",
      "Group": "real\\std\\1",
      "Name": "John Smith",
      "Email": "john.smith@example.com",
      ...
    }
  },
  "timestamp": "2025-01-24T20:30:00.000000"
}
```

## Troubleshooting Checklist

- [ ] Is the MT5 server authenticating successfully? (Check logs)
- [ ] Is the group name exactly correct? (case-sensitive)
- [ ] Does your manager account have permission for this group?
- [ ] Is your server IP whitelisted on MT5?
- [ ] Are the passwords complex enough? (if providing them)
- [ ] Is the email format valid? (if providing it)

## Quick Test Groups

If `"real\\std\\1"` doesn't work, try:
- `"demo"` or `"demoforex"` (usually available for testing)
- Ask your MT5 administrator for the exact group names you have access to