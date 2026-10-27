# Vercel entry point: Vercel serves the `handler` class as a serverless function (vercel.json routes /api/* here)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quiz import Handler as handler  # noqa: E402,F401
