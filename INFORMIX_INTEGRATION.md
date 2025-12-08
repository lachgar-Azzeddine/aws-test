# Corteza-Informix Database Integration Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration Components](#configuration-components)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [ODBC Configuration](#odbc-configuration)
6. [Corteza Configuration](#corteza-configuration)
7. [Environment-Specific Setup](#environment-specific-setup)
8. [Testing and Verification](#testing-and-verification)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## Overview

This guide explains how to integrate an IBM Informix database with Corteza as an additional data source alongside the main PostgreSQL database. This allows Corteza to read and write data to both databases simultaneously.

### Key Concepts

- **Main Database**: PostgreSQL (stores Corteza configuration, users, modules metadata)
- **Additional Data Sources**: Informix (for application data via DAL - Data Access Layer)
- **DAL Service**: Corteza's Data Access Layer that manages multiple database connections
- **ODBC**: Open Database Connectivity - the bridge between Go applications and Informix

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Corteza Application                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  DAL (Data Access Layer) Service                    │  │
│  │  ┌─────────────────┐  ┌──────────────────────────┐  │  │
│  │  │  PostgreSQL     │  │  Informix Connection     │  │  │
│  │  │  (Main DB)      │  │  via ODBC                │  │  │
│  │  └─────────────────┘  └──────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Web Interface & API                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ ODBC Driver
                              │
┌─────────────────────────────────────────────────────────────┐
│              IBM Informix Database                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Database:    │  │ Port: 9088   │  │ Protocol:    │      │
│  │ testdb       │  │ (ONSOCTCP)   │  │ onsoctcp     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration Components

The integration requires configuration in three areas:

1. **ODBC Files** (`/odbc/` directory)
   - `odbc.ini` - Data source definitions
   - `odbcinst.ini` - Driver definitions
   - `sqlhosts` - Informix server connectivity

2. **Corteza Service** (Docker container)
   - Mounts ODBC configuration files
   - Contains Informix ODBC driver libraries
   - Runs Corteza server with DAL support

3. **Corteza Database Connections** (Web UI/API)
   - Defines DAL connections in Corteza
   - Maps modules to external databases

---

## Step-by-Step Setup

### Phase 1: ODBC Configuration

Configure ODBC files in the `/odbc/` directory:

#### 1.1 Configure `odbc.ini`

Create or update `/odbc/odbc.ini`:

```ini
[ODBC Data Sources]
Infdrv2=IBM Informix Informix ODBC DRIVER

[Infdrv2]
Driver=/root/odbc/lib/cli/iclis09b.so
Description=IBM Informix ODBC Driver
Servername=informix              # Must match sqlhosts entry
Database=testdb                  # Your Informix database name
LogonID=informix                 # Informix username
pwd=in4mix                       # Informix password
CursorBehavior=0
CLIENT_LOCALE=en_us.8859-1       # Client locale
DB_LOCALE=en_us.8859-1           # Database locale
TRANSLATIONDLL=/home/informix/odbc/lib/esql/igo4a304.so

[ODBC]
UNICODE=UCS-2
Trace=0
TraceFile=/tmp/odbctrace.out
InstallDir=/extra/informix
TRACEDLL=idmrs09a.so
```

#### 1.2 Configure `odbcinst.ini`

Create or update `/odbc/odbcinst.ini`:

```ini
[ODBC Drivers]
IBM Informix Informix ODBC DRIVER=Installed

[IBM Informix Informix ODBC DRIVER]
Driver=/root/odbc/lib/cli/iclis09b.so
Setup=/root/odbc/lib/cli/iclis09b.so
APILevel=1
ConnectFunctions=YYY
DriverODBCVer=03.51
FileUsage=0
SQLLevel=1
smProcessPerConnect=Y
```

#### 1.3 Configure `sqlhosts`

Create or update `/odbc/sqlhosts`:

```
informix        onsoctcp        ifx         9088
```

Format: `<servername> <protocol> <hostname> <port>`

- **servername**: Must match `Servername` in `odbc.ini`
- **protocol**: Network protocol (onsoctcp = TCP/IP with shared memory)
- **hostname**: Container name or IP address of Informix server
- **port**: Informix port number

### Phase 2: Docker Compose Configuration

Ensure your `docker-compose.yml` mounts the ODBC files:

```yaml
services:
  corteza:
    # ... other configuration ...
    volumes:
      - ./odbc/odbcinst.ini:/etc/odbcinst.ini
      - ./odbc/odbc.ini:/root/.odbc.ini
      - ./odbc/sqlhosts:/root/odbc/etc/sqlhosts
      # ... other volumes ...
    environment:
      - INFORMIXDIR=/root/odbc
      - LD_LIBRARY_PATH=/root/odbc/lib:/root/odbc/lib/cli:/root/odbc/lib/esql

  ifx:
    image: ibmcom/informix-developer-database:14.10.FC7W1DE
    # ... other configuration ...
```

### Phase 3: Corteza Database Connection

Create a DAL connection in Corteza via web interface or API.

#### Via Web Interface

1. Navigate to: **Admin Panel** → **Settings** → **Database Connections**
2. Click **Create New Connection**
3. Fill in:
   - **Handle**: `informix-connection`
   - **Type**: `corteza::dal:connection:dsn`
   - **Name**: `Informix Database`
   - **Connection Type**: `informix`
   - **DSN**: `informix://DSN=Infdrv2;Database=testdb;LogonID=informix;pwd=in4mix`
   - **Model Identifier**: `{{namespace}}_{{module}}`

#### Via API

```bash
curl -X POST http://localhost/api/system/dal/connections/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "handle": "informix-connection",
    "type": "corteza::dal:connection:dsn",
    "meta": {
      "name": "Informix Database",
      "ownership": "admin-srm@srm-cs.ma"
    },
    "config": {
      "dal": {
        "type": "informix",
        "params": {
          "dsn": "informix://Infdrv2"
        },
        "modelIdent": "{{namespace}}_{{module}}"
      }
    }
  }'
```

#### Via Direct Configuration

For the working configuration you discovered:

**Connection Parameters:**

```
Type: corteza::dal:connection:dsn
```

**DSN Format:**

```json
{
  "dsn": "informix://DSN=Infdrv2;Database=testdb;LogonID=informix;pwd=in4mix"
}
```

---

## ODBC Configuration Details

### `odbc.ini` Parameters

| Parameter     | Description                          | Example                          |
| ------------- | ------------------------------------ | -------------------------------- |
| Driver        | Path to ODBC driver library          | `/root/odbc/lib/cli/iclis09b.so` |
| Servername    | Server identifier (matches sqlhosts) | `informix`                       |
| Database      | Informix database name               | `testdb`                         |
| LogonID       | Database username                    | `informix`                       |
| pwd           | Database password                    | `in4mix`                         |
| CLIENT_LOCALE | Client locale setting                | `en_us.8859-1`                   |
| DB_LOCALE     | Database locale setting              | `en_us.8859-1`                   |
| UNICODE       | Unicode mode                         | `UCS-2` or `UCS-4`               |

### `sqlhosts` Parameters

Format: `<servername> <protocol> <hostname> <port>`

| Field      | Description              | Example                |
| ---------- | ------------------------ | ---------------------- |
| servername | Unique server identifier | `informix`             |
| protocol   | Connection protocol      | `onsoctcp`, `olsoctcp` |
| hostname   | Server hostname/IP       | `ifx`, `192.168.1.100` |
| port       | Port number              | `9088`                 |

**Supported Protocols:**

- `onsoctcp` - TCP/IP with shared memory
- `olsoctcp` - TCP/IP with local loopback
- `onsocecs` - Shared memory with password authentication
- `drsoctcp` - Direct TCP/IP connection

---

## Environment-Specific Setup

### Development Environment

For development with local Informix:

```ini
# odbc.ini - Development
[dev_informix]
Driver=/root/odbc/lib/cli/iclis09b.so
Servername=dev_ifx
Database=devdb
LogonID=devuser
pwd=devpass
CLIENT_LOCALE=en_us.8859-1
DB_LOCALE=en_us.8859-1

# sqlhosts - Development
dev_ifx    onsoctcp    localhost    9088
```

**Corteza DSN:** `informix://DSN=dev_informix;Database=devdb;LogonID=devuser;pwd=devpass`

### Staging Environment

```ini
# odbc.ini - Staging
[staging_informix]
Driver=/root/odbc/lib/cli/iclis09b.so
Servername=staging_ifx
Database=staging_db
LogonID=staging_user
pwd=staging_pass
CLIENT_LOCALE=en_us.8859-1
DB_LOCALE=en_us.8859-1

# sqlhosts - Staging
staging_ifx    onsoctcp    staging-ifx.srm-cs.ma    9088
```

**Corteza DSN:** `informix://DSN=staging_informix;Database=staging_db;LogonID=staging_user;pwd=staging_pass`

### Production Environment

```ini
# odbc.ini - Production
[prod_informix]
Driver=/root/odbc/lib/cli/iclis09b.so
Servername=prod_ifx
Database=production_db
LogonID=prod_user
pwd=<secure_password>
CLIENT_LOCALE=en_us.8859-1
DB_LOCALE=en_us.8859-1

# sqlhosts - Production
prod_ifx    onsoctcp    prod-informix.srm-cs.ma    9088
```

**Corteza DSN:** `informix://DSN=prod_informix;Database=production_db;LogonID=prod_user;pwd=<secure_password>`

### Environment Variable Configuration

Create environment-specific `.env` files:

```bash
# .env.development
INFORMIX_SERVER=dev_ifx
INFORMIX_DATABASE=devdb
INFORMIX_USER=devuser
INFORMIX_PASSWORD=devpass
INFORMIX_HOST=localhost
INFORMIX_PORT=9088

# .env.staging
INFORMIX_SERVER=staging_ifx
INFORMIX_DATABASE=staging_db
INFORMIX_USER=staging_user
INFORMIX_PASSWORD=staging_pass
INFORMIX_HOST=staging-ifx.srm-cs.ma
INFORMIX_PORT=9088

# .env.production
INFORMIX_SERVER=prod_ifx
INFORMIX_DATABASE=production_db
INFORMIX_USER=prod_user
INFORMIX_PASSWORD=<secure_password>
INFORMIX_HOST=prod-informix.srm-cs.ma
INFORMIX_PORT=9088
```

Then generate ODBC configuration from environment variables:

```bash
#!/bin/bash
# generate_odbc_config.sh

source .env.${ENVIRONMENT:-development}

cat > odbc.ini << EOF
[ODBC Data Sources]
${INFORMIX_SERVER}=IBM Informix Informix ODBC DRIVER

[${INFORMIX_SERVER}]
Driver=/root/odbc/lib/cli/iclis09b.so
Servername=${INFORMIX_SERVER}
Database=${INFORMIX_DATABASE}
LogonID=${INFORMIX_USER}
pwd=${INFORMIX_PASSWORD}
CLIENT_LOCALE=en_us.8859-1
DB_LOCALE=en_us.8859-1

[ODBC]
UNICODE=UCS-2
Trace=0

EOF

cat > sqlhosts << EOF
${INFORMIX_SERVER}    onsoctcp    ${INFORMIX_HOST}    ${INFORMIX_PORT}
EOF
```

---

## Testing and Verification

### 1. Verify ODBC Driver Installation

```bash
docker compose exec corteza odbcinst -q -d
```

Expected output:

```
[IBM Informix Informix ODBC DRIVER]
```

### 2. Verify DSN Configuration

```bash
docker compose exec corteza odbcinst -q -s
```

Expected output:

```
[Infdrv2]
[ODBC]
```

### 3. Test Informix Connectivity

```bash
docker compose exec corteza bash -c "getent hosts ifx"
```

Expected output: IP address of Informix container

### 4. Test ODBC Connection

```bash
docker compose exec corteza bash -c "odbcinst -q -s -l"
```

### 5. Verify Corteza DAL Connection

Check Corteza logs:

```bash
docker compose logs corteza | grep -i dal
```

Look for successful connection messages:

```
{"level":"info","msg":"dal connection created successfully","ID":"..."}
```

### 6. Test via API

```bash
curl -X GET http://localhost/api/system/dal/connections/ \
  -H "Authorization: Bearer <TOKEN>"
```

---

## Troubleshooting

### Error: "Data source name not found"

**Cause:** DSN name not found in `odbc.ini`

**Solution:**

1. Verify DSN exists in `odbc.ini`: `grep "^\[.*\]" /odbc/odbc.ini`
2. Use correct DSN name in Corteza configuration
3. Ensure `odbc.ini` is mounted to `/root/.odbc.ini` in corteza container

**Check:**

```bash
docker compose exec corteza cat /root/.odbc.ini | grep -A 10 "^\[.*\]"
```

### Error: "Driver not found"

**Cause:** ODBC driver library not found or not installed

**Solution:**

1. Verify driver library exists: `ls -la /root/odbc/lib/cli/iclis09b.so`
2. Check `LD_LIBRARY_PATH` includes driver directory
3. Verify driver is registered in `odbcinst.ini`

**Check:**

```bash
docker compose exec corteza env | grep LD_LIBRARY_PATH
```

### Error: "Could not connect to database"

**Cause:** Cannot reach Informix server

**Solution:**

1. Verify Informix container is running: `docker compose ps ifx`
2. Check network connectivity: `docker compose exec corteza getent hosts ifx`
3. Verify port is correct in `sqlhosts`
4. Check Informix logs: `docker compose logs ifx`

### Error: "CSRF token not found"

**Cause:** Cannot authenticate to Corteza API

**Solution:**

1. Use web interface to create connection (no API required)
2. Or implement proper CSRF handling in API requests

### Error: "Database locale mismatch"

**Cause:** CLIENT_LOCALE and DB_LOCALE don't match database locale

**Solution:**

1. Check actual database locale: `SELECT * FROM sysmaster:sysdbslocale`
2. Update locale settings in `odbc.ini` to match

---

## DSN Format Reference

### Formats

#### 1. DSN Name Only (Recommended)

```
informix://Infdrv2
```

Corteza driver strips `informix://` and uses `Infdrv2` as DSN name.

#### 2. Full ODBC String

```
informix://DSN=Infdrv2;Database=testdb;LogonID=informix;pwd=in4mix
```

Explicit connection string with all parameters.

#### 3. URL Format (Not Recommended for Informix)

```
informix://informix:in4mix@ifx:9088/testdb?CLIENT_LOCALE=en_us.8859-1&DB_LOCALE=en_us.8859-1
```

URL format - may work but less reliable than DSN-based approach.

---

## Maintenance

### Regular Tasks

1. **Monitor Connection Health**
   - Check DAL connection status in Corteza Admin panel
   - Review connection issues in logs

2. **Update ODBC Configuration**
   - Keep ODBC driver libraries updated
   - Review and update DSN configurations

3. **Security**
   - Rotate Informix passwords regularly
   - Use environment variables for sensitive data
   - Limit database user permissions

### Backup and Recovery

1. **ODBC Configuration Backup**

```bash
tar -czf odbc_backup_$(date +%Y%m%d).tar.gz odbc/
```

2. **Corteza DAL Connection Export**
   Export connection configurations via API for backup

### Performance Optimization

1. **Connection Pooling**
   Configure in `odbc.ini`:

   ```ini
   InformixPooling=1
   InformixCPTimeout=60
   ```

2. **Cursor Behavior**

   ```ini
   CursorBehavior=0  # Default
   # or
   CursorBehavior=1  # Close cursor on commit
   ```

---

## Additional Resources

- [Corteza DAL Documentation](https://docs.cortezaproject.org/)
- [IBM Informix ODBC Guide](https://www.ibm.com/docs/en/informix/14.10)
- [ODBC Specification](https://docs.microsoft.com/en-us/sql/odbc/)

---

## Quick Reference

### Essential Files

- `/odbc/odbc.ini` - Data source definitions
- `/odbc/odbcinst.ini` - Driver definitions
- `/odbc/sqlhosts` - Informix connectivity

### Key Commands

```bash
# List ODBC drivers
odbcinst -q -d

# List DSNs
odbcinst -q -s

# Check Informix connectivity
getent hosts ifx

# View Corteza logs
docker compose logs corteza | grep -i dal
```

### Quick Setup Checklist

- [ ] Configure `odbc.ini` with correct DSN
- [ ] Configure `odbcinst.ini` with driver path
- [ ] Configure `sqlhosts` with server info
- [ ] Mount ODBC files to corteza container
- [ ] Set INFORMIXDIR environment variable
- [ ] Create DAL connection in Corteza
- [ ] Test connection

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Maintained By:** DevOps Team
