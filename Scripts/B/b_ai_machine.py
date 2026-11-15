from __future__ import annotations

import json
from pathlib import Path


def validate_machine(path: Path) -> dict:
    data = json.loads(path.read_text(encoding='utf-8'))

    required_top = {'version', 'enemyKinds', 'stateTransitions', 'transitionConditions'}
    missing = required_top - set(data.keys())
    if missing:
        raise ValueError(f'Missing top-level keys: {sorted(missing)}')

    enemy_kinds = data['enemyKinds']
    if not enemy_kinds:
        raise ValueError('enemyKinds is empty')

    valid_states = {
        'Patrol', 'Suspicious', 'Investigate', 'Chase', 'Combat', 'Return', 'Stunned', 'Defeated'
    }

    for name, config in enemy_kinds.items():
        if not isinstance(config.get('stateFlow'), list):
            raise ValueError(f'{name}: missing stateFlow list')
        if config['stateFlow'] and not set(config['stateFlow']).issubset(valid_states):
            raise ValueError(f'{name}: invalid state in stateFlow')

    transitions = data['stateTransitions']
    for state, next_states in transitions.items():
        if state not in valid_states:
            raise ValueError(f'Unknown state transition source: {state}')
        for next_state in next_states:
            if next_state not in valid_states and next_state != 'None':
                raise ValueError(f'Unknown state transition target: {next_state}')

    return data


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    path = repo_root / 'SourceData' / 'B' / 'EnemyAIStateMachine.json'
    try:
        data = validate_machine(path)
    except Exception as exc:
        print(f'ERROR: {exc}')
        return 1

    print(f'Validated AI state machine v{data["version"]} for {len(data["enemyKinds"])} enemy kinds.')
    for name in data['enemyKinds']:
        print(f'- {name}: {len(data["enemyKinds"][name]["stateFlow"])} states')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
