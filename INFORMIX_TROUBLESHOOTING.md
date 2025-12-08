# Informix-Corteza Integration Troubleshooting Guide

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Errors and Solutions](#common-errors-and-solutions)
3. [Connection Issues](#connection-issues)
4. [Authentication Errors](#authentication-errors)
5. [Configuration Problems](#configuration-problems)
6. [Performance Issues](#performance-issues)
7. [Docker-Specific Issues](#docker-specific-issues)
8. [Testing and Validation](#testing-and-validation)
9. [Log Analysis](#log-analysis)
10. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Step 1: Verify All Components are Running

```bash
# Check all containers
docker compose ps

# Expected output should show:
# - corteza (Up)
# - ifx (Up, healthy)
# - postgres (Up, healthy)
```

### Step 2: Check Informix Connectivity

```bash
# Test DNS resolution from corteza container
docker compose exec corteza getent hosts ifx

# Expected: IP address of ifx container (e.g., 172.x.x.x)

# Check if port is accessible
docker compose exec corteza bash -c "timeout 5 nc -zv ifx 9088 || echo 'Connection failed'"

# Expected: Connection succeeded (or timeout if port not listening)
```

### Step 3: Verify ODBC Configuration

```bash
# Check ODBC drivers are registered
docker compose exec corteza odbcinst -q -d

# Expected output:
# [IBM Informix Informix ODBC DRIVER]

# Check DSNs are configured
docker compose exec corteza odbcinst -q -s

# Expected output:
# [Infdrv2]
# [ODBC]

# Verify DSN details
docker compose exec corteza cat /root/.odbc.ini | grep -A 10 "^\[Infdrv2\]"
```

### Step 4: Check Environment Variables

```bash
# In corteza container
docker compose exec corteza env | grep -i informix

# Expected:
# INFORMIXDIR=/root/odbc
# LD_LIBRARY_PATH contains /root/odbc/lib:/root/odbc/lib/cli
```

### Step 5: Test DSN Connection

```bash
# Use odbcinst to verify DSN can be read
docker compose exec corteza bash -c "odbcinst -q -s -l | head -5"
```

---

## Common Errors and Solutions

### Error 1: "Data source name not found, and no default driver specified"

**Symptoms:**

- Corteza logs show: `SQLDriverConnect: {IM002} [unixODBC][Driver Manager]Data source name not found`
- Connection fails in web interface
- API returns connection error

**Root Cause:**

- DSN name in Corteza doesn't match odbc.ini
- odbc.ini file not mounted correctly
- ODBC configuration files have incorrect paths

**Solutions:**

1. **Verify DSN Name in odbc.ini:**

```bash
# Check if DSN exists
docker compose exec corteza grep "^\[.*\]" /root/.odbc.ini

# Should show: [Infdrv2]
```

2. **Check File Mounting:**

```bash
# Verify odbc.ini is mounted
docker compose exec corteza ls -la /root/.odbc.ini

# Should show file exists and is readable
```

3. **Verify Corteza DSN:**
   In web interface or API, use:

```
DSN: informix://DSN=Infdrv2;Database=testdb;LogonID=informix;pwd=in4mix
```

**NOT:** `informix://DSN=Infdrv2` (this is incorrect)

4. **Check DSN Section Headers:**

```bash
# Verify exact section header
docker compose exec corteza grep "^\[Infdrv2\]" /root/.odbc.ini

# Should show: [Infdrv2]
# NOT: [ Infdrv2 ] or [Infdrv2 ]
```

---

### Error 2: "Driver not found"

**Symptoms:**

- Error message mentions driver library not found
- ODBC driver not registered

**Root Cause:**

- Driver library path incorrect
- Driver not registered in odbcinst.ini
- Missing LD_LIBRARY_PATH configuration

**Solutions:**

1. **Verify Driver Library Exists:**

```bash
docker compose exec corteza ls -la /root/odbc/lib/cli/iclis09b.so

# Should show file exists (approximately 1.9MB)
```

2. **Check odbcinst.ini Registration:**

```bash
docker compose exec corteza cat /etc/odbcinst.ini | grep -A 3 "IBM Informix"

# Should show:
# [IBM Informix Informix ODBC DRIVER]
# Driver=/root/odbc/lib/cli/iclis09b.so
```

3. **Verify LD_LIBRARY_PATH:**

```bash
docker compose exec corteza env | grep LD_LIBRARY_PATH

# Should include: /root/odbc/lib:/root/odbc/lib/cli
```

4. **Check Driver Registration:**

```bash
docker compose exec corteza odbcinst -q -d

# Should list: [IBM Informix Informix ODBC DRIVER]
```

---

### Error 3: "Could not connect to database"

**Symptoms:**

- Connection timeout
- Unable to reach Informix server
- Network-related errors

**Root Cause:**

- Informix server not running
- Incorrect hostname in sqlhosts
- Network connectivity issues
- Wrong port configuration

**Solutions:**

1. **Verify Informix is Running:**

```bash
docker compose ps ifx

# Should show 'Up' and 'healthy'
```

2. **Check Informix Logs:**

```bash
docker compose logs ifx | tail -20

# Look for startup errors or connection issues
```

3. **Test Network Connectivity:**

```bash
# From corteza container
docker compose exec corteza getent hosts ifx

# Should resolve to IP address

# Test port connectivity
docker compose exec corteza timeout 5 bash -c "exec 3<>/dev/tcp/ifx/9088" && echo "Port 9088 is open" || echo "Port 9088 is closed"
```

4. **Verify sqlhosts Configuration:**

```bash
docker compose exec corteza cat /root/odbc/etc/sqlhosts

# Should show:
# informix        onsoctcp        ifx         9088

# Verify format: <servername> <protocol> <hostname> <port>
# Must match Servername in odbc.ini
```

---

### Error 4: "Invalid password or username"

**Symptoms:**

- Authentication failed errors
- Login denied messages

**Root Cause:**

- Incorrect username or password in odbc.ini
- User doesn't have database access
- Account locked or expired

**Solutions:**

1. **Verify Credentials in odbc.ini:**

```bash
docker compose exec corteza grep -E "LogonID|pwd" /root/.odbc.ini | grep Infdrv2 -A 2

# Check if credentials are correct
```

2. **Test with Informix:**

```bash
# Connect to ifx container
docker compose exec ifx bash

# Connect to database
dbaccess testdb - <<EOF
SELECT COUNT(*) FROM systables;
EOF

# Should succeed with testdb database
```

3. **Check User Permissions:**

```bash
# In ifx container
dbaccess sysmaster - <<EOF
SELECT username, usertype FROM sysusers WHERE username = 'informix';
EOF
```

---

### Error 5: "Database not found"

**Symptoms:**

- Error says database doesn't exist
- Specified database name incorrect

**Root Cause:**

- Wrong database name in odbc.ini
- Database doesn't exist on server
- User doesn't have access to database

**Solutions:**

1. **List Available Databases:**

```bash
# In ifx container
dbaccess sysmaster - <<EOF
SELECT name FROM sysdatabases;
EOF
```

2. **Check DSN Database Parameter:**

```bash
docker compose exec corteza grep "Database=" /root/.odbc.ini | grep Infdrv2

# Should show correct database name (e.g., testdb)
```

---

## Connection Issues

### Issue: Intermittent Connection Failures

**Diagnosis:**

- Connections work sometimes but not always
- Timeout errors appear randomly

**Solutions:**

1. **Enable Connection Pooling:**
   Add to `/odbc/odbc.ini`:

```ini
InformixPooling=1
InformixCPTimeout=60
```

2. **Check Network Stability:**

```bash
# Ping test from corteza to ifx
docker compose exec corteza ping -c 10 ifx

# Check packet loss and latency
```

3. **Verify Container Networking:**

```bash
# Check corteza network
docker network inspect runner-src_internal

# Verify both corteza and ifx are in same network
```

---

### Issue: Slow Connection Times

**Diagnosis:**

- Connections take >5 seconds
- Poor performance

**Solutions:**

1. **Enable Connection Pooling:**

```ini
# In odbc.ini [ODBC] section or DSN section
InformixPooling=1
InformixCPTimeout=300
```

2. **Optimize DNS Resolution:**

```bash
# Add ifx to hosts file
docker compose exec corteza bash -c "echo '$(docker compose exec -T ifx hostname -I | tr -d " ")  ifx' >> /etc/hosts"
```

3. **Check Informix Performance:**

```bash
# In ifx container
onstat -

# Check server status and performance metrics
```

---

## Authentication Errors

### Issue: CSRF Token Errors (Web Interface)

**Symptoms:**

- 403 Forbidden errors
- CSRF token not found
- Cannot authenticate via web interface

**Solutions:**

1. **Use API Directly:**

```bash
# Get token via API
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin-os@srm-cs.ma","password":"admin-os@srm-cs.ma"}'

# Use returned token for API calls
```

2. **Clear Browser Cookies:**

- Clear cookies for localhost
- Try incognito/private browsing mode

3. **Use Alternative Admin Account:**

- Try: <admin-srm@srm-cs.ma>
- Or: <viewer-srm@srm-cs.ma>

---

## Configuration Problems

### Issue: ODBC Files Not Mounted

**Diagnosis:**

- Files exist in ./odbc/ but not in container
- Configuration changes don't take effect

**Solutions:**

1. **Verify docker-compose.yml Mounts:**

```yaml
# Check in docker-compose.yml
volumes:
  - ./odbc/odbcinst.ini:/etc/odbcinst.ini
  - ./odbc/odbc.ini:/root/.odbc.ini
  - ./odbc/sqlhosts:/root/odbc/etc/sqlhosts
```

2. **Recreate Containers:**

```bash
docker compose down
docker compose up -d
```

3. **Verify Mounts:**

```bash
# Check files are mounted
docker compose exec corteza ls -la /root/.odbc.ini
docker compose exec corteza ls -la /etc/odbcinst.ini
docker compose exec corteza ls -la /root/odbc/etc/sqlhosts
```

---

### Issue: Changes Not Taking Effect

**Diagnosis:**

- Configuration updated but errors persist
- Old values still being used

**Solutions:**

1. **Restart Corteza Container:**

```bash
docker compose restart corteza
```

2. **Clear Configuration Cache:**

```bash
# Remove any cached configuration
docker compose exec corteza rm -f /tmp/*.ini /tmp/*.log
docker compose restart corteza
```

3. **Verify Configuration Update:**

```bash
# Check actual file in container
docker compose exec corteza cat /root/.odbc.ini
```

---

## Performance Issues

### Issue: Slow Queries

**Diagnosis:**

- Queries take longer than expected
- Timeout errors

**Solutions:**

1. **Enable Query Logging in Informix:**

```bash
# In ifx container
onmode -wf SQLLOG=1
```

2. **Check Query Plans:**

```bash
# Connect to database
dbaccess testdb - <<EOF
SET EXPLAIN ON;
SELECT * FROM your_table WHERE condition;
SET EXPLAIN OFF;
EOF
```

3. **Optimize Connection Pooling:**

```ini
# In odbc.ini
InformixPooling=1
InformixCPTimeout=300
InformixCPMatch=1  # Use relaxed matching for better reuse
```

---

### Issue: High CPU/Memory Usage

**Diagnosis:**

- Container using excessive resources
- Slow response times

**Solutions:**

1. **Monitor Resource Usage:**

```bash
docker stats corteza ifx

# Watch CPU and memory usage
```

2. **Adjust Pool Settings:**

```ini
# Reduce connection pool timeout
InformixCPTimeout=60
```

3. **Check for Connection Leaks:**

```bash
# In ifx container
onstat -g cnp

# Check connection pool statistics
```

---

## Docker-Specific Issues

### Issue: Cannot Resolve Container Name

**Diagnosis:**

- DNS resolution fails for 'ifx'
- Hostname not found errors

**Solutions:**

1. **Verify Network:**

```bash
# Check network
docker network inspect runner-src_internal

# Both corteza and ifx must be connected
```

2. **Check Service Names:**

```bash
# In docker-compose.yml
services:
  ifx:  # Service name used as hostname
    # ...

  corteza:
    # Uses 'ifx' as hostname to connect
```

3. **Add Explicit DNS:**

```yaml
# In docker-compose.yml
services:
  corteza:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

---

### Issue: Container Restart Loops

**Diagnosis:**

- Containers restarting continuously
- Service not staying up

**Solutions:**

1. **Check Logs:**

```bash
docker compose logs --tail=50 ifx
docker compose logs --tail=50 corteza

# Look for fatal errors
```

2. **Verify Configuration:**

```bash
# Check config files
docker compose exec ifx cat /opt/ibm/config/onconfig
```

3. **Check Resource Limits:**

```yaml
# In docker-compose.yml
services:
  ifx:
    mem_limit: 2g
    cpu_shares: 1024
```

---

## Testing and Validation

### Test 1: Basic Connectivity

```bash
#!/bin/bash
# Test 1: Check all containers running
echo "=== Checking Containers ==="
docker compose ps | grep -E "corteza|ifx" | grep "Up"

# Test 2: Check DNS resolution
echo "=== DNS Resolution ==="
docker compose exec corteza getent hosts ifx

# Test 3: Check port connectivity
echo "=== Port Connectivity ==="
docker compose exec corteza timeout 5 nc -zv ifx 9088

# Test 4: Check ODBC drivers
echo "=== ODBC Drivers ==="
docker compose exec corteza odbcinst -q -d

# Test 5: Check DSNs
echo "=== DSNs ==="
docker compose exec corteza odbcinst -q -s

echo "=== Tests Complete ==="
```

### Test 2: Full Connection Test

```bash
#!/bin/bash
# Complete integration test

# 1. Get authentication token
echo "=== Authentication ==="
TOKEN=$(curl -s -X POST http://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin-os@srm-cs.ma","password":"admin-os@srm-cs.ma"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "Failed to get auth token"
  exit 1
fi

echo "Token: ${TOKEN:0:20}..."

# 2. Create DAL connection
echo "=== Creating DAL Connection ==="
curl -X POST http://localhost/api/system/dal/connections/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "handle": "test-informix",
    "type": "corteza::dal:connection:dsn",
    "meta": {"name": "Test Connection"},
    "config": {
      "dal": {
        "type": "informix",
        "params": {"dsn": "informix://Infdrv2"},
        "modelIdent": "{{namespace}}_{{module}}"
      }
    }
  }'

echo -e "\n=== Test Complete ==="
```

---

## Log Analysis

### Corteza Logs

```bash
# View real-time logs
docker compose logs -f corteza

# Filter for DAL messages
docker compose logs corteza | grep -i dal

# Filter for connection errors
docker compose logs corteza | grep -i "could not connect"
```

**What to look for:**

- `dal connection created` - Successful connection
- `could not connect` - Connection failed
- `DSN` - DSN-related messages
- `ODBC` - ODBC-specific errors

### Informix Logs

```bash
# View Informix logs
docker compose logs ifx | tail -100

# Check online log
docker compose exec ifx onstat -

# Check error log
docker compose exec ifx find /opt/ibm -name "*.log" -o -name "*online*" 2>/dev/null
```

### ODBC Trace Logs

```bash
# Enable tracing
# Edit odbc.ini:
# [ODBC]
# Trace=1
# TraceFile=/tmp/odbctrace.out

# View trace
docker compose exec corteza cat /tmp/odbctrace.out

# Disable after debugging:
# [ODBC]
# Trace=0
```

---

## Getting Help

### Information to Gather

Before seeking help, collect:

1. **Configuration:**

```bash
# Save configuration
docker compose exec corteza cat /root/.odbc.ini > /tmp/odbc_config.txt
docker compose exec corteza cat /etc/odbcinst.ini > /tmp/odbcinst_config.txt
docker compose exec corteza cat /root/odbc/etc/sqlhosts > /tmp/sqlhosts_config.txt
```

2. **Logs:**

```bash
# Save logs
docker compose logs corteza > /tmp/corteza_logs.txt
docker compose logs ifx > /tmp/informix_logs.txt
```

3. **Environment:**

```bash
# Save environment
docker compose exec corteza env > /tmp/corteza_env.txt
docker compose ps > /tmp/container_status.txt
```

4. **Error Messages:**

```bash
# Capture exact error
docker compose logs corteza 2>&1 | grep -A 5 -B 5 "ERROR"
```

### Common Resources

- **Corteza Documentation:** <https://docs.cortezaproject.org/>
- **Informix Documentation:** <https://www.ibm.com/docs/en/informix>
- **ODBC Reference:** <https://docs.microsoft.com/en-us/sql/odbc/>

### Support Channels

- **Corteza Community:** [Community Forum](https://forum.cortezaproject.org/)
- **IBM Informix Support:** IBM Support Portal
- **Internal Team:** <devops@srm-cs.ma>

---

## Quick Reference

### Essential Commands

```bash
# Restart services
docker compose restart

# Check logs
docker compose logs -f <service>

# Execute commands in container
docker compose exec <service> bash

# Check connectivity
docker compose exec corteza nc -zv ifx 9088

# List ODBC drivers
docker compose exec corteza odbcinst -q -d

# List DSNs
docker compose exec corteza odbcinst -q -s
```

### Key Files

| File          | Location                      | Purpose             |
| ------------- | ----------------------------- | ------------------- |
| odbc.ini      | `/odbc/odbc.ini`              | DSN definitions     |
| odbcinst.ini  | `/odbc/odbcinst.ini`          | Driver definitions  |
| sqlhosts      | `/odbc/sqlhosts`              | Server connectivity |
| Corteza logs  | `docker compose logs corteza` | Application logs    |
| Informix logs | `docker compose logs ifx`     | Database logs       |

### File Paths in Containers

| Path                             | Mounted From          | Purpose              |
| -------------------------------- | --------------------- | -------------------- |
| `/root/.odbc.ini`                | `./odbc/odbc.ini`     | User DSN config      |
| `/etc/odbcinst.ini`              | `./odbc/odbcinst.ini` | System driver config |
| `/root/odbc/etc/sqlhosts`        | `./odbc/sqlhosts`     | Server connectivity  |
| `/root/odbc/lib/cli/iclis09b.so` | Built-in              | ODBC driver library  |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**For:** SRM-CS Team
