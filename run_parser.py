#!/usr/bin/env python3
"""
Entry point script that handles Python path setup and .env loading.
Run this from project root: python run_parser.py
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

# Now import and run main
from src.main import main

if __name__ == "__main__":
    sys.exit(main())
