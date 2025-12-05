# Entrypoint Function

This page documents the `entrypoint` function, which is the main entry point for the agent.

## Function Signature

```python
async def entrypoint(ctx: JobContext):
```

The entrypoint function is called when the agent is dispatched to a job.

## Parameters

### ctx: JobContext

The job context provided by the LiveKit Agents framework.

| Property | Type | Description |
|----------|------|-------------|
| `ctx.room` | `rtc.Room` | The LiveKit room |
| `ctx.job` | `Job` | The current job |
| `ctx.job.metadata` | `str` | JSON metadata from dispatch |
| `ctx.api` | `LiveKitAPI` | API client for LiveKit services |
| `ctx.api.sip` | `SIPService` | SIP-specific API |
| `ctx.api.room` | `RoomService` | Room management API |

## Implementation

### 1. Connect to Room

```python
logger.info(f"connecting to room {ctx.room.name}")
await ctx.connect()
```

Establishes connection to the LiveKit room.

### 2. Parse Dial Information

```python
dial_info = json.loads(ctx.job.metadata)
participant_identity = phone_number = dial_info["phone_number"]
```

Extracts the dial information from the job metadata:

| Field | Description |
|-------|-------------|
| `phone_number` | The number to call |
| `transfer_to` | Number for transfers |

### 3. Create Agent

```python
agent = OutboundCaller(
    name="Jayden",
    appointment_time="next Tuesday at 3pm",
    dial_info=dial_info,
)
```

Instantiates the OutboundCaller agent with customer details.

### 4. Configure Session

```python
session = AgentSession(
    turn_detection=EnglishModel(),
    vad=silero.VAD.load(),
    stt=deepgram.STT(),
    tts=cartesia.TTS(),
    llm=openai.LLM(model="gpt-4o"),
)
```

Configures the agent session with:

| Component | Provider | Description |
|-----------|----------|-------------|
| `turn_detection` | English Model | Detects conversation turns |
| `vad` | Silero | Voice activity detection |
| `stt` | Deepgram | Speech-to-text |
| `tts` | Cartesia | Text-to-speech |
| `llm` | OpenAI | Language model (GPT-4o) |

### 5. Start Session

```python
session_started = asyncio.create_task(
    session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVCTelephony(),
        ),
    )
)
```

Starts the session as a background task. Uses Krisp for noise cancellation.

### 6. Create SIP Participant

```python
try:
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

Initiates the SIP call. Blocks until the call is answered.

### 7. Wait for Participant

```python
await session_started
participant = await ctx.wait_for_participant(identity=participant_identity)
logger.info(f"participant joined: {participant.identity}")
agent.set_participant(participant)
```

Waits for the session to start and the participant to join.

### 8. Error Handling

```python
except api.TwirpError as e:
    logger.error(
        f"error creating SIP participant: {e.message}, "
        f"SIP status: {e.metadata.get('sip_status_code')} "
        f"{e.metadata.get('sip_status')}"
    )
    ctx.shutdown()
```

Handles SIP errors and shuts down gracefully.

## Alternative Configurations

### Realtime Model

Use OpenAI's speech-to-speech model:

```python
session = AgentSession(
    llm=openai.realtime.RealtimeModel()
)
```

### Without Noise Cancellation

```python
await session.start(
    agent=agent,
    room=ctx.room,
    # Omit room_input_options
)
```

### Custom Turn Detection

```python
from livekit.plugins.turn_detector import CustomModel

session = AgentSession(
    turn_detection=CustomModel(threshold=0.5),
    # ... other config
)
```

## Full Code Reference

```python
async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect()

    # Parse dial information
    dial_info = json.loads(ctx.job.metadata)
    participant_identity = phone_number = dial_info["phone_number"]

    # Create agent
    agent = OutboundCaller(
        name="Jayden",
        appointment_time="next Tuesday at 3pm",
        dial_info=dial_info,
    )

    # Configure session
    session = AgentSession(
        turn_detection=EnglishModel(),
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        tts=cartesia.TTS(),
        llm=openai.LLM(model="gpt-4o"),
    )

    # Start session
    session_started = asyncio.create_task(
        session.start(
            agent=agent,
            room=ctx.room,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVCTelephony(),
            ),
        )
    )

    # Initiate call
    try:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=outbound_trunk_id,
                sip_call_to=phone_number,
                participant_identity=participant_identity,
                wait_until_answered=True,
            )
        )

        await session_started
        participant = await ctx.wait_for_participant(identity=participant_identity)
        logger.info(f"participant joined: {participant.identity}")
        agent.set_participant(participant)

    except api.TwirpError as e:
        logger.error(
            f"error creating SIP participant: {e.message}, "
            f"SIP status: {e.metadata.get('sip_status_code')} "
            f"{e.metadata.get('sip_status')}"
        )
        ctx.shutdown()
```

## CLI Integration

The entrypoint is registered with the CLI:

```python
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="outbound-caller",
        )
    )
```

This allows running the agent with:

```bash
python agent.py dev
```
