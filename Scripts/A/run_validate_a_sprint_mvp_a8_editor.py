"""Full editor runner: Blueprint action database is disabled in commandlets."""
from pathlib import Path
import unreal
try:
    path = Path(__file__).with_name('validate_a_sprint_mvp_a8.py')
    exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'), {'__file__': str(path), '__name__': '__main__'})
finally:
    unreal.SystemLibrary.quit_editor()

