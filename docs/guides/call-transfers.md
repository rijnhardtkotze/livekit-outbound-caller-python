# Call Transfers

This guide explains how to configure and use call transfers to hand off conversations to human operators.

## Overview

The OutboundCaller agent can transfer calls to human operators when:

- The user explicitly requests to speak with a person
- The conversation requires human intervention
- Complex issues arise that the AI cannot handle

## Configuration

### Transfer Number

The transfer destination is specified in the dispatch metadata:

```bash
lk dispatch create \
  --new-room \
  --agent-name outbound-caller \
  --metadata '{"phone_number": "+1234567890", "transfer_to": "+9876543210"}'
```

The `transfer_to` field contains the phone number for the human operator.

### Accessing Transfer Info

The agent accesses the transfer number from `dial_info`:

```python
class OutboundCaller(Agent):
    def __init__(self, *, dial_info: dict[str, Any], ...):
        self.dial_info = dial_info
```

## Transfer Implementation

### The transfer_call Tool

```python
@function_tool()
async def transfer_call(self, ctx: RunContext):
    """Transfer the call to a human agent, called after confirming with the user"""
    
    transfer_to = self.dial_info["transfer_to"]
    if not transfer_to:
        return "cannot transfer call"
    
    logger.info(f"transferring call to {transfer_to}")
    
    # Let the user know about the transfer
    await ctx.session.generate_reply(
        instructions="let the user know you'll be transferring them"
    )
    
    job_ctx = get_job_context()
    try:
        await job_ctx.api.sip.transfer_sip_participant(
            api.TransferSIPParticipantRequest(
                room_name=job_ctx.room.name,
                participant_identity=self.participant.identity,
                transfer_to=f"tel:{transfer_to}",
            )
        )
        logger.info(f"transferred call to {transfer_to}")
    except Exception as e:
        logger.error(f"error transferring call: {e}")
        await ctx.session.generate_reply(
            instructions="there was an error transferring the call."
        )
        await self.hangup()
```

### Transfer Flow

1. **User Request**: User asks to speak with a human
2. **Confirmation**: Agent confirms the transfer with the user
3. **Notification**: Agent informs user they're being transferred
4. **SIP Transfer**: The SIP participant is transferred
5. **Handoff**: User is connected to the human operator

## SIP Transfer Request

The transfer uses LiveKit's SIP API:

```python
await job_ctx.api.sip.transfer_sip_participant(
    api.TransferSIPParticipantRequest(
        room_name=job_ctx.room.name,
        participant_identity=self.participant.identity,
        transfer_to=f"tel:{transfer_to}",
    )
)
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `room_name` | The current LiveKit room |
| `participant_identity` | Identity of the participant to transfer |
| `transfer_to` | Destination in `tel:+1234567890` format |

## Error Handling

Handle transfer failures gracefully:

```python
try:
    await job_ctx.api.sip.transfer_sip_participant(...)
except api.TwirpError as e:
    logger.error(f"Transfer failed: {e.message}")
    await ctx.session.generate_reply(
        instructions="there was an error transferring the call."
    )
    await self.hangup()
except Exception as e:
    logger.error(f"Unexpected error during transfer: {e}")
    await ctx.session.generate_reply(
        instructions="I apologize, but I'm unable to transfer your call at this time."
    )
```

## Customizing Transfer Behavior

### Pre-Transfer Actions

You can perform actions before the transfer:

```python
@function_tool()
async def transfer_call(self, ctx: RunContext):
    """Transfer the call to a human agent"""
    
    # Log the transfer reason
    await log_transfer_reason(
        participant=self.participant.identity,
        reason="user_requested"
    )
    
    # Gather conversation summary for the operator
    summary = await generate_conversation_summary(ctx.session)
    
    # Notify the operator (if your system supports it)
    await notify_operator(
        transfer_to=self.dial_info["transfer_to"],
        summary=summary
    )
    
    # Perform the transfer
    await ctx.session.generate_reply(
        instructions="let the user know you'll be transferring them"
    )
    
    # ... rest of transfer logic
```

### Conditional Transfers

Route to different operators based on context:

```python
@function_tool()
async def transfer_call(
    self,
    ctx: RunContext,
    department: str,
):
    """Transfer the call to the appropriate department.
    
    Args:
        department: The department to transfer to (billing, scheduling, medical)
    """
    
    transfer_numbers = {
        "billing": "+1111111111",
        "scheduling": "+2222222222",
        "medical": "+3333333333",
    }
    
    transfer_to = transfer_numbers.get(department)
    if not transfer_to:
        return f"Unknown department: {department}"
    
    # Perform transfer...
```

## Best Practices

### 1. Always Confirm

Confirm with the user before transferring:

```python
# In agent instructions:
"""
When the user would like to be transferred to a human agent, 
first confirm with them. Upon confirmation, use the transfer_call tool.
"""
```

### 2. Set Expectations

Inform users about potential wait times:

```python
await ctx.session.generate_reply(
    instructions="Let the user know they may experience a brief hold while being transferred"
)
```

### 3. Handle Failures Gracefully

Always have a fallback:

```python
except Exception as e:
    await ctx.session.generate_reply(
        instructions="Apologize and offer to have someone call them back"
    )
    # Log for follow-up
    await schedule_callback(self.dial_info["phone_number"])
```

### 4. Log Transfers

Track transfers for analytics:

```python
logger.info(f"Transfer initiated: {self.participant.identity} -> {transfer_to}")
```

## Troubleshooting

### Transfer Not Working

1. Verify `transfer_to` is in E.164 format (+1234567890)
2. Check SIP trunk supports transfers
3. Verify the destination number is valid

### User Disconnected

If the user disconnects during transfer:

- The transfer will fail
- Log the failure and handle cleanup
- Consider callback scheduling

### Operator Not Available

If the operator line is busy:

```python
except api.TwirpError as e:
    if "busy" in e.message.lower():
        await ctx.session.generate_reply(
            instructions="Our operators are currently busy. Offer to have them call back."
        )
```

## Next Steps

- [Voicemail Detection](voicemail-detection.md): Handle voicemail scenarios
- [API Reference](../api/agent.md): Complete API documentation
