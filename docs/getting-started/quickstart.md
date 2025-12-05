# Quick Start

This guide will help you make your first outbound call with the LiveKit agent.

## Prerequisites

Before starting, ensure you have:

- Completed the [Installation](installation.md) steps
- Configured your [Environment Variables](configuration.md)
- A SIP outbound trunk configured in LiveKit

## Start the Agent

Run the agent in development mode:

```bash
python agent.py dev
```

You should see output similar to:

```
INFO - Connecting to LiveKit server...
INFO - Worker connected
INFO - Waiting for dispatch...
```

The agent is now running and waiting for dispatch commands.

## Make an Outbound Call

In a new terminal, use the LiveKit CLI to dispatch a call:

```bash
lk dispatch create \
  --new-room \
  --agent-name outbound-caller \
  --metadata '{"phone_number": "+1234567890", "transfer_to": "+9876543210"}'
```

Replace the phone numbers with:

- `phone_number`: The number you want to call
- `transfer_to`: The number for human operator transfers

## What Happens Next

1. **Room Created**: LiveKit creates a new room for the call
2. **Agent Starts**: The OutboundCaller agent initializes
3. **Call Initiated**: The SIP participant is created and dialing begins
4. **Connection**: When the recipient answers, the conversation begins
5. **Conversation**: The AI agent conducts the appointment confirmation call

## Sample Conversation

The agent is configured as a dental practice scheduling assistant. A typical conversation might look like:

> **Agent**: Hello, this is a call from Dr. Smith's Dental Practice. Am I speaking with Jayden?
>
> **User**: Yes, this is Jayden.
>
> **Agent**: Great! I'm calling to confirm your upcoming appointment scheduled for next Tuesday at 3pm. Would you like to confirm this appointment?
>
> **User**: Yes, that works for me.
>
> **Agent**: Perfect! Your appointment is confirmed for next Tuesday at 3pm. Is there anything else I can help you with?

## Available Commands

During the call, the agent can:

| Action | Description |
|--------|-------------|
| Confirm Appointment | Confirm the scheduled appointment |
| Look Up Availability | Check for alternative appointment times |
| Transfer Call | Transfer to a human operator |
| End Call | Gracefully end the conversation |

## Monitoring the Call

Watch the agent's terminal output for logs:

```
INFO - connecting to room my-room-123
INFO - participant joined: +1234567890
INFO - confirming appointment for +1234567890 on Tuesday at 3pm
```

## Ending the Call

The call ends when:

- The user says goodbye and the agent uses `end_call`
- The call is transferred to a human operator
- Voicemail is detected
- The user hangs up

## Troubleshooting

### Call Not Connecting

- Verify your `SIP_OUTBOUND_TRUNK_ID` is correct
- Check that the phone number format is valid (E.164 format recommended)
- Review LiveKit dashboard for SIP errors

### Agent Not Responding

- Ensure `OPENAI_API_KEY` is valid
- Check that model files are downloaded (`python agent.py download-files`)
- Verify all required environment variables are set

### Audio Quality Issues

The agent uses Krisp noise cancellation. If you experience issues:

- Check your microphone settings
- Ensure `livekit-plugins-noise-cancellation` is installed

## Next Steps

- [Making Calls](../guides/making-calls.md): Deep dive into the calling workflow
- [Function Tools](../guides/function-tools.md): Learn about available agent tools
- [Call Transfers](../guides/call-transfers.md): Configure call transfers
