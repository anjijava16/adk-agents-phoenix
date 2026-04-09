"""PostgreSQL persistent session service for ADK agents."""

import json
import uuid
from datetime import datetime
from typing import Optional, List
import logging

import psycopg2
import psycopg2.extras
from google.adk.sessions import BaseSessionService, Session
from google.adk.events import Event

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  Connection config — update these or pass via constructor
# ─────────────────────────────────────────────────────────────
DEFAULT_DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "agent_session_db",
    "user":     "welcome",
    "password": "Maxis12345",
}


class PostgresSessionService(BaseSessionService):
    """Persistent PostgreSQL session service that correctly implements ADK's interface.

    Drop-in replacement for SQLiteSessionService.
    Stores sessions + full ADK Event history so the Runner can
    restore conversation context on every call.

    Usage:
        session_service = PostgresSessionService()          # uses DEFAULT_DB_CONFIG
        session_service = PostgresSessionService(db_config={...})  # custom config
    """

    def __init__(self, db_config: Optional[dict] = None):
        """Initialize and connect to PostgreSQL.

        Args:
            db_config: Optional dict with keys: host, port, dbname, user, password.
                       Falls back to DEFAULT_DB_CONFIG if not provided.
        """
        self._db_config = db_config or DEFAULT_DB_CONFIG
        self._connection = psycopg2.connect(**self._db_config)
        # Auto-commit off — we manage transactions manually
        self._connection.autocommit = False
        self._initialize_database()
        logger.info(
            f"✓ PostgresSessionService initialized — "
            f"DB: {self._db_config['dbname']} @ {self._db_config['host']}:{self._db_config['port']}"
        )

    # ──────────────────────────────────────────────────────────
    #  Schema bootstrap
    # ──────────────────────────────────────────────────────────

    def _initialize_database(self) -> None:
        """Create tables if they don't already exist."""
        with self._connection.cursor() as cur:

            # sessions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id   TEXT        NOT NULL,
                    app_name     TEXT        NOT NULL,
                    user_id      TEXT        NOT NULL,
                    state        JSONB       NOT NULL DEFAULT '{}',
                    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (app_name, user_id, session_id)
                )
            """)

            # events table — stores serialized ADK Event objects
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id           BIGSERIAL   PRIMARY KEY,
                    app_name     TEXT        NOT NULL,
                    user_id      TEXT        NOT NULL,
                    session_id   TEXT        NOT NULL,
                    event_json   JSONB       NOT NULL,
                    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (app_name, user_id, session_id)
                        REFERENCES sessions (app_name, user_id, session_id)
                        ON DELETE CASCADE
                )
            """)

            # Index for fast event lookups per session
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_session
                ON events (app_name, user_id, session_id, id ASC)
            """)

        self._connection.commit()
        logger.debug("PostgreSQL schema initialized")

    # ──────────────────────────────────────────────────────────
    #  ADK BaseSessionService interface
    # ──────────────────────────────────────────────────────────

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: Optional[str] = None,
        state: Optional[dict] = None,
    ) -> Session:
        """Create a new session (or silently reuse existing one).

        Called by Runner the very first time a session_id is used.
        Uses INSERT ... ON CONFLICT DO NOTHING so re-calling with the
        same session_id never wipes existing data.

        Args:
            app_name:   Application name
            user_id:    User identifier
            session_id: Optional — a new UUID is generated if omitted
            state:      Optional initial state dict

        Returns:
            Session object (with any pre-existing events if session already existed)
        """
        session_id = session_id or str(uuid.uuid4())
        state_json = json.dumps(state or {})

        with self._connection.cursor() as cur:
            cur.execute("""
                INSERT INTO sessions (session_id, app_name, user_id, state)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (app_name, user_id, session_id) DO NOTHING
            """, (session_id, app_name, user_id, state_json))

        self._connection.commit()
        logger.info(f"Session created (or already existed): {session_id}")

        # Always return via get_session so events are loaded too
        return await self.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        config=None,
    ) -> Optional[Session]:
        """Retrieve a session WITH its full event history.

        The Runner calls this at the start of every run_async() to
        rebuild the LLM conversation context from stored events.

        Args:
            app_name:   Application name
            user_id:    User identifier
            session_id: Session identifier
            config:     Unused (required by ADK interface)

        Returns:
            Session with events list populated, or None if not found
        """
        with self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

            # ── 1. Fetch session row ──────────────────────────────
            cur.execute("""
                SELECT session_id, app_name, user_id, state
                FROM sessions
                WHERE app_name = %s AND user_id = %s AND session_id = %s
            """, (app_name, user_id, session_id))

            row = cur.fetchone()
            if not row:
                return None

            # state is already a dict because psycopg2 decodes JSONB automatically
            state = row["state"] if isinstance(row["state"], dict) else json.loads(row["state"])

            # ── 2. Fetch ALL events in chronological order ────────
            #    This is the KEY step — without events the Runner
            #    has no conversation history to send to the LLM.
            cur.execute("""
                SELECT event_json
                FROM events
                WHERE app_name = %s AND user_id = %s AND session_id = %s
                ORDER BY id ASC
            """, (app_name, user_id, session_id))

            event_rows = cur.fetchall()

        # ── 3. Deserialize each event back into ADK Event objects ──
        events: List[Event] = []
        for event_row in event_rows:
            try:
                raw = event_row["event_json"]
                # psycopg2 JSONB → already a dict; fall back to string parse
                event_data = raw if isinstance(raw, dict) else json.loads(raw)
                event = Event.model_validate(event_data)
                events.append(event)
            except Exception as e:
                logger.warning(f"Skipping unparseable event: {e}")

        return Session(
            id=row["session_id"],
            app_name=row["app_name"],
            user_id=row["user_id"],
            state=state,
            events=events,   # ← Runner uses this list to rebuild LLM context
        )

    async def append_event(self, session: Session, event: Event) -> Event:
        """Persist an ADK Event to PostgreSQL.

        The Runner calls this automatically after EVERY event:
          • user message
          • tool / function call
          • tool / function response
          • final agent reply

        You never need to call this manually in main.py.

        Args:
            session: The current Session object (in-memory)
            event:   The ADK Event to persist

        Returns:
            The same event (required by ADK interface)
        """
        # Let base class update the in-memory session.events list
        await super().append_event(session, event)

        event_json = event.model_dump_json()           # ADK Event → JSON string
        state_json = json.dumps(dict(session.state))   # latest state snapshot

        with self._connection.cursor() as cur:

            # Insert the new event row
            cur.execute("""
                INSERT INTO events (app_name, user_id, session_id, event_json)
                VALUES (%s, %s, %s, %s::jsonb)
            """, (session.app_name, session.user_id, session.id, event_json))

            # Keep the session's state column up to date
            cur.execute("""
                UPDATE sessions
                SET state = %s::jsonb, updated_at = NOW()
                WHERE app_name = %s AND user_id = %s AND session_id = %s
            """, (state_json, session.app_name, session.user_id, session.id))

        self._connection.commit()
        logger.debug(f"Event persisted → session={session.id}")
        return event

    async def delete_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> None:
        """Delete a session and all its events (CASCADE handles events table).

        Args:
            app_name:   Application name
            user_id:    User identifier
            session_id: Session identifier
        """
        with self._connection.cursor() as cur:
            cur.execute("""
                DELETE FROM sessions
                WHERE app_name = %s AND user_id = %s AND session_id = %s
            """, (app_name, user_id, session_id))
        self._connection.commit()
        logger.info(f"Session deleted: {session_id}")

    async def list_sessions(
        self,
        app_name: str,
        user_id: Optional[str] = None,
    ) -> list:
        """List sessions for an app, optionally filtered by user.

        Args:
            app_name: Application name
            user_id:  Optional — filter to a specific user

        Returns:
            List of session dicts ordered by most-recently-updated first
        """
        with self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if user_id:
                cur.execute("""
                    SELECT session_id, app_name, user_id, created_at, updated_at
                    FROM sessions
                    WHERE app_name = %s AND user_id = %s
                    ORDER BY updated_at DESC
                """, (app_name, user_id))
            else:
                cur.execute("""
                    SELECT session_id, app_name, user_id, created_at, updated_at
                    FROM sessions
                    WHERE app_name = %s
                    ORDER BY updated_at DESC
                """, (app_name,))
            rows = cur.fetchall()

        return [dict(row) for row in rows]

    # ──────────────────────────────────────────────────────────
    #  Utility helpers
    # ──────────────────────────────────────────────────────────

    async def get_session_event_count(self, app_name: str, user_id: str, session_id: str) -> int:
        """Return total number of events stored for a session.

        Useful for logging / debugging how much history exists.
        """
        with self._connection.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM events
                WHERE app_name = %s AND user_id = %s AND session_id = %s
            """, (app_name, user_id, session_id))
            return cur.fetchone()[0]

    async def clear_all_sessions(self) -> None:
        """⚠️ Delete ALL sessions and events. Use only in testing."""
        with self._connection.cursor() as cur:
            cur.execute("DELETE FROM events")
            cur.execute("DELETE FROM sessions")
        self._connection.commit()
        logger.warning("All sessions and events cleared from database")

    def close(self) -> None:
        """Close the PostgreSQL connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("PostgreSQL connection closed")

    def __del__(self):
        self.close()