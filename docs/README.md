# ILNET TELECOM - Network Supervision Platform

## 🎯 Project Overview

This is a comprehensive, secure network monitoring and traffic analysis platform designed for ILNET TELECOM. The platform provides real-time supervision of network devices with a modern dashboard, advanced alerting, and detailed analytics.

### Key Features

✅ **SNMP-based Device Monitoring**
- Real-time metrics collection from network devices
- Support for routers, switches, and other SNMP-enabled devices
- Interface traffic analysis and error tracking

✅ **Real-time Dashboard**
- Grafana-based visualization
- Customizable dashboards
- Live metric streaming

✅ **Advanced Alerting**
- Prometheus alerting rules
- Multiple notification channels
- Alert aggregation and inhibition

✅ **Security First**
- JWT-based API authentication
- TLS/SSL support
- Secure credential management
- Role-based access control (RBAC)

✅ **Scalable Architecture**
- Docker containerization
- Redis caching
- Time-series database (Prometheus)
- Modular Python codebase

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           Network Devices (SNMP)                    │
│    (Routers, Switches, Firewalls, etc.)            │
└──────────────────────────┬──────────────────────────┘
                           │ SNMP v2c
                           ↓
┌─────────────────────────────────────────────────────┐
│      SNMP Collector (Python Flask)                  │
│  - Device management                                │
│  - Metrics collection                               │
│  - API (REST)                                       │
│  - Authentication (JWT)                             │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
           ↓                          ↓
   ┌──────────────┐         ┌──────────────┐
   │  Prometheus  │         │    Redis     │
   │  Time-Series │         │    Cache     │
   │   Database   │         │              │
   └──────┬───────┘         └──────────────┘
          │
          ↓
   ┌──────────────┐
   │   Grafana    │
   │  Dashboard   │
   │  & Alerts    │
   └──────┬───────┘
          │
          ↓
   ┌──────────────────────┐
   │   AlertManager       │
   │   - Email            │
   │   - Webhooks         │
   │   - PagerDuty, etc.  │
   └──────────────────────┘
```

## 📋 Technology Stack

| Component | Technology | Version |
|-----------|-----------|----------|
| Backend | Python | 3.11 |
| Web Framework | Flask | 3.0+ |
| SNMP | pysnmp | 4.4+ |
| Monitoring | Prometheus | Latest |
| Visualization | Grafana | Latest |
| Cache | Redis | 7+ |
| Containerization | Docker & Docker Compose | Latest |
| Authentication | JWT | - |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- Python 3.11+ (for local development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Raiwe235/ilnet-telecom-monitoring.git
cd ilnet-telecom-monitoring
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start services**
```bash
docker-compose -f config/docker-compose.yml up -d
```

4. **Access the platform**
- Collector API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- AlertManager: http://localhost:9093

### Health Check
```bash
curl http://localhost:8000/api/health
```

## 📚 Documentation

- [Architecture Guide](./docs/ARCHITECTURE.md)
- [Installation Guide](./docs/INSTALLATION.md)
- [API Documentation](./docs/API.md)
- [Configuration Guide](./docs/CONFIGURATION.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)

## 🔒 Security

### Authentication
- JWT tokens for API access
- Token expiration (configurable)
- Secure password handling

### Encryption
- TLS/SSL support
- Secure credential storage
- Redis password protection

### Best Practices
- Change default credentials
- Use strong JWT secret
- Enable TLS in production
- Restrict API access
- Regular security updates

## 🛠️ Development

### Setup Development Environment
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov pytest-flask
```

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/test_auth.py -v
```

### Code Style
```bash
# Format code
pytest --flake8 --pylint

# Run linter
flake8 src/
pylint src/
```

## 📊 API Endpoints

### Authentication
```
POST /api/auth/login
  Request: {"username": "admin", "password": "xxx"}
  Response: {"token": "jwt...", "expires_in": 3600}
```

### Devices
```
GET    /api/devices/                    # List all devices
GET    /api/devices/<device_id>         # Get device info
POST   /api/devices/                    # Add device
DELETE /api/devices/<device_id>         # Remove device
POST   /api/devices/test/<device_id>    # Test connection
POST   /api/devices/test                # Test all connections
```

### Collector
```
GET    /api/collector/status            # Collector status
POST   /api/collector/collect           # Collect all metrics
POST   /api/collector/collect/<dev_id>  # Collect device metrics
```

### Health
```
GET    /api/health                      # Health check
GET    /api/status                      # System status
GET    /metrics                         # Prometheus metrics
```

## 📈 Monitoring Capabilities

### Device Metrics
- Device uptime
- System information
- Device availability

### Interface Metrics
- Interface status (up/down)
- Bandwidth usage (in/out)
- Error rates (in/out)
- Packet discards (in/out)
- Interface speed

### System Metrics
- Collection duration
- Collection errors
- API request metrics
- Resource utilization

## 🔔 Alerting Rules

### Severity Levels
- **Critical**: Device down (5+ minutes)
- **Warning**: Interface down, high error rate
- **Info**: Slow metrics collection

### Alert Channels
- Webhooks
- Email
- PagerDuty integration ready
- Slack integration ready

## 📁 Project Structure

```
ilnet-telecom-monitoring/
├── src/
│   ├── api/                    # Flask API
│   │   ├── app.py
│   │   ├── routes.py
│   │   └── auth.py
│   ├── snmp_collector/         # SNMP collection
│   │   ├── collector.py
│   │   ├── device_manager.py
│   │   ├── snmp_manager.py
│   │   └── prometheus_exporter.py
│   ├── config.py               # Configuration
│   └── logger.py               # Logging
├── config/                     # Configuration files
│   ├── docker-compose.yml
│   ├── prometheus.yml
│   ├── snmp_devices.json
│   └── grafana/
├── deploy/                     # Deployment configs
│   └── monitoring/
│       ├── alerts.yml
│       ├── recording_rules.yml
│       └── alertmanager.yml
├── docker/                     # Docker files
│   ├── collector.Dockerfile
│   └── entrypoint.sh
├── tests/                      # Test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_devices.py
│   ├── test_collector.py
│   └── test_health.py
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── API.md
│   ├── CONFIGURATION.md
│   └── TROUBLESHOOTING.md
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── Makefile                    # Build automation
├── docker-compose.yml          # Main compose file
└── README.md                   # This file
```

## 🐛 Troubleshooting

### Services not starting
```bash
# Check logs
docker-compose logs -f collector

# Verify connectivity
docker-compose exec snmp-collector curl http://prometheus:9090/-/healthy
```

### SNMP connection issues
- Verify device IP and SNMP community string
- Check firewall rules (port 161 UDP)
- Ensure SNMP is enabled on device

### Metrics not appearing
- Check collector logs
- Verify Prometheus scrape config
- Test device connection via API

See [Troubleshooting Guide](./docs/TROUBLESHOOTING.md) for more help.

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

See CONTRIBUTING.md for guidelines.

## 📞 Support

For issues and questions:
- GitHub Issues: [Report a bug](https://github.com/Raiwe235/ilnet-telecom-monitoring/issues)
- Documentation: See `docs/` folder
- Email: support@ilnet-telecom.sn

## 🎯 Roadmap

- [ ] SNMP v3 support
- [ ] NetFlow/sFlow integration
- [ ] Machine learning anomaly detection
- [ ] Advanced forecasting
- [ ] Multi-tenancy support
- [ ] Mobile app
- [ ] Kubernetes deployment
- [ ] Cloud integration (AWS, Azure, GCP)

---

**Made with ❤️ for ILNET TELECOM**
