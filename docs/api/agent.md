# OutboundCaller Agent

This page documents the `OutboundCaller` agent class and its methods.

## Class Overview

```python
class OutboundCaller(Agent):
    """AI agent for making outbound calls via LiveKit SIP.

    This agent handles dental practice appointment scheduling calls,
    including voicemail detection, call transfers, and appointment
    confirmation.

    Attributes:
        participant: Reference to the remote call participant.
            Set after the call is connected via set_participant().
        dial_info: Dictionary containing phone numbers and call metadata.
            Expected keys: 'phone_number', 'transfer_to' (optional).
        instructions: The agent's system prompt for conversation behavior.

    Example:
        >>> agent = OutboundCaller(
        ...     name="Jayden",
        ...     appointment_time="Tuesday at 3pm",
        ...     dial_info={"phone_number": "+1234567890", "transfer_to": "+0987654321"},
        ... )
        >>> agent.set_participant(participant)
    """

    participant: rtc.RemoteParticipant | None
    dial_info: dict[str, Any]
    instructions: str

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
            appointment_time: The scheduled appointment time string
                (e.g., "next Tuesday at 3pm").
            dial_info: Dictionary containing call configuration.
                Required keys:
                - 'phone_number': str - The number to dial in E.164 format.
                Optional keys:
                - 'transfer_to': str - Number for call transfers.

        Raises:
            KeyError: If 'phone_number' is missing from dial_info.
        """
        ...
```

The `OutboundCaller` class extends the LiveKit `Agent` class and implements a dental practice scheduling assistant.

## Constructor

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | The customer's name |
| `appointment_time` | `str` | The scheduled appointment time |
| `dial_info` | `dict[str, Any]` | Dial information including phone number and transfer destination |

### Example

```python
agent = OutboundCaller(
    name="Jayden",
    appointment_time="next Tuesday at 3pm",
    dial_info={
        "phone_number": "+1234567890",
        "transfer_to": "+9876543210"
    },
)
```

## Properties

### participant

```python
self.participant: rtc.RemoteParticipant | None
```

Reference to the remote participant (the person being called). Set after the call is connected.

### dial_info

```python
self.dial_info: dict[str, Any]
```

Dictionary containing dial information passed from the dispatch metadata.

### instructions

```python
self.instructions: str
```

The agent's system prompt, configured in the constructor.

## Methods

### set_participant

```python
def set_participant(self, participant: rtc.RemoteParticipant):
```

Sets the reference to the remote participant.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `participant` | `rtc.RemoteParticipant` | The connected remote participant |

**Example:**

```python
participant = await ctx.wait_for_participant(identity=participant_identity)
agent.set_participant(participant)
```

### hangup

```python
async def hangup(self):
```

Helper function to hang up the call by deleting the LiveKit room.

**Example:**

```python
await self.hangup()
```

**Implementation:**

```python
async def hangup(self):
    job_ctx = get_job_context()
    await job_ctx.api.room.delete_room(
        api.DeleteRoomRequest(
            room=job_ctx.room.name,
        )
    )
```

## Function Tools

### transfer_call

```python
@function_tool()
async def transfer_call(self, ctx: RunContext):
```

Transfers the call to a human agent.

**When Called:** After the user requests and confirms a transfer to a human operator.

**Behavior:**
1. Validates transfer number exists
2. Generates a reply to inform the user
3. Initiates SIP transfer
4. Handles errors gracefully

### end_call

```python
@function_tool()
async def end_call(self, ctx: RunContext):
```

Gracefully ends the call.

**When Called:** When the user indicates they want to end the conversation.

**Behavior:**
1. Waits for current speech to finish
2. Calls `hangup()` to delete the room

### look_up_availability

```python
@function_tool()
async def look_up_availability(
    self,
    ctx: RunContext,
    date: str,
):
```

Checks appointment availability for a given date.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `date` | `str` | The date to check availability for |

**Returns:** Dictionary with `available_times` list.

**Example Return:**

```python
{
    "available_times": ["1pm", "2pm", "3pm"],
}
```

### confirm_appointment

```python
@function_tool()
async def confirm_appointment(
    self,
    ctx: RunContext,
    date: str,
    time: str,
):
```

Confirms an appointment at a specific date and time.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `date` | `str` | The appointment date |
| `time` | `str` | The appointment time |

**Returns:** `"reservation confirmed"`

### detected_answering_machine

```python
@function_tool()
async def detected_answering_machine(self, ctx: RunContext):
```

Handles voicemail detection.

**When Called:** When the agent detects a voicemail greeting.

**Behavior:** Logs the detection and hangs up the call.

## Usage Example

```python
# Create the agent
agent = OutboundCaller(
    name="Jayden",
    appointment_time="next Tuesday at 3pm",
    dial_info=dial_info,
)

# Configure the session
session = AgentSession(
    turn_detection=EnglishModel(),
    vad=silero.VAD.load(),
    stt=deepgram.STT(),
    tts=cartesia.TTS(),
    llm=openai.LLM(model="gpt-4o"),
)

# Start the session
await session.start(
    agent=agent,
    room=ctx.room,
    room_input_options=RoomInputOptions(
        noise_cancellation=noise_cancellation.BVCTelephony(),
    ),
)

# Set participant after connection
participant = await ctx.wait_for_participant(identity=participant_identity)
agent.set_participant(participant)
```

## Extending the Agent

To add new functionality, create a subclass:

```python
class CustomCaller(OutboundCaller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @function_tool()
    async def my_custom_tool(self, ctx: RunContext, param: str):
        """Custom tool description.
        
        Args:
            param: Description of the parameter
        """
        # Custom implementation
        return result
```
