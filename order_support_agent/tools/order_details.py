from google.adk.tools import ToolContext

ORDER_STATUS_TO_ISSUES = {
    "delivered": ["not delivered","general inquiry", "damaged item", "wrong item", "refund"],
}

ISSUE_TO_ORDER_STATUS = {
    issue: [
        status for status, issues in ORDER_STATUS_TO_ISSUES.items()
        if issue in issues
    ]
    for status, issues in ORDER_STATUS_TO_ISSUES.items()
    for issue in issues
}


def map_issue_to_valid_status(tool_context: ToolContext, issue_type: str) -> dict:
    """
    Tool to identify the issue and map it against the corresponding status. Use extract_order_id tool, if order ID is not known.

    :param issue_type: It is the issue that the user is facing with their current order
    :return: A dictionary that would have the order ID, status of the order delivery
    """
    order_id = tool_context.state.get("order_id")
    issue = tool_context.state.get(f"order:{order_id}:issue_type")


    if order_id is None or issue is None:
        return {"status" : "error", "message": "Please provide the missing information."}

    valid_statuses = ISSUE_TO_ORDER_STATUS.get(issue)

    if not valid_statuses:
        return {
            "status": "error",
            "message": f"Unknown or unsupported issue type: {issue_type}",
        }


    tool_context.state[f"order:{tool_context.state.get("order_id")}:order_status"] = valid_statuses[0]

    return {
        "status": "success",
        "issue_type": issue_type,
        "valid_statuses": valid_statuses[0],
    }
