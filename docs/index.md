# LiveKit Outbound Caller

Welcome to the documentation for the Python Outbound Call Agent using LiveKit.

## Overview

This project demonstrates a full workflow of an AI agent that makes outbound calls using LiveKit SIP and the Python [Agents Framework](https://github.com/livekit/agents).

The agent can use a pipeline of STT, LLM, and TTS models, or a realtime speech-to-speech model (such as ones from OpenAI and Gemini).

## Features

- **Making Outbound Calls**: Initiate SIP calls to phone numbers
- **Voicemail Detection**: Automatically detect and handle voicemail
- **Function Calling**: Look up availability and schedule appointments
- **Call Transfers**: Transfer calls to human operators when needed
- **Intent Detection**: Detect when the user wants to end the call
- **Noise Cancellation**: Uses Krisp for background voice and noise removal

## Quick Start

Get started quickly with these steps:

1. Clone the repository
2. Set up your environment variables
3. Install dependencies
4. Run the agent

See the [Installation Guide](getting-started/installation.md) for detailed instructions.

## Architecture

The agent is built on top of the LiveKit Agents Framework and uses:

- **LiveKit SIP**: For making and receiving phone calls
- **OpenAI GPT-4o**: For natural language understanding and generation
- **Deepgram**: For speech-to-text (STT)
- **Cartesia**: For text-to-speech (TTS)
- **Silero VAD**: For voice activity detection
- **Krisp**: For noise cancellation

## Project Structure

```
├── agent.py              # Main entry point with OutboundCaller agent
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── mkdocs.yml           # Documentation configuration
└── docs/                # Documentation source files
```

## Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher
- A LiveKit account with SIP trunk configured
- API keys for OpenAI (required), Deepgram (optional), and Cartesia (optional)

## Next Steps

- [Installation](getting-started/installation.md): Set up your development environment
- [Configuration](getting-started/configuration.md): Configure API keys and environment
- [Quick Start](getting-started/quickstart.md): Make your first outbound call
