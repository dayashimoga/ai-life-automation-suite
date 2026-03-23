import sys
import os

# Add the app root to sys.path so pytest can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
