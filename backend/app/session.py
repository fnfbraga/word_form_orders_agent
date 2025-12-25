"""Session management for the form filler application."""

import uuid
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class FormData:
    """Collected form data from the user."""
    name: str | None = None
    street: str | None = None
    postal_code_city: str | None = None
    country: str | None = None
    movies: list[dict[str, str]] = field(default_factory=list)

    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        return all([
            self.name,
            self.street,
            self.postal_code_city,
            self.country,
            len(self.movies) > 0
        ])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "street": self.street,
            "postal_code_city": self.postal_code_city,
            "country": self.country,
            "movies": self.movies
        }


@dataclass
class FormStructure:
    """Detected structure of the uploaded form."""
    has_name_field: bool = False
    has_street_field: bool = False
    has_postal_city_field: bool = False
    has_country_field: bool = False
    has_movie_table: bool = False
    movie_table_index: int | None = None
    has_checkbox_list: bool = False
    available_movies: list[str] = field(default_factory=list)
    placeholders: dict[str, str] = field(default_factory=dict)


@dataclass
class Session:
    """User session containing file and form state."""
    id: str
    file_path: Path
    created_at: datetime
    form_structure: FormStructure | None = None
    form_data: FormData = field(default_factory=FormData)
    chat_history: list[dict[str, str]] = field(default_factory=list)
    message_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    is_complete: bool = False

    def __post_init__(self):
        # Ensure message_queue is always an asyncio.Queue
        if not isinstance(self.message_queue, asyncio.Queue):
            self.message_queue = asyncio.Queue()


class SessionManager:
    """Manages user sessions with auto-expiration."""

    def __init__(self, expiry_hours: int = 1):
        self._sessions: dict[str, Session] = {}
        self._expiry_delta = timedelta(hours=expiry_hours)
        self._upload_dir = Path("uploads")
        self._upload_dir.mkdir(exist_ok=True)

    def create_session(self, file_path: Path) -> Session:
        """Create a new session for an uploaded file."""
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            file_path=file_path,
            created_at=datetime.now()
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID, returns None if expired or not found."""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        # Check expiration
        if datetime.now() - session.created_at > self._expiry_delta:
            self.delete_session(session_id)
            return None

        return session

    def delete_session(self, session_id: str) -> None:
        """Delete a session and its associated file."""
        session = self._sessions.pop(session_id, None)
        if session and session.file_path.exists():
            session.file_path.unlink()

    def cleanup_expired(self) -> int:
        """Remove all expired sessions. Returns count of removed sessions."""
        now = datetime.now()
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session.created_at > self._expiry_delta
        ]
        for sid in expired:
            self.delete_session(sid)
        return len(expired)

    @property
    def upload_dir(self) -> Path:
        """Get the upload directory path."""
        return self._upload_dir


# Global session manager instance
session_manager = SessionManager()


