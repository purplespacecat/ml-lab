"""
Gradio UI for D&D Character Class Predictor
Provides a user-friendly interface to predict character classes
"""
import os
import logging
import gradio as gr
import requests
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

MODEL_SERVER_URL = os.getenv('MODEL_SERVER_URL', 'http://localhost:8000')


def predict_character_class(strength, dexterity, constitution, intelligence, wisdom, charisma):
    """
    Call the model server to predict character class

    Args:
        strength: Strength ability score (3-20)
        dexterity: Dexterity ability score (3-20)
        constitution: Constitution ability score (3-20)
        intelligence: Intelligence ability score (3-20)
        wisdom: Wisdom ability score (3-20)
        charisma: Charisma ability score (3-20)

    Returns:
        Tuple of (predicted class, confidence bar chart, detailed probabilities)
    """
    try:
        # Prepare the request
        payload = {
            "strength": int(strength),
            "dexterity": int(dexterity),
            "constitution": int(constitution),
            "intelligence": int(intelligence),
            "wisdom": int(wisdom),
            "charisma": int(charisma)
        }

        # Call the prediction API
        response = requests.post(f"{MODEL_SERVER_URL}/predict", json=payload)
        response.raise_for_status()

        result = response.json()

        # Extract results
        predicted_class = result['predicted_class']
        confidence = result['confidence']
        all_probs = result['all_probabilities']

        # Format output
        prediction_text = f"## Predicted Class: **{predicted_class}**\n\nConfidence: **{confidence:.2%}**"

        # Sort probabilities for better visualization
        sorted_probs = dict(sorted(all_probs.items(), key=lambda x: x[1], reverse=True))

        # Create detailed probability text
        prob_details = "### All Class Probabilities:\n\n"
        for class_name, prob in sorted_probs.items():
            bar = "█" * int(prob * 20)
            prob_details += f"**{class_name}**: {prob:.2%} {bar}\n\n"

        return prediction_text, sorted_probs, prob_details

    except requests.exceptions.ConnectionError:
        error_msg = f"❌ Cannot connect to model server at {MODEL_SERVER_URL}\n\nPlease ensure the model server is running."
        return error_msg, {}, error_msg
    except requests.exceptions.HTTPError as e:
        error_msg = f"❌ Error from model server: {e.response.text}"
        return error_msg, {}, error_msg
    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        return error_msg, {}, error_msg


def get_server_status():
    """Check if the model server is healthy"""
    try:
        response = requests.get(f"{MODEL_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            return "✅ Model Server: **Online**"
        else:
            return f"⚠️  Model Server: **Degraded** (Status: {response.status_code})"
    except:
        return "❌ Model Server: **Offline**"


# Preset character examples
EXAMPLE_CHARACTERS = [
    [16, 12, 14, 8, 10, 10],   # Barbarian
    [10, 16, 12, 12, 11, 12],  # Rogue
    [8, 12, 11, 16, 12, 10],   # Wizard
    [14, 10, 12, 10, 11, 14],  # Paladin
    [10, 13, 11, 12, 11, 15],  # Bard
]


# Create Gradio interface
with gr.Blocks(title="D&D Character Class Predictor", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🎲 D&D Character Class Predictor

        Enter your character's ability scores to predict their most suitable class!

        This ML model was trained on typical ability score distributions for each D&D 5e class.
        """
    )

    # Server status
    status_display = gr.Markdown(get_server_status())

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Ability Scores")
            gr.Markdown("*Standard D&D ability score range: 3-20*")

            strength = gr.Slider(
                minimum=3, maximum=20, value=10, step=1,
                label="💪 Strength",
                info="Physical power and athletic ability"
            )
            dexterity = gr.Slider(
                minimum=3, maximum=20, value=10, step=1,
                label="🤸 Dexterity",
                info="Agility, reflexes, and balance"
            )
            constitution = gr.Slider(
                minimum=3, maximum=20, value=10, step=1,
                label="❤️  Constitution",
                info="Health, stamina, and vital force"
            )
            intelligence = gr.Slider(
                minimum=3, maximum=20, value=10, step=1,
                label="🧠 Intelligence",
                info="Reasoning and memory"
            )
            wisdom = gr.Slider(
                minimum=3, maximum=20, value=10, step=1,
                label="🦉 Wisdom",
                info="Awareness, intuition, and insight"
            )
            charisma = gr.Slider(
                minimum=3, maximum=20, value=10, step=1,
                label="✨ Charisma",
                info="Force of personality and leadership"
            )

            predict_btn = gr.Button("🔮 Predict Class", variant="primary", size="lg")
            refresh_status_btn = gr.Button("🔄 Refresh Server Status", size="sm")

        with gr.Column(scale=1):
            gr.Markdown("### Prediction Results")
            prediction_output = gr.Markdown("*Results will appear here*")

            gr.Markdown("### Probability Distribution")
            probability_chart = gr.BarPlot(
                x="class",
                y="probability",
                title="Class Probabilities",
                y_lim=[0, 1],
                height=300,
                interactive=False
            )

            probability_details = gr.Markdown("")

    # Examples
    gr.Markdown("### 📋 Try These Example Characters")
    gr.Examples(
        examples=EXAMPLE_CHARACTERS,
        inputs=[strength, dexterity, constitution, intelligence, wisdom, charisma],
        label="Click an example to load preset ability scores"
    )

    # Event handlers
    predict_btn.click(
        fn=predict_character_class,
        inputs=[strength, dexterity, constitution, intelligence, wisdom, charisma],
        outputs=[prediction_output, probability_chart, probability_details]
    )

    refresh_status_btn.click(
        fn=get_server_status,
        outputs=status_display
    )

    # Add information footer
    gr.Markdown(
        """
        ---
        ### 📚 About This Project

        This is a production-lite ML pipeline demonstration featuring:
        - **MLflow** for experiment tracking and model registry
        - **PostgreSQL** for MLflow backend storage
        - **MinIO** for artifact storage (S3-compatible)
        - **FastAPI** for model serving
        - **Gradio** for the user interface
        - **Docker Compose** for orchestration

        **Model**: Random Forest Classifier trained on synthetic D&D character data
        """
    )


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Gradio UI for D&D Character Class Predictor")
    logger.info(f"Model Server URL: {MODEL_SERVER_URL}")
    logger.info("=" * 60)

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
