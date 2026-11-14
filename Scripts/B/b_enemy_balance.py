from __future__ import annotations

import csv
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
}


def validate_balance(path: Path) -> list[dict[str, str]]:
    with path.open('r', newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f'{path}: empty CSV file')

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f'{path}: missing columns: {sorted(missing)}')

        rows = list(reader)
        if not rows:
            raise ValueError(f'{path}: no rows found')

        for row in rows:
            name = (row.get('Name') or '').strip()
            if not name:
                raise ValueError(f'{path}: row with empty Name')

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
