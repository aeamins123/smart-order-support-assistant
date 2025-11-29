import re
from typing import Any, Dict

from google.adk.tools import ToolContext

ISSUE_KEYWORDS = {
    "not delivered": ["not received", "didn't arrive", "never came", "never got it"],
    "late delivery": ["late", "delayed", "taking too long", "waiting long"],
    "damaged item": ["broken", "damaged", "cracked", "defective"],
    "wrong item": ["wrong", "different item", "not what I ordered"],
    "refund": ["refund", "return money", "need my money back"]}


def extract_order_id(tool_context: ToolContext, user_query:str) -> dict:
    """
    Extracts an order ID from the user's query or response and stores it in session state.
    This tool must be called whenever an order ID is detected in user message,
    including when the user replies with just the ID after being asked for it.
    This tool scans the user's message for an order ID using a regex pattern.
    If an order ID is found, it is saved into session state and marked as valid.
    If no ID is detected, the tool returns a response indicating that the order ID
    is missing and therefore invalid.

    Args:
        user_query (str): The raw message provided by the user.

    Returns:
        dict: {
            "order_id": str | None,     # The extracted order ID, if found
            "is_valid": bool            # True if an ID was found, False otherwise
        }
    """

    # Example patterns: OR12345, ORDER-1234, #12345, 123-456
    match = re.search(r"(?:OR|ORDER[- ]?|#?)(\d{4,12})", user_query, re.IGNORECASE)
    if match:
        tool_context.state["order_id"] = match.group(1)
        if  tool_context.state.get("pending_issues"):
            tool_context.state[f"order:{tool_context.state.get('order_id')}:issue_type"] = tool_context.state.get("pending_issues")
            tool_context.state["pending_issues"] = None
        return {"order_id": match.group(1), "is_valid" : True}
    return {"order_id": None, "is_valid":False, "message": "Could you please provide a valid order ID?"}


def detect_issue_type(
    tool_context: ToolContext,
    user_query: str
) -> Dict[str, Any]:
    """
    Tool to detect the issue type from the user's message and store it in session state. This tool should be invoked only if Order ID is known

    This function analyzes the user's text to determine what kind of problem they are
    facing with their order — for example: "not delivered", "late delivery",
    "damaged item", "wrong item", "refund", or a general inquiry.

    Use extract_order_id to identify the Order ID. If a recognized issue type is found, it is saved in `session.state["order_issue"]`.
    If no known issue type is detected, the state value remains unset and the tool
    returns an indication that the issue is unknown.

    Args:
        user_query: The user's input message describing their issue.

    Returns:
        A dictionary with:
            - "issue_type": detected issue type or None
            - "status": "success" (issue detected) or "unknown" (no match found)
    """
    # Mapping of keywords to issue types
    issue_keywords = {
        "not delivered": ["didn't arrive", "not delivered", "never came", "didn't receive", "missing"],
        "late delivery": ["late", "delayed", "still waiting"],
        "damaged item": ["broken", "damaged", "cracked", "defective", "not working"],
        "wrong item": ["wrong item", "different item", "incorrect item"],
        "refund": ["refund", "return my money", "money back", "cancel order", "return request"],
    }

    detected_issue = None
    lower_query = user_query.lower()

    # Look for matching keywords
    for issue_type, keywords in issue_keywords.items():
        if any(keyword in lower_query for keyword in keywords):
            detected_issue = issue_type
            break

    # Update session state only if issue detected
    if detected_issue:
        if not tool_context.state.get("order_id"):
            tool_context.state["pending_issues"] = detected_issue
            return {"status": "error", "message": "Order ID is missing. Please ask for the Order ID", "issue_type":None}
        tool_context.state[f"order:{tool_context.state.get('order_id')}:issue_type"] = detected_issue
        return {"status": "success", "issue_type": detected_issue}

    return {"status": "error", "message":"I have saved your order ID. Could you tell me what issue you are facing?"}

