# ### FILE: commshubproject/tests/test_drafter.py
from src.drafter import Drafter
import os

def test_drafter_initialization():
    # Will initialize genai if api key exists
    drafter = Drafter()
    assert drafter.model is not None
