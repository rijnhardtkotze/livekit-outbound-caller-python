# Configuration

This guide explains how to configure the LiveKit Outbound Caller with the necessary credentials and settings.

## Environment Variables

The project uses environment variables for configuration. Copy the example file to create your local configuration:

```bash
cp .env.example .env.local
```

Then edit `.env.local` with your credentials.

## Required Variables

### LiveKit Credentials

| Variable | Description |
|----------|-------------|
| `LIVEKIT_URL` | Your LiveKit server URL (e.g., `wss://your-app.livekit.cloud`) |
| `LIVEKIT_API_KEY` | Your LiveKit API key |
| `LIVEKIT_API_SECRET` | Your LiveKit API secret |

!!! info "Getting LiveKit Credentials"
    You can obtain these from the [LiveKit Cloud Dashboard](https://cloud.livekit.io) or your self-hosted LiveKit server.

### SIP Configuration

| Variable | Description |
|----------|-------------|
| `SIP_OUTBOUND_TRUNK_ID` | The ID of your SIP outbound trunk |

!!! warning "SIP Trunk Required"
    You must have a SIP outbound trunk configured before making calls. See the [LiveKit SIP Documentation](https://docs.livekit.io/agents/start/telephony/) for setup instructions.

### AI Service Credentials

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o | Yes |
| `DEEPGRAM_API_KEY` | Deepgram API key for STT | Optional |
| `CARTESIA_API_KEY` | Cartesia API key for TTS | Optional |

!!! note "Optional Services"
    Deepgram and Cartesia are only needed when using the pipelined model approach. If using OpenAI's realtime speech-to-speech model, you only need the OpenAI API key.

## Example Configuration

Your `.env.local` file should look like this:

```bash
# LiveKit Credentials
LIVEKIT_URL=wss://your-app.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# SIP Configuration
SIP_OUTBOUND_TRUNK_ID=your-trunk-id

# AI Services
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key
```

## Agent Configuration

The agent behavior is configured in `agent.py`. Key configuration options:

### Agent Name

The agent name used for dispatching:

```python
cli.run_app(
    WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="outbound-caller",  # Change this to customize
    )
)
```

### Agent Instructions

The agent's system prompt is set in the `OutboundCaller` class:

```python
self.instructions = f"""
You are a scheduling assistant for a dental practice...
"""
```

### Model Configuration

The AI models are configured in the `entrypoint` function:

```python
session = AgentSession(
    turn_detection=EnglishModel(),
    vad=silero.VAD.load(),
    stt=deepgram.STT(),
    tts=cartesia.TTS(),
    llm=openai.LLM(model="gpt-4o"),
)
```

You can switch to OpenAI's realtime model:

```python
session = AgentSession(
    llm=openai.realtime.RealtimeModel()
)
```

## Validating Configuration

Run the agent in development mode to verify your configuration:

```bash
python agent.py dev
```

If successful, you should see:

```
INFO - Connecting to LiveKit server...
INFO - Worker connected
```

## Next Steps

- [Quick Start](quickstart.md): Make your first outbound call
- [Making Calls](../guides/making-calls.md): Learn more about the calling workflow
