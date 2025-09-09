# Expose the Flask WSGI app to Vercel's Python runtime
import os
import sys

# Ensure project root is on the import path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from server import app as app  # Vercel looks for a module-level `app`

