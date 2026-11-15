"""Validate Division C's F0 narrative sources without modifying any files."""

import ast
import csv
import sys
from pathlib import Path
import json
from validate_preparation import validate_preparation

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "SourceData" / "C"
SPEAKERS = {"Agent", "Jack", "Supervisor", "Director", "FutureSelf", "Interventor", "System"}
PHASES = {"FindJack", "OpenEscapeRoute", "ProtectJack", "DiscoverTruth", "FinalChoice"}
ENTRIES = {
    "Briefing_01", "JackFound_01", "FutureMessage_01", "Truth_01",
    "Correction_Order", "SupervisorEncounter_01", "EndingOfficial_01",
    "EndingAuthentic_01", "ContinuityAltered_01", "CombatWarning_01",
}
EXPECTED_DIALOGUE = {
    *(f"Briefing_{index:02}" for index in range(1, 6)),
    *(f"JackFound_{index:02}" for index in range(1, 4)),
    "FutureMessage_01",
    *(f"Truth_{index:02}" for index in range(1, 6)),
    "Correction_Order",
    *(f"SupervisorEncounter_{index:02}" for index in range(1, 5)),
    "EndingOfficial_01", "EndingAuthentic_01", "EndingAuthentic_02",
    "ContinuityAltered_01", "CombatWarning_01",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_rows(filename, headers, key):
    path = SOURCE / filename
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == headers, f"{filename}: unexpected CSV headers")
        rows = list(reader)
    require(bool(rows), f"{filename}: empty source")
    for line, row in enumerate(rows, start=2):
        require(None not in row and None not in row.values(), f"{filename}:{line}: malformed CSV")
        require(bool(row[key].strip()), f"{filename}:{line}: empty row identifier")
        require(bool(row.get("Text", row.get("Items", "")).strip()), f"{filename}:{line}: empty text")
    keys = [row[key] for row in rows]
    require(len(keys) == len(set(keys)), f"{filename}: duplicate row identifier")
    return {row[key]: row for row in rows}


def validate_dialogue():
    rows = read_rows(
        "DT_Dialogue.csv", ["Name", "Speaker", "Text", "Duration", "NextRow"], "Name"
    )
    require(set(rows) == EXPECTED_DIALOGUE, "Dialogue coverage differs from the design quotation inventory")
    for key, row in rows.items():
        require(row["Speaker"] in SPEAKERS, f"{key}: unknown ESpeaker token")
        require(float(row["Duration"]) == 0, f"{key}: unreviewed automatic dialogue timing")
        target = row["NextRow"]
        require(target == "None" or target in rows, f"{key}: broken NextRow reference {target}")
        visited = set()
        current = key
        while current != "None":
            require(current not in visited, f"{key}: dialogue cycle at {current}")
            visited.add(current)
            current = rows[current]["NextRow"]

    reached = set()
    for entry in ENTRIES:
        current = entry
        while current != "None":
            reached.add(current)
            current = rows[current]["NextRow"]
    require(reached == set(rows), "Dialogue rows are unreachable from the documented entry rows")
    incoming = {row["NextRow"] for row in rows.values() if row["NextRow"] != "None"}
    require(not (ENTRIES & incoming), "A dialogue entry unexpectedly belongs to another conversation")
    require(rows["Correction_Order"]["NextRow"] == "None", "Correction_Order must remain the terminal agreed row")
    return len(rows)


def validate_checklist():
    rows = read_rows(
        "DT_Checklist.csv",
        ["Name", "Phase", "Items", "CompletedMask", "bIsRewritten"],
        "Name",
    )
    require(set(rows) == PHASES, "Checklist must cover only the five documented gameplay phases")
    for key, row in rows.items():
        require(row["Phase"] == key, f"{key}: mismatched EStoryPhase")
        items = ast.literal_eval(row["Items"])
        mask = ast.literal_eval(row["CompletedMask"])
        require(isinstance(items, tuple) and isinstance(mask, tuple), f"{key}: invalid Unreal array syntax")
        require(len(items) == len(mask), f"{key}: completion mask length differs from item count")
        require(all(isinstance(item, str) and item.strip() for item in items), f"{key}: invalid checklist text")
        require(all(type(value) is bool for value in mask), f"{key}: non-boolean completion mask")
        rewritten = key == "FinalChoice"
        require(row["bIsRewritten"] == str(rewritten), f"{key}: incorrect rewrite flag")
        require(len(items) == (4 if rewritten else 3), f"{key}: missing narrative orders")
        if rewritten:
            require(mask == (True, True, False, False), "FinalChoice: incorrect rewritten completion mask")
            require("Frame Jack" in items[2] and "Eliminate Jack" in items[3], "FinalChoice: missing changed orders")
        else:
            require("identity" in items[2], f"{key}: missing identity-protection order")
            require(mask[2] is False, f"{key}: ongoing identity protection must not be marked complete")
    return len(rows)


def validate_narrative_text():
    rows = read_rows("NarrativeText.csv", ["Key", "Kind", "Text", "Status"], "Key")
    required = {
        "NursingRecord_Title", "NursingRecord_Summary",
        "FabricatedReport_Title", "FabricatedReport_Summary",
        "OfficialFile_Title", "OfficialFile_Summary",
        "AuthenticFile_Title", "AuthenticFile_Summary",
        "OfficialEnding_Summary", "AuthenticEnding_Summary",
        "ContinuityAltered_Title", "ContinuityAltered_Body",
    }
    require(set(rows) == required, "Narrative text inventory is incomplete")
    for key, row in rows.items():
        require(row["Kind"] in {"Document", "FinalDocument", "Ending", "Notice"}, f"{key}: unknown text kind")
        require(row["Status"] in {"Adapted", "DesignSummary"}, f"{key}: missing design status")
        require("CORTE FINAL" not in row["Text"], f"{key}: obsolete player-facing title")
    return len(rows)


def main():
    preparation = validate_preparation(ROOT)
    dialogue_count = validate_dialogue()
    checklist_count = validate_checklist()
    text_count = validate_narrative_text()
    print(
        f"PASS: {dialogue_count} dialogue rows, {checklist_count} checklist rows, "
        f"{text_count} narrative text entries; schemas, links and masks are valid."
    )
    print(json.dumps(preparation, sort_keys=True))
    print("Unreal import, runtime behavior and F1 acceptance remain untested.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, SyntaxError, TypeError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
