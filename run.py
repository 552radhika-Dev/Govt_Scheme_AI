"""
Application Launcher for Haqdarshak Scheme AI Citizen FAQ Generator & Workbench.
Starts the FastAPI server with live interactive Web UI on http://localhost:8000
"""

import sys
import uvicorn


def main():
    print("=" * 70)
    print("  HAQDARSHAK SCHEME KNOWLEDGE BASE & CITIZEN FAQ AI")
    print("  Scenario A3 · Case Study Assignment")
    print("=" * 70)
    print("\nStarting local server on: http://localhost:8000")
    print("Open http://localhost:8000 in your browser to interact with the demo.\n")

    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
