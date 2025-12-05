# VitalSigns

**Humanitarian Early Warning System for Global Health and Food Security**

VitalSigns is an open-source platform that detects emerging signals of disease outbreaks, hunger, and public-health stress across regions globally. It aggregates privacy-preserving data from multiple sources to compute risk indices and generate actionable alerts.

> **DISCLAIMER**: VitalSigns provides informational risk indicators only. It does not provide medical advice and should not replace professional health assessments or official public health guidance.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Data Sources](#data-sources)
- [Risk Indices](#risk-indices)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Dashboard](#dashboard)
- [Deployment](#deployment)
- [Development](#development)
- [Ethical Guidelines](#ethical-guidelines)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

VitalSigns answers the critical question: **"Where are people hurting?"**

In practical terms, it identifies where health, hunger, disease, and clinic-capacity signals indicate rising suffering or emerging outbreaks. The system focuses on **positive content signals** (detecting distress) rather than absence detection.

### Key Principles

1. **Privacy-Preserving**: All data is aggregated and anonymized. No individual tracking.
2. **Humanitarian Focus**: Built for NGOs, health organizations, and humanitarian responders.
3. **Open & Transparent**: Open-source with clear methodology.
4. **Evidence-Based**: Risk calculations use established epidemiological models.

---

## Features

### Core Capabilities

- **Global Risk Monitoring**: Real-time risk indices for regions worldwide
- **Disease Outbreak Detection**: Track malaria, cholera, measles, dengue, respiratory illness
- **Hunger Stress Indicators**: Food price monitoring and harvest assessments
- **Health System Strain**: Clinic capacity and resource availability
- **Alert System**: Automated alerts when thresholds are exceeded
- **Interactive Dashboard**: Global map with drill-down capabilities

### Risk Indices Computed

| Index | Description |
|-------|-------------|
| Vital Risk Index | Composite score combining all risk factors |
| Hunger Stress Index | Food security and nutrition risk |
| Health System Strain | Healthcare capacity and resource strain |
| Disease Outbreak Index | Combined disease risk score |
| Malaria Risk | Malaria-specific outbreak risk |
| Cholera Risk | Cholera-specific outbreak risk |
| Measles Risk | Measles-specific outbreak risk |
| Dengue Risk | Dengue-specific outbreak risk |
| Respiratory Risk | Respiratory illness outbreak risk |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           VitalSigns Architecture                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   Weather   │    │   Health    │    │    Food     │                 │
│  │    APIs     │    │   Reports   │    │   Prices    │                 │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                 │
│         │                  │                  │                         │
│         └────────────┬─────┴──────────────────┘                         │
│                      │                                                   │
│                      ▼                                                   │
│         ┌────────────────────────┐                                      │
│         │   Signal Processor     │                                      │
│         │  - Validation          │                                      │
│         │  - Normalization       │                                      │
│         │  - Anomaly Detection   │                                      │
│         └────────────┬───────────┘                                      │
│                      │                                                   │
│                      ▼                                                   │
│         ┌────────────────────────┐                                      │
│         │   PostgreSQL Database  │                                      │
│         │  - Regions             │                                      │
│         │  - Signals             │                                      │
│         │  - Risk Indices        │                                      │
│         │  - Alerts              │                                      │
│         └────────────┬───────────┘                                      │
│                      │                                                   │
│                      ▼                                                   │
│         ┌────────────────────────┐                                      │
│         │   Risk Calculator      │                                      │
│         │  - Weighted Scoring    │                                      │
│         │  - Seasonal Adjustment │                                      │
│         │  - Alert Generation    │                                      │
│         └────────────┬───────────┘                                      │
│                      │                                                   │
│                      ▼                                                   │
│         ┌────────────────────────┐        ┌────────────────────────┐   │
│         │   FastAPI Backend      │◄──────►│   React Dashboard      │   │
│         │   REST API             │        │   - Global Map         │   │
│         │                        │        │   - Risk Charts        │   │
│         └────────────────────────┘        │   - Alert Panel        │   │
│                                           └────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend**
- Python 3.11+
- FastAPI (REST API framework)
- SQLAlchemy 2.0 (async ORM)
- PostgreSQL 15 (database)
- Redis (caching)
- Celery (task queue)

**Frontend**
- React 18 with TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Query (data fetching)
- Leaflet (mapping)
- Recharts (visualization)

**Infrastructure**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Nginx (reverse proxy)

---

## Data Sources

VitalSigns integrates **aggregated, privacy-preserving** data from multiple sources:

| Category | Examples |
|----------|----------|
| Weather | Rainfall, temperature, humidity, drought indices |
| Food Security | Staple food prices, harvest indicators, crop conditions |
| Health Reports | Disease case counts (aggregated), vaccination coverage |
| Health Facilities | Bed occupancy, medicine stock, staff availability |
| Water Quality | Contamination indices, sanitation access |
| Humanitarian | Displacement data, food insecurity phases |

### Data Privacy Requirements

All data sources must meet these criteria:
- ✅ Aggregated (not individual-level)
- ✅ Anonymized
- ✅ From reputable organizations
- ✅ Privacy-compliant
- ❌ No personal identifiers
- ❌ No individual tracking
- ❌ No device-level data

---

## Risk Indices

### Calculation Methodology

Risk indices are computed using weighted combinations of signals:

```
Risk Score = Σ (Signal_i × Weight_i × Confidence_i)
```

#### Malaria Risk Calculation
| Signal | Weight |
|--------|--------|
| Rainfall | 0.25 |
| Temperature | 0.20 |
| Humidity | 0.15 |
| Reported Cases | 0.25 |
| Bed Occupancy | 0.15 |

#### Risk Level Thresholds
| Level | Score Range | Description |
|-------|-------------|-------------|
| Critical | 80-100 | Immediate action required |
| High | 60-79 | Urgent attention needed |
| Moderate | 40-59 | Elevated concern |
| Low | 20-39 | Below normal levels |
| Minimal | 0-19 | Normal conditions |

### Seasonal Adjustments

Risk calculations account for seasonal patterns (e.g., malaria season, rainy season) by comparing current values against historical baselines for the same period.

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for development)
- Python 3.11+ (for development)
- PostgreSQL 15+ (or use Docker)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/vitalsigns.git
cd vitalsigns

# Start all services
docker-compose up -d

# Access the dashboard
open http://localhost:80

# Access the API docs
open http://localhost:8000/api/v1/docs
```

### Development Setup

**Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Application
APP_NAME=VitalSigns
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vitalsigns

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Risk Thresholds
DEFAULT_RISK_THRESHOLD=0.7
ALERT_THRESHOLD=0.8
```

---

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
Currently, the API is open. Authentication will be added in v1.0.

### Endpoints

#### Regions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/regions` | List all regions |
| GET | `/regions/{code}` | Get region details |
| GET | `/regions/{code}/children` | Get child regions |

#### Risks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/risks/summary` | Get global risk summary |
| GET | `/risks/map` | Get risk data for map |
| GET | `/risks/regions/{code}` | Get region risk details |
| GET | `/risks/diseases/{type}` | Get disease-specific risks |

#### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/alerts` | List all alerts |
| GET | `/alerts/active` | Get active alerts |
| GET | `/alerts/{id}` | Get alert details |
| POST | `/alerts/{id}/acknowledge` | Acknowledge alert |
| POST | `/alerts/{id}/resolve` | Resolve alert |

#### Signals
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/signals/types` | Get signal type summary |
| GET | `/signals/regions/{code}` | Get region signals |
| GET | `/signals/regions/{code}/timeseries` | Get signal time series |

### Example Response

```json
{
  "region_id": 1,
  "region_code": "KE",
  "region_name": "Kenya",
  "vital_risk_index": 45.3,
  "risk_level": "moderate",
  "hunger_stress_index": 38.5,
  "health_system_strain_index": 42.1,
  "disease_outbreak_index": 55.2,
  "confidence_score": 0.85,
  "calculation_date": "2024-01-15T12:00:00Z"
}
```

---

## Dashboard

The VitalSigns dashboard provides:

### Global Map View
- Interactive world map with risk markers
- Color-coded risk levels
- Click to drill down to region details
- Real-time updates

### Risk Summary Panel
- Distribution of regions by risk level
- Top 10 highest-risk regions
- Disease-specific hotspots

### Region Detail View
- Risk index breakdown
- 7-day trend chart
- Disease-specific risk scores
- Active alerts

### Alerts Panel
- Active alerts by severity
- Alert acknowledgement
- Alert resolution workflow

---

## Deployment

### Production Deployment

1. **Update environment variables** for production settings
2. **Enable HTTPS** with a reverse proxy (nginx, traefik)
3. **Set up database backups** for PostgreSQL
4. **Configure monitoring** (Prometheus, Grafana)

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

Helm charts are available in the `k8s/` directory (coming soon).

---

## Development

### Running Tests

**Backend**
```bash
cd backend
pytest --cov=app
```

**Frontend**
```bash
cd frontend
npm test
```

### Code Quality

**Backend**
```bash
# Linting
ruff check .

# Formatting
ruff format .

# Type checking
mypy app
```

**Frontend**
```bash
# Linting
npm run lint

# Type checking
npx tsc --noEmit
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Ethical Guidelines

### Data Privacy

- **No individual data**: All data must be aggregated
- **No tracking**: No device or personal identifiers
- **Transparency**: Clear documentation of data sources
- **Consent**: Only use properly licensed data

### Responsible Use

- **Not medical advice**: System provides indicators, not diagnoses
- **Uncertainty disclosure**: Confidence scores accompany all outputs
- **Bias awareness**: Regular audits for algorithmic bias
- **Human oversight**: Alerts require human review

### False Positive Handling

- Conservative thresholds to minimize false alarms
- Clear labeling of confidence levels
- Resolution workflow for false positives
- Continuous model improvement

---

## Roadmap

### MVP (Current)
- [x] Core risk calculation engine
- [x] Basic dashboard with map
- [x] REST API
- [x] Docker deployment

### v1.0
- [ ] Authentication & authorization
- [ ] Real data source integrations
- [ ] Email/SMS alert notifications
- [ ] Historical data analysis

### v1.5
- [ ] Machine learning risk models
- [ ] Predictive forecasting
- [ ] Mobile application
- [ ] Multi-language support

### v2.0
- [ ] Real-time streaming data
- [ ] Integration with humanitarian coordination systems
- [ ] Advanced visualization tools
- [ ] Public API for researchers

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- World Health Organization (WHO) for disease surveillance methodologies
- FEWS NET for food security frameworks
- OpenStreetMap contributors for mapping data
- All humanitarian organizations working to protect vulnerable populations

---

## Contact

- **Project Lead**: [Your Name]
- **Email**: vitalsigns@example.org
- **Issues**: [GitHub Issues](https://github.com/your-org/vitalsigns/issues)

---

*VitalSigns - Because every signal matters.*
