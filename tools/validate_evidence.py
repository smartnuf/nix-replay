#!/usr/bin/env python3
"""Validate the mechanically decidable invariants of the D2 evidence base."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


SOURCE_ID = re.compile(r"^S\d{4}$")
CLAIM_ID = re.compile(r"^[CHJ]\d{4}$")
MARKDOWN_ID_CANDIDATE = re.compile(r"\b[SCHJ]\d+\b")
MARKDOWN_BRACKETED_ID = re.compile(r"\[([SCHJ][^\]\s]*)\]")

SOURCE_CLASSES = {
    "contemporary-primary",
    "first-person-account",
    "institutional-record",
    "independent-analysis",
    "community-report",
    "project-experiment-or-synthesis",
}
SOURCE_STATUSES = {"active", "retired", "superseded"}
CLAIM_KINDS = {"fact", "report", "inference", "hypothesis", "judgement"}
CLAIM_STATUSES = {"supported", "provisional", "open", "contested", "retired"}
CONFIDENCES = {"high", "medium", "low"}
EVIDENCE_RELATIONS = {
    "contradicts",
    "historical-support",
    "motivates",
    "supports",
}
CLAIM_PREFIXES = {
    "fact": "C",
    "report": "C",
    "inference": "H",
    "hypothesis": "H",
    "judgement": "J",
}
SOURCE_IDENTITY_FIELDS = {
    "creators",
    "kind",
    "published",
    "publisher",
    "title",
    "version",
}
CLAIM_IDENTITY_FIELDS = {"attributed_to", "kind", "statement"}

SOURCE_FIELDS = {
    "id",
    "status",
    "title",
    "creators",
    "published",
    "kind",
    "publisher",
    "url",
    "snapshot_url",
    "version",
    "accessed",
    "source_class",
    "authority",
    "scope",
    "rights_status",
    "intended_use",
    "notes",
    "superseded_by",
    "lifecycle_note",
}
REQUIRED_SOURCE_FIELDS = SOURCE_FIELDS - {
    "snapshot_url",
    "superseded_by",
    "lifecycle_note",
}
CLAIM_FIELDS = {
    "id",
    "statement",
    "kind",
    "status",
    "confidence",
    "attributed_to",
    "scope",
    "evidence",
    "caveats",
    "relevance",
    "reviewed",
}
REQUIRED_CLAIM_FIELDS = CLAIM_FIELDS - {"attributed_to"}
EVIDENCE_FIELDS = {"source", "locator", "relation"}
ROOT_FIELDS = {
    "sources.yaml": {"schema_version", "updated", "sources"},
    "claims.yaml": {"schema_version", "updated", "claims"},
}
SCHEMA_VERSIONS = {"sources.yaml": 2, "claims.yaml": 1}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _display(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _parse_yaml(text: str, label: str, errors: list[str]) -> Any:
    try:
        return yaml.load(text, Loader=UniqueKeyLoader)
    except (ValueError, yaml.YAMLError) as exc:
        errors.append(f"{label}: invalid YAML: {exc}")
    return None


def _load_yaml(path: Path, root: Path, errors: list[str]) -> Any:
    label = _display(path, root)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{label}: cannot read file: {exc}")
        return None
    return _parse_yaml(text, label, errors)


def _resolve_revision(
    root: Path, revision: str, errors: list[str]
) -> str | None:
    result = subprocess.run(
        [
            "git",
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{revision}^{{commit}}",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = result.stderr.strip() or "revision not found"
        errors.append(f"baseline {revision!r}: {detail}")
        return None
    return result.stdout.strip()


def _load_yaml_at_revision(
    root: Path,
    revision: str,
    relative_path: str,
    errors: list[str],
) -> Any:
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative_path}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    label = f"{revision}:{relative_path}"
    if result.returncode:
        detail = result.stderr.strip() or "file not found"
        errors.append(f"{label}: cannot read baseline file: {detail}")
        return None
    return _parse_yaml(result.stdout, label, errors)


def _is_blank(value: Any) -> bool:
    return value is None or isinstance(value, str) and not value.strip()


def _check_date(value: Any, location: str, errors: list[str]) -> None:
    if type(value) is dt.date:
        return
    if isinstance(value, str):
        try:
            parsed = dt.date.fromisoformat(value)
        except ValueError:
            pass
        else:
            if parsed.isoformat() == value:
                return
    errors.append(f"{location}: expected an ISO calendar date (YYYY-MM-DD)")


def _check_fields(
    record: dict[str, Any],
    required: set[str],
    allowed: set[str],
    location: str,
    errors: list[str],
) -> None:
    missing = sorted(name for name in required if name not in record)
    unknown = sorted(name for name in record if name not in allowed)
    if missing:
        errors.append(
            f"{location}: missing required fields: {', '.join(missing)}"
        )
    if unknown:
        errors.append(f"{location}: unknown fields: {', '.join(unknown)}")
    for name in sorted(required & record.keys()):
        if _is_blank(record[name]):
            errors.append(f"{location}.{name}: must not be blank")


def _check_root(
    document: Any,
    filename: str,
    collection: str,
    errors: list[str],
) -> list[Any]:
    if not isinstance(document, dict):
        errors.append(f"research/{filename}: document must be a mapping")
        return []

    location = f"research/{filename}"
    _check_fields(
        document,
        ROOT_FIELDS[filename],
        ROOT_FIELDS[filename],
        location,
        errors,
    )
    expected_version = SCHEMA_VERSIONS[filename]
    version = document.get("schema_version")
    if type(version) is not int or version != expected_version:
        errors.append(
            f"{location}.schema_version: expected integer {expected_version}"
        )
    _check_date(document.get("updated"), f"{location}.updated", errors)
    records = document.get(collection)
    if not isinstance(records, list):
        errors.append(f"{location}.{collection}: expected a list")
        return []
    return records


def _check_non_empty_string(
    value: Any, location: str, errors: list[str]
) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{location}: expected a non-empty string")


def _check_string_list(
    value: Any,
    location: str,
    errors: list[str],
    *,
    allow_empty: bool = True,
) -> None:
    if not isinstance(value, list):
        errors.append(f"{location}: expected a list")
        return
    if not value and not allow_empty:
        errors.append(f"{location}: must not be empty")
    for index, item in enumerate(value):
        _check_non_empty_string(item, f"{location}[{index}]", errors)


def _validate_sources(
    records: list[Any], errors: list[str]
) -> dict[str, dict[str, Any]]:
    registered: dict[str, dict[str, Any]] = {}
    scalar_fields = REQUIRED_SOURCE_FIELDS - {
        "creators",
        "published",
        "accessed",
    }

    for index, record in enumerate(records):
        location = f"research/sources.yaml:sources[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{location}: expected a mapping")
            continue
        _check_fields(
            record,
            REQUIRED_SOURCE_FIELDS,
            SOURCE_FIELDS,
            location,
            errors,
        )

        identifier = record.get("id")
        valid_identifier = (
            isinstance(identifier, str) and SOURCE_ID.fullmatch(identifier)
        )
        if not valid_identifier:
            errors.append(f"{location}.id: expected S followed by four digits")
        elif identifier in registered:
            errors.append(f"{location}.id: duplicate identifier {identifier}")
        else:
            registered[identifier] = record

        for name in sorted(scalar_fields & record.keys()):
            _check_non_empty_string(record[name], f"{location}.{name}", errors)
        _check_string_list(
            record.get("creators"),
            f"{location}.creators",
            errors,
            allow_empty=False,
        )
        if record.get("source_class") not in SOURCE_CLASSES:
            errors.append(
                f"{location}.source_class: expected one of "
                f"{', '.join(sorted(SOURCE_CLASSES))}"
            )
        if record.get("status") not in SOURCE_STATUSES:
            errors.append(
                f"{location}.status: expected one of "
                f"{', '.join(sorted(SOURCE_STATUSES))}"
            )
        published = record.get("published")
        if (
            isinstance(published, bool)
            or not isinstance(published, (str, int, dt.date))
            or _is_blank(published)
        ):
            errors.append(
                f"{location}.published: expected a date, year, or non-empty "
                "string"
            )
        _check_date(record.get("accessed"), f"{location}.accessed", errors)
        if "snapshot_url" in record:
            _check_non_empty_string(
                record["snapshot_url"], f"{location}.snapshot_url", errors
            )
    _validate_source_lifecycle(registered, errors)
    return registered


def _validate_source_lifecycle(
    records: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    for identifier, record in records.items():
        location = f"research/sources.yaml:{identifier}"
        status = record.get("status")
        has_target = "superseded_by" in record
        has_note = "lifecycle_note" in record

        if status == "active":
            if has_target or has_note:
                errors.append(
                    f"{location}: active sources must omit lifecycle fields"
                )
        elif status == "retired":
            if has_target:
                errors.append(
                    f"{location}: retired sources must omit superseded_by"
                )
            if not has_note:
                errors.append(
                    f"{location}: retired sources require lifecycle_note"
                )
        elif status == "superseded":
            if not has_target:
                errors.append(
                    f"{location}: superseded sources require superseded_by"
                )
            if not has_note:
                errors.append(
                    f"{location}: superseded sources require lifecycle_note"
                )

        if has_note:
            _check_non_empty_string(
                record["lifecycle_note"], f"{location}.lifecycle_note", errors
            )
        if not has_target:
            continue
        target = record["superseded_by"]
        if not isinstance(target, str) or not SOURCE_ID.fullmatch(target):
            errors.append(
                f"{location}.superseded_by: expected a source identifier"
            )
        elif target == identifier:
            errors.append(
                f"{location}.superseded_by: must not refer to itself"
            )
        elif target not in records:
            errors.append(
                f"{location}.superseded_by: unknown source identifier {target}"
            )
        elif records[target].get("status") == "retired":
            errors.append(
                f"{location}.superseded_by: target {target} is retired"
            )

    reported_cycles: set[frozenset[str]] = set()
    for start in records:
        positions: dict[str, int] = {}
        path: list[str] = []
        current = start
        while (
            current in records
            and records[current].get("status") == "superseded"
        ):
            if current in positions:
                cycle = frozenset(path[positions[current] :])
                if cycle not in reported_cycles:
                    errors.append(
                        "research/sources.yaml: supersession cycle: "
                        + " -> ".join((*path[positions[current] :], current))
                    )
                    reported_cycles.add(cycle)
                break
            positions[current] = len(path)
            path.append(current)
            target = records[current].get("superseded_by")
            if not isinstance(target, str):
                break
            current = target


def _validate_claims(
    records: list[Any], source_ids: set[str], errors: list[str]
) -> dict[str, dict[str, Any]]:
    registered: dict[str, dict[str, Any]] = {}
    scalar_fields = REQUIRED_CLAIM_FIELDS - {"evidence", "caveats", "reviewed"}

    for index, record in enumerate(records):
        location = f"research/claims.yaml:claims[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{location}: expected a mapping")
            continue
        _check_fields(
            record,
            REQUIRED_CLAIM_FIELDS,
            CLAIM_FIELDS,
            location,
            errors,
        )

        identifier = record.get("id")
        valid_identifier = (
            isinstance(identifier, str) and CLAIM_ID.fullmatch(identifier)
        )
        if not valid_identifier:
            errors.append(
                f"{location}.id: expected C, H, or J followed by four digits"
            )
        elif identifier in registered:
            errors.append(f"{location}.id: duplicate identifier {identifier}")
        else:
            registered[identifier] = record

        for name in sorted(scalar_fields & record.keys()):
            _check_non_empty_string(record[name], f"{location}.{name}", errors)

        kind = record.get("kind")
        if kind not in CLAIM_KINDS:
            errors.append(
                f"{location}.kind: expected one of "
                f"{', '.join(sorted(CLAIM_KINDS))}"
            )
        elif isinstance(identifier, str) and CLAIM_ID.fullmatch(identifier):
            expected = CLAIM_PREFIXES[kind]
            if not identifier.startswith(expected):
                errors.append(
                    f"{location}.id: {kind} records require the {expected} "
                    "prefix"
                )

        if record.get("status") not in CLAIM_STATUSES:
            errors.append(
                f"{location}.status: expected one of "
                f"{', '.join(sorted(CLAIM_STATUSES))}"
            )
        if record.get("confidence") not in CONFIDENCES:
            errors.append(
                f"{location}.confidence: expected one of "
                f"{', '.join(sorted(CONFIDENCES))}"
            )

        if kind == "report":
            _check_non_empty_string(
                record.get("attributed_to"),
                f"{location}.attributed_to",
                errors,
            )
        elif "attributed_to" in record:
            errors.append(
                f"{location}.attributed_to: allowed only for reports"
            )

        evidence = record.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{location}.evidence: expected a list")
        else:
            if record.get("status") == "supported" and not evidence:
                errors.append(
                    f"{location}.evidence: supported claims require evidence"
                )
            for evidence_index, item in enumerate(evidence):
                item_location = f"{location}.evidence[{evidence_index}]"
                if not isinstance(item, dict):
                    errors.append(f"{item_location}: expected a mapping")
                    continue
                _check_fields(
                    item,
                    EVIDENCE_FIELDS,
                    EVIDENCE_FIELDS,
                    item_location,
                    errors,
                )
                for name in sorted(EVIDENCE_FIELDS & item.keys()):
                    _check_non_empty_string(
                        item[name], f"{item_location}.{name}", errors
                    )
                source = item.get("source")
                if isinstance(source, str) and source not in source_ids:
                    errors.append(
                        f"{item_location}.source: unknown source identifier "
                        f"{source}"
                    )
                if item.get("relation") not in EVIDENCE_RELATIONS:
                    errors.append(
                        f"{item_location}.relation: expected one of "
                        f"{', '.join(sorted(EVIDENCE_RELATIONS))}"
                    )

        _check_string_list(
            record.get("caveats"), f"{location}.caveats", errors
        )
        _check_date(record.get("reviewed"), f"{location}.reviewed", errors)
    return registered


def _validate_markdown_ids(
    root: Path,
    source_ids: set[str],
    claim_ids: set[str],
    errors: list[str],
) -> None:
    paths: set[Path] = set()
    for relative_directory in ("research", "experiments", "publishing"):
        directory = root / relative_directory
        if directory.is_dir():
            paths.update(directory.rglob("*.md"))
    synthesis = root / "docs" / "research-synthesis.md"
    if synthesis.is_file():
        paths.add(synthesis)

    for path in sorted(paths):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{_display(path, root)}: cannot read file: {exc}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            bracketed = list(MARKDOWN_BRACKETED_ID.finditer(line))
            candidates = [
                (match.span(1), match.group(1)) for match in bracketed
            ]
            for match in MARKDOWN_ID_CANDIDATE.finditer(line):
                if any(
                    start <= match.start() and match.end() <= end
                    for (start, end), _ in candidates
                ):
                    continue
                candidates.append((match.span(), match.group()))
            for _, identifier in candidates:
                pattern = SOURCE_ID if identifier.startswith("S") else CLAIM_ID
                if not pattern.fullmatch(identifier):
                    errors.append(
                        f"{_display(path, root)}:{line_number}: malformed "
                        f"identifier {identifier}"
                    )
                    continue
                known = source_ids if identifier.startswith("S") else claim_ids
                if identifier not in known:
                    errors.append(
                        f"{_display(path, root)}:{line_number}: unknown "
                        f"identifier {identifier}"
                    )


def _index_baseline_records(
    document: Any,
    collection: str,
    identifier_pattern: re.Pattern[str],
    label: str,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(document, dict) or not isinstance(
        document.get(collection), list
    ):
        errors.append(f"{label}: baseline register has invalid shape")
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for record in document[collection]:
        if not isinstance(record, dict):
            errors.append(f"{label}: baseline record must be a mapping")
            continue
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier_pattern.fullmatch(
            identifier
        ):
            errors.append(f"{label}: baseline record has malformed identifier")
        elif identifier in indexed:
            errors.append(
                f"{label}: duplicate baseline identifier {identifier}"
            )
        else:
            indexed[identifier] = record
    return indexed


def _validate_identifier_history(
    previous_sources: dict[str, dict[str, Any]],
    previous_claims: dict[str, dict[str, Any]],
    current_sources: dict[str, dict[str, Any]],
    current_claims: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    for identifier, previous in previous_sources.items():
        current = current_sources.get(identifier)
        if current is None:
            errors.append(
                f"research/sources.yaml: allocated identifier {identifier} "
                "must remain in the register"
            )
        elif previous.get("status") in {"retired", "superseded"}:
            if current != previous:
                errors.append(
                    f"research/sources.yaml: inactive record {identifier} "
                    "must not change"
                )
        else:
            changed = sorted(
                field
                for field in SOURCE_IDENTITY_FIELDS
                if current.get(field) != previous.get(field)
            )
            if changed:
                errors.append(
                    f"research/sources.yaml: source identity {identifier} "
                    f"must not change fields: {', '.join(changed)}"
                )

    for identifier, previous in previous_claims.items():
        current = current_claims.get(identifier)
        if current is None:
            errors.append(
                f"research/claims.yaml: allocated identifier {identifier} "
                "must remain in the register"
            )
        elif previous.get("status") == "retired" and current != previous:
            errors.append(
                f"research/claims.yaml: retired record {identifier} "
                "must not change"
            )
        else:
            changed = sorted(
                field
                for field in CLAIM_IDENTITY_FIELDS
                if current.get(field) != previous.get(field)
            )
            if changed:
                errors.append(
                    f"research/claims.yaml: claim identity {identifier} "
                    f"must not change fields: {', '.join(changed)}"
                )

    previous_links = _evidence_links(previous_claims)
    for link in sorted(_evidence_links(current_claims) - previous_links):
        claim_id, source_id, locator, relation = link
        source = current_sources.get(source_id)
        if source and source.get("status") == "retired":
            errors.append(
                f"research/claims.yaml:{claim_id}: new evidence link to "
                f"retired source {source_id} ({locator}; {relation})"
            )


def _evidence_links(
    claims: dict[str, dict[str, Any]],
) -> set[tuple[str, str, str, str]]:
    links: set[tuple[str, str, str, str]] = set()
    for claim_id, claim in claims.items():
        evidence = claim.get("evidence")
        if not isinstance(evidence, list):
            continue
        for item in evidence:
            if not isinstance(item, dict):
                continue
            values = (
                item.get("source"),
                item.get("locator"),
                item.get("relation"),
            )
            if all(isinstance(value, str) for value in values):
                source, locator, relation = values
                links.add((claim_id, source, locator, relation))
    return links


def validate_repository(
    root: Path, baseline_ref: str | None = None
) -> list[str]:
    """Return all structural evidence errors found below *root*."""

    root = root.resolve()
    errors: list[str] = []
    research_dir = root / "research"
    sources_document = _load_yaml(research_dir / "sources.yaml", root, errors)
    claims_document = _load_yaml(research_dir / "claims.yaml", root, errors)
    source_records = _check_root(
        sources_document, "sources.yaml", "sources", errors
    )
    claim_records = _check_root(
        claims_document, "claims.yaml", "claims", errors
    )
    sources = _validate_sources(source_records, errors)
    claims = _validate_claims(claim_records, set(sources), errors)
    _validate_markdown_ids(
        root, set(sources), set(claims), errors
    )

    if baseline_ref:
        revision = _resolve_revision(root, baseline_ref, errors)
        if revision:
            previous_sources_document = _load_yaml_at_revision(
                root, revision, "research/sources.yaml", errors
            )
            previous_claims_document = _load_yaml_at_revision(
                root, revision, "research/claims.yaml", errors
            )
            previous_sources = _index_baseline_records(
                previous_sources_document,
                "sources",
                SOURCE_ID,
                f"{revision}:research/sources.yaml",
                errors,
            )
            previous_claims = _index_baseline_records(
                previous_claims_document,
                "claims",
                CLAIM_ID,
                f"{revision}:research/claims.yaml",
                errors,
            )
            _validate_identifier_history(
                previous_sources,
                previous_claims,
                sources,
                claims,
                errors,
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the validator's repository)",
    )
    parser.add_argument(
        "--baseline-ref",
        help="Git revision whose allocated identifiers must be retained",
    )
    arguments = parser.parse_args(argv)
    errors = validate_repository(arguments.root, arguments.baseline_ref)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        print(
            f"evidence validation failed with {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print("evidence validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
