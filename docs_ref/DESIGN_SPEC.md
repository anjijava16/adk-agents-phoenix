# DESIGN_SPEC.md - ADK Agents Phoenix

## Overview

ADK Agents Phoenix is a multi-package framework for building, scaling, and observing AI agents using Google's Agent Development Kit (ADK). The project provides:

1. **Modular architecture** - Separate packages for agents, tools, models, configuration, logging, and tracing
2. **Phoenix tracing integration** - Full OpenTelemetry instrumentation with Phoenix for distributed tracing
3. **Multi-model support** - Unified factory for OpenAI, Anthropic, and Google LLMs
4. **Production-ready logging** - Structured logging with configurable levels
5. **Extensible tools system** - Easy-to-add tool modules with automatic registration

## Example Use Cases

### 1. Weather Information Retrieval
User: "What is the weather in New York?"
Agent: Uses `get_weather` tool → Phoenix traces the tool call → Returns weather report

### 2. Multi-Model Comparison
Run the same query through different models to compare responses:
```python
for model in ["gpt-4o", "claude-3-opus-20240229"]:
    agent = create_agent("comparison_agent", model_name=model)
    # Compare outputs in Phoenix dashboard
```

### 3. Tool Chain Execution
Agent chains multiple tools together while Phoenix traces each step:
- Tool 1: Get weather → Tool 2: Format report → Tool 3: Send notification

## Tools Required

### Current Tools
- **get_weather** - Retrieves weather information for a city
  - Input: city name (string)
  - Output: JSON with status and report/error
  - API: Mock (local implementation)

### Future Tools
- Search engine integration (Google Custom Search)
- Database queries (SQL, Vector databases)
- External API calls (REST, GraphQL)
- Email/notification services

## Constraints & Safety Rules

1. **Tool Safety**
   - All tool calls must be logged
   - Tool execution must include error handling
   - Tools must timeout gracefully (no infinite loops)

2. **Model Constraints**
   - Agent must use only registered tools
   - Agent cannot modify system settings at runtime
   - Model responses are rate-limited per session

3. **Data Privacy**
   - No sensitive data in logs (PII filtering)
   - Phoenix traces do not contain raw user data
   - Session data persists only in-memory (unless explicitly enabled)

4. **Tracing**
   - Phoenix endpoint must be reachable (graceful fallback if not)
   - Tracing should add <10% overhead
   - All tool calls and model invocations are traced

## Success Criteria

### Functional Requirements
- ✅ Agent successfully calls tools
- ✅ Multiple tools can be registered and executed
- ✅ Agent uses different LLM models
- ✅ All operations are traced to Phoenix
- ✅ Logging captures relevant events

### Quality Thresholds
- Tool success rate: >95%
- Phoenix tracing latency: <100ms overhead per call
- No memory leaks with repeated agent runs
- Log messages are properly structured and useful

### Non-Functional Requirements
- Code is modular and testable
- Configuration is environment-driven
- New tools can be added without modifying core agent code
- Framework works with Python 3.13+

## Edge Cases to Handle

1. **Tool Execution Failure**
   - Phoenix endpoint unreachable → Fall back to in-memory logging
   - Model API error → Use fallback model
   - Tool timeout → Return error response gracefully

2. **Configuration Issues**
   - Missing environment variables → Use sensible defaults
   - Invalid model name → Raise clear error message
   - Malformed Phoenix endpoint → Disable tracing and warn

3. **Session Management**
   - Concurrent requests to same session → Queue or error handling
   - Session timeout → Cleanup and create new session
   - Memory pressure → Implement session eviction

4. **Model Fallback**
   - Primary model unavailable → Switch to fallback model
   - Rate limits exceeded → Queue requests or error

## Architecture Decisions

### Package Structure
- **agents/** - Agent definitions (decoupled from tools)
- **tools/** - Individual tool implementations (tool_name.py per tool)
- **models/** - Model factory (supports multiple providers)
- **config/** - Environment-driven configuration
- **logging/** - Structured logging
- **tracing/** - Phoenix OpenTelemetry integration

### Why This Structure?
1. **Scalability** - Add tools without touching agent code
2. **Testability** - Each package can be tested independently
3. **Reusability** - Share tools across multiple agents
4. **Maintainability** - Clear separation of concerns
5. **Observability** - Structured logging + Phoenix tracing

### Technology Choices
- **Google ADK** - Official agent framework for Google Cloud
- **LiteLLM** - Unified interface for multiple LLM providers
- **OpenTelemetry** - Standard for observability instrumentation
- **Phoenix** - LLM observability platform (traces, evals, monitoring)

## Implementation Phases

### Phase 1: Foundation ✅
- Modular package structure
- Configuration management
- Logging infrastructure
- Phoenix tracing integration
- Single agent with weather tool

### Phase 2: Expansion (Future)
- Multiple agents
- More tools (search, database, APIs)
- Test suite
- CI/CD pipeline

### Phase 3: Production (Future)
- Cloud deployment (Cloud Run, GKE)
- Persistent session storage
- Authentication/authorization
- Analytics dashboard

## Evaluation Strategy

### Manual Testing
1. Run agent with different queries
2. Verify tool execution via logs
3. Inspect Phoenix dashboard for traces
4. Test model fallback scenarios

### Automated Testing
1. Unit tests for each tool
2. Agent instruction tests
3. Tool registration tests
4. Configuration loading tests

### Observability
1. Phoenix UI shows all traces
2. Logs capture all agent decisions
3. Metrics: success rate, latency, tool usage
