# Installation

This guide walks you through setting up the LiveKit Outbound Caller Python project.

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.10+**: The project requires Python 3.10 or higher
- **Git**: For cloning the repository
- **LiveKit Account**: With a SIP outbound trunk configured
- **API Keys**: OpenAI (required), Deepgram (optional), Cartesia (optional)

## Clone the Repository

```bash
git clone https://github.com/livekit-examples/outbound-caller-python.git
cd outbound-caller-python
```

## Create Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

=== "Linux/macOS"

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

=== "Windows"

    ```powershell
    python3 -m venv venv
    venv\Scripts\Activate.ps1
    ```

## Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

This will install:

- `livekit`: Core LiveKit SDK
- `livekit-agents`: Agent framework with plugins
- `livekit-plugins-noise-cancellation`: Krisp noise cancellation
- `python-dotenv`: Environment variable loading

## Download Required Files

Some plugins require additional model files. Download them with:

```bash
python agent.py download-files
```

## Install LiveKit CLI (Optional)

The LiveKit CLI (`lk`) is useful for dispatching calls and debugging:

=== "macOS"

    ```bash
    brew install livekit-cli
    ```

=== "Linux"

    ```bash
    curl -sSL https://get.livekit.io/cli | bash
    ```

=== "Windows"

    Download from [LiveKit CLI Releases](https://github.com/livekit/livekit-cli/releases)

## Verify Installation

Check that everything is installed correctly:

```bash
python -c "import livekit; print(livekit.__version__)"
```

## Next Steps

Now that you have the project installed, proceed to:

- [Configuration](configuration.md): Set up your environment variables
- [Quick Start](quickstart.md): Make your first outbound call
