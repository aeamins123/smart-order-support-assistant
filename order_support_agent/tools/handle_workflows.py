from google.adk.tools import ToolContext

from flows.damaged_item_workflow import damaged_item_workflow
from flows.not_delivered_workflow import handle_not_delivered_workflow_for_agent


def handle_workflows(tool_context : ToolContext, user_message:str) -> dict:
    """
    Decides which workflow should run based on order state stored in session. Before executing, ask for confirmation.
    Once all required parameters are present, this tool triggers the matching workflow.
    :param user_message : The user query / response

    :return:
    based on the issue type identified, assigned workflow will be invoked to resolve the issue.
    """
    order_id = tool_context.state.get("order_id")
    issue_type = tool_context.state.get(f"order:{order_id}:issue_type")
    status = tool_context.state.get(f"order:{order_id}:order_status")

    # Check missing information
    if not order_id or not issue_type or not status:
        return {
            "status": "error",
            "message": "All required information to process the request is still not complete"
        }

    if issue_type == "not delivered":
        # Call workflow programmatically
        return handle_not_delivered_workflow_for_agent(tool_context, order_id, status, user_message)
    elif issue_type == "damaged item":
        return damaged_item_workflow(tool_context, user_message)