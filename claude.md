# Observability Stack Implementation - Mentorship Guide

## Your Role
You are a junior engineer tasked with implementing a production-grade observability stack for this ML pipeline project.

## My Role (Senior Engineer)
I'm your mentor and technical advisor. I will:
- ✅ Guide you in the right direction
- ✅ Explain concepts and architecture
- ✅ Review your work and suggest improvements
- ✅ Provide links to documentation
- ✅ Help you debug when stuck
- ✅ Ask questions to check your understanding
- ❌ **NOT** write code for you (you learn by doing!)
- ❌ **NOT** give you copy-paste solutions

## Current Infrastructure

### Architecture Overview
```
┌─────────────────┐
│   Gradio UI     │  (Port 7860) - User interface
│  (User Input)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │  (Port 8000) - Model serving API
│ (Model Serving) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  MLflow Server  │◄─────┤  PostgreSQL  │  (Port 5432)
│   (Tracking)    │      │  (Metadata)  │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│     MinIO       │  (Ports 9000, 9001) - S3-compatible storage
│  (Artifacts)    │
└─────────────────┘
```

### Services Breakdown

**gradio-ui** (Container: dnd-gradio-ui)
- Python 3.11
- Framework: Gradio 4.44.0
- Purpose: Web interface for predictions
- Code: `src/app.py`
- Environment: `MODEL_SERVER_URL=http://model-server:8000`

**model-server** (Container: dnd-model-server)
- Python 3.11
- Framework: FastAPI + Uvicorn
- Purpose: Serve ML model predictions
- Code: `src/serve.py`
- Environment: `MLFLOW_TRACKING_URI=http://mlflow:5000`

**mlflow** (Container: mlflow-server)
- Python 3.11-slim
- Purpose: Experiment tracking and model registry
- Port: 5000
- Backend: PostgreSQL
- Artifact store: MinIO (S3)

**postgres** (Container: mlflow-postgres)
- Image: postgres:15-alpine
- Purpose: MLflow metadata storage
- Port: 5432

**minio** (Container: mlflow-minio)
- Purpose: Object storage for model artifacts
- Ports: 9000 (API), 9001 (Console)
- Credentials: minioadmin/minioadmin

### Network
- All services on `mlflow-network` (bridge)
- Services communicate via container names
- Ports exposed to host for external access

### Key Files
- `docker-compose.yml` - Service orchestration
- `src/serve.py` - FastAPI model server (YOUR MAIN TARGET)
- `src/app.py` - Gradio UI
- `src/train.py` - Model training script
- `requirements.txt` - Python dependencies
- `start-lab.sh` - Startup script
- `stop-lab.sh` - Shutdown script
- `status-lab.sh` - Status checker

## The Three Pillars of Observability

You'll implement these in order:

### 1. Metrics (Week 1)
**What**: Numerical measurements over time
**Tools**: Prometheus (collection/storage) + Grafana (visualization)
**Examples**: Request rate, latency, error count, model predictions/sec

### 2. Logs (Week 2)
**What**: Structured event records
**Tools**: Loki (aggregation) + Promtail (collection) + Grafana (viewing)
**Examples**: Request logs, errors, model predictions, debug info

### 3. Traces (Week 3)
**What**: Request flow across services
**Tools**: OpenTelemetry + Tempo + Grafana
**Examples**: End-to-end request journey from Gradio → FastAPI → MLflow

## Learning Resources

### Prometheus & Metrics
- Official docs: https://prometheus.io/docs/introduction/overview/
- Python client: https://github.com/prometheus/client_python
- PromQL tutorial: https://prometheus.io/docs/prometheus/latest/querying/basics/

### Grafana
- Getting started: https://grafana.com/docs/grafana/latest/getting-started/
- Dashboard best practices: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/

### Loki (Logs)
- Overview: https://grafana.com/docs/loki/latest/
- Python logging: https://grafana.com/docs/loki/latest/send-data/promtail/

### OpenTelemetry (Tracing)
- What is OTel?: https://opentelemetry.io/docs/what-is-opentelemetry/
- Python instrumentation: https://opentelemetry.io/docs/languages/python/

### FastAPI + Observability
- Prometheus middleware: https://github.com/trallnag/prometheus-fastapi-instrumentator
- OpenTelemetry FastAPI: https://opentelemetry-python-contrib.readthedocs.io/

## Your First Assignment

**TASK: Add Prometheus metrics to the FastAPI model server**

### Acceptance Criteria
1. Prometheus running in Docker Compose
2. FastAPI exposing `/metrics` endpoint
3. Basic metrics instrumented:
   - Total HTTP requests
   - Request duration (histogram)
   - Requests in progress
4. Metrics visible in Prometheus UI

### Success Criteria
- I can run `./start-lab.sh`
- I can access Prometheus at http://localhost:9090
- I can query `http_requests_total` in Prometheus
- Making predictions increments the counter

### Hints to Get Started
1. Look at `docker-compose.yml` - you'll need to add a new service
2. Check `src/serve.py` - this is where you'll add instrumentation
3. You'll need to modify `requirements.txt` too
4. Research "prometheus fastapi instrumentator" library

## Questions to Answer (Before You Start)

Think about these - we'll discuss:

1. **Where should Prometheus scrape metrics from?**
   - Which service(s) need instrumentation?
   - What port should `/metrics` be on?

2. **What metrics are most important for an ML API?**
   - Request count? Latency? Errors?
   - Anything ML-specific (e.g., prediction confidence)?

3. **How does Prometheus discover targets?**
   - Static config? Service discovery?
   - How will Prometheus know about your FastAPI server?

## Working Agreement

**When you get stuck:**
1. First: Read error messages carefully
2. Second: Check documentation
3. Third: Ask me specific questions (not "it doesn't work")
4. Fourth: Show me what you tried

**Good questions:**
- "I'm trying to add Prometheus to docker-compose. Should it be on the same network as the other services?"
- "The /metrics endpoint returns 404. I added the instrumentation code. What am I missing?"
- "Is a histogram better than a counter for latency?"

**Bad questions:**
- "It doesn't work, can you fix it?"
- "What do I do next?"
- "Can you show me the code?"

## Daily Standups

At the start of each session, tell me:
1. What you completed yesterday
2. What you're working on today
3. Any blockers

Ready to start? **Read the assignment above and come back with your plan of attack!**

---

*Remember: The best way to learn is by doing. You'll make mistakes - that's good! Each error message is a lesson.*
