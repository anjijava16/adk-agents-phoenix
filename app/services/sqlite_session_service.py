"""SQLite persistent session service for ADK agents."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List
import logging

from google.adk.sessions import BaseSessionService, Session
from google.adk.events import Event

logger = logging.getLogger(__name__)


class SQLiteSessionService(BaseSessionService):
    """Persistent SQLite session service that correctly implements ADK's interface."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "agents_database.db"
        else:
            db_path = Path(db_path)

        self.db_path = db_path
        self._connection = sqlite3.connect(str(db_path), check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_database()
        logger.info(f"✓ SQLiteSessionService initialized — DB: {db_path}")

    def _initialize_database(self) -> None:
        cursor = self._connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  TEXT NOT NULL,
                app_name    TEXT NOT NULL,
                user_id     TEXT NOT NULL,
                state       TEXT NOT NULL DEFAULT '{}',
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL,
                PRIMARY KEY (app_name, user_id, session_id)
            )
        """)

        # ✅ Store ADK Event objects as serialized JSON blobs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name    TEXT NOT NULL,
                user_id     TEXT NOT NULL,
                session_id  TEXT NOT NULL,
                event_json  TEXT NOT NULL,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (app_name, user_id, session_id)
                    REFERENCES sessions(app_name, user_id, session_id)
                    ON DELETE CASCADE
            )
        """)

        self._connection.commit()

    # ------------------------------------------------------------------
    # ✅ Correctly implement ADK's BaseSessionService interface
    # ------------------------------------------------------------------

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: Optional[str] = None,
        state: Optional[dict] = None,
    ) -> Session:
        """Create a new session. Called by Runner on first use."""
        from google.adk.sessions.session import Session as ADKSession
        import uuid

        session_id = session_id or str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        state_json = json.dumps(state or {})

        cursor = self._connection.cursor()
        # ✅ Use INSERT OR IGNORE — don't overwrite existing sessions
        cursor.execute("""
            INSERT OR IGNORE INTO sessions
                (session_id, app_name, user_id, state, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, app_name, user_id, state_json, now, now))
        self._connection.commit()

        logger.info(f"Session created: {session_id}")
        # Return session WITH its existing events (if any)
        return await self.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        config=None,
    ) -> Optional[Session]:
        """Retrieve session with full event history for context continuity."""
        cursor = self._connection.cursor()

        cursor.execute("""
            SELECT session_id, app_name, user_id, state
            FROM sessions
            WHERE app_name = ? AND user_id = ? AND session_id = ?
        """, (app_name, user_id, session_id))

        row = cursor.fetchone()
        if not row:
            return None

        state = json.loads(row["state"])

        # ✅ Load all stored ADK events to restore conversation context
        cursor.execute("""
            SELECT event_json FROM events
            WHERE app_name = ? AND user_id = ? AND session_id = ?
            ORDER BY id ASC
        """, (app_name, user_id, session_id))

        event_rows = cursor.fetchall()
        events = []
        for event_row in event_rows:
            try:
                event_data = json.loads(event_row["event_json"])
                event = Event.model_validate(event_data)
                events.append(event)
            except Exception as e:
                logger.warning(f"Skipping unparseable event: {e}")

        session = Session(
            id=row["session_id"],
            app_name=row["app_name"],
            user_id=row["user_id"],
            state=state,
            events=events,  # ✅ This is what gives the Runner conversation history
        )
        return session

    async def append_event(self, session: Session, event: Event) -> Event:
        """Called by ADK Runner after every turn to persist the event."""
        # Let the base class update the in-memory session state
        await super().append_event(session, event)

        now = datetime.utcnow().isoformat()
        # ✅ Serialize the ADK Event and persist it
        event_json = event.model_dump_json()

        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT INTO events (app_name, user_id, session_id, event_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (session.app_name, session.user_id, session.id, event_json, now))

        # Also persist any state changes the event carried
        state_json = json.dumps(dict(session.state))
        cursor.execute("""
            UPDATE sessions SET state = ?, updated_at = ?
            WHERE app_name = ? AND user_id = ? AND session_id = ?
        """, (state_json, now, session.app_name, session.user_id, session.id))

        self._connection.commit()
        logger.debug(f"Event persisted for session {session.id}")
        return event

    async def delete_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> None:
        cursor = self._connection.cursor()
        cursor.execute("""
            DELETE FROM sessions
            WHERE app_name = ? AND user_id = ? AND session_id = ?
        """, (app_name, user_id, session_id))
        self._connection.commit()

    async def list_sessions(
        self, app_name: str, user_id: Optional[str] = None
    ) -> list:
        cursor = self._connection.cursor()
        if user_id:
            cursor.execute("""
                SELECT session_id, app_name, user_id, created_at, updated_at
                FROM sessions WHERE app_name = ? AND user_id = ?
                ORDER BY updated_at DESC
            """, (app_name, user_id))
        else:
            cursor.execute("""
                SELECT session_id, app_name, user_id, created_at, updated_at
                FROM sessions WHERE app_name = ?
                ORDER BY updated_at DESC
            """, (app_name,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        if self._connection:
            self._connection.close()

    def __del__(self):
        self.close()