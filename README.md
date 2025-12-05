<a href="https://livekit.io/">
  <img src="./.github/assets/livekit-mark.png" alt="LiveKit logo" width="100" height="100">
</a>

# Python Outbound Call Agent

<p>
  <a href="https://docs.livekit.io/agents/overview/">LiveKit Agents Docs</a>
  •
  <a href="https://livekit.io/cloud">LiveKit Cloud</a>
  •
  <a href="https://blog.livekit.io/">Blog</a>
</p>

This example demonstrates an full workflow of an AI agent that makes outbound calls. It uses LiveKit SIP and Python [Agents Framework](https://github.com/livekit/agents).

It can use a pipeline of STT, LLM, and TTS models, or a realtime speech-to-speech model. (such as ones from OpenAI and Gemini).

This example builds on concepts from the [Outbound Calls](https://docs.livekit.io/agents/start/telephony/#outbound-calls) section of the docs. Ensure that a SIP outbound trunk is configured before proceeding.

## Features

This example demonstrates the following features:

- Making outbound calls
- Detecting voicemail
- Looking up availability via function calling
- Transferring to a human operator
- Detecting intent to end the call
- Uses Krisp background voice cancellation to handle noisy environments
- **Web UI for dispatching calls** (via Cloudflare Workers)
- **Cloudflare Workers API** for serverless call dispatching

## Architecture

This project consists of two components:

1. **Python Agent** (`agent.py`) - The LiveKit agent that handles the actual phone calls. This runs as a persistent process that connects to LiveKit rooms and manages real-time audio/voice interactions.

2. **Cloudflare Worker** (`worker/`) - A serverless API and web UI for dispatching outbound calls. This provides:
   - A simple web interface for making calls
   - REST API endpoints for programmatic call dispatching
   - Runs on Cloudflare's edge network for low latency

## Dev Setup

### Python Agent Setup

Clone the repository and install dependencies to a virtual environment:

```shell
git clone https://github.com/livekit-examples/outbound-caller-python.git
cd outbound-caller-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python agent.py download-files
```

Set up the environment by copying `.env.example` to `.env.local` and filling in the required values:

- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`
- `SIP_OUTBOUND_TRUNK_ID`
- `DEEPGRAM_API_KEY` - optional, only needed when using pipelined models
- `CARTESIA_API_KEY` - optional, only needed when using pipelined models

Run the agent:

```shell
python3 agent.py dev
```

Now, your worker is running, and waiting for dispatches in order to make outbound calls.

### Cloudflare Worker Setup

The Cloudflare Worker provides a web UI and API for dispatching calls.

```shell
cd worker
npm install
```

Copy `.dev.vars.example` to `.dev.vars` and fill in your LiveKit credentials:

```shell
cp .dev.vars.example .dev.vars
```

Run the worker locally:

```shell
npm run dev
```

Open http://localhost:8787 in your browser to access the web UI.

#### Deploying to Cloudflare

1. Create a Cloudflare account at https://dash.cloudflare.com
2. Set up your environment variables in the Cloudflare dashboard under Workers > Settings > Variables
3. Deploy:

```shell
npm run deploy
```

## Making Calls

### Option 1: Web UI (Cloudflare Worker)

1. Open the Cloudflare Worker URL (local: http://localhost:8787, or your deployed URL)
2. Enter the phone number to call
3. Optionally enter a transfer number for human handoff
4. Click "Make Call"

### Option 2: REST API

POST to the `/api/dispatch` endpoint:

```shell
curl -X POST http://localhost:8787/api/dispatch \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+1234567890", "transferTo": "+9876543210"}'
```

### Option 3: LiveKit CLI

You can dispatch an agent to make a call by using the `lk` CLI:

```shell
lk dispatch create \
  --new-room \
  --agent-name outbound-caller \
  --metadata '{"phone_number": "+1234567890", "transfer_to": "+9876543210"}'
```

## API Endpoints

The Cloudflare Worker exposes the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/dispatch` | POST | Dispatch an outbound call |
| `/api/dispatch/:roomName` | GET | List dispatches for a room |
| `/api/rooms` | GET | List active rooms/calls |
