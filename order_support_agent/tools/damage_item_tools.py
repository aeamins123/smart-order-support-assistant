from google.adk.tools import ToolContext

from rag.vectorstore import collection


def classify_damage(tool_context: ToolContext, user_query: str) -> dict:
    """
    Classifies the severity of a damaged item based on user description.
    Returns: { severity: minor | major | unsure }
    """
    text = user_query.lower()

    if any(x in text for x in ["cracked", "chip", "scratched", "small dent"]):
        severity = "minor"
        damage = next((x for x in ["cracked", "chip", "scratched", "small dent"] if x in text), None)
    elif any(x in text for x in ["broken", "shattered", "completely damaged", "not working", "dead"]):
        severity = "major"
        damage = next((x for x in ["broken", "shattered", "completely damaged", "not working", "dead"] if x in text), None)
    else:
        severity = "unsure"
        damage = None
    tool_context.state["damage:severity"] = severity
    tool_context.state["damage"] = damage
    return {"severity": severity}



def search_damage_policy(query: str, tool_context: ToolContext, damage_analysis:str="") -> dict:
    results = collection.query(query_texts=[query, damage_analysis], n_results=3)
    matches = results["documents"][0]
    tool_context.state["policy_info"] = " ".join(matches)
    return {
        "matches": matches,
        "policy_summary": "\n".join(matches)
    }


def user_confirmed_resolution(tool_context: ToolContext, query: str) -> dict:
    text = query.lower()
    solution = ""
    if "replacement" or "replace" in text:
        solution = "replacement"
        tool_context.state['preferred_resolution'] = "replacement"
    elif "refund" in text:
        solution = "refund"
        tool_context.state['preferred_resolution'] = "refund"

    return{
            "customer_preferred_solution" : solution,
            "possible_solution" : tool_context.state.get()
        }

def image_detector_tool(image: bytes, tool_context: ToolContext) -> dict:
    """
    A tool to detect objects present in an uploaded image.

    Args:
        image: The raw bytes of the image to analyze.

    Returns:
        A dictionary containing the detected objects.
    """
    from damage_detector_agent.agent import image_damage_analysis_agent
    ai_gen_response = image_damage_analysis_agent.run(image)
    tool_context.state["damage_analysis_results"].append(ai_gen_response)
    return {"issue_summary_from_uploaded_image": ai_gen_response}