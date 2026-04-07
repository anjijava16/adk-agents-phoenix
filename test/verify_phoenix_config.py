#!/usr/bin/env python
"""
Verify Phoenix project configuration.

This script checks that the Phoenix project name is correctly configured
and that the .env file is being loaded properly.
"""

import os
import sys
from pathlib import Path


def verify_phoenix_config():
    """Verify Phoenix configuration is set to arize_adk."""
    print("=" * 70)
    print("Phoenix Configuration Verification")
    print("=" * 70)

    # Check .env file exists
    env_file = Path(__file__).parent / ".env"
    print(f"\n1. Check .env file:")
    print(f"   Location: {env_file}")
    print(f"   Exists: {env_file.exists()}")

    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "PHOENIX_PROJECT_NAME=arize_adk" in content:
                print(f"   ✓ PHOENIX_PROJECT_NAME=arize_adk found in .env")
            else:
                print(f"   ✗ PHOENIX_PROJECT_NAME=arize_adk NOT found in .env")
                return False

    # Import and check settings
    print(f"\n2. Load settings from configuration:")
    try:
        from app.config import get_settings

        settings = get_settings()
        print(f"   Phoenix Project: {settings.phoenix_project_name}")
        print(f"   Phoenix Endpoint: {settings.phoenix_endpoint}")
        print(f"   Phoenix Enabled: {settings.phoenix_enabled}")

        if settings.phoenix_project_name == "arize_adk":
            print(f"   ✓ Phoenix project correctly set to arize_adk")
        else:
            print(
                f"   ✗ Phoenix project is '{settings.phoenix_project_name}', expected 'arize_adk'"
            )
            return False

    except Exception as e:
        print(f"   ✗ Error loading settings: {e}")
        return False

    # Check tracing resource
    print(f"\n3. Check OpenTelemetry resource attributes:")
    try:
        from app.tracing import setup_phoenix_tracing

        provider = setup_phoenix_tracing(console_output=False)
        resource_attrs = provider.resource.attributes

        if resource_attrs.get("project.name") == "arize_adk":
            print(f"   ✓ Resource project.name: {resource_attrs.get('project.name')}")
        else:
            print(
                f"   ✗ Resource project.name is '{resource_attrs.get('project.name')}', expected 'arize_adk'"
            )
            return False

        print(f"   ✓ Resource service.name: {resource_attrs.get('service.name')}")
        print(f"   ✓ Resource service.version: {resource_attrs.get('service.version')}")

    except Exception as e:
        print(f"   ✗ Error setting up tracing: {e}")
        return False

    # Success!
    print("\n" + "=" * 70)
    print("✅ All checks passed!")
    print("=" * 70)
    print(f"\nTraces will be sent to Phoenix project: arize_adk")
    print(f"Phoenix UI: http://127.0.0.1:6006\n")

    return True


if __name__ == "__main__":
    success = verify_phoenix_config()
    sys.exit(0 if success else 1)
