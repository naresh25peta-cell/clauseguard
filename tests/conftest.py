"""conftest.py — sets a dummy OPENAI_API_KEY so modules can import without a real key."""
import os
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy")
