"""
FastAPI Model Serving for D&D Character Class Predictor
Loads model from MLflow and serves predictions via REST API
"""
import os
import logging
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import mlflow.pyfunc
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="D&D Character Class Predictor API",
    description="Predict D&D character class based on ability scores",
    version="1.0.0"
)

# Global model variable
model = None
model_info = {}


class CharacterStats(BaseModel):
    """Character ability scores"""
    strength: int = Field(..., ge=3, le=20, description="Strength score (3-20)")
    dexterity: int = Field(..., ge=3, le=20, description="Dexterity score (3-20)")
    constitution: int = Field(..., ge=3, le=20, description="Constitution score (3-20)")
    intelligence: int = Field(..., ge=3, le=20, description="Intelligence score (3-20)")
    wisdom: int = Field(..., ge=3, le=20, description="Wisdom score (3-20)")
    charisma: int = Field(..., ge=3, le=20, description="Charisma score (3-20)")

    class Config:
        json_schema_extra = {
            "example": {
                "strength": 16,
                "dexterity": 12,
                "constitution": 14,
                "intelligence": 8,
                "wisdom": 10,
                "charisma": 10
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response"""
    predicted_class: str
    confidence: float
    all_probabilities: Dict[str, float]
    input_stats: CharacterStats


def load_model():
    """Load the latest model from MLflow"""
    global model, model_info

    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
    model_name = os.getenv('MODEL_NAME', 'dnd-character-classifier')
    model_stage = os.getenv('MODEL_STAGE', 'None')

    mlflow.set_tracking_uri(mlflow_uri)

    try:
        if model_stage == "Production" or model_stage == "Staging":
            # Load specific stage
            model_uri = f"models:/{model_name}/{model_stage}"
            logger.info(f"Loading model from stage: {model_stage}")
        else:
            # Load latest version
            model_uri = f"models:/{model_name}/latest"
            logger.info("Loading latest model version")

        model = mlflow.pyfunc.load_model(model_uri)
        model_info = {
            'model_name': model_name,
            'model_uri': model_uri,
            'mlflow_tracking_uri': mlflow_uri
        }
        logger.info(f"Model loaded successfully: {model_uri}")

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        logger.info("Attempting to load latest version from runs...")

        try:
            # Fallback: try to load the latest run
            client = mlflow.tracking.MlflowClient()
            registered_models = client.search_registered_models(f"name='{model_name}'")

            if registered_models:
                latest_version = registered_models[0].latest_versions[0]
                model_uri = f"models:/{model_name}/{latest_version.version}"
                model = mlflow.pyfunc.load_model(model_uri)
                model_info = {
                    'model_name': model_name,
                    'model_uri': model_uri,
                    'version': latest_version.version,
                    'mlflow_tracking_uri': mlflow_uri
                }
                logger.info(f"Model loaded from version {latest_version.version}")
            else:
                raise Exception(f"No registered model found: {model_name}")

        except Exception as e2:
            logger.error(f"Fallback also failed: {e2}")
            raise


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    try:
        load_model()
        logger.info("Model server ready!")
    except Exception as e:
        logger.warning(f"Failed to load model on startup: {e}")
        logger.info("Model will attempt to load on first prediction request")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "D&D Character Class Predictor",
        "model_loaded": model is not None
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_info": model_info}


@app.post("/predict", response_model=PredictionResponse)
async def predict(stats: CharacterStats):
    """
    Predict character class based on ability scores

    Returns the predicted class, confidence, and probabilities for all classes
    """
    global model

    if model is None:
        try:
            load_model()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Model not available: {str(e)}"
            )

    try:
        # Prepare input data
        input_data = pd.DataFrame([{
            'strength': stats.strength,
            'dexterity': stats.dexterity,
            'constitution': stats.constitution,
            'intelligence': stats.intelligence,
            'wisdom': stats.wisdom,
            'charisma': stats.charisma
        }])

        # Get prediction
        prediction = model.predict(input_data)[0]

        # Get probabilities if available
        try:
            # Access the underlying sklearn model to get probabilities
            sklearn_model = model._model_impl.python_model if hasattr(model, '_model_impl') else None

            if sklearn_model is None:
                # Try alternative access method
                sklearn_model = model.unwrap_python_model()

            if hasattr(sklearn_model, 'predict_proba'):
                probabilities = sklearn_model.predict_proba(input_data)[0]
                classes = sklearn_model.classes_
                prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
                confidence = float(max(probabilities))
            else:
                prob_dict = {prediction: 1.0}
                confidence = 1.0

        except Exception as e:
            logger.warning(f"Could not get probabilities: {e}")
            prob_dict = {prediction: 1.0}
            confidence = 1.0

        return PredictionResponse(
            predicted_class=prediction,
            confidence=confidence,
            all_probabilities=prob_dict,
            input_stats=stats
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.get("/classes")
async def get_classes():
    """Get list of all possible D&D classes"""
    classes = [
        "Barbarian", "Fighter", "Paladin", "Ranger", "Rogue",
        "Bard", "Cleric", "Druid", "Monk", "Sorcerer", "Warlock", "Wizard"
    ]
    return {"classes": classes}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
