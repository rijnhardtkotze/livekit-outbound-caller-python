# Function Tools

This guide explains the function tools available to the OutboundCaller agent and how to create new ones.

## Overview

Function tools allow the AI agent to perform actions during a conversation. They are decorated Python methods that the LLM can call based on the conversation context.

## Available Tools

### transfer_call

Transfers the call to a human operator:

```python
@function_tool()
async def transfer_call(self, ctx: RunContext):
    """Transfer the call to a human agent, called after confirming with the user"""
    
    transfer_to = self.dial_info["transfer_to"]
    if not transfer_to:
        return "cannot transfer call"
    
    # Inform the user
    await ctx.session.generate_reply(
        instructions="let the user know you'll be transferring them"
    )
    
    # Perform the transfer
    await job_ctx.api.sip.transfer_sip_participant(
        api.TransferSIPParticipantRequest(
            room_name=job_ctx.room.name,
            participant_identity=self.participant.identity,
            transfer_to=f"tel:{transfer_to}",
        )
    )
```

**When used**: When the user requests to speak with a human.

### end_call

Gracefully ends the conversation:

```python
@function_tool()
async def end_call(self, ctx: RunContext):
    """Called when the user wants to end the call"""
    
    # Wait for current speech to finish
    current_speech = ctx.session.current_speech
    if current_speech:
        await current_speech.wait_for_playout()
    
    await self.hangup()
```

**When used**: When the user says goodbye or indicates they want to end the call.

### look_up_availability

Checks appointment availability:

```python
@function_tool()
async def look_up_availability(
    self,
    ctx: RunContext,
    date: str,
):
    """Called when the user asks about alternative appointment availability

    Args:
        date: The date of the appointment to check availability for
    """
    # Simulate API call delay
    await asyncio.sleep(3)
    return {
        "available_times": ["1pm", "2pm", "3pm"],
    }
```

**When used**: When the user asks about available appointment times.

### confirm_appointment

Confirms an appointment:

```python
@function_tool()
async def confirm_appointment(
    self,
    ctx: RunContext,
    date: str,
    time: str,
):
    """Called when the user confirms their appointment on a specific date.
    Use this tool only when they are certain about the date and time.

    Args:
        date: The date of the appointment
        time: The time of the appointment
    """
    return "reservation confirmed"
```

**When used**: When the user confirms they want to book an appointment.

### detected_answering_machine

Handles voicemail detection:

```python
@function_tool()
async def detected_answering_machine(self, ctx: RunContext):
    """Called when the call reaches voicemail. Use this tool AFTER you hear the voicemail greeting"""
    await self.hangup()
```

**When used**: When the agent detects a voicemail greeting instead of a live person.

## Creating New Tools

### Basic Structure

```python
@function_tool()
async def my_new_tool(
    self,
    ctx: RunContext,
    param1: str,
    param2: int,
):
    """Clear description of what this tool does.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter
    """
    # Implementation
    result = await some_operation(param1, param2)
    return result
```

### Best Practices

1. **Clear Docstrings**: The docstring is used by the LLM to understand when to use the tool

2. **Type Hints**: Always include type hints for parameters

3. **Async Functions**: All tools should be async

4. **Error Handling**: Handle errors gracefully

```python
@function_tool()
async def check_patient_records(
    self,
    ctx: RunContext,
    patient_id: str,
):
    """Look up patient records in the system.
    
    Args:
        patient_id: The unique identifier for the patient
    """
    try:
        records = await database.get_patient(patient_id)
        return {"status": "found", "records": records}
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return {"status": "error", "message": "Unable to retrieve records"}
```

### Parameter Types

Supported parameter types:

- `str`: Text input
- `int`: Integer numbers
- `float`: Decimal numbers
- `bool`: True/False values
- `list`: Arrays
- `dict`: Objects

### Returning Results

Tools can return:

- **Strings**: Simple text responses
- **Dictionaries**: Structured data
- **None**: No return value needed

```python
# String return
return "appointment confirmed"

# Dictionary return
return {
    "status": "success",
    "appointment_id": "12345",
    "date": "2024-01-15",
    "time": "3pm"
}

# No return
await self.hangup()
# Implicitly returns None
```

## Tool Context

The `RunContext` provides access to:

```python
ctx.session          # The AgentSession
ctx.session.generate_reply(instructions="...")  # Generate a specific reply
ctx.session.current_speech  # Currently playing speech
```

## Example: Custom Tool

Here's an example of a custom tool for checking insurance:

```python
@function_tool()
async def verify_insurance(
    self,
    ctx: RunContext,
    insurance_id: str,
    provider: str,
):
    """Verify the patient's insurance coverage.
    
    Args:
        insurance_id: The patient's insurance ID number
        provider: The name of the insurance provider
    """
    logger.info(f"Verifying insurance {insurance_id} with {provider}")
    
    # Call external insurance verification API
    try:
        result = await insurance_api.verify(
            id=insurance_id,
            provider=provider
        )
        return {
            "verified": result.is_valid,
            "coverage": result.coverage_type,
            "copay": result.copay_amount
        }
    except Exception as e:
        logger.error(f"Insurance verification failed: {e}")
        return {
            "verified": False,
            "error": "Unable to verify insurance at this time"
        }
```

## Next Steps

- [Call Transfers](call-transfers.md): Deep dive into call transfer functionality
- [Voicemail Detection](voicemail-detection.md): Handle voicemail scenarios
- [API Reference](../api/agent.md): Complete API documentation
