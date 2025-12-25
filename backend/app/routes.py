"""API routes for the form filler application."""

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.session import session_manager


router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message from user."""
    message: str


class UploadResponse(BaseModel):
    """Response after file upload."""
    session_id: str
    message: str


class StatusResponse(BaseModel):
    """Session status response."""
    is_complete: bool
    form_data: dict


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a .docx file and create a new session."""
    # Validate file type
    if not file.filename or not file.filename.endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="Only .docx files are accepted"
        )

    # Save the file
    file_path = session_manager.upload_dir / f"{file.filename}"
    
    # Handle duplicate filenames
    counter = 1
    original_stem = file_path.stem
    while file_path.exists():
        file_path = session_manager.upload_dir / f"{original_stem}_{counter}.docx"
        counter += 1

    content = await file.read()
    file_path.write_bytes(content)

    # Create session
    session = session_manager.create_session(file_path)

    # Initialize the agent for this session
    from app.agent import initialize_session
    await initialize_session(session)

    return UploadResponse(
        session_id=session.id,
        message="Document uploaded successfully. Starting conversation..."
    )


@router.post("/chat/{session_id}")
async def send_message(session_id: str, chat_message: ChatMessage):
    """Send a message to the agent."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    # Add user message to history
    session.chat_history.append({
        "role": "user",
        "content": chat_message.message
    })

    # Process with agent
    from app.agent import process_message
    await process_message(session, chat_message.message)

    return {"status": "processing"}


@router.get("/chat/stream/{session_id}")
async def stream_messages(session_id: str):
    """SSE endpoint for streaming agent responses."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    async def event_generator():
        """Generate SSE events from the message queue."""
        while True:
            try:
                # Wait for messages with timeout
                message = await asyncio.wait_for(
                    session.message_queue.get(),
                    timeout=30.0
                )
                
                if message.get("type") == "done":
                    yield f"data: {json.dumps(message)}\n\n"
                    break
                elif message.get("type") == "close":
                    break
                else:
                    yield f"data: {json.dumps(message)}\n\n"
                    
            except asyncio.TimeoutError:
                # Send keepalive
                yield ": keepalive\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/status/{session_id}", response_model=StatusResponse)
async def get_status(session_id: str):
    """Get the current status of a session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    return StatusResponse(
        is_complete=session.is_complete,
        form_data=session.form_data.to_dict()
    )


@router.get("/download/{session_id}")
async def download_document(session_id: str):
    """Download the filled document."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    if not session.is_complete:
        raise HTTPException(
            status_code=400,
            detail="Form is not complete. Please provide all required information."
        )

    # Generate the filled document
    from app.tools.update import generate_filled_document
    output_path = generate_filled_document(session)

    return FileResponse(
        path=output_path,
        filename=f"filled_{session.file_path.name}",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


