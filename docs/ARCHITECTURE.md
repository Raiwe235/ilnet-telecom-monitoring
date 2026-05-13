# Architecture Overview

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Network Devices (SNMP-enabled)              │
│  Routers │ Switches │ Firewalls │ Load Balancers │ etc.  │
└─────────────────────┬──────────────────────────────────┘
                      │ SNMP v2c (Port 161/UDP)
                      │ Polling Interval: 30-60s
                      ▼
    ┌─────────────────────────────────────┐
    │   SNMP Collector Container          │
    │   (Python Flask Application)        │
    ├─────────────────────────────────────┤
    │ • SNMPManager (Connection)          │
    │ • DeviceManager (Configuration)     │
    │ • PrometheusExporter (Metrics)      │
    │ • Flask API (REST Interface)        │
    │ • JWT Authentication                │
    └─────────────────────────────────────┘
         │                           │
         │ Push Metrics              │ REST API
         │ (Port 8000)              │ JSON
         ▼                           ▼
    ┌──────────────────┐    ┌──────────────────┐
    │   Prometheus     │    │   API Consumers  │
    │  Time-Series DB  │    │   (External)     │
    │  (Port 9090)     │    │                  │
    └────────┬─────────┘    └──────────────────┘
             │
             │ Metrics
             │ (Port 9090/HTTP)
             ▼
    ┌──────────────────┐
    │     Grafana      │
    │   Dashboard      │
    │  (Port 3000)     │
    └────────┬─────────┘
             │
             │ Alerts
             ▼
    ┌──────────────────┐
    │  AlertManager    │
    │  (Port 9093)     │
    └────────┬─────────┘
             │
    ┌────────┴─────────────────┬───────────┐
    │                          │           │
    ▼                          ▼           ▼
  Email              Webhooks    Slack   PagerDuty
```

## Component Details

### SNMP Collector
**Purpose**: Primary component for device data collection

**Key Modules**:
- `SNMPManager`: Handles SNMP communication
  - Supports SNMPv2c (v3 ready)
  - Connection pooling
  - Error handling and retries
  - OID caching

- `DeviceManager`: Manages device inventory
  - JSON-based configuration
  - Device CRUD operations
  - Device tagging and classification
  - SNMP manager instantiation

- `PrometheusExporter`: Exports metrics
  - Prometheus client library integration
  - Custom metrics definition
  - Gauge and Counter types
  - Automatic metric registration

- `SNMPCollector`: Main orchestration
  - Periodic collection scheduling
  - Metric aggregation
  - Error tracking and reporting
  - Status monitoring

### API Layer (Flask)
**Purpose**: REST interface for platform interaction

**Routes**:
- `/api/auth/` - Authentication endpoints
- `/api/devices/` - Device management
- `/api/collector/` - Collection control
- `/api/health` - Health checks
- `/metrics` - Prometheus metrics export

**Security**:
- JWT token-based auth
- Route protection decorators
- CORS handling
- Request validation

### Storage & Caching

**Prometheus**:
- Time-series storage
- Data retention: 15 days (configurable)
- Query language (PromQL)
- Rule evaluation engine

**Redis**:
- Session caching
- Device connection pooling
- Metrics buffering
- Optional: event queue

### Visualization & Alerting

**Grafana**:
- Dashboard creation and sharing
- Panel types: Graphs, Tables, Gauges, Heatmaps
- Data source: Prometheus
- User management
- Alerting rules

**AlertManager**:
- Alert routing and deduplication
- Group management
- Inhibition rules
- Multiple receiver support

## Data Flow

### Collection Cycle
1. Collector initialization loads device configuration
2. Main loop iterates through enabled devices
3. For each device:
   - Test SNMP connectivity
   - Collect system OIDs (uptime, sysName, etc.)
   - Walk interface table
   - Extract traffic and error metrics
4. Update Prometheus metrics
5. Record collection duration and errors
6. Store in time-series database

### Query Flow
1. Grafana dashboard requests data
2. Prometheus evaluates PromQL queries
3. Time-series data retrieved from storage
4. Data aggregation and transformation
5. JSON response to dashboard
6. Client-side rendering

### Alert Flow
1. Prometheus evaluates alert rules
2. State changes trigger alerts
3. AlertManager groups and deduplicates
4. Receivers dispatch notifications
5. User notification (email, Slack, etc.)

## Scalability Considerations

### Current Architecture
- Single collector instance
- Suitable for networks with <1000 devices
- Collection interval: 30-60 seconds

### Future Scaling
- Multiple collector instances (sharding)
- Load balancer for API
- Distributed Prometheus (Thanos)
- Elasticsearch for long-term storage
- Kafka for event streaming

## Security Architecture

### Network Security
- TLS/SSL encryption support
- SNMP v2c (clear) → v3 (encrypted) migration path
- Firewall rules per component
- Network segmentation

### Application Security
- JWT token validation
- Password hashing
- Input validation
- SQL injection prevention
- CORS configuration

### Data Security
- Redis password protection
- Prometheus basic auth ready
- Metrics access control
- Audit logging

## Deployment Architecture

### Development
- Docker Compose with all services
- SQLite for persistence
- Mock SNMP devices

### Production
- Kubernetes or Docker Swarm
- Separate database service
- Load balancing
- High availability
- Backup strategy

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Collection latency | <30s | Per device |
| Dashboard response | <2s | P95 |
| Alert delivery | <5m | From trigger to notification |
| Data retention | 15 days | Configurable |
| Device capacity | 1000+ | Per instance |
| API throughput | 1000+ req/s | With load balancing |

## Monitoring the Monitor

### Self-Monitoring Metrics
- Collector uptime
- API response times
- Database query latency
- Redis hit ratio
- Prometheus scrape duration
- Alert delivery success

### Internal Alerting
- Collector process crashes
- Database connectivity loss
- High memory usage
- Failed metric collections
- API errors
