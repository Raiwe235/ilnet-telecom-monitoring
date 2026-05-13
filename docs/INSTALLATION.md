# Installation Guide

## Prerequisites

### System Requirements
- OS: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- CPU: 2+ cores
- RAM: 4GB minimum, 8GB recommended
- Disk: 20GB minimum (for metrics storage)

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Python 3.11+ (for local development)

### Network Requirements
- Access to SNMP devices (port 161/UDP)
- HTTP/HTTPS access for dashboard (port 3000)
- API access (port 8000)

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/Raiwe235/ilnet-telecom-monitoring.git
cd ilnet-telecom-monitoring
```

### 2. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

**Important settings to configure:**
```env
SNMP_COMMUNITY=public          # SNMP community string
COLLECTOR_INTERVAL=30          # Collection interval (seconds)
PROMETHEUS_RETENTION=15d       # Data retention period
GRAFANA_ADMIN_PASSWORD=admin   # Change this!
JWT_SECRET_KEY=your-secret     # Use strong value
TLS_ENABLED=false              # Set to true in production
```

### 3. Configure Devices

Edit `config/snmp_devices.json`:

```json
{
  "devices": {
    "router_main": {
      "host": "192.168.1.1",
      "name": "Main Router",
      "community": "public",
      "version": "2c",
      "device_type": "router",
      "tags": ["core", "production"],
      "enabled": true
    },
    "switch_core": {
      "host": "192.168.1.2",
      "name": "Core Switch",
      "community": "public",
      "version": "2c",
      "device_type": "switch",
      "tags": ["core", "production"],
      "enabled": true
    }
  }
}
```

### 4. Start Services

```bash
# Start all services in background
docker-compose -f config/docker-compose.yml up -d

# Verify services are running
docker-compose -f config/docker-compose.yml ps

# View logs
docker-compose -f config/docker-compose.yml logs -f
```

### 5. Verify Installation

```bash
# Check collector health
curl http://localhost:8000/api/health

# Check Prometheus
curl http://localhost:9090/-/healthy

# Check AlertManager
curl http://localhost:9093/-/healthy
```

### 6. Access Web Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / admin* |
| Prometheus | http://localhost:9090 | N/A |
| AlertManager | http://localhost:9093 | N/A |
| Collector API | http://localhost:8000 | JWT auth |

*Change Grafana password immediately!

## Local Development Setup

### 1. Create Python Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-flask  # For testing
```

### 3. Configure Environment

```bash
cp .env.example .env
export FLASK_ENV=development
export FLASK_APP=src.api.app
```

### 4. Run Collector

```bash
python -m src.api.app
```

### 5. Run Tests

```bash
pytest
pytest --cov=src --cov-report=html
```

## Production Deployment

### 1. Security Hardening

```bash
# Generate strong JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
JWT_SECRET_KEY=<generated-secret>
TLS_ENABLED=true
DEBUG=false
```

### 2. SSL/TLS Configuration

```bash
# Create certificate directory
mkdir -p certs

# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out certs/server.crt -keyout certs/server.key -days 365

# Or use Let's Encrypt (production)
# See HTTPS_SETUP.md for details
```

### 3. Database Backup

```bash
# Create backup directory
mkdir -p backups

# Setup automated backups
crontab -e
# Add: 0 2 * * * docker-compose exec prometheus tar czf /backups/prometheus-$(date +\%Y\%m\%d).tar.gz /prometheus
```

### 4. Monitoring the Monitor

Set up external monitoring:
- Uptime robot for health checks
- Log aggregation (ELK stack)
- Metrics export to central monitoring

## Troubleshooting Installation

### Services won't start

```bash
# Check Docker daemon
docker ps

# Check Docker Compose version
docker-compose --version

# Verify image builds
docker-compose -f config/docker-compose.yml build --no-cache

# Check logs
docker-compose logs collector
```

### Port conflicts

```bash
# Find process using port
lsof -i :8000
fuser 8000/tcp

# Change ports in docker-compose.yml or .env
```

### SNMP not working

```bash
# Test SNMP connectivity from collector
docker-compose exec snmp-collector snmpwalk -v 2c -c public 192.168.1.1 1.3.6.1.2.1.1.1.0

# Verify network connectivity
docker-compose exec snmp-collector ping 192.168.1.1

# Check firewall
sudo iptables -L | grep 161
```

### API authentication fails

```bash
# Check JWT secret
grep JWT_SECRET_KEY .env

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

## Upgrading Installation

```bash
# Backup data
docker-compose exec prometheus tar czf /backups/prometheus-backup.tar.gz /prometheus

# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f config/docker-compose.yml build --no-cache
docker-compose -f config/docker-compose.yml down
docker-compose -f config/docker-compose.yml up -d

# Verify health
curl http://localhost:8000/api/health
```

## Uninstallation

```bash
# Stop and remove containers
docker-compose -f config/docker-compose.yml down

# Remove volumes (data)
docker-compose -f config/docker-compose.yml down -v

# Remove images
docker rmi ilnet-collector:latest
```

## Next Steps

1. Configure additional devices in `config/snmp_devices.json`
2. Create Grafana dashboards
3. Configure alert channels
4. Set up backup strategy
5. Implement monitoring of the monitor
6. Document your customizations

See [Configuration Guide](./CONFIGURATION.md) for detailed setup instructions.
