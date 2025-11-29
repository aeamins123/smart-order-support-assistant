import asyncio
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from order_support_agent.agent import order_support_app
import sqlite3
from config import GOOGLE_API_KEY

db_url = "sqlite:///my_agent_data.db"
session_service=DatabaseSessionService(db_url=db_url)
# Create runner with the resumable app
runner = Runner(
        app=order_support_app,  # Pass the app instead of the agent
        session_service=session_service,
    )
USER_ID="Amina"

async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str = None,
    session_name: str = "default",
):
    print(f"\n ### Session: {session_name}")

    # Get app name from the Runner
    app_name = runner_instance.app_name

    # Attempt to create a new session or retrieve an existing one
    existing = await session_service.get_session(
        app_name=app_name, user_id=USER_ID, session_id=session_name
    )

    if existing:
        session = existing
    else:
        session = await session_service.create_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )

    # Process queries if provided
    if user_queries:
        # Convert single query to list for uniform processing
        if type(user_queries) == str:
            user_queries = [user_queries]

        # Process each query in the list sequentially
        for query in user_queries:
            print(f"\nUser > {query}")

            # Convert the query string to the ADK Content format
            query = types.Content(role="user", parts=[types.Part(text=query)])

            # Stream the agent's response asynchronously
            async for event in runner_instance.run_async(
                user_id=USER_ID, session_id=session.id, new_message=query
            ):
                # Check if the event contains valid content
                if event.content and event.content.parts:
                    # Filter out empty or "None" responses before printing
                    if (
                        event.content.parts[0].text != "None"
                        and event.content.parts[0].text
                    ):
                        print("{model}>", event.content.parts[0].text)
                        # return event.content.parts[0].text
                    else:
                        print("model dint respond")

    else:
        print("No queries!")

# Execute the async function
asyncio.run(run_session(runner_instance=runner, user_queries=["Where is my order ORDER-240240"],session_name="session1"))

def check_data_in_db():
    with sqlite3.connect("my_agent_data.db") as connection:
        cursor = connection.cursor()
        result = cursor.execute(
            "select app_name, session_id, author, content from events"
        )
        print([_[0] for _ in result.description])
        for each in result.fetchall():
            print(each)

# check_data_in_db()