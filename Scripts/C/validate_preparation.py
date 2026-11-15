"""Check C's design data without executing or replacing gameplay systems."""

import ast
import copy
import csv
import hashlib
import json
import re


def check(condition, message):
    if not condition:
        raise ValueError(message)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def contract_tokens(root):
    text = (root / "docs/plan/01_CONTRATOS_Y_PROPIEDAD.md").read_text(encoding="utf-8")
    block = re.findall(r"\x60\x60\x60text\s*\n(.*?)\x60\x60\x60", text, re.S)[0]
    enums = {}
    current = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if not line.startswith(" "):
            current, values = line.split(None, 1)
            enums[current] = []
        else:
            values = line.strip()
        enums[current].extend(value.strip() for value in values.split(",") if value.strip())
    return enums


def source_quotes(root, manifest):
    lines = (root / manifest["source_document"]).read_text(encoding="utf-8").splitlines()
    return [
        line[1:].strip() for line in lines
        if line.startswith("> ") and line[2:].strip() and not line.startswith("> **Norma")
    ]


def validate_sequences(rows, manifest, quotes):
    used_rows = []
    used_quotes = []
    ids = []
    for sequence in manifest["sequences"]:
        ids.append(sequence["id"])
        entries = sequence["rows"]
        check(bool(entries), "Empty narrative sequence")
        check(sequence["entry"] == entries[0]["row"], "Sequence entry mismatch")
        for index, entry in enumerate(entries):
            key = entry["row"]
            check(key in rows, f"Sequence references missing dialogue {key}")
            expected_next = entries[index + 1]["row"] if index + 1 < len(entries) else "None"
            check(rows[key]["NextRow"] == expected_next, f"{key}: cross-scene, cyclic or reordered NextRow")
            ordinal = entry["source_quote_ordinal"]
            check(1 <= ordinal <= len(quotes), f"{key}: source quotation is missing")
            actual_hash = hashlib.sha256(quotes[ordinal - 1].encode("utf-8")).hexdigest()
            check(actual_hash == entry["source_quote_sha256"], f"{key}: source changed; review its translation")
            used_rows.append(key)
            used_quotes.append(ordinal)
    check(len(ids) == len(set(ids)), "Duplicate narrative sequence identifier")
    check(len(used_rows) == len(set(used_rows)) and set(used_rows) == set(rows), "Dialogue coverage is not one-to-one")
    check(sorted(used_quotes) == list(range(1, len(quotes) + 1)), "Source quotation coverage is not one-to-one")


def validate_transitions(spec, enums, known_flags):
    phases = enums["EStoryPhase"]
    check(spec["phases"] == phases, "Phase order differs from the existing contract")
    check(spec["initial_phase"] == phases[0] and spec["terminal_phase"] == phases[-1], "Invalid phase endpoints")
    check(set(spec["evidence_types"]) == set(enums["EEvidenceType"]), "Evidence token drift")
    policies = [policy["event"] for policy in spec["event_policy"]]
    check(len(policies) == len(set(policies)) and set(policies) == set(enums["EStoryEvent"]), "Incomplete event policy")
    rules = {}
    advancing = []
    for rule in spec["transitions"]:
        phase, target, event = rule["phase"], rule["next_phase"], rule["event"]
        check(phase in phases and target in phases and event in enums["EStoryEvent"], "Unknown transition token")
        check(phase != phases[-1], "GameEnded must remain terminal")
        key = (phase, event)
        check(key not in rules, "Ambiguous phase/event rule")
        rules[key] = rule
        check(set(rule["required_flags"]) <= known_flags, "Undocumented narrative flag")
        if phase != target:
            check(phases.index(target) == phases.index(phase) + 1, "Transition skips a phase")
            advancing.append((phase, target))
    check(advancing == list(zip(phases[:-1], phases[1:])), "Phase progression is incomplete or reordered")
    check(len(rules) == 6, "Unexpected phase rule count")
    boss = rules.get(("FinalChoice", "SupervisorDefeated"))
    check(boss is not None and boss["next_phase"] == "FinalChoice" and not boss["allowed_endings"], "Boss defeat must not select an ending")
    final = rules.get(("FinalChoice", "FinalDocumentRegistered"))
    check(final is not None and final["next_phase"] == "GameEnded", "Final registration rule is missing")
    check(final["requires_supervisor_defeat"] is True, "Final registration bypasses the Supervisor gate")
    check(set(final["allowed_endings"]) == set(enums["EEndingType"]) - {"None"}, "Final registration has invalid ending choices")
    truth = rules.get(("DiscoverTruth", "TruthRevealed"))
    check(truth is not None and {"bJackSafe", "bEvidenceFound", "bFalseReportFound"} <= set(truth["required_flags"]), "Truth reveal lacks its prerequisite facts")


def validate_table_document(root, spec):
    text = (root / "docs/plan/C_NARRATIVA_INTERACCION_UI.md").read_text(encoding="utf-8")
    section = text.split("## 5.", 1)[1].split("## 6.", 1)[0]
    documented = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells[0] in spec["phases"]:
            event = re.search(r"\x60(\w+)\x60", cells[1])
            check(event is not None and len(cells) == 4, "Malformed C transition table")
            documented.append((cells[0], event.group(1), cells[2]))
    expected = [(rule["phase"], rule["event"], rule["next_phase"]) for rule in spec["transitions"]]
    check(documented == expected, "C plan and prepared transition data disagree")


def validate_preview_cases(fixtures, sequences, checklist, strings):
    check(fixtures["presentation_only"] is True and fixtures["automatic_gameplay_locks"] is False, "Preview is not presentation-only")
    check(all(path.startswith("/Game/Unscripted/UI/Test/") for path in fixtures["planned_assets"]), "Preview asset path is outside C test ownership")
    sequence_ids = {sequence["id"] for sequence in sequences["sequences"]}
    for case in fixtures["dialogue_cases"]:
        check(case["sequence"] in sequence_ids, "Preview refers to a missing conversation")
    for case in fixtures["checklist_cases"]:
        check(case["phase"] in checklist, "Preview refers to a missing checklist")
        row = checklist[case["phase"]]
        items, mask = ast.literal_eval(row["Items"]), ast.literal_eval(row["CompletedMask"])
        check(len(items) == case["expected_item_count"] and sum(mask) == case["expected_completed_count"], "Preview checklist expectation differs from the CSV")
    count = fixtures["preserve_completed_prefix"]
    initial = ast.literal_eval(checklist["FindJack"]["Items"])
    rewritten = ast.literal_eval(checklist["FinalChoice"]["Items"])
    check(initial[:count] == rewritten[:count], "Rewriting changes the wording of already completed orders")
    keys = [row["Key"] for row in strings]
    check(len(keys) == len(set(keys)), "Duplicate UI string key")
    check(all(row["Text"].strip() and row["Status"] in {"Adapted", "Proposal"} for row in strings), "Invalid UI text or review status")
    check(strings and set(strings[0]) == {"Key", "Text", "Status"}, "Unexpected UI string headers")


def negative_checks(dialogue, manifest, quotes, spec, enums, known_flags):
    cases = []
    altered = copy.deepcopy(dialogue)
    altered["JackFound_03"]["NextRow"] = "Truth_02"
    cases.append(("cross-scene dialogue", lambda: validate_sequences(altered, manifest, quotes)))
    cyclic = copy.deepcopy(dialogue)
    cyclic["JackFound_03"]["NextRow"] = "JackFound_01"
    cases.append(("cyclic dialogue", lambda: validate_sequences(cyclic, manifest, quotes)))
    stale = copy.deepcopy(manifest)
    stale["sequences"][0]["rows"][0]["source_quote_sha256"] = "0" * 64
    cases.append(("stale source quotation", lambda: validate_sequences(dialogue, stale, quotes)))
    bad_gate = copy.deepcopy(spec)
    bad_gate["transitions"][-1]["requires_supervisor_defeat"] = False
    cases.append(("missing Supervisor gate", lambda: validate_transitions(bad_gate, enums, known_flags)))
    bad_boss = copy.deepcopy(spec)
    bad_boss["transitions"][-2]["next_phase"] = "GameEnded"
    cases.append(("boss-selected ending", lambda: validate_transitions(bad_boss, enums, known_flags)))
    bad_ending = copy.deepcopy(spec)
    bad_ending["transitions"][-1]["allowed_endings"].append("None")
    cases.append(("invalid ending choice", lambda: validate_transitions(bad_ending, enums, known_flags)))
    for label, operation in cases:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError(f"Invalid fixture was accepted: {label}")
    return len(cases)


def validate_preparation(root):
    source = root / "SourceData/C"
    dialogue = {row["Name"]: row for row in read_csv(source / "DT_Dialogue.csv")}
    checklist = {row["Name"]: row for row in read_csv(source / "DT_Checklist.csv")}
    manifest = read_json(source / "NarrativeSequences.json")
    spec = read_json(source / "StoryTransitions.json")
    fixtures = read_json(source / "WidgetPreviewCases.json")
    strings = read_csv(source / "UIStrings.csv")
    enums = contract_tokens(root)
    flags_text = (root / "docs/05_NIVEL_MISIONES_Y_HUD.md").read_text(encoding="utf-8")
    known_flags = set(re.findall(r"(?m)^(b\w+)\s*=", flags_text))
    quotes = source_quotes(root, manifest)
    check({row["Speaker"] for row in dialogue.values()} <= set(enums["ESpeaker"]), "Speaker tokens differ from the shared documentation")
    validate_sequences(dialogue, manifest, quotes)
    validate_transitions(spec, enums, known_flags)
    validate_table_document(root, spec)
    validate_preview_cases(fixtures, manifest, checklist, strings)
    rejected = negative_checks(dialogue, manifest, quotes, spec, enums, known_flags)
    return {
        "source_quotes": len(quotes),
        "dialogue_sequences": len(manifest["sequences"]),
        "transition_rules": len(spec["transitions"]),
        "event_policies": len(spec["event_policy"]),
        "ui_strings": len(strings),
        "invalid_fixtures_rejected": rejected,
        "unreal_import_tested": False,
        "widget_assets_created": False,
        "runtime_tested": False,
    }
