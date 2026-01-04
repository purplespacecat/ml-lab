"""
D&D Character Class Predictor Training Script
Trains a model to predict character class based on ability scores
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import mlflow
import mlflow.sklearn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# D&D Classes and their typical stat distributions
CLASS_PROFILES = {
    'Barbarian': {'str': 15, 'dex': 12, 'con': 14, 'int': 8, 'wis': 10, 'cha': 10},
    'Fighter': {'str': 14, 'dex': 13, 'con': 13, 'int': 10, 'wis': 11, 'cha': 10},
    'Paladin': {'str': 14, 'dex': 10, 'con': 12, 'int': 10, 'wis': 11, 'cha': 14},
    'Ranger': {'str': 12, 'dex': 15, 'con': 12, 'int': 10, 'wis': 14, 'cha': 10},
    'Rogue': {'str': 10, 'dex': 16, 'con': 12, 'int': 12, 'wis': 11, 'cha': 12},
    'Bard': {'str': 10, 'dex': 13, 'con': 11, 'int': 12, 'wis': 11, 'cha': 15},
    'Cleric': {'str': 12, 'dex': 10, 'con': 13, 'int': 10, 'wis': 15, 'cha': 12},
    'Druid': {'str': 10, 'dex': 12, 'con': 12, 'int': 11, 'wis': 15, 'cha': 11},
    'Monk': {'str': 12, 'dex': 15, 'con': 12, 'int': 10, 'wis': 14, 'cha': 10},
    'Sorcerer': {'str': 10, 'dex': 12, 'con': 12, 'int': 11, 'wis': 10, 'cha': 15},
    'Warlock': {'str': 10, 'dex': 12, 'con': 11, 'int': 11, 'wis': 11, 'cha': 15},
    'Wizard': {'str': 8, 'dex': 12, 'con': 11, 'int': 16, 'wis': 12, 'cha': 10},
}


def generate_character_data(n_samples_per_class=500):
    """Generate synthetic D&D character data"""
    data = []

    for class_name, base_stats in CLASS_PROFILES.items():
        for _ in range(n_samples_per_class):
            # Add random variation to base stats (standard deviation of 2)
            character = {
                'strength': max(3, min(20, int(np.random.normal(base_stats['str'], 2)))),
                'dexterity': max(3, min(20, int(np.random.normal(base_stats['dex'], 2)))),
                'constitution': max(3, min(20, int(np.random.normal(base_stats['con'], 2)))),
                'intelligence': max(3, min(20, int(np.random.normal(base_stats['int'], 2)))),
                'wisdom': max(3, min(20, int(np.random.normal(base_stats['wis'], 2)))),
                'charisma': max(3, min(20, int(np.random.normal(base_stats['cha'], 2)))),
                'class': class_name
            }
            data.append(character)

    return pd.DataFrame(data)


def train_model(n_estimators=100, max_depth=10, random_state=42):
    """Train the D&D character class predictor"""

    # Set MLflow tracking URI
    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("dnd-character-classifier")

    print(f"MLflow Tracking URI: {mlflow_uri}")
    print("Generating synthetic training data...")

    # Generate data
    df = generate_character_data(n_samples_per_class=500)

    # Save sample data for reference
    os.makedirs('../data', exist_ok=True)
    df.head(100).to_csv('../data/sample_characters.csv', index=False)

    print(f"Generated {len(df)} characters across {df['class'].nunique()} classes")
    print(f"\nClass distribution:\n{df['class'].value_counts()}")

    # Prepare features and target
    feature_cols = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    X = df[feature_cols]
    y = df['class']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

    # Start MLflow run
    with mlflow.start_run(run_name="random-forest-classifier"):
        # Log parameters
        params = {
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'random_state': random_state,
            'model_type': 'RandomForestClassifier',
            'n_samples_per_class': 500
        }
        mlflow.log_params(params)

        print("\nTraining Random Forest Classifier...")

        # Train model
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\nModel Performance:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)

        # Log per-class accuracy
        for class_name in df['class'].unique():
            class_mask = y_test == class_name
            if class_mask.sum() > 0:
                class_accuracy = accuracy_score(y_test[class_mask], y_pred[class_mask])
                mlflow.log_metric(f"accuracy_{class_name.lower()}", class_accuracy)

        # Log feature importances
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)

        print(f"\nFeature Importances:\n{feature_importance}")

        for _, row in feature_importance.iterrows():
            mlflow.log_metric(f"importance_{row['feature']}", row['importance'])

        # Log confusion matrix as artifact
        cm = confusion_matrix(y_test, y_pred)
        cm_df = pd.DataFrame(
            cm,
            index=sorted(df['class'].unique()),
            columns=sorted(df['class'].unique())
        )

        cm_path = "/tmp/confusion_matrix.csv"
        cm_df.to_csv(cm_path)
        mlflow.log_artifact(cm_path)

        # Log the model
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name="dnd-character-classifier",
            input_example=X_test.head(1),
            signature=mlflow.models.infer_signature(X_train, y_train)
        )

        run_id = mlflow.active_run().info.run_id
        print(f"\nMLflow Run ID: {run_id}")
        print(f"Model registered as: dnd-character-classifier")

    return model, accuracy


if __name__ == "__main__":
    print("=" * 60)
    print("D&D Character Class Predictor - Training Script")
    print("=" * 60)

    model, accuracy = train_model(n_estimators=100, max_depth=10)

    print("\n" + "=" * 60)
    print(f"Training completed! Final accuracy: {accuracy:.4f}")
    print("=" * 60)
