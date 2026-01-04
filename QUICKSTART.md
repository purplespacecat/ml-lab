# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Start Services (1 minute)

```bash
# Using Make (recommended)
make up

# Or using Docker Compose directly
docker-compose up -d
```

Wait for all services to start. Check status:
```bash
make status
# or
docker-compose ps
```

## Step 2: Train the Model (2 minutes)

```bash
# Install Python dependencies (first time only)
pip install -r requirements.txt

# Train the model
python src/train.py
```

You should see:
- Training progress
- Model metrics (accuracy ~85-90%)
- MLflow run ID
- Model registered message

## Step 3: Verify in MLflow (30 seconds)

1. Open http://localhost:5000
2. Click "Models" in the left sidebar
3. You should see "dnd-character-classifier"
4. Click on it to see the registered version

## Step 4: Use the UI (1 minute)

1. Open http://localhost:7860
2. Adjust the ability score sliders
3. Click "Predict Class"
4. See your predicted D&D class!

Try the example characters for quick testing.

## Step 5: Test the API (30 seconds)

```bash
# Health check
curl http://localhost:8000/health

# Make a prediction (Barbarian stats)
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

## Troubleshooting

### "Model not available" error

The model server starts before training. Just train a model first:
```bash
python src/train.py
```

Then restart the model server:
```bash
docker-compose restart model-server
```

### Services not starting

Check Docker Desktop is running and WSL2 integration is enabled.

```bash
# View logs
docker-compose logs

# Restart everything
docker-compose down
docker-compose up -d
```

### Python dependencies issues

Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Next Steps

- Explore the MLflow UI to see experiment details
- Try different model parameters in `src/train.py`
- Modify the Gradio UI in `src/app.py`
- Add new features to the API in `src/serve.py`

## Stopping Everything

```bash
make down
# or
docker-compose down
```

To remove all data:
```bash
make clean
# or
docker-compose down -v
```
