# D&D Character Class Predictor - Production-Lite ML Pipeline

A complete ML pipeline demonstrating production practices with a fun D&D character class prediction model. This project showcases MLOps best practices using MLflow, Docker, and modern Python ML tools.

## Features

- **ML Model**: Random Forest classifier predicting D&D character class from ability scores
- **Experiment Tracking**: MLflow for tracking experiments, parameters, and metrics
- **Model Registry**: Centralized model versioning and deployment
- **Artifact Storage**: MinIO (S3-compatible) for storing model artifacts
- **Backend Storage**: PostgreSQL for MLflow metadata
- **Model Serving**: FastAPI REST API for predictions
- **User Interface**: Gradio web UI for interactive predictions
- **Containerization**: Docker Compose orchestration for all services

## Architecture

```
┌─────────────────┐
│   Gradio UI     │  (Port 7860)
│  (User Input)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │  (Port 8000)
│ (Model Serving) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  MLflow Server  │◄─────┤  PostgreSQL  │
│   (Tracking)    │      │  (Metadata)  │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│     MinIO       │
│  (Artifacts)    │
└─────────────────┘
```

## Quick Start

### Prerequisites

- Docker Desktop with WSL2 (for Windows)
- Docker Compose
- Python 3.11+ (for local training)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd ml-lab

# Create environment file
cp .env.example .env
```

### 2. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Check service health
docker-compose ps
```

Services will be available at:
- **MLflow UI**: http://localhost:5000
- **MinIO Console**: http://localhost:9001 (user: minioadmin, password: minioadmin)
- **Model API**: http://localhost:8000
- **Gradio UI**: http://localhost:7860

### 3. Train the Model

You have two options:

#### Option A: Train Locally (Recommended for first run)

```bash
# Install dependencies
pip install -r requirements.txt

# Train the model
cd src
python train.py
```

#### Option B: Train in Docker

```bash
# Run training in a container
docker-compose run --rm model-server python src/train.py
```

### 4. Access the UI

Open your browser to http://localhost:7860 and start predicting character classes!

## Project Structure

```
ml-lab/
├── docker-compose.yml          # Container orchestration
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── Dockerfile.serve            # FastAPI server container
├── Dockerfile.ui               # Gradio UI container
├── src/
│   ├── train.py               # Model training script
│   ├── serve.py               # FastAPI serving layer
│   └── app.py                 # Gradio UI application
├── data/
│   └── sample_characters.csv  # Generated sample data
└── README.md                  # This file
```

## Usage Guide

### Training a New Model

The training script generates synthetic D&D character data and trains a Random Forest classifier:

```bash
python src/train.py
```

The script will:
1. Generate 6,000 synthetic characters (500 per class)
2. Train a Random Forest classifier
3. Log metrics, parameters, and artifacts to MLflow
4. Register the model in the MLflow Model Registry

### Viewing Experiments in MLflow

1. Navigate to http://localhost:5000
2. Browse experiments under "dnd-character-classifier"
3. Compare runs, view metrics, and explore artifacts
4. Promote models to "Production" stage for serving

### Using the API

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Make a Prediction
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "strength": 16,
    "dexterity": 12,
    "constitution": 14,
    "intelligence": 8,
    "wisdom": 10,
    "charisma": 10
  }'
```

#### Get All Classes
```bash
curl http://localhost:8000/classes
```

### Using the Gradio UI

1. Open http://localhost:7860
2. Adjust ability score sliders (3-20 range)
3. Click "Predict Class"
4. View prediction results and probability distribution

Try the example characters for quick testing!

## D&D Classes

The model predicts one of 12 D&D 5e classes:

| Class      | Primary Stats    | Description                          |
|------------|------------------|--------------------------------------|
| Barbarian  | STR, CON         | Fierce warriors with primal rage    |
| Fighter    | STR, DEX, CON    | Master of martial combat            |
| Paladin    | STR, CHA         | Holy warriors with divine powers    |
| Ranger     | DEX, WIS         | Wilderness warriors and trackers    |
| Rogue      | DEX              | Cunning scouts and assassins        |
| Bard       | CHA              | Inspiring musicians and diplomats   |
| Cleric     | WIS              | Divine spellcasters and healers     |
| Druid      | WIS              | Nature magic and shapeshifting      |
| Monk       | DEX, WIS         | Martial artists with ki powers      |
| Sorcerer   | CHA              | Innate magical ability              |
| Warlock    | CHA              | Pact magic from otherworldly beings |
| Wizard     | INT              | Scholarly arcane spellcasters       |

## Development

### Running Services Individually

```bash
# Just infrastructure (for local development)
docker-compose up postgres minio minio-init mlflow

# Install dependencies locally
pip install -r requirements.txt

# Run model server locally
cd src
uvicorn serve:app --reload --host 0.0.0.0 --port 8000

# Run Gradio UI locally
python app.py
```

### Environment Variables

Key environment variables (see `.env.example`):

- `MLFLOW_TRACKING_URI`: MLflow server URL
- `MODEL_NAME`: Registered model name
- `MODEL_STAGE`: Model stage to serve (Production/Staging/None)
- `MINIO_ROOT_USER`: MinIO admin username
- `MINIO_ROOT_PASSWORD`: MinIO admin password
- `POSTGRES_USER/PASSWORD/DB`: PostgreSQL credentials

## Troubleshooting

### Model Server Can't Load Model

**Problem**: "Model not available" error

**Solutions**:
1. Ensure you've trained a model first
2. Check MLflow UI for registered models
3. Verify environment variables are correct
4. Check Docker logs: `docker-compose logs model-server`

### MinIO Connection Issues

**Problem**: Artifact storage failures

**Solutions**:
1. Verify MinIO is running: `docker-compose ps minio`
2. Check bucket exists: http://localhost:9001
3. Ensure minio-init completed: `docker-compose logs minio-init`

### PostgreSQL Connection Refused

**Problem**: MLflow can't connect to database

**Solutions**:
1. Wait for PostgreSQL to fully start (check health)
2. Restart services: `docker-compose restart`
3. Check logs: `docker-compose logs postgres`

### WSL2 Specific Issues

**Problem**: Services not accessible from Windows browser

**Solutions**:
1. Ensure Docker Desktop WSL2 integration is enabled
2. Try accessing via WSL2 IP instead of localhost
3. Check Windows firewall settings

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Next Steps

Potential enhancements:

- [ ] Add model versioning workflow
- [ ] Implement A/B testing between model versions
- [ ] Add model monitoring and drift detection
- [ ] Create batch prediction pipeline
- [ ] Add authentication to API endpoints
- [ ] Implement CI/CD pipeline
- [ ] Add data validation with Great Expectations
- [ ] Create model performance dashboard
- [ ] Add automated retraining triggers
- [ ] Deploy to cloud (AWS/GCP/Azure)

## Technology Stack

- **ML Framework**: scikit-learn
- **Experiment Tracking**: MLflow
- **Database**: PostgreSQL
- **Object Storage**: MinIO
- **API Framework**: FastAPI
- **UI Framework**: Gradio
- **Containerization**: Docker & Docker Compose
- **Python Version**: 3.11

## License

MIT

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
