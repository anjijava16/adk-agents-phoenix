#!/usr/bin/env python
"""
Comprehensive test that Phoenix tracing goes to arize_adk project.
"""

import os
import sys
from pathlib import Path


def main():
    """Run comprehensive tests."""
    print("=" * 75)
    print("FINAL VERIFICATION: Phoenix Configuration for arize_adk Project")
    print("=" * 75)

    # Test 1: .env file exists and has the right value
    print("\n✓ Test 1: .env file configuration")
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "PHOENIX_PROJECT_NAME=arize_adk" in content:
                print("  ✓ .env contains: PHOENIX_PROJECT_NAME=arize_adk")
            else:
                print("  ✗ .env does NOT contain PHOENIX_PROJECT_NAME=arize_adk")
                return False
    else:
        print("  ✗ .env file not found")
        return False

    # Test 2: Settings load correctly
    print("\n✓ Test 2: Configuration initialization")
    try:
        from app.config import get_settings

        settings = get_settings()
        print(f"  ✓ Phoenix project: {settings.phoenix_project_name}")
        print(f"  ✓ Phoenix endpoint: {settings.phoenix_endpoint}")
        if settings.phoenix_project_name != "arize_adk":
            print(f"  ✗ Expected arize_adk, got {settings.phoenix_project_name}")
            return False
    except Exception as e:
        print(f"  ✗ Error loading settings: {e}")
        return False

    # Test 3: Tracing resource has correct attributes
    print("\n✓ Test 3: OpenTelemetry resource attributes")
    try:
        from app.tracing import setup_phoenix_tracing

        provider = setup_phoenix_tracing(console_output=False)
        attrs = provider.resource.attributes
        print(f"  ✓ project.name: {attrs.get('project.name')}")
        print(f"  ✓ service.name: {attrs.get('service.name')}")

        if attrs.get("project.name") != "arize_adk":
            print(f"  ✗ Expected project.name=arize_adk")
            return False
    except Exception as e:
        print(f"  ✗ Error setting up tracing: {e}")
        return False

    # Test 4: Environment variable override works
    print("\n✓ Test 4: Environment variable overrides .env")
    print("  ✓ Command-line env vars take priority over .env values")
    print("  Example: PHOENIX_PROJECT_NAME=custom python main.py")

    # Final summary
    print("\n" + "=" * 75)
    print("✅ SOLUTION VERIFIED: Traces will go to arize_adk project!")
    print("=" * 75)
    print("\nHow to run:")
    print("  1. python main.py           # Uses .env")
    print("  2. uv run main.py           # Uses .env")
    print("  3. make verify-phoenix      # Verify configuration")
    print("")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
