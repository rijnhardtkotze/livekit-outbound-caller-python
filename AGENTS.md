# AI Coding Agents Guide

This document provides comprehensive instructions for AI coding assistants (OpenCode, Claude Code, Gemini Code, Codex, and similar tools) working with the LiveKit Outbound Caller Python project.

## Project Overview

This is a Python-based AI agent that makes outbound SIP calls using the LiveKit Agents Framework. The agent can:

- Make outbound SIP calls
- Detect voicemail and handle accordingly
- Perform function calling for appointment scheduling
- Transfer calls to human operators
- Use Krisp for background noise cancellation

## Repository Structure

```
├── agent.py              # Main entry point with OutboundCaller agent class
├── requirements.txt      # Python dependencies
├── .env.example          # Template for environment variables
├── .env.local            # Local environment configuration (gitignored)
├── taskfile.yaml         # Task runner configuration
├── COPILOT.md            # GitHub Copilot specific guidance
├── AGENTS.md             # This file - AI agents guidance
├── README.md             # Project documentation
└── docs/                 # Documentation site
```

## Development Setup

### Prerequisites

- Python 3.10+
- A LiveKit account with SIP trunk configured
- API keys for: OpenAI, Deepgram (optional), Cartesia (optional)

### Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download required model files
python agent.py download-files

# Run the agent in development mode
python agent.py dev
```

### Environment Variables

Required environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `LIVEKIT_URL` | LiveKit server URL |
| `LIVEKIT_API_KEY` | LiveKit API key |
| `LIVEKIT_API_SECRET` | LiveKit API secret |
| `OPENAI_API_KEY` | OpenAI API key for LLM |
| `SIP_OUTBOUND_TRUNK_ID` | SIP outbound trunk identifier |
| `DEEPGRAM_API_KEY` | (Optional) For speech-to-text |
| `CARTESIA_API_KEY` | (Optional) For text-to-speech |

## Code Conventions

### Google Style Docstrings

Always use Google style docstrings for all functions, methods, and classes:

```python
def process_data(data: dict[str, Any], validate: bool = True) -> str:
    """Process and validate input data.

    Transforms the input dictionary into a string representation,
    optionally validating the data structure before processing.

    Args:
        data: The input dictionary containing data to process.
            Must contain at least a 'phone_number' key.
        validate: Whether to validate the data before processing.
            Defaults to True.

    Returns:
        A string representation of the processed data.

    Raises:
        ValueError: If data is empty or missing required keys.
        TypeError: If data is not a dictionary.

    Example:
        >>> result = process_data({"phone_number": "+1234567890"})
        >>> print(result)
        '+1234567890'
    """
    if validate and not data:
        raise ValueError("Data cannot be empty")
    return str(data)
```

### Type Hints

Always use comprehensive type hints for function parameters, return types, and class attributes:

```python
from __future__ import annotations
from typing import Any, Optional, Union
from collections.abc import Callable, Awaitable

def process_data(
    data: dict[str, Any],
    callback: Optional[Callable[[str], Awaitable[None]]] = None,
) -> str:
    """Process and validate input data.

    Args:
        data: The input dictionary containing data to process.
        callback: Optional async callback function to invoke after processing.

    Returns:
        A string representation of the processed data.
    """
    return str(data)


async def fetch_participant(
    room_name: str,
    identity: str,
    timeout: float = 30.0,
) -> Optional[rtc.RemoteParticipant]:
    """Fetch a participant from a room by identity.

    Args:
        room_name: The name of the LiveKit room.
        identity: The participant's unique identity.
        timeout: Maximum time to wait for the participant in seconds.

    Returns:
        The remote participant if found, None otherwise.
    """
    pass
```

### Pydantic Strongly Typed Models

Use Pydantic models for structured data validation and serialization:

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class DialInfo(BaseModel):
    """Information required to dial an outbound call.

    Attributes:
        phone_number: The phone number to dial in E.164 format.
        transfer_to: Optional phone number for call transfers.
        caller_name: Optional name of the person being called.
    """

    phone_number: str = Field(
        ...,
        description="Phone number in E.164 format (e.g., +1234567890)",
        pattern=r"^\+[1-9]\d{1,14}$",
    )
    transfer_to: Optional[str] = Field(
        default=None,
        description="Phone number for transfers in E.164 format",
        pattern=r"^\+[1-9]\d{1,14}$",
    )
    caller_name: Optional[str] = Field(
        default=None,
        description="Name of the person being called",
    )

    @field_validator("transfer_to")
    @classmethod
    def validate_transfer_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate optional transfer phone number format.

        Args:
            v: The phone number string to validate, or None.

        Returns:
            The validated phone number or None if not provided.

        Raises:
            ValueError: If provided and the phone number format is invalid.
        """
        if v is not None:
            e164_pattern = r"^\+[1-9]\d{1,14}$"
            if not re.match(e164_pattern, v):
                raise ValueError(
                    f"Phone number must be in E.164 format (e.g., +1234567890), got: {v}"
                )
        return v


class AppointmentSlot(BaseModel):
    """Represents an available appointment time slot.

    Attributes:
        date: The date of the appointment (YYYY-MM-DD format).
        time: The time of the appointment (HH:MM format).
        duration_minutes: Duration of the appointment in minutes.
        is_available: Whether the slot is currently available.
    """

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM format")
    duration_minutes: int = Field(default=30, ge=15, le=120)
    is_available: bool = Field(default=True)
```

### Async/Await Patterns

This project is async-first. All I/O operations must be async:

```python
async def my_function(room_name: str) -> dict[str, Any]:
    """Perform an async operation on a room.

    Args:
        room_name: The name of the LiveKit room.

    Returns:
        A dictionary containing the operation result.
    """
    result = await some_async_operation()
    return result
```

### Logging

Use the project's logging pattern:

```python
logger = logging.getLogger("outbound-caller")
logger.setLevel(logging.INFO)
logger.info(f"descriptive message with {context}")
```

### Function Tools

When creating new agent tools, follow this pattern with comprehensive docstrings and type hints:

```python
@function_tool()
async def my_tool(
    self,
    ctx: RunContext,
    phone_number: str,
    options: Optional[dict[str, Any]] = None,
) -> dict[str, Union[str, bool]]:
    """Perform an action on the given phone number.

    This tool is called by the agent when it needs to perform
    a specific action related to phone operations.

    Args:
        ctx: The run context containing session and agent state.
        phone_number: The target phone number in E.164 format.
        options: Optional dictionary of additional options.
            Supported keys:
            - 'validate': bool - Whether to validate the number (default: True)
            - 'timeout': int - Operation timeout in seconds (default: 30)

    Returns:
        A dictionary containing:
        - 'success': bool - Whether the operation succeeded
        - 'message': str - A human-readable result message
        - 'data': Optional[dict] - Additional result data

    Raises:
        ValueError: If the phone number format is invalid.

    Example:
        >>> result = await my_tool(ctx, "+1234567890", {"validate": True})
        >>> print(result["success"])
        True
    """
    # Implementation
    return {"success": True, "message": "Operation completed"}

## Key Classes and Functions

### OutboundCaller (Agent)

The main agent class that handles:
- Call initiation and management
- Tool functions for appointment scheduling
- Call transfers
- Voicemail detection

```python
class OutboundCaller(Agent):
    """AI agent for making outbound calls via LiveKit SIP.

    This agent handles dental practice appointment scheduling calls,
    including voicemail detection, call transfers, and appointment
    confirmation.

    Attributes:
        participant: Reference to the remote call participant.
        dial_info: Dictionary containing phone numbers and call metadata.

    Example:
        >>> agent = OutboundCaller(
        ...     name="Jayden",
        ...     appointment_time="Tuesday at 3pm",
        ...     dial_info={"phone_number": "+1234567890"},
        ... )
    """

    participant: rtc.RemoteParticipant | None
    dial_info: dict[str, Any]

    def __init__(
        self,
        *,
        name: str,
        appointment_time: str,
        dial_info: dict[str, Any],
    ) -> None:
        """Initialize the OutboundCaller agent.

        Args:
            name: The customer's name for personalized greeting.
            appointment_time: The scheduled appointment time string.
            dial_info: Dictionary with 'phone_number' and optional 'transfer_to'.
        """
        ...
```

Important methods with type signatures:

- `set_participant(participant: rtc.RemoteParticipant) -> None`: Sets the remote participant reference
- `async hangup() -> None`: Ends the call by deleting the room
- `async transfer_call(ctx: RunContext) -> str`: Transfers to a human operator
- `async end_call(ctx: RunContext) -> None`: Gracefully ends the call
- `async look_up_availability(ctx: RunContext, date: str) -> dict[str, list[str]]`: Checks appointment availability
- `async confirm_appointment(ctx: RunContext, date: str, time: str) -> str`: Confirms an appointment
- `async detected_answering_machine(ctx: RunContext) -> None`: Handles voicemail detection

### entrypoint (Function)

```python
async def entrypoint(ctx: JobContext) -> None:
    """Main entry point for the outbound caller agent.

    Orchestrates the complete outbound call flow from room connection
    through call initiation and participant management.

    Args:
        ctx: The job context containing room and API access.

    Raises:
        api.TwirpError: If SIP participant creation fails.

    Example:
        >>> cli.run_app(
        ...     WorkerOptions(
        ...         entrypoint_fnc=entrypoint,
        ...         agent_name="outbound-caller",
        ...     )
        ... )
    """
    ...
```

The main entry point that:
1. Connects to the LiveKit room
2. Parses dial information from job metadata
3. Creates the OutboundCaller agent
4. Configures the AgentSession with STT/TTS/LLM
5. Initiates the SIP call

## Common Patterns

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

## Error Handling

Follow the existing error handling patterns:

```python
try:
    await some_api_call()
except api.TwirpError as e:
    logger.error(f"error description: {e.message}")
    # Handle gracefully - don't crash the agent
```

## Testing Changes

1. Run the agent locally: `python agent.py dev`
2. Dispatch a test call using the LiveKit CLI:

```bash
lk dispatch create \
  --new-room \
  --agent-name outbound-caller \
  --metadata '{"phone_number": "+1234567890", "transfer_to": "+9876543210"}'
```

3. Monitor logs for errors
4. Verify SIP call behavior

## Security Considerations

1. **Never commit API keys**: Use environment variables
2. **Validate phone numbers**: Sanitize inputs before SIP calls
3. **Handle sensitive data carefully**: Be cautious with logging patient information
4. **Review generated code**: Always verify AI suggestions for security issues

## Adding New Features

When adding new functionality:

1. Determine if it's a new tool function or modification to existing logic
2. Follow the async pattern consistently
3. Add proper type hints
4. Include comprehensive docstrings
5. Update the agent's instructions if the new tool should be available
6. Test the feature end-to-end

## Dependencies

Key dependencies in `requirements.txt`:

- `livekit`: Core LiveKit SDK
- `livekit-agents`: Agent framework with plugins for OpenAI, Deepgram, Cartesia, Silero
- `livekit-plugins-noise-cancellation`: Krisp noise cancellation
- `python-dotenv`: Environment variable loading

## Useful Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/overview/)
- [LiveKit SIP Documentation](https://docs.livekit.io/agents/start/telephony/)
- [LiveKit Agents Framework](https://github.com/livekit/agents)
- [LiveKit Python SDK](https://github.com/livekit/python-sdks)

## Commands Reference

| Command | Description |
|---------|-------------|
| `python agent.py dev` | Run agent in development mode |
| `python agent.py download-files` | Download required model files |
| `lk dispatch create --new-room --agent-name outbound-caller --metadata '{...}'` | Dispatch a call |
