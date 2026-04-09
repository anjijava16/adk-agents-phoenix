# Enhanced SQLiteSessionService - Documentation

## Overview

The enhanced `SQLiteSessionService` implements a **Redis/S3-like session management pattern** using **SQLite** for persistent storage. It's designed to work seamlessly with ADK agents while maintaining conversation history, event tracking, and multi-session support.

## Key Features

### 1. **Persistent Storage**
- Stores all session data in `agents_database.db` at project root
- Data survives application restarts
- No need for external Redis or S3 infrastructure

### 2. **Conversation History**
- Automatically tracks all queries and responses within a session
- Previous context available when resuming existing sessions
- New sessions start with fresh context

### 3. **Event Tracking**
- Record any type of event: `user_query`, `agent_response`, `function_call`, etc.
- Full event history with timestamps
- Queryable by event type

### 4. **Multi-Session Support**
- Different `session_id` = separate conversation contexts
- Same `session_id` = continues previous conversation
- Perfect for multi-user or multi-scenario applications

## Database Schema

```sql
-- Main sessions table
sessions (
    session_id TEXT PRIMARY KEY,
    app_name TEXT,
    user_id TEXT,
    created_at TEXT,
    updated_at TEXT,
    data TEXT  -- JSON metadata
)

-- Key-value storage for session data
session_data (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    key TEXT,
    value TEXT,  -- JSON
    created_at TEXT,
    UNIQUE(session_id, key)
)

-- Event log for tracking queries, responses, etc.
events (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    event_type TEXT,  -- 'user_query', 'agent_response', etc.
    content TEXT,     -- JSON
    created_at TEXT
)
```

## Core Methods

### Session Management

#### `process_query_with_conversation(session_id, query, app_name, user_id)`
**Purpose**: Main entry point for handling user queries with automatic history management

**Returns**:
```python
{
    "session_id": "session_1",
    "is_new_session": True,  # or False if existing
    "conversation_history": [...],
    "current_query": "What is Bitcoin?",
    "total_messages": 1
}
```

**Behavior**:
- New `session_id` → Creates session + starts conversation
- Existing `session_id` → Retrieves history + appends query

#### `create_session(app_name, user_id, session_id, metadata)`
Create a new session manually

#### `get_session(app_name, user_id, session_id)`
Retrieve an existing session

#### `delete_session(session_id)`
Delete a session and all associated events

### Event Tracking

#### `append_event(session_id, event_type, content)`
Record an event in the session

**Example**:
```python
await session_service.append_event(
    session_id="session_1",
    event_type="user_query",
    content={"query": "What is Bitcoin?", "turn": 1}
)
```

#### `get_events(session_id, event_type=None, limit=None)`
Retrieve events from a session

**Example**:
```python
# Get all events
events = await session_service.get_events("session_1")

# Get only user queries
queries = await session_service.get_events("session_1", event_type="user_query")

# Get last 10 events
recent = await session_service.get_events("session_1", limit=10)
```

#### `get_conversation_history(session_id)`
Get only user queries and agent responses (filtered from all events)

#### `get_session_summary(session_id)`
Get comprehensive session summary including all statistics

### Session Listing

#### `list_sessions(app_name, user_id=None)`
List all sessions for an app or specific user

## Usage Examples

### Example 1: Basic Multi-Turn Conversation

```python
from app.services import SQLiteSessionService

session_service = SQLiteSessionService()

# First query - new session
result1 = await session_service.process_query_with_conversation(
    session_id="user_chat_1",
    query="What is Bitcoin?",
    app_name="my_app",
    user_id="user_123"
)
# Output: is_new_session=True, total_messages=1

# Second query - same session
result2 = await session_service.process_query_with_conversation(
    session_id="user_chat_1",
    query="What's its current price?",
    app_name="my_app",
    user_id="user_123"
)
# Output: is_new_session=False, total_messages=2 (previous history available)

# Different session - fresh start
result3 = await session_service.process_query_with_conversation(
    session_id="user_chat_2",
    query="Tell me about Ethereum",
    app_name="my_app",
    user_id="user_123"
)
# Output: is_new_session=True, total_messages=1
```

### Example 2: Event Tracking

```python
# Record multiple events
await session_service.append_event(
    session_id="chat_1",
    event_type="user_query",
    content={"query": "What is blockchain?", "source": "web"}
)

await session_service.append_event(
    session_id="chat_1",
    event_type="agent_response",
    content={"response": "Blockchain is...", "model": "gpt-4"}
)

await session_service.append_event(
    session_id="chat_1",
    event_type="function_call",
    content={"function": "get_price", "args": {"coin": "BTC"}}
)

# Retrieve events
all_events = await session_service.get_events("chat_1")
queries_only = await session_service.get_events("chat_1", event_type="user_query")
```

### Example 3: Session Summary

```python
summary = await session_service.get_session_summary("chat_1")

print(f"Total events: {summary['total_events']}")
print(f"Total messages: {summary['total_messages']}")
print(f"Last activity: {summary['last_activity']}")

# Access conversation
for msg in summary['conversation_history']:
    if msg['event_type'] == 'user_query':
        print(f"User: {msg['content']['query']}")
    elif msg['event_type'] == 'agent_response':
        print(f"Agent: {msg['content']['response']}")
```

## Integration with ADK Agents

### In `main.py`:

```python
from app.services import SQLiteSessionService

async def main(query: str, session_id: str):
    # Initialize session service
    session_service = SQLiteSessionService()
    
    # Process query with history
    result = await session_service.process_query_with_conversation(
        session_id=session_id,
        query=query,
        app_name="my_agent_app",
        user_id=settings.user_id,
    )
    
    # Log context
    logger.info(f"Is new session: {result['is_new_session']}")
    logger.info(f"Total messages: {result['total_messages']}")
    
    # Record user query as event
    await session_service.append_event(
        session_id=session_id,
        event_type="user_query",
        content={"query": query}
    )
    
    # Run agent with runner
    runner = Runner(
        agent=agent,
        app_name="my_agent_app",
        session_service=session_service
    )
    
    async for event in runner.run_async(
        user_id=settings.user_id,
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)])
    ):
        # Process events...
        
        # Record agent response
        if event.is_final_response():
            response = event.content.parts[0].text
            await session_service.append_event(
                session_id=session_id,
                event_type="agent_response",
                content={"response": response}
            )
```

## Comparison: SQLite vs Redis/S3

| Feature | SQLite | Redis/S3 |
|---------|--------|----------|
| **Setup** | Zero (local file) | Requires Redis + S3 |
| **Persistence** | All data stored locally | Redis (memory) + S3 (backup) |
| **Performance** | Very fast (local) | Fast (but network latency) |
| **Scalability** | Single machine | Distributed (if needed) |
| **Data Access** | Direct queries | Key-value only |
| **Cost** | Free | Paid services |
| **Learning Curve** | Simple | Moderate |
| **Use Case** | Development, local deployment | Production multi-node systems |

## Best Practices

### ✅ Do's

- Use meaningful `session_id` values (e.g., `user_123_chat_1`)
- Record both user queries and agent responses as events
- Use consistent `app_name` across your application
- Call `close()` when shutting down (for cleanup)
- Use `get_session_summary()` for analytics

### ❌ Don'ts

- Don't change `session_id` mid-conversation (creates new session)
- Don't store sensitive data in plain text
- Don't forget to close the session service
- Don't assume events are atomic (may have timing issues in concurrent scenarios)

## Advanced: Custom Event Types

```python
# You can use any custom event type
await session_service.append_event(
    session_id="session_1",
    event_type="custom_metric",  # Custom type
    content={
        "latency_ms": 234,
        "tokens_used": 150,
        "model": "gpt-4"
    }
)
```

## Troubleshooting

### Issue: Database is locked
**Solution**: Ensure only one process accesses the database. Connection uses `check_same_thread=False`, but concurrent writes can cause locks.

### Issue: Sessions not persisting
**Solution**: Call `close()` before exiting, or ensure commits are happening with `await` calls.

### Issue: Can't import SQLiteSessionService
**Solution**: Ensure app is properly initialized: `from app.services import SQLiteSessionService`

## Running the Example

```bash
cd /Users/welcome/Desktop/sai_welcome_hanuman/adk_agents_phoenix

# Run the enhanced example
python examples/sqlite_enhanced_session_example.py
```

## Database Location

The SQLite database file is stored at:
```
/Users/welcome/Desktop/sai_welcome_hanuman/adk_agents_phoenix/agents_database.db
```

You can inspect it using:
```bash
sqlite3 agents_database.db

# Then use SQL:
sqlite> SELECT * FROM sessions;
sqlite> SELECT * FROM events WHERE session_id = 'session_1';
sqlite> SELECT * FROM session_data WHERE session_id = 'session_1';
```

## Summary

The enhanced `SQLiteSessionService` provides a complete solution for session management with:
- ✅ Persistent storage (SQLite)
- ✅ Conversation history tracking
- ✅ Event logging and retrieval
- ✅ Multi-session support
- ✅ Zero external dependencies (beyond SQLite, which is built-in)
- ✅ Perfect for development and production single-node deployments

It's designed as a **drop-in replacement** for the Redis/S3 pattern but with the simplicity and efficiency of local SQLite storage.
