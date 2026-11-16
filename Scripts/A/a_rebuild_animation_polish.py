"""Apply the A/B animation pass and reload validation in one editor session."""
from pathlib import Path
import runpy
repo=Path(__file__).resolve().parents[2]
for script in ('Scripts/A/a_polish_animation_assets.py','Scripts/B/b_install_attack_animation.py','Scripts/A/a_install_animation_polish.py','Scripts/A/a_validate_animation_polish.py'):
    runpy.run_path(str(repo/script),run_name='__main__')
