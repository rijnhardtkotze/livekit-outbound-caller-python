# Best Practices for Using GitHub Copilot

This document provides guidance on effectively using GitHub Copilot when working with the LiveKit Outbound Caller Python project.

For comprehensive AI assistant guidance (including OpenCode, Claude Code, Gemini Code, and Codex), see [AGENTS.md](AGENTS.md).

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
├── mkdocs.yml            # Documentation configuration
├── COPILOT.md            # This file - GitHub Copilot guidance
├── AGENTS.md             # AI coding assistants guide
├── README.md             # Project documentation
└── docs/                 # Documentation site
    ├── index.md          # Documentation home
    ├── getting-started/  # Installation, configuration, quickstart
    ├── guides/           # Feature guides (calls, transfers, voicemail)
    ├── api/              # API reference (agent, entrypoint)
    └── contributing/     # Development and AI assistants guides
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

### Async/Await Patterns

This project is async-first. All I/O operations must be async:

```python
async def my_function():
    result = await some_async_operation()
    return result
```

### Type Hints

Always use type hints for function parameters and return types:

```python
from __future__ import annotations
from typing import Any

def process_data(data: dict[str, Any]) -> str:
    return str(data)
```

### Logging

Use the project's logging pattern:

```python
logger = logging.getLogger("outbound-caller")
logger.setLevel(logging.INFO)
logger.info(f"descriptive message with {context}")
```

### Function Tools

When creating new agent tools, follow this pattern:

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
    return result
```

## Key Classes and Functions

### OutboundCaller (Agent)

The main agent class that handles:
- Call initiation and management
- Tool functions for appointment scheduling
- Call transfers
- Voicemail detection

Important methods:
- `set_participant()`: Sets the remote participant reference
- `hangup()`: Ends the call by deleting the room
- `transfer_call()`: Transfers to a human operator
- `end_call()`: Gracefully ends the call
- `look_up_availability()`: Checks appointment availability
- `confirm_appointment()`: Confirms an appointment
- `detected_answering_machine()`: Handles voicemail detection

### entrypoint (Function)

The main entry point that:
1. Connects to the LiveKit room
2. Parses dial information from job metadata
3. Creates the OutboundCaller agent
4. Configures the AgentSession with STT/TTS/LLM
5. Initiates the SIP call

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
4. **Review generated code**: Always verify Copilot suggestions for security issues

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

## Documentation Resources

### Project Documentation

- [Getting Started - Installation](docs/getting-started/installation.md)
- [Getting Started - Configuration](docs/getting-started/configuration.md)
- [Getting Started - Quick Start](docs/getting-started/quickstart.md)
- [Guide - Making Calls](docs/guides/making-calls.md)
- [Guide - Function Tools](docs/guides/function-tools.md)
- [Guide - Call Transfers](docs/guides/call-transfers.md)
- [Guide - Voicemail Detection](docs/guides/voicemail-detection.md)
- [API - OutboundCaller Agent](docs/api/agent.md)
- [API - Entrypoint Function](docs/api/entrypoint.md)
- [Contributing - Development Guide](docs/contributing/development.md)
- [Contributing - AI Assistants Guide](docs/contributing/ai-assistants.md)

### External Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/overview/)
- [LiveKit SIP Documentation](https://docs.livekit.io/agents/start/telephony/)
- [LiveKit Agents Framework](https://github.com/livekit/agents)
- [LiveKit Python SDK](https://github.com/livekit/python-sdks)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)

## Commands Reference

| Command | Description |
|---------|-------------|
| `python agent.py dev` | Run agent in development mode |
| `python agent.py download-files` | Download required model files |
| `lk dispatch create --new-room --agent-name outbound-caller --metadata '{...}'` | Dispatch a call |
| `mkdocs serve` | Serve documentation locally |
| `mkdocs build` | Build documentation site |
