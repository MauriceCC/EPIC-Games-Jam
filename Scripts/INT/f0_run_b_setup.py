"""Integration runner entry point for Division B setup."""
import sys
from pathlib import Path
import unreal

b_dir = Path(__file__).resolve().parent.parent / 'B'
if str(b_dir) not in sys.path:
    sys.path.insert(0, str(b_dir))
import b_editor_setup

b_editor_setup.build_and_verify_all()
