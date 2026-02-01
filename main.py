#!/usr/bin/env python3
"""
Web monitoring program entry
Used to start web monitoring tasks, can be scheduled via crontab
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_monitor import main

if __name__ == "__main__":
    main()