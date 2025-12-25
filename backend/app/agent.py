"""Google ADK Agent configuration for the form filler."""

import os
from typing import Any

from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.session import Session
from app.tools.inspect import inspect_form_structure
from app.tools.validate import validate_country
from app.tools.update import update_order_document, add_movie


# Session service for ADK
session_service = InMemorySessionService()

# Store runners and sessions per user session
_runners: dict[str, Runner] = {}
_app_sessions: dict[str, Session] = {}


def _get_current_session(session_id: str) -> Session | None:
    """Get the current app session by ID."""
    return _app_sessions.get(session_id)


# Tool functions that will be exposed to the agent
def inspect_form(session_id: str) -> dict:
    """
    Inspect the uploaded document to identify form fields and structure.
    Call this first to understand what fields need to be filled.
    
    Args:
        session_id: The session ID (automatically provided)
    
    Returns:
        Dictionary with detected fields and movie table info
    """
    session = _get_current_session(session_id)
    if not session:
        return {"error": "Session not found"}
    return inspect_form_structure(session)


def validate_shipping_country(country_name: str) -> dict:
    """
    Validate if a country name is a real, valid country for shipping.
    Always call this before accepting a country value from the user.
    
    Args:
        country_name: The country name to validate
    
    Returns:
        Dictionary with is_valid boolean and message
    """
    return validate_country(country_name)


def update_customer_info(
    session_id: str,
    name: str | None = None,
    street: str | None = None,
    postal_code_city: str | None = None,
    country: str | None = None
) -> dict:
    """
    Update the customer's shipping information.
    Use this to save name, street address, postal code/city, or country.
    Only provide the fields you want to update.
    
    Args:
        session_id: The session ID (automatically provided)
        name: Customer's full name
        street: Street address
        postal_code_city: Postal/ZIP code and city combined
        country: Country (must be validated first using validate_shipping_country)
    
    Returns:
        Dictionary with current form state and missing fields
    """
    session = _get_current_session(session_id)
    if not session:
        return {"error": "Session not found"}
    return update_order_document(
        session,
        name=name,
        street=street,
        postal_code_city=postal_code_city,
        country=country
    )


def add_movie_to_order(session_id: str, title: str, language: str) -> dict:
    """
    Add a movie to the order. Call this for each movie the customer wants.
    
    Args:
        session_id: The session ID (automatically provided)
        title: The movie title
        language: The language of the movie
    
    Returns:
        Dictionary with the added movie and current movie list
    """
    session = _get_current_session(session_id)
    if not session:
        return {"error": "Session not found"}
    return add_movie(session, title=title, language=language)


def check_form_completion(session_id: str) -> dict:
    """
    Check if all required form fields are complete.
    Call this to see what information is still missing.
    
    Args:
        session_id: The session ID (automatically provided)
    
    Returns:
        Dictionary with completion status and missing fields
    """
    session = _get_current_session(session_id)
    if not session:
        return {"error": "Session not found"}
    return update_order_document(session)


SYSTEM_INSTRUCTION = """You are a friendly and helpful assistant that helps users fill out movie order forms.

Your job is to:
1. First inspect the uploaded form to understand its structure
2. Guide the user through providing all required information:
   - Name (customer's full name)
   - Street address
   - Postal code and city
   - Country (MUST be validated before accepting)
   - List of movies with their titles and languages

IMPORTANT RULES:
- Always validate country names using validate_shipping_country before accepting them
- If a country is invalid (like "Narnia"), reject it and ask for a valid country
- Allow users to add multiple movies - always ask "Would you like to add another movie?"
- Be conversational and helpful, don't be robotic
- After each piece of information, confirm what you've received
- When all information is complete, let the user know they can download their filled form

Start by greeting the user and inspecting the form, then ask for their information step by step.
If the user provides multiple pieces of information at once, process them all.

CRITICAL: When calling tools that need session_id, always use the session_id that was provided in the system context.
"""


def create_agent_for_session(session_id: str) -> Agent:
    """Create an agent configured for a specific session."""
    
    # Create wrapper functions that inject the session_id
    def inspect_form_wrapper() -> dict:
        """Inspect the uploaded document to identify form fields and structure."""
        return inspect_form(session_id)
    
    def validate_country_wrapper(country_name: str) -> dict:
        """Validate if a country name is valid for shipping."""
        return validate_shipping_country(country_name)
    
    def update_name(name: str) -> dict:
        """Update customer's full name."""
        return update_customer_info(session_id, name=name)
    
    def update_street(street: str) -> dict:
        """Update customer's street address."""
        return update_customer_info(session_id, street=street)
    
    def update_postal_code_city(postal_code_city: str) -> dict:
        """Update customer's postal code and city."""
        return update_customer_info(session_id, postal_code_city=postal_code_city)
    
    def update_country(country: str) -> dict:
        """Update customer's country. Must be validated first using validate_country_wrapper."""
        return update_customer_info(session_id, country=country)
    
    def add_movie_wrapper(title: str, language: str) -> dict:
        """Add a movie to the order."""
        return add_movie_to_order(session_id, title, language)
    
    def check_completion_wrapper() -> dict:
        """Check if all required fields are complete."""
        return check_form_completion(session_id)
    
    return Agent(
        model="gemini-2.0-flash",
        name="form_filler_agent",
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            inspect_form_wrapper,
            validate_country_wrapper,
            update_name,
            update_street,
            update_postal_code_city,
            update_country,
            add_movie_wrapper,
            check_completion_wrapper
        ]
    )


async def initialize_session(session: Session) -> None:
    """Initialize the ADK agent for a new session."""
    # Store app session
    _app_sessions[session.id] = session
    
    # Create ADK session (sync method)
    adk_session = session_service.create_session(
        app_name="form_filler",
        user_id=session.id,
        session_id=session.id
    )
    
    # Create agent with session-specific tools
    agent = create_agent_for_session(session.id)
    
    # Create runner
    runner = Runner(
        agent=agent,
        app_name="form_filler",
        session_service=session_service
    )
    
    _runners[session.id] = runner
    
    # Send initial message to start the conversation
    await process_message(session, "[System: User has uploaded a document. Start the conversation.]")


async def process_message(session: Session, user_message: str) -> None:
    """Process a user message through the agent and stream responses."""
    runner = _runners.get(session.id)
    if not runner:
        await session.message_queue.put({
            "type": "error",
            "content": "Session not properly initialized"
        })
        return
    
    try:
        # Create proper content object for ADK
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        )
        
        # Run the agent
        async for event in runner.run_async(
            user_id=session.id,
            session_id=session.id,
            new_message=content
        ):
            # Handle different event types
            if hasattr(event, 'content') and event.content:
                # Text response from agent
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            # Add to chat history
                            session.chat_history.append({
                                "role": "assistant",
                                "content": part.text
                            })
                            # Send to stream
                            await session.message_queue.put({
                                "type": "message",
                                "role": "assistant",
                                "content": part.text
                            })
        
        # Signal completion of this response
        await session.message_queue.put({
            "type": "done",
            "is_complete": session.is_complete
        })
        
    except Exception as e:
        await session.message_queue.put({
            "type": "error",
            "content": str(e)
        })
