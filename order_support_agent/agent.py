from google.adk.agents import LlmAgent
from google.adk.apps import App, ResumabilityConfig
from google.adk.models import Gemini
from google.genai import types
from google.adk.tools import FunctionTool, AgentTool

from order_support_agent.tools.damage_item_tools import classify_damage, search_damage_policy
from order_support_agent.tools.extract_information import extract_order_id, detect_issue_type
from order_support_agent.tools.handle_workflows import handle_workflows
from order_support_agent.tools.order_details import map_issue_to_valid_status

# Import damage detector agent (will be created as a separate function)
def create_damage_detector_agent():
    """Creates and returns the damage detector agent for image analysis."""
    from damage_detector_agent.agent import image_damage_analysis_agent
    return image_damage_analysis_agent

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# Create image generation imagegen_agent with pausable tool
order_support_agent = LlmAgent(
    name="order_issue_support_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction="""You are a support agent who is specialized in order related issues. 
    You're entitled to use tools as mentioned below. 
    After every tool call, you MUST send a natural-language message to the user summarizing the tool result and guiding the next step. 
    If a tool call was executed in the previous turn, your next output must NOT be another tool call. It must always be a user-facing message.
    Never call the same tool more than once unless the user provides new information.

    1. Request Order ID first.
        1a. Use extract_order_id to capture it and store in state under order_id.
        1b. If missing, ask explicitly. Do not proceed until obtained.
        1c. If the Order ID is already stored in session state, reuse it and do not ask again.
    2. Identify the issue.
        2a. Once Order ID is stored, ask the user to describe their problem.
        2b. Use detect_issue_type to determine the issue type and store it in state under order:<order_id>:issue_type.
        2c. Do not reveal order status or details until issue type is confirmed.    
    4. Use map_issue_to_valid_status tool for fetching the order status from the system.
        4a. Do not assume things. if status is delivered, it means order is delivered to the customer. 
        4b. Do NOT call map_issue_to_valid_status unless both order_id AND order:<order_id>:issue_type are present.
        4c. Store the order status in state under order:<order_id>:order_status
    5. All required information is now complete. 
    6. Resolution - The handle_workflows tool should only be called when the next step or resolution based on the issue needs to be provided after requesting confirmation from the user. Otherwise, do not call it. 
        6a. Use appropriate tools as mentioned in the workflow for different requirements
        6b. Mandatory Check for uploaded images for damaged / defective products.
            6b.1. If user uploads an image along with their message, use the create_damage_detector to analyze the image for damage assessment.
            6b.2. The damage detector agent will provide comprehensive damage analysis including severity, type, and recommendations.
    7. If "workflow" = "complete" in session state, it means all tasks has been completed. Otherwise, try resolving the user question from handle_workflows
    """,
    tools=[
        FunctionTool(func=extract_order_id), 
        FunctionTool(func=detect_issue_type), 
        FunctionTool(func=map_issue_to_valid_status), 
        FunctionTool(func=handle_workflows),
        FunctionTool(func=classify_damage),
        FunctionTool(func=search_damage_policy),
        AgentTool(agent=create_damage_detector_agent())
    ],
)

root_agent = order_support_agent

print("✅ Post Delivery Order Support Agent created!")

order_support_app = App(
    name="order_coordinator",
    root_agent=order_support_agent,
    resumability_config=ResumabilityConfig(is_resumable=True)
)

print("✅ Resumable app created!")
