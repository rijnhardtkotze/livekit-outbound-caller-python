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
- **Cloudflare Compute Cloud integration** - Use Cloudflare Workers AI for LLM and AI Gateway for STT/TTS

## Dev Setup

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

### Making a call

You can dispatch an agent to make a call by using the `lk` CLI:

```shell
lk dispatch create \
  --new-room \
  --agent-name outbound-caller \
  --metadata '{"phone_number": "+1234567890", "transfer_to": "+9876543210"}'
```

## Cloudflare Compute Cloud Integration

This agent supports using [Cloudflare Compute Cloud](https://www.cloudflare.com/) services for AI inference, providing benefits such as:

- **Global edge deployment** - Lower latency by running inference closer to users
- **Cost optimization** - Cloudflare Workers AI offers competitive pricing for LLM inference
- **Unified management** - Manage all AI services through Cloudflare's dashboard
- **Enhanced security** - API keys are protected behind Cloudflare's infrastructure

### Enabling Cloudflare

To use Cloudflare services, add the following to your `.env.local`:

```shell
USE_CLOUDFLARE=true
CLOUDFLARE_ACCOUNT_ID=<your Cloudflare Account ID>
CLOUDFLARE_API_TOKEN=<your Cloudflare API Token>
CLOUDFLARE_AI_GATEWAY_ID=<your Cloudflare AI Gateway ID>  # Optional, for STT/TTS proxying
CLOUDFLARE_LLM_MODEL=@cf/meta/llama-3.1-8b-instruct  # Optional, defaults to Llama 3.1 8B
```

### What Gets Replaced

When `USE_CLOUDFLARE=true`:

| Component | Default | With Cloudflare |
|-----------|---------|-----------------|
| LLM | OpenAI GPT-4o | Cloudflare Workers AI (Llama 3.1 8B or configured model) |
| STT | Deepgram (direct) | Deepgram via Cloudflare AI Gateway |
| TTS | Cartesia (direct) | Cartesia via Cloudflare AI Gateway |

### Setting Up Cloudflare

1. **Create a Cloudflare account** at [cloudflare.com](https://www.cloudflare.com/)

2. **Get your Account ID**: Find it in the Cloudflare dashboard URL or in the Overview page

3. **Create an API Token**:
   - Go to **My Profile** → **API Tokens** → **Create Token**
   - Use the "Workers AI" template or create a custom token with:
     - `Workers AI:Read` and `Workers AI:Edit` permissions

4. **Set up AI Gateway** (optional, for STT/TTS proxying):
   - Go to **AI** → **AI Gateway** → **Create Gateway**
   - Note the Gateway ID for your configuration
   - Configure the gateway to allow Deepgram and Cartesia providers

### Available Cloudflare LLM Models

You can use any model available on [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/models/):

- `@cf/meta/llama-3.1-8b-instruct` (default)
- `@cf/meta/llama-3.1-70b-instruct`
- `@cf/mistral/mistral-7b-instruct-v0.1`
- `@cf/google/gemma-7b-it`
- And many more...
