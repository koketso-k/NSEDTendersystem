# Tender Insight Hub
> Cloud-native SaaS platform for South African SMEs to discover, analyze, and manage public tender opportunities using AI-powered insights

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Project Overview

**Tender Insight Hub** is an innovative cloud-native SaaS platform designed to revolutionize how South African Small and Medium Enterprises (SMEs) navigate public procurement opportunities. Built with cutting-edge AI technology, the platform simplifies complex tender documents, enables intelligent analysis, and helps SMEs assess their readiness to compete for government contracts.

### 🌟 Key Features

- **🔍 Intelligent Search & Filtering** - Advanced keyword search with province, deadline, buyer, and budget filters
- **🤖 AI-Powered Document Summarization** - Automated extraction and summarization of tender documents using HuggingFace transformers
- **📊 Readiness Scoring** - Automated suitability assessment comparing company profiles to tender requirements (0-100 scale)
- **👥 Collaborative Workspaces** - Team-based tender tracking with status management and internal notes
- **📈 Analytics Dashboard** - Government spending insights and tender analytics
- **🔗 Public API** - RESTful API for third-party integrations and civic tech applications

### 🏢 SaaS Pricing Tiers

| Tier | Users | Features | Price |
|------|-------|----------|-------|
| **Free** | 1 user | 3 tender searches/week, Basic filtering | Free |
| **Basic** | Up to 3 users | Unlimited searches, AI summaries, Readiness scoring | Paid |
| **Pro** | Unlimited users | All Basic features + Report exports, Advanced analytics | Paid |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- MongoDB 6.0+
- Node.js 18+ (for frontend)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-team/tender-insight-hub.git
   cd tender-insight-hub
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize databases**
   ```bash
   python scripts/setup_db.py
   python scripts/seed_data.py
   ```

5. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc
   - Application: http://localhost:3000 (frontend)

### 🐳 Docker Quick Start

```bash
docker-compose up -d
```

## 🏗️ System Architecture

**Backend Framework:** FastAPI (Python 3.11)  
**Databases:** 
- PostgreSQL (User data, tender metadata, workspaces)
- MongoDB (AI summaries, readiness scores, analytics)
- Redis (Caching, session management, rate limiting)

**AI/ML Integration:** HuggingFace Transformers (BART, T5)  
**Authentication:** JWT with multi-tenant isolation  
**Deployment:** Docker + CI/CD via GitHub Actions

## 📚 Documentation

### 📋 Project Management
- [**Project Charter**](docs/project-management/project-charter.md) - Comprehensive project overview and governance
- [Requirements Specification](docs/project-management/requirements-specification.md) - Detailed functional and non-functional requirements
- [Team Roles & Responsibilities](docs/project-management/team-roles.md) - Individual team member responsibilities
- [Project Timeline](docs/project-management/project-timeline.md) - Development milestones and deadlines

### 🏗️ Architecture & Design
- [**System Architecture**](docs/architecture/system-architecture.md) - High-level system design and component interactions
- [**Database Design**](docs/architecture/database-design.md) - Multi-database schema and integration patterns
- [**API Specification**](docs/architecture/api-specification.md) - Complete API endpoint documentation
- [Integration Plan](docs/architecture/integration-plan.md) - External API and service integrations

### 👨‍💻 Development
- [Setup Guide](docs/development/setup-guide.md) - Detailed local development environment setup
- [Coding Standards](docs/development/coding-standards.md) - Code style guidelines and best practices
- [Testing Strategy](docs/development/testing-strategy.md) - Testing framework and coverage requirements
- [Deployment Guide](docs/development/deployment-guide.md) - Production deployment procedures

### 🎓 Academic
- [NSED742 Submission](docs/academic/nsed742-submission.md) - University course requirements and deliverables
- [Assignment Mapping](docs/academic/assignment-context.md) - How project features map to course objectives

## 🔗 API Endpoints

### Core Endpoints
- `GET /api/v1/tenders/search` - Search and filter tenders with keyword matching
- `POST /api/v1/summary/extract` - Extract and summarize tender documents
- `POST /api/v1/readiness/check` - Calculate company-tender suitability score
- `GET /api/v1/workspace` - Manage team tender workspace

### Public API (Third-party Access)
- `GET /api/enriched-releases` - Filtered tenders with AI summaries and scores
- `GET /api/analytics/spend-by-buyer` - Government spending analytics
- `POST /api/summary/extract` - Document summarization service
- `POST /api/readiness/check` - Suitability assessment service

**📖 Full API Documentation:** [Swagger UI](http://localhost:8000/docs) | [ReDoc](http://localhost:8000/redoc)

## 👥 Team

**Academic Context:** NSED742 - Software Engineering & Design  
**Supervisor:** Dr. Silas Verkijika  
**Institution:** University of Sol Plaatje

### Core Development Team

| Role | Name | Student ID | GitHub | Responsibilities |
|------|------|------------|---------|------------------|
| **Project Manager** | Sinethemba Mthembu | 202201661 | [@Sne-M-Crypto](https://github.com/Sne-M-Crypto) | Project coordination, stakeholder management, risk mitigation |
| **Lead Developer** | Ashwill Bradley Herman | 202108414 | [@AshwillHerman](https://github.com/AshwillHerman) | Technical architecture, code quality, API design |
| **DevOps Engineer** | Koketso Kgogo | 202107686 | [@koketso-k](https://github.com/koketso-k) | Infrastructure, CI/CD, deployment automation |
| **Backend Developer** | Onthatile Kilelo | 202213333 | [@OG-Kilelo](https://github.com/OG-kilelo) | Database design, AI integration, backend services |
| **Product Owner** | Khethiwe Skosana | 202205775 | [@khethiweSkosana](https://github.khethiwe-skosana) | Requirements gathering, UX design, market validation |

### Team Leadership Rotation
Each team member serves as **Team Lead** for specific development cycles:
- **Sprint 1-2:** Sinethemba Mthembu (Foundation & Planning)
- **Sprint 3-4:** Ashwill Bradley Herman (Core Development)
- **Sprint 5-6:** Koketso Kgogo (Infrastructure & Testing)
- **Sprint 7-8:** Onthatile Kilelo (AI Integration & Optimization)
- **Sprint 9:** Khethiwe Skosana (Launch & Validation)

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.100+
- **Language:** Python 3.11
- **Authentication:** JWT with bcrypt
- **Validation:** Pydantic v2
- **Testing:** pytest + TestClient
- **Documentation:** OpenAPI/Swagger

### Databases
- **SQL:** PostgreSQL 15 (Users, tenders, workspaces)
- **NoSQL:** MongoDB 6.0 (AI summaries, analytics)
- **Cache:** Redis 7.0 (Sessions, rate limiting)

### AI/ML
- **Models:** HuggingFace Transformers
  - Summarization: `facebook/bart-large-cnn`
  - Alternative: `t5-small`
- **Processing:** pandas, numpy
- **Document Parsing:** pdfplumber, python-docx

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Deployment:** Railway/Render (staging), AWS/GCP (production)
- **Monitoring:** Prometheus + Grafana

## 🧪 Testing & Quality Assurance

- **Unit Tests:** 80%+ coverage requirement
- **Integration Tests:** API endpoint validation
- **E2E Tests:** Full user workflow testing
- **Performance:** <2s response time target
- **Security:** OWASP compliance, vulnerability scanning

### Running Tests
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Coverage report
pytest --cov=app --cov-report=html tests/
```

## 🚀 Deployment

### Development
```bash
uvicorn app.main:app --reload
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### CI/CD Pipeline
- **Continuous Integration:** Automated testing on pull requests
- **Continuous Deployment:** Automatic deployment to staging on main branch merge
- **Quality Gates:** Code coverage, security scans, performance tests

## 🔒 Security & Compliance

- **Authentication:** JWT tokens with refresh mechanism
- **Authorization:** Role-based access control (RBAC)
- **Data Protection:** POPIA compliance for South African data laws
- **API Security:** Rate limiting, CORS configuration, input validation
- **Infrastructure:** SSL/TLS encryption, secure environment variables

## 📊 Performance Metrics

- **Target Response Time:** <2 seconds (95th percentile)
- **Availability:** 99.5% uptime SLA
- **Concurrent Users:** Support for 1,000+ simultaneous users
- **AI Processing:** <30 seconds for document summarization
- **Database Performance:** <100ms query response time

## 🤝 Contributing

This is an academic project for NSED742. Contributions are limited to team members during the development period.

### Development Workflow
1. Create feature branch from `develop`
2. Implement feature with tests
3. Submit pull request with description
4. Code review by team lead
5. Merge after approval and CI passes

### Code Standards
- Follow PEP 8 for Python code
- Use type hints for all functions
- Write docstrings for public methods
- Maintain test coverage above 80%

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Academic Use:** This project is developed as part of NSED742 coursework at the University of the Sol Plaatje. All work is original and properly attributed.

## 🙏 Acknowledgments

- **Dr. Silas Verkijika** - Academic supervisor and project guidance
- **OCDS eTenders API** - Primary data source for South African tender information
- **HuggingFace Community** - Open-source AI models and transformers library
- **FastAPI Community** - Modern Python web framework
- **University of the Sol Plaatje** - Academic institution and research support

## 📞 Support & Contact

- **Project Issues:** [GitHub Issues](https://github.com/your-team/tender-insight-hub/issues)
- **Documentation:** [Project Wiki](https://github.com/your-team/tender-insight-hub/wiki)
- **Team Communication:** Internal Slack workspace
- **Academic Queries:** Contact project supervisor

---

**🎓 NSED742 - Software Engineering & Design | University of the Sol Plaatje | 2025**

