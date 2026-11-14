"""Local, session-only F0 script runner; no network listener or startup hook.

Reads Saved/F0_job.json and writes Saved/F0_job_result.json. Only scripts in
this directory whose name starts with f0_ may run. A job with stop=true
unregisters the editor callback. The runner also expires after two hours.
"""
import json
from pathlib import Path
import time
import traceback
import unreal

base = Path(__file__).resolve().parent
saved = Path(unreal.Paths.project_saved_dir()).resolve()
state = {'last': None, 'poll': 0.0, 'started': time.monotonic()}

def tick(delta):
    now = time.monotonic()
    if now - state['poll'] < 0.5:
        return
    state['poll'] = now
    if now - state['started'] > 86400:
        unreal.unregister_slate_post_tick_callback(state['handle'])
        return
    job_path = saved / 'F0_job.json'
    if not job_path.exists():
        return
    try:
        job = json.loads(job_path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return
    if job['id'] == state['last']:
        return
    state['last'] = job['id']
    result = {'id': job['id'], 'success': False}
    try:
        if job.get('stop'):
            unreal.unregister_slate_post_tick_callback(state['handle'])
        else:
            script = (base / job['script']).resolve()
            assert script.parent == base and script.name.startswith('f0_') and script.suffix == '.py'
            assert script.name != 'f0_worker.py'
            namespace = {'__file__': str(script), '__name__': '__main__'}
            exec(compile(script.read_text(encoding='utf-8-sig'), str(script), 'exec'), namespace)
        result['success'] = True
    except Exception:
        result['error'] = traceback.format_exc()
        unreal.log_error(result['error'])
    (saved / 'F0_job_result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')

state['handle'] = unreal.register_slate_post_tick_callback(tick)
print('F0 local runner active for this editor session; no network listener.')
