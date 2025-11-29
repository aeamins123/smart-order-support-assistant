from google.adk.tools import ToolContext


def handle_not_delivered_workflow_for_agent(tool_context : ToolContext, order_id : str, order_status : str, user_message : str) ->dict[str, str] | str:
    """
       This workflow is triggered only after all required session state information
       (order_id, detected issue type, and mapped order status) is already known.
       Its purpose is to drive the conversation toward resolution by executing
       business actions such as escalation, investigation, or arrangement of a replacement.

       Parameters
       ----------
       order_id : str
           The unique identifier of the customer's order currently under discussion.
       order_status : str
           The system-recorded status for the order (expected to be `"delivered"` for this workflow).
       user_message : str
           The response message from user

       Returns
       -------
       dict
           A structured response containing:
           - `"action"` : ask_user to give questions back to the customer, workflow_completed - the resolution is taken.
           - additional fields describing the next recommended steps or actions
             (e.g., escalation raised, investigation ticket generated, replacement offered).

       Notes
       -----
       This tool does not validate the issue type again; it assumes the LLM has already
       confirmed that the customer's complaint is specifically a **"not delivered"**
       scenario that contradicts the system-recorded `"delivered"` status.
       """

    # Initializing the workflow
    if tool_context.state.get("substep") is None:
        tool_context.state["substep"] = "confirm_details"
        tool_context.state["check_with_neighbourhood"]=False
        tool_context.state["resolution_confirmed"] = None
        tool_context.state["workflow"] = "not_started"
    # Step 1 - Confirming details :
    # Check if the user has asked with neighbours / family / security
    # If yes, was the order delivered to them?
    if tool_context.state.get(f"order:{order_id}:order_status") == "delivered" and tool_context.state["substep"] == "confirm_details":
        tool_context.state["workflow"] = "in_progress"
        tool_context.state["substep"] = "ask_verification"
        return {
            "action" : "ask_user",
            "requires_user_response" : True,
            "message" : "Have you had a chance to check with neighbours, family, or security?"
        }

    # Step 2 - Ask for verification

    if tool_context.state.get("substep") == "ask_verification":
        user_text = user_message.lower()

        confirmations = ["yes", "checked", "i did", "i have", "already checked"]
        if any(c in user_text for c in confirmations):
            tool_context.state["check_with_neighbourhood"]= True
            tool_context.state["substep"] = "investigation_pending"
            return {
                "action" : "ask_user",
                "requires_user_response" : True,
                "message":
                    "The order is not delivered with neighbours / family / security. Apologize and inform the user if they would like to"
                    "start an investigation "

            }
        # If user hasn’t checked anything yet
        not_checked = ["no", "not yet", "haven’t", "did not"]
        if any(c in user_text for c in not_checked):
            tool_context.state["substep"]= "investigation_started"
            return {
                "action": "ask_user",
                "requires_user_response": True,
                "message":
                    "No problem. Could you please check the following:\n"
                    "- Around the delivery area\n"
                    "- With neighbors\n"
                    "- In your mailbox\n"
                    "- With building staff or reception\n\n"
                    "Let me know once you’ve checked these."
            }

        # Fallback: user said something unclear
        return {
            "action" : "ask_user",
            "requires_user_response": True,
            "message": "I want to make sure I understand you correctly.\n"
            "Have you checked around your property, with neighbors, or with building staff?"
        }

    # Step 3 - Start the investigation

    if tool_context.state.get("substep") == "investigation_pending":
        user_text = user_message.lower()

        if "yes" in user_text or "start" in user_text or "please do" in user_text:
            tool_context.state["substep"] = "investigation_started"

            # Here you will later add an internal tool call to file the investigation
            return {
                "action" : "ask_user",
                "requires_user_response" : True,
                "message":
                    "I want to make sure I understand you correctly.\n"
                    "Have you checked around your property, with neighbors, or with building staff?"

            }

        if "no" in user_text:
            tool_context.state["substep"] = "investigation_started"
            return {"action":"continue_workflow", "requires_user_response" : True, "message":"No worries. Let me know anytime if you’d like me to start the investigation."}

        return {"action": "ask_user", "requires_user_response":True, "message":"Would you like me to begin the missing package investigation?"}

        # ---------------------------
        # STEP 4 — Provide interim solution
        # ---------------------------
    if tool_context.state.get("substep") == "investigation_started":
        user_text = user_message.lower()

        if "refund" in user_text:
            tool_context.state["substep"] = "completed"
            tool_context.state["workflow"] = "completed"

            tool_context.state["resolution_confirmed"] = "refund"
            return {"action": "workflow_completed","requires_user_response" : True, "message": "Understood — I'll proceed with a refund once the carrier "
                                                     "confirms the package is missing. You'll be updated soon."
                    }

        if "replacement" in user_text or "replace" in user_text:
            tool_context.state["substep"] = "completed"
            tool_context.state["workflow"] = "completed"
            tool_context.state["resolution_confirmed"] = "replacement"

            return {
                "action": "workflow_completed",
                "requires_user_response" : True,
                "message": "Great — I'll arrange a replacement as soon as the carrier completes "
                "the investigation. You'll receive updates shortly."
            }

        return {"action": "ask_user","requires_user_response" : True, "message":
            "Would you prefer a refund or a replacement after the investigation completes?"
                }

    if tool_context.state["workflow"] == "completed":
        return{
        "action" : "workflow_completed",
        "requires_user_response" : False,
        "message" : "workflow to handle the non delivered order concerns are completed. Inform user that appropriate action mapped against state.resolution_confirmed will be taken."
    }