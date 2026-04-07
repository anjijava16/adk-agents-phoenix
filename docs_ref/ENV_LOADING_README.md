"""
README: .env File Loading and Phoenix Configuration

This document explains how the application loads the .env file and how
Phoenix tracing is configured to use the arize_adk project.

## Problem (SOLVED)

Previously, when running `uv run main.py` or `python main.py`, environment
variables from .env were NOT being automatically loaded. This meant traces
would go to the default project instead of "arize_adk".

## Solution

The application now automatically loads the .env file using python-dotenv.
This happens when app.config is first imported, before any other code runs.

## How it Works

1. **python-dotenv dependency** - Added to pyproject.toml
2. **Automatic loading** - app/config/settings.py loads .env on import
3. **Environment variable priority** - Command-line vars override .env values
4. **No manual sourcing needed** - Just run: python main.py or uv run main.py

## Configuration Order (Highest Priority First)

1. Command-line environment variables
   Example: PHOENIX_PROJECT_NAME=custom_project python main.py

2. Values from .env file
   Example: PHOENIX_PROJECT_NAME=arize_adk in .env

3. Hardcoded defaults in code
   Example: default="arize_adk" in settings.py

## Files Modified

- pyproject.toml: Added python-dotenv dependency
- app/config/settings.py: Added .env loading on import
- main.py: Added debug logging of configuration
- README.md: Updated usage instructions
- Makefile: Added verify-phoenix command
- verify_phoenix_config.py: New verification script

## Testing

Run the verification script to confirm everything is working:

    python verify_phoenix_config.py

Expected output:
    ✅ All checks passed!
    Traces will be sent to Phoenix project: arize_adk

## Usage Examples

### Default (loads from .env)
    python main.py
    # Uses: PHOENIX_PROJECT_NAME=arize_adk

    uv run main.py
    # Uses: PHOENIX_PROJECT_NAME=arize_adk

### Override project name
    PHOENIX_PROJECT_NAME=custom_project python main.py
    # Uses: PHOENIX_PROJECT_NAME=custom_project (overrides .env)

### Start and test manually
    python verify_phoenix_config.py
    # Shows all configuration details

    make verify-phoenix
    # Same as above via Makefile

## Key Points

✅ .env file is automatically loaded on every run
✅ No need to manually source .env
✅ Works with both `python main.py` and `uv run main.py`
✅ Environment variables still take priority over .env
✅ Traces automatically go to arize_adk project
✅ Verification script confirms configuration

## Troubleshooting

If traces are NOT going to arize_adk:

1. Run verify_phoenix_config.py to check settings
2. Check that .env file has: PHOENIX_PROJECT_NAME=arize_adk
3. Confirm Phoenix endpoint is reachable: http://127.0.0.1:6006
4. Check logs for: "Setting up Phoenix tracing to ... (project: arize_adk)"

Still having issues?
- Make sure python-dotenv was installed (pip install python-dotenv)
- Delete __pycache__ and .venv, reinstall
- Run: python verify_phoenix_config.py for detailed diagnostics
"""

if __name__ == "__main__":
    print(__doc__)
