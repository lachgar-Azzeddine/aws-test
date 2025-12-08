# Authentication Guide

## Default Admin User (Created Automatically)

When you start the backend for the first time, a default admin user is automatically created:

```
Username: admin
Password: admin123
```

⚠️ **IMPORTANT:** Change this password after first login!

---

## How to Login and Get Access Token

### Option 1: Using Swagger UI (Easiest)

1. **Open Swagger UI:**
   ```
   http://localhost:8008/docs
   ```

2. **Click the "Authorize" button** (top right, lock icon)

3. **Enter credentials:**
   - **Username:** `admin`
   - **Password:** `admin123`
   - **Leave other fields empty**

4. **Click "Authorize"**

5. **Now all API calls will include the JWT token automatically!**

---

### Option 2: Using cURL (For Scripts)

**Step 1: Get Access Token**

```bash
curl -X POST "http://localhost:8008/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Step 2: Use Token in API Calls**

```bash
# Store token in variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Make authenticated API call
curl -X GET "http://localhost:8008/virtual-machines" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Option 3: Using Python requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8008/token",
    data={
        "username": "admin",
        "password": "admin123"
    }
)
token = response.json()["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
vms = requests.get("http://localhost:8008/virtual-machines", headers=headers)
print(vms.json())
```

---

## API Endpoints Reference

### Authentication Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/token` | Login and get JWT access token |

**Request Body (form-data):**
```
username: admin
password: admin123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Protected Endpoints (Require Authentication)

All other API endpoints require the JWT token in the `Authorization` header:

```
Authorization: Bearer <your-token-here>
```

**Examples:**
- `GET /virtual-machines` - List all VMs
- `GET /zones` - List network zones
- `GET /ansible-roles` - Check deployment status
- `POST /start-install` - Start deployment
- `GET /configuration` - Get full configuration

---

## Token Expiration

- **JWT tokens expire after 30 minutes**
- If you get `401 Unauthorized`, request a new token
- Swagger UI handles this automatically

---

## Creating Additional Users

### Via SQL (Direct Database)

```bash
# Connect to database
docker exec -it postgres psql -U harmonisation -d harmonisation
```

```sql
-- Generate encrypted password first (use Python)
-- Then insert user
INSERT INTO "user" (username, password, is_active, role)
VALUES (
    'testuser',
    'gAAAAABnQfR...encrypted_password_here...',  -- Use encrypt_password()
    true,
    'user'  -- or 'admin'
);
```

### Via Python Script

Create a file `create_user.py`:

```python
from cryptography.fernet import Fernet

ENCRYPTION_KEY = "uOdT_oGBMvG8N7_rpBg1UVlwVK7BD6igm0l4IqJD8cA="
fernet = Fernet(ENCRYPTION_KEY)

def encrypt_password(plain_password: str):
    encoded_pwd = plain_password.encode()
    encrypted_pwd_bytes = fernet.encrypt(encoded_pwd)
    return encrypted_pwd_bytes.decode()

# Example
username = "testuser"
password = "testpass123"
encrypted = encrypt_password(password)

print(f"Username: {username}")
print(f"Encrypted Password: {encrypted}")
print(f"\nSQL:")
print(f"INSERT INTO \"user\" (username, password, is_active, role)")
print(f"VALUES ('{username}', '{encrypted}', true, 'user');")
```

Run it:
```bash
docker exec backend python create_user.py
```

---

## Changing the Default Password

### Option 1: Via Database

```sql
-- Connect to database
docker exec -it postgres psql -U harmonisation -d harmonisation

-- Encrypt new password first (use Python script above)
-- Then update
UPDATE "user"
SET password = 'gAAAAABnQfR...new_encrypted_password...'
WHERE username = 'admin';
```

### Option 2: Via API (if user update endpoint exists)

Check the API documentation at `http://localhost:8008/docs` for user management endpoints.

---

## Troubleshooting

### "Invalid credentials" Error

```bash
# Verify default user exists
docker exec -it postgres psql -U harmonisation -d harmonisation \
  -c "SELECT username, is_active, role FROM \"user\";"
```

Should show:
```
 username | is_active | role
----------+-----------+-------
 admin    | t         | admin
```

### Token Expired

Simply request a new token:
```bash
curl -X POST "http://localhost:8008/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Backend Not Creating User

Check logs:
```bash
docker logs backend | grep -i "admin user"
```

Should see:
```
✅ Default admin user created (username: admin, password: admin123)
⚠️  CHANGE DEFAULT PASSWORD AFTER FIRST LOGIN!
```

If not, delete the database and restart:
```bash
docker compose down
sudo rm -rf data/postgres/*
docker compose up -d
```

---

## Security Best Practices

1. ✅ **Change default password immediately**
2. ✅ **Use strong passwords (12+ characters, mixed case, numbers, symbols)**
3. ✅ **Don't share JWT tokens**
4. ✅ **Rotate the encryption key for production** (change `ENCRYPTION_KEY` in repository.py)
5. ✅ **Use HTTPS in production** (tokens sent over HTTP are visible)
6. ✅ **Set proper token expiration** (default: 30 minutes)

---

## Quick Test

```bash
# 1. Login
curl -X POST "http://localhost:8008/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 2. Copy the access_token from response

# 3. Test protected endpoint
curl -X GET "http://localhost:8008/virtual-machines" \
  -H "Authorization: Bearer <paste-token-here>"

# Should return: [] (empty list initially)
```

---

**You're all set!** Use `admin` / `admin123` to access the API. 🔐
