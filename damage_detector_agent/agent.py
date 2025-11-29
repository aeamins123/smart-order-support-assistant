from google.adk.agents import LlmAgent
from google.adk.apps import App, ResumabilityConfig
from google.adk.models import Gemini
from google.genai import types
from config import GOOGLE_API_KEY

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# Create image damage analysis agent
image_damage_analysis_agent = LlmAgent(
    name="image_damage_analysis_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""You are a specialized image damage analysis agent. Your primary function is to analyze uploaded images to assess damage in products or items.

    Your capabilities:
    1. Analyze uploaded images to detect and classify damage
    2. Assess damage severity (minor, major, critical)
    3. Identify specific damage types (scratches, cracks, dents, etc.)
    4. Generate a short summary describing the damage with relevant details. 

    Always provide clear, actionable feedback to users about the damage detected.
    """,
    # tools=[FunctionTool(func=analyze_damage_image)],
)

print("✅ Image Damage Analysis Agent created!")

# Root agent for image damage analysis app
root_agent = image_damage_analysis_agent
