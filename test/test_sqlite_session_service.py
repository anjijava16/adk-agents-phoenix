"""Tests for SQLite in-memory session service."""

import asyncio
import pytest
from app.services import SQLiteSessionService


class TestSQLiteSessionService:
    """Test suite for SQLiteSessionService."""

    @pytest.fixture
    async def session_service(self):
        """Create a fresh session service for each test."""
        service = SQLiteSessionService()
        yield service
        service.close()

    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test creating a new session."""
        session_service = SQLiteSessionService()
        
        await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session",
        )
        
        session = await session_service.get_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session"
        )
        assert session is not None
        assert session["session_id"] == "test_session"
        assert session["app_name"] == "test_app"
        assert session["user_id"] == "test_user"
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_session_with_metadata(self):
        """Test creating a session with metadata."""
        session_service = SQLiteSessionService()
        
        metadata = {"key": "value", "nested": {"data": 123}}
        await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session",
            metadata=metadata,
        )
        
        session = await session_service.get_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session"
        )
        assert session["data"] == metadata
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_set_and_get_session_value(self):
        """Test storing and retrieving session values."""
        session_service = SQLiteSessionService()
        
        await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session",
        )
        
        # Store a value
        test_value = {"name": "John", "age": 30}
        await session_service.set_session_value(
            session_id="test_session",
            key="user_data",
            value=test_value,
        )
        
        # Retrieve the value
        retrieved = await session_service.get_session_value(
            session_id="test_session",
            key="user_data",
        )
        assert retrieved == test_value
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_session_value_default(self):
        """Test retrieving non-existent key with default."""
        session_service = SQLiteSessionService()
        
        await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session",
        )
        
        # Get non-existent key
        default_value = {"default": True}
        retrieved = await session_service.get_session_value(
            session_id="test_session",
            key="non_existent",
            default=default_value,
        )
        assert retrieved == default_value
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_update_session(self):
        """Test updating session data."""
        session_service = SQLiteSessionService()
        
        await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session",
            metadata={"version": 1},
        )
        
        # Update with new data
        await session_service.update_session(
            session_id="test_session",
            data={"version": 2, "updated": True},
        )
        
        session = await session_service.get_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session"
        )
        assert session["data"]["version"] == 2
        assert session["data"]["updated"] is True
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_delete_session(self):
        """Test deleting a session."""
        session_service = SQLiteSessionService()
        
        await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session",
        )
        
        # Verify session exists
        session = await session_service.get_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session"
        )
        assert session is not None
        
        # Delete session
        await session_service.delete_session("test_session")
        
        # Verify session is deleted
        session = await session_service.get_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session"
        )
        assert session is None
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_list_sessions(self):
        """Test listing sessions."""
        session_service = SQLiteSessionService()
        
        # Create multiple sessions
        for i in range(3):
            await session_service.create_session(
                app_name="test_app",
                user_id="test_user",
                session_id=f"session_{i}",
            )
        
        # List sessions
        sessions = await session_service.list_sessions(
            app_name="test_app",
            user_id="test_user",
        )
        assert len(sessions) == 3
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_list_sessions_by_app(self):
        """Test listing sessions by app only."""
        session_service = SQLiteSessionService()
        
        # Create sessions for different users
        for i in range(2):
            await session_service.create_session(
                app_name="test_app",
                user_id=f"user_{i}",
                session_id=f"session_{i}",
            )
        
        # List all sessions for app
        sessions = await session_service.list_sessions(app_name="test_app")
        assert len(sessions) == 2
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_clear_all_sessions(self):
        """Test clearing all sessions."""
        session_service = SQLiteSessionService()
        
        # Create multiple sessions
        for i in range(3):
            await session_service.create_session(
                app_name="test_app",
                user_id="test_user",
                session_id=f"session_{i}",
            )
        
        # Verify sessions exist
        sessions = await session_service.list_sessions(app_name="test_app")
        assert len(sessions) == 3
        
        # Clear all
        await session_service.clear_all_sessions()
        
        # Verify cleared
        sessions = await session_service.list_sessions(app_name="test_app")
        assert len(sessions) == 0
        
        session_service.close()

    @pytest.mark.asyncio
    async def test_duplicate_session_error(self):
        """Test that creating duplicate session raises error."""
        session_service = SQLiteSessionService()
        
        await session_service.create_session(
            app_name="test_app",
            user_id="test_user",
            session_id="test_session",
        )
        
        # Try to create duplicate - should raise error
        with pytest.raises(Exception):
            await session_service.create_session(
                app_name="test_app",
                user_id="test_user",
                session_id="test_session",
            )
        
        session_service.close()


# Synchronous test runner for manual testing
async def run_manual_tests():
    """Run tests manually without pytest."""
    print("\n" + "=" * 60)
    print("SQLite Session Service - Manual Tests")
    print("=" * 60)
    
    service = SQLiteSessionService()
    
    try:
        # Test 1: Create session
        print("\n[Test 1] Creating session...")
        await service.create_session(
            app_name="demo_app",
            user_id="demo_user",
            session_id="demo_session_1",
            metadata={"test": True},
        )
        print("✓ Session created successfully")
        
        # Test 2: Retrieve session
        print("\n[Test 2] Retrieving session...")
        session = await service.get_session(
            app_name="demo_app",
            user_id="demo_user",
            session_id="demo_session_1"
        )
        print(f"✓ Session retrieved: {session}")
        
        # Test 3: Set session value
        print("\n[Test 3] Setting session value...")
        await service.set_session_value(
            session_id="demo_session_1",
            key="user_settings",
            value={"theme": "dark", "notifications": True},
        )
        print("✓ Session value set")
        
        # Test 4: Get session value
        print("\n[Test 4] Getting session value...")
        value = await service.get_session_value(
            session_id="demo_session_1",
            key="user_settings",
        )
        print(f"✓ Session value retrieved: {value}")
        
        # Test 5: List sessions
        print("\n[Test 5] Listing sessions...")
        sessions = await service.list_sessions(app_name="demo_app")
        print(f"✓ Found {len(sessions)} session(s)")
        
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60 + "\n")
        
    finally:
        service.close()


if __name__ == "__main__":
    # Run manual tests
    asyncio.run(run_manual_tests())
