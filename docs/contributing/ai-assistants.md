# AI Assistants Guide

This guide provides information for AI coding assistants working with the LiveKit Outbound Caller project.

## Overview

This document is intended for AI assistants including:

- GitHub Copilot
- OpenCode
- Claude Code
- Gemini Code
- Codex
- Other AI coding tools

For detailed instructions, see the [AGENTS.md](../../AGENTS.md) file in the repository root.

## Project Summary

| Aspect | Details |
|--------|---------|
| Language | Python 3.10+ |
| Framework | LiveKit Agents |
| Type | Outbound calling agent |
| Main File | `agent.py` |

## Key Patterns

### Async/Await

All I/O operations must be async:

```python
async def my_function():
    result = await some_operation()
    return result
```

### Type Hints

Always use type hints:

```python
from typing import Any

def process(data: dict[str, Any]) -> str:
    return str(data)
```

### Function Tools

```python
@function_tool()
async def my_tool(
    self,
    ctx: RunContext,
    param: str,
):
    """Clear description.
    
    Args:
        param: Parameter description
    """
    return result
```

### Logging

```python
logger = logging.getLogger("outbound-caller")
logger.info(f"message with {context}")
```

## Quick Reference

### Start Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python agent.py download-files
python agent.py dev
```

### Make a Call

```bash
lk dispatch create \
  --new-room \
  --agent-name outbound-caller \
  --metadata '{"phone_number": "+1234567890", "transfer_to": "+9876543210"}'
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LIVEKIT_URL` | Yes | LiveKit server URL |
| `LIVEKIT_API_KEY` | Yes | API key |
| `LIVEKIT_API_SECRET` | Yes | API secret |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `SIP_OUTBOUND_TRUNK_ID` | Yes | SIP trunk ID |
| `DEEPGRAM_API_KEY` | No | For STT |
| `CARTESIA_API_KEY` | No | For TTS |

## Code Structure

### OutboundCaller Class

Main agent class with:

- `__init__`: Sets instructions and dial info
- `set_participant`: Sets remote participant reference
- `hangup`: Ends call by deleting room
- `transfer_call`: Transfers to human
- `end_call`: Gracefully ends call
- `look_up_availability`: Checks appointments
- `confirm_appointment`: Confirms booking
- `detected_answering_machine`: Handles voicemail

### entrypoint Function

Entry point that:

1. Connects to room
2. Parses metadata
3. Creates agent
4. Configures session
5. Initiates SIP call

## Common Tasks

### Add a New Tool

```python
@function_tool()
async def new_tool(
    self,
    ctx: RunContext,
    param: str,
):
    """Tool description.
    
    Args:
        param: Parameter description
    """
    # Implementation
    return result
```

### Handle Errors

```python
try:
    await operation()
except api.TwirpError as e:
    logger.error(f"Error: {e.message}")
    # Handle gracefully
```

### Room Operations

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

## Security Guidelines

1. Never commit API keys
2. Use environment variables
3. Validate phone numbers
4. Handle sensitive data carefully
5. Review all generated code

## Resources

- [AGENTS.md](../../AGENTS.md) - Detailed AI assistant guide
- [COPILOT.md](../../COPILOT.md) - GitHub Copilot specific guide
- [LiveKit Docs](https://docs.livekit.io/agents/overview/) - Official documentation
