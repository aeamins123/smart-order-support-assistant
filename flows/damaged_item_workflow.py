from google.adk.tools import ToolContext


def damaged_item_workflow(tool_context: ToolContext, user_query: str):
    # Step 1: Check if severity already known
    severity = tool_context.state.get("damage:severity")

    # Ask user for description only once
    if not severity:
        tool_context.state["workflow"] = "in progress"
        tool_context.state["substep"] = "check_severity"
        return {
            "action": "ask_user",
            "message": "I'm sorry to hear the item arrived damaged. Could you describe the damage?"
        }
    else:
        tool_context.state["substep"] = "check_image"


    # Step 2: Infer severity using classify_damage tool
    if severity is None and tool_context.state.get("substep") == "check_severity":
        tool_context.state["substep"] = "check_image"
        return {
            "action": "tool_call",
            "tool": "classify_damage",
            "args": {"user_query": user_query}
        }

    if tool_context.state.get("substep")== "check_image":
        tool_context.state["substep"] = "policy_retrieval"
        return {
            "action" : "tool_call",
            "tool" : "image_detector_tool",
            "args" : {"user_query" : user_query}
        }

    # Step 3: RAG retrieval based on severity
    if (tool_context.state["damage:severity"] == "minor" or tool_context.state["damage:severity"] == "major") and tool_context.state.get("substep")=="policy_retrieval":
        tool_context.state["user_confirmation"] = True
        return {
            "next_step": "tool_call",
            "tool" : "search_damage_policy",
            "args": {"user_query": user_query, "damage_analysis" : tool_context.state.get("damage_analysis_results")}
        }
    #
    if tool_context.state.get("user_confirmation"):
        return {
            "next_step" : "tool_call",
            "instruction" : "user_confirmed_resolution",
            "args": {"user_query" : user_query}
        }
