# Development Guide

This guide explains how to set up a development environment and contribute to the LiveKit Outbound Caller project.

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- A code editor (VS Code recommended)

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/livekit-examples/outbound-caller-python.git
cd outbound-caller-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download model files
python agent.py download-files
```

### Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env.local
```

Fill in your credentials. For development, you'll need at minimum:

- LiveKit URL and credentials
- OpenAI API key
- SIP trunk ID (for making actual calls)

## Project Structure

```
├── agent.py              # Main application code
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── .env.local            # Local environment (gitignored)
├── taskfile.yaml         # Task runner configuration
├── mkdocs.yml            # Documentation configuration
├── docs/                 # Documentation source
├── AGENTS.md             # AI assistants guide
├── COPILOT.md            # GitHub Copilot guide
└── README.md             # Project overview
```

## Running the Agent

### Development Mode

```bash
python agent.py dev
```

This starts the agent in development mode with hot reloading.

### Production Mode

```bash
python agent.py start
```

## Testing Changes

### Manual Testing

1. Start the agent in development mode
2. Use the LiveKit CLI to dispatch a call:

```bash
lk dispatch create \
  --new-room \
  --agent-name outbound-caller \
  --metadata '{"phone_number": "+1234567890", "transfer_to": "+9876543210"}'
```

3. Monitor the logs for behavior
4. Test various conversation flows

### Test Without Making Calls

For development without making actual SIP calls, you can:

1. Use the LiveKit Playground to simulate participants
2. Mock the SIP participant creation
3. Use test phone numbers from your SIP provider

## Code Style

### Python Style

- Use type hints for all function parameters and returns
- Follow PEP 8 conventions
- Use async/await for all I/O operations
- Include docstrings for all public functions

### Example

```python
async def process_request(
    request: dict[str, Any],
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Process an incoming request.
    
    Args:
        request: The request data to process
        timeout: Maximum time to wait in seconds
        
    Returns:
        The processed response data
    """
    # Implementation
```

### Logging

Use the project's logger:

```python
logger = logging.getLogger("outbound-caller")
logger.info(f"Processing request for {user_id}")
```

## Adding New Features

### Adding a New Function Tool

1. Add the method to the `OutboundCaller` class
2. Decorate with `@function_tool()`
3. Include clear docstring
4. Add type hints

```python
@function_tool()
async def my_new_feature(
    self,
    ctx: RunContext,
    param: str,
):
    """Description of what this tool does.
    
    Args:
        param: Description of the parameter
    """
    # Implementation
    return result
```

### Modifying Agent Behavior

1. Update the agent instructions in `__init__`
2. Add or modify function tools
3. Test the new behavior end-to-end

## Documentation

### Building Docs

Install MkDocs and dependencies:

```bash
pip install mkdocs-material pymdown-extensions
```

Serve documentation locally:

```bash
mkdocs serve
```

Build for production:

```bash
mkdocs build
```

### Documentation Structure

- `docs/index.md` - Home page
- `docs/getting-started/` - Setup guides
- `docs/guides/` - Feature guides
- `docs/api/` - API reference
- `docs/contributing/` - Contribution guides

## Submitting Changes

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add insurance verification tool
fix: handle empty phone number gracefully
docs: update configuration guide
```

## Troubleshooting

### Common Issues

**Agent won't start:**
- Check environment variables are set
- Verify Python version is 3.10+
- Ensure dependencies are installed

**Calls not connecting:**
- Verify SIP trunk configuration
- Check phone number format (E.164)
- Review LiveKit dashboard for errors

**Audio quality issues:**
- Ensure noise cancellation plugin is installed
- Check network connectivity
- Verify microphone/speaker settings

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/overview/)
- [LiveKit SIP Documentation](https://docs.livekit.io/agents/start/telephony/)
- [Python SDK Reference](https://github.com/livekit/python-sdks)
