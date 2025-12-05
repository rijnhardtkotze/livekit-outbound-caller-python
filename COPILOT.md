# Best Practices for Using GitHub Copilot

This document provides guidance on effectively using GitHub Copilot when working with the LiveKit Outbound Caller Python project.

## Project Overview

This project is a Python-based outbound call agent using the LiveKit Agents Framework. It demonstrates:

- Making outbound SIP calls
- Voicemail detection
- Function calling for appointment scheduling
- Call transfers to human operators
- Background noise cancellation with Krisp

## Code Structure

When prompting Copilot, keep these structural elements in mind:

- **`agent.py`**: Main entry point containing the `OutboundCaller` agent class and entrypoint function
- **Environment variables**: Loaded from `.env.local` (see `.env.example` for required keys)
- **Dependencies**: Listed in `requirements.txt`

## Best Practices

### 1. Provide Context About LiveKit

When generating code, include context about LiveKit's agent framework:

```python
# Using LiveKit Agents Framework
# Agent class extends livekit.agents.Agent
# Function tools use @function_tool() decorator
```

### 2. Use Type Hints

This project uses Python type hints. When prompting Copilot:

- Always specify parameter types and return types
- Use `from __future__ import annotations` for forward references
- Reference existing patterns like `RunContext` for function tools

### 3. Async/Await Patterns

This project is async-first. Ensure Copilot-generated code:

- Uses `async def` for functions that perform I/O
- Properly awaits coroutines
- Uses `asyncio.create_task()` for concurrent operations

### 4. Function Tool Conventions

When creating new function tools:

```python
@function_tool()
async def my_tool(
    self,
    ctx: RunContext,
    param: str,
):
    """Clear description of what the tool does
    
    Args:
        param: Description of the parameter
    """
    # Implementation
```

### 5. Logging

Use the project's logging pattern:

```python
logger = logging.getLogger("outbound-caller")
logger.info(f"descriptive message with {context}")
```

### 6. Error Handling

Follow the existing error handling patterns:

```python
try:
    await some_api_call()
except api.TwirpError as e:
    logger.error(f"error description: {e.message}")
    # Handle gracefully
```

## Prompting Tips

### Adding New Features

When asking Copilot to add features, be specific about:

1. The LiveKit API being used
2. Whether it involves SIP, room management, or agent behavior
3. The async nature of the operation

### Example Prompts

**Good prompt:**
> "Add a function tool that checks if a phone number is in a do-not-call list before dialing, following the existing @function_tool pattern with proper type hints and RunContext"

**Less effective prompt:**
> "Check phone number before calling"

### Referencing Documentation

Point Copilot to relevant documentation:

- [LiveKit Agents Docs](https://docs.livekit.io/agents/overview/)
- [LiveKit SIP Documentation](https://docs.livekit.io/agents/start/telephony/)

## Security Considerations

When using Copilot with this project:

1. **Never commit API keys**: Ensure generated code uses environment variables
2. **Validate phone numbers**: Sanitize inputs before making SIP calls
3. **Handle sensitive data**: Patient information should be logged carefully
4. **Review generated code**: Always verify Copilot suggestions for security issues

## Testing Generated Code

Before merging Copilot-generated code:

1. Run the agent locally with `python agent.py dev`
2. Test with the `lk dispatch create` command (see README.md for full example with required parameters)
3. Verify SIP call behavior
4. Check logs for errors

## Common Patterns to Follow

### Room Management

```python
job_ctx = get_job_context()
await job_ctx.api.room.delete_room(
    api.DeleteRoomRequest(room=job_ctx.room.name)
)
```

### SIP Operations

```python
await ctx.api.sip.create_sip_participant(
    api.CreateSIPParticipantRequest(
        room_name=ctx.room.name,
        sip_trunk_id=outbound_trunk_id,
        sip_call_to=phone_number,
        participant_identity=participant_identity,
        wait_until_answered=True,
    )
)
```

### Agent Session Configuration

```python
session = AgentSession(
    turn_detection=EnglishModel(),
    vad=silero.VAD.load(),
    stt=deepgram.STT(),
    tts=cartesia.TTS(),
    llm=openai.LLM(model="gpt-4o"),
)
```

## Resources

- [LiveKit Agents Framework](https://github.com/livekit/agents)
- [LiveKit Python SDK](https://github.com/livekit/python-sdks)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
