# Vercel entry point: Vercel serves the `handler` class as a serverless function (vercel.json routes /api/* here)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quiz import Handler  # noqa: E402


# must be a literal top-level `class handler`: Vercel finds functions by scanning the source,
# and an import alias (`import Handler as handler`) is not detected
class handler(Handler):
    pass
