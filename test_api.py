#!/usr/bin/env python3
"""
Test script for Git MCP Server API.
Sends HTTP requests to the running server and validates JSON responses.
"""

import json
import sys
import requests

BASE_URL = "http://localhost:8080"

def test_endpoint(command, args=None, expected_keys=None):
    """Test a single endpoint and return success/failure."""
    payload = {"command": command}
    if args is not None:
        payload["args"] = args

    try:
        resp = requests.post(f"{BASE_URL}/git/command", json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Validate basic structure
        if not isinstance(data, dict):
            print(f"❌ {command}: Response is not a JSON object")
            return False
        if "success" not in data or "output" not in data or "error" not in data:
            print(f"❌ {command}: Missing required fields in response")
            return False
        if not isinstance(data["success"], bool):
            print(f"❌ {command}: 'success' field is not a boolean")
            return False

        if data["success"]:
            if data["error"] is not None:
                print(f"❌ {command}: Success but error field is not null")
                return False
            if data["output"] is None:
                print(f"❌ {command}: Success but output is null")
                return False
            # Optional: check for expected keys in output
            if expected_keys and isinstance(data["output"], dict):
                for key in expected_keys:
                    if key not in data["output"]:
                        print(f"⚠️  {command}: Expected key '{key}' not found in output")
                        # Not failing, just warning
        else:
            if data["error"] is None:
                print(f"❌ {command}: Failure but error field is null")
                return False
            if data["output"] is not None:
                print(f"❌ {command}: Failure but output is not null")
                return False

        print(f"✅ {command}: {json.dumps(data, indent=2)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ {command}: Request failed - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ {command}: Invalid JSON response - {e}")
        return False

def main():
    print("Testing Git MCP Server API...")
    print(f"Using base URL: {BASE_URL}")
    print()

    all_passed = True

    # Test status
    print("--- Testing status ---")
    if not test_endpoint("status", expected_keys=["branch", "staged", "unstaged", "untracked"]):
        all_passed = False
    print()

    # Test diff (without args)
    print("--- Testing diff (no args) ---")
    if not test_endpoint("diff", expected_keys=["diff"]):
        all_passed = False
    print()

    # Test diff with staged=true
    print("--- Testing diff (staged:true) ---")
    if not test_endpoint("diff", args={"staged": True}, expected_keys=["diff"]):
        all_passed = False
    print()

    # Test diff with file (if a file exists, we can't guarantee, but we can still test)
    print("--- Testing diff (file:README.md) ---")
    if not test_endpoint("diff", args={"file": "README.md"}, expected_keys=["diff"]):
        all_passed = False
    print()

    # Test log
    print("--- Testing log ---")
    if not test_endpoint("log", expected_keys=["commits"]):
        all_passed = False
    print()

    # Test log with n=5
    print("--- Testing log (n:5) ---")
    if not test_endpoint("log", args={"n": 5}, expected_keys=["commits"]):
        all_passed = False
    print()

    # Test invalid command
    print("--- Testing invalid command ---")
    payload = {"command": "invalid"}
    try:
        resp = requests.post(f"{BASE_URL}/git/command", json=payload, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if not data["success"] and data["output"] is None and isinstance(data["error"], str):
            print(f"✅ invalid command: correctly returned error - {data['error']}")
        else:
            print(f"❌ invalid command: expected failure with error message")
            all_passed = False
    except Exception as e:
        print(f"❌ invalid command: request failed - {e}")
        all_passed = False
    print()

    if all_passed:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()