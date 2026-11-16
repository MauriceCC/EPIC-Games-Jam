"""Apply only the authorized death presentation pass; never save all packages."""
import runpy
from pathlib import Path
import unreal as u

try:
    for filename in ('a_build_death_motion.py', 'a_install_death_presentation.py'):
        runpy.run_path(str(Path(__file__).with_name(filename)), run_name='__main__')
finally:
    u.SystemLibrary.quit_editor()
