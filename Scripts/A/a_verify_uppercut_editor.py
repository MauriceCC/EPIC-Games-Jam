"""Reapply integration and run asynchronous PIE checks in the full editor."""
import sys,runpy,traceback
from pathlib import Path
import unreal as u
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here))
try:
    from a_install_uppercut import main
    main()
    runpy.run_path(str(here/'a_test_uppercut.py'),run_name='__main__')
except Exception:
    (here/'uppercut_runner_error.txt').write_text(traceback.format_exc())
    u.SystemLibrary.quit_editor()
    raise
