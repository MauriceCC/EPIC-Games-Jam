from __future__ import annotations

import csv
import math
from pathlib import Path

REQUIRED_COLUMNS = {
    'Name',
    'Health',
    'AttackDamage',
    'PostureDamage',
    'VisionRange',
    'DetectionRange',
    'WalkSpeed',
    'RunSpeed',
    'AlertDelaySeconds',
    'StunDurationSeconds',
    'TemporalFreezeDurationSeconds',
    'NeutralizeWindowSeconds',
    'Priority',
    'Notes',
    'MaxPosture',
    'WindupSeconds',
    'CutDurationPercent',
}


def validate_balance(path: Path) -> list[dict[str, str]]:
    with path.open('r', newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f'{path}: empty CSV file')

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f'{path}: missing columns: {sorted(missing)}')

        rows = list(reader)
        if not rows:
            raise ValueError(f'{path}: no rows found')

        seen = set()
        for row in rows:
            name = (row.get('Name') or '').strip()
            if not name:
                raise ValueError(f'{path}: row with empty Name')
            if name in seen:
                raise ValueError(f'{path}: repeated enemy {name}')
            seen.add(name)
            for field in REQUIRED_COLUMNS - {'Name', 'Notes'}:
                value = float(row.get(field) or 'nan')
                if not math.isfinite(value) or value < 0:
                    raise ValueError(f'{path}: {name}.{field} must be a finite nonnegative number')
                if field in {'Health', 'Priority', 'CutDurationPercent'} and not value.is_integer():
                    raise ValueError(f'{path}: {name}.{field} must be an integer')
            if float(row['Health']) <= 0 or not 0 < float(row['WalkSpeed']) <= float(row['RunSpeed']):
                raise ValueError(f'{path}: {name} has invalid health or movement speeds')
            if float(row['CutDurationPercent']) > 100:
                raise ValueError(f'{path}: {name}.CutDurationPercent cannot exceed 100')

        expected = {'Pursuer', 'Interventor', 'Supervisor', 'Jack'}
        if missing := expected - seen:
            raise ValueError(f'{path}: missing rows: {sorted(missing)}')

        return rows


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    csv_path = repo_root / 'SourceData' / 'B' / 'DT_EnemyBalance.csv'

    try:
        rows = validate_balance(csv_path)
    except Exception as exc:  # pragma: no cover - CLI validation output
        print(f'ERROR: {exc}')
        return 1

    print(f'Validated {len(rows)} enemy rows in {csv_path.relative_to(repo_root)}')
    for row in rows:
        print(f"- {row['Name']}: HP {row['Health']}, Damage {row['AttackDamage']}, Vision {row['VisionRange']}m")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
