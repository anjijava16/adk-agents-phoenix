"""
Example of using enhanced SQLiteSessionService with conversation history and event tracking.

This example demonstrates:
1. Creating multiple sessions (like Redis/S3 implementation)
2. Tracking conversation history across multiple queries
3. Recording events (user queries, agent responses)
4. Retrieving session summaries
5. Similar pattern to Redis/S3 implementation but with SQLite persistence

Similar to the Redis/S3 example but using SQLite for persistence.
"""

import asyncio
from app.services import SQLiteSessionService


async def main():
    """Demonstrate enhanced SQLiteSessionService functionality."""
    
    # Initialize the session service with persistent storage
    session_service = SQLiteSessionService()
    
    # Session parameters
    APP_NAME = "sqlite_enhanced_example"
    USER_ID = "user_123"
    SESSION_ID = "session_capital_info"
    
    print("=" * 70)
    print("Enhanced SQLite Session Service - Multi-Turn Conversation Example")
    print("(Similar to Redis/S3 implementation but with SQLite)")
    print("=" * 70)
    
    # Simulate multi-turn conversation
    queries = [
        "What is the capital of Kenya?",
        "What about Italy?",
        "Which countries have I asked about?",
        "Tell me all the capitals I've mentioned so far."
    ]
    
    print(f"\nStarting conversation in session: {SESSION_ID}")
    print("-" * 70)
    
    # Process multiple queries in the same session
    for turn, query in enumerate(queries, 1):
        print(f"\n[Turn {turn}] User: {query}")
        
        # Process query with conversation history management
        result = await session_service.process_query_with_conversation(
            session_id=SESSION_ID,
            query=query,
            app_name=APP_NAME,
            user_id=USER_ID,
        )
        
        # Show session state
        if result['is_new_session']:
            print(f"  ✓ New session created")
        else:
            print(f"  ✓ Session retrieved (conversation history available)")
        
        print(f"  Total messages in history: {result['total_messages']}")
        
        # Record user query as an event
        await session_service.append_event(
            session_id=SESSION_ID,
            event_type="user_query",
            content={
                "query": query,
                "turn": turn,
            }
        )
        
        # Simulate agent response
        if "Kenya" in query:
            response = "🇰🇪 The capital of Kenya is Nairobi."
        elif "Italy" in query:
            response = "🇮🇹 The capital of Italy is Rome."
        elif "countries" in query.lower():
            response = "📍 You've asked about Kenya and Italy."
        else:
            response = "📚 The capitals are: Nairobi (Kenya) and Rome (Italy)."
        
        print(f"[Turn {turn}] Agent: {response}")
        
        # Record agent response as an event
        await session_service.append_event(
            session_id=SESSION_ID,
            event_type="agent_response",
            content={
                "response": response,
                "turn": turn,
            }
        )
    
    # Retrieve complete session summary
    print("\n" + "=" * 70)
    print("Session Summary and History")
    print("=" * 70)
    
    summary = await session_service.get_session_summary(SESSION_ID)
    
    print(f"\n📊 Session Statistics:")
    print(f"   Session ID: {summary['session_id']}")
    print(f"   Total Events: {summary['total_events']}")
    print(f"   Conversation Messages: {summary['total_messages']}")
    print(f"   Last Activity: {summary['last_activity']}")
    
    # Display full conversation
    print(f"\n💬 Full Conversation History:")
    print("-" * 70)
    for msg in summary['conversation_history']:
        timestamp = msg['timestamp'].split('T')[1].split('.')[0]  # Extract HH:MM:SS
        if msg['event_type'] == 'user_query':
            print(f"[{timestamp}] User: {msg['content']['query']}")
        elif msg['event_type'] == 'agent_response':
            print(f"[{timestamp}] Agent: {msg['content']['response']}")
    
    # Test retrieval from existing session
    print("\n" + "=" * 70)
    print("Testing Existing Session Retrieval")
    print("=" * 70)
    
    # Same session ID - should retrieve existing session
    result2 = await session_service.process_query_with_conversation(
        session_id=SESSION_ID,
        query="Can you summarize everything?",
        app_name=APP_NAME,
        user_id=USER_ID,
    )
    
    print(f"\n✓ Existing session retrieved (is_new_session: {result2['is_new_session']})")
    print(f"✓ Previous conversation history preserved: {result2['total_messages']} messages")
    print(f"✓ New query added to history")
    
    # Test with a different session ID
    print("\n" + "=" * 70)
    print("Testing New Session (Different Session ID)")
    print("=" * 70)
    
    NEW_SESSION_ID = "session_weather"
    
    result3 = await session_service.process_query_with_conversation(
        session_id=NEW_SESSION_ID,
        query="What's the weather today?",
        app_name=APP_NAME,
        user_id=USER_ID,
    )
    
    print(f"\n✓ New session created: {result3['is_new_session']}")
    print(f"✓ Session ID: {result3['session_id']}")
    print(f"✓ Starting fresh with 1 message in history")
    
    # Record event for new session
    await session_service.append_event(
        session_id=NEW_SESSION_ID,
        event_type="user_query",
        content={"query": "What's the weather today?"}
    )
    
    # List all sessions for the user
    print("\n" + "=" * 70)
    print("User Sessions Overview")
    print("=" * 70)
    
    sessions = await session_service.list_sessions(APP_NAME, USER_ID)
    
    print(f"\n📋 Total Sessions: {len(sessions)}")
    for session in sessions:
        print(f"   • {session['session_id']}")
        print(f"     Created: {session['created_at']}")
        print(f"     Updated: {session['updated_at']}")
    
    # Get events for specific type
    print("\n" + "=" * 70)
    print("Event Tracking")
    print("=" * 70)
    
    user_queries = await session_service.get_events(
        SESSION_ID,
        event_type="user_query"
    )
    
    print(f"\n🔍 Total User Queries in Session: {len(user_queries)}")
    for event in user_queries:
        print(f"   • {event['content']['query']}")
    
    # Summary comparison
    print("\n" + "=" * 70)
    print("SQLiteSessionService vs Redis/S3 Implementation")
    print("=" * 70)
    print("""
    ✓ Both support multiple sessions (different session_ids)
    ✓ Both track conversation history across queries
    ✓ Both support event recording and retrieval
    ✓ Both retrieve previous context for existing sessions
    ✓ SQLite version uses persistent local database (agents_database.db)
    ✓ No need for Redis/S3 infrastructure (all-in-one solution)
    ✓ Perfect for local development and deployment
    """)
    
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    
    # Close connection
    session_service.close()


if __name__ == "__main__":
    asyncio.run(main())
