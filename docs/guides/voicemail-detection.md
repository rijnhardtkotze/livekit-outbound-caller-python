# Voicemail Detection

This guide explains how the OutboundCaller agent detects and handles voicemail scenarios.

## Overview

When making outbound calls, the agent may encounter voicemail instead of a live person. The agent is equipped to:

- Detect voicemail greetings
- Handle the call appropriately
- Avoid leaving incomplete or confusing messages

## How It Works

### Detection Method

The agent uses AI-based detection through its conversation context. When the agent hears a voicemail greeting (e.g., "You've reached the voicemail of..."), it recognizes the pattern and calls the `detected_answering_machine` tool.

### The Detection Tool

```python
@function_tool()
async def detected_answering_machine(self, ctx: RunContext):
    """Called when the call reaches voicemail. Use this tool AFTER you hear the voicemail greeting"""
    logger.info(f"detected answering machine for {self.participant.identity}")
    await self.hangup()
```

## Agent Instructions

The agent's instructions guide voicemail handling:

```python
self.instructions = f"""
You are a scheduling assistant for a dental practice...

Note: If you detect that you've reached voicemail (you hear a voicemail greeting), 
use the detected_answering_machine tool to end the call appropriately.
"""
```

## Detection Patterns

The agent recognizes common voicemail patterns:

- "You've reached the voicemail of..."
- "Please leave a message after the beep..."
- "The person you are calling is not available..."
- "Hi, you've reached [name]. I can't come to the phone right now..."
- Standard carrier voicemail prompts

## Customizing Behavior

### Leave a Message

Instead of hanging up, you could leave a message:

```python
@function_tool()
async def detected_answering_machine(self, ctx: RunContext):
    """Called when the call reaches voicemail."""
    
    logger.info(f"Voicemail detected for {self.participant.identity}")
    
    # Leave a brief message
    await ctx.session.generate_reply(
        instructions="""
        Leave a brief, professional voicemail message:
        - Introduce yourself as calling from Dr. Smith's Dental Practice
        - Mention you're calling about their upcoming appointment
        - Ask them to call back at the office number
        - Keep it under 30 seconds
        """
    )
    
    # Wait for the message to finish
    if ctx.session.current_speech:
        await ctx.session.current_speech.wait_for_playout()
    
    await self.hangup()
```

### Schedule Retry

Schedule a retry call instead:

```python
@function_tool()
async def detected_answering_machine(self, ctx: RunContext):
    """Called when the call reaches voicemail."""
    
    logger.info(f"Voicemail detected, scheduling retry for {self.participant.identity}")
    
    # Schedule a retry (implement your retry logic)
    await schedule_retry_call(
        phone_number=self.dial_info["phone_number"],
        retry_after_minutes=60,
        max_retries=3
    )
    
    await self.hangup()
```

### Track Voicemail Stats

Log voicemail for analytics:

```python
@function_tool()
async def detected_answering_machine(self, ctx: RunContext):
    """Called when the call reaches voicemail."""
    
    # Log for analytics
    await analytics.track_event(
        event="voicemail_detected",
        properties={
            "phone_number": self.dial_info["phone_number"],
            "timestamp": datetime.now().isoformat(),
            "call_duration": ctx.session.duration
        }
    )
    
    await self.hangup()
```

## Best Practices

### 1. Quick Detection

Detect voicemail quickly to avoid wasting resources:

```python
# The tool should be called as soon as voicemail is detected
# Don't wait for the entire greeting to play
```

### 2. Graceful Handling

Handle the transition smoothly:

```python
@function_tool()
async def detected_answering_machine(self, ctx: RunContext):
    """Called when the call reaches voicemail."""
    
    # Stop any current speech
    if ctx.session.current_speech:
        ctx.session.current_speech.cancel()
    
    # Clean up resources
    await self.hangup()
```

### 3. Logging

Always log voicemail detection:

```python
logger.info(
    f"Voicemail detected | "
    f"phone: {self.participant.identity} | "
    f"time: {datetime.now().isoformat()}"
)
```

## SIP-Level Detection

For more robust detection, you can also use SIP-level signals. Some SIP providers include answering machine detection (AMD):

```python
await ctx.api.sip.create_sip_participant(
    api.CreateSIPParticipantRequest(
        room_name=ctx.room.name,
        sip_trunk_id=outbound_trunk_id,
        sip_call_to=phone_number,
        participant_identity=participant_identity,
        wait_until_answered=True,
        # Some providers support AMD headers
        headers={"X-AMD-Enable": "true"}
    )
)
```

!!! note "Provider Support"
    SIP-level AMD depends on your telephony provider's capabilities. Check with your provider for available options.

## Handling Edge Cases

### Voicemail vs. IVR

Sometimes you might reach an IVR (Interactive Voice Response) system instead of voicemail:

```python
@function_tool()
async def detected_ivr_system(self, ctx: RunContext):
    """Called when the call reaches an IVR system instead of a person."""
    
    logger.info(f"IVR system detected for {self.participant.identity}")
    
    # You might want to navigate the IVR or hang up
    await self.hangup()
```

### Partial Voicemail

If the agent starts speaking before detecting voicemail:

```python
@function_tool()
async def detected_answering_machine(self, ctx: RunContext):
    """Called when the call reaches voicemail."""
    
    # Cancel any ongoing speech
    if ctx.session.current_speech:
        ctx.session.current_speech.cancel()
    
    # Brief pause before hanging up
    await asyncio.sleep(0.5)
    
    await self.hangup()
```

## Troubleshooting

### False Positives

If the agent incorrectly detects voicemail:

- Review the conversation logs
- Adjust the agent's instructions to be more specific
- Consider adding confirmation logic

### Missed Voicemail

If voicemail isn't being detected:

- Ensure the agent instructions mention voicemail detection
- Check that the tool is properly decorated
- Review logs for any errors

## Next Steps

- [Making Calls](making-calls.md): Learn about the complete calling workflow
- [Function Tools](function-tools.md): Create custom detection tools
- [API Reference](../api/agent.md): Complete API documentation
