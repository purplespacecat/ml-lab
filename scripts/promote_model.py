#!/usr/bin/env python3
"""
Script to promote a model to Production stage in MLflow
"""
import os
import argparse
from dotenv import load_dotenv
import mlflow
from mlflow.tracking import MlflowClient

load_dotenv()


def promote_model(model_name: str, version: str = None, stage: str = "Production"):
    """
    Promote a model version to a specific stage

    Args:
        model_name: Name of the registered model
        version: Version number to promote (or 'latest')
        stage: Target stage (Production, Staging, Archived)
    """
    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')
    mlflow.set_tracking_uri(mlflow_uri)

    client = MlflowClient()

    try:
        # Get model versions
        model_versions = client.search_model_versions(f"name='{model_name}'")

        if not model_versions:
            print(f"❌ No model found with name: {model_name}")
            return

        # Determine which version to promote
        if version is None or version == "latest":
            # Get the latest version
            latest_version = max([int(mv.version) for mv in model_versions])
            version = str(latest_version)
            print(f"Promoting latest version: {version}")
        else:
            print(f"Promoting specified version: {version}")

        # Transition to new stage
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=True  # Archive old versions in this stage
        )

        print(f"✅ Successfully promoted {model_name} version {version} to {stage}")

        # Show current model versions and stages
        print("\nCurrent model versions:")
        model_versions = client.search_model_versions(f"name='{model_name}'")
        for mv in sorted(model_versions, key=lambda x: int(x.version), reverse=True):
            print(f"  Version {mv.version}: {mv.current_stage}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Promote MLflow model to a stage")
    parser.add_argument(
        "--model-name",
        default="dnd-character-classifier",
        help="Name of the registered model"
    )
    parser.add_argument(
        "--version",
        default="latest",
        help="Version to promote (default: latest)"
    )
    parser.add_argument(
        "--stage",
        default="Production",
        choices=["Production", "Staging", "Archived"],
        help="Target stage (default: Production)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("MLflow Model Promotion Tool")
    print("=" * 60)

    promote_model(args.model_name, args.version, args.stage)
