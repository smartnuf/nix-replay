#!/usr/bin/env python3
"""Validate the mechanically decidable invariants of the D2 evidence base."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import Any

import yaml


SOURCE_ID = re.compile(r"^S\d{4}$")
CLAIM_ID = re.compile(r"^[CHJ]\d{4}$")
MARKDOWN_ID = re.compile(r"\b[SCHJ]\d{4}\b")

SOURCE_CLASSES = {
    "contemporary-primary",
    "first-person-account",
    "institutional-record",
    "independent-analysis",
    "community-report",
    "project-experiment-or-synthesis",
}
CLAIM_KINDS = {"fact", "report", "inference", "hypothesis", "judgement"}
CLAIM_STATUSES = {"supported", "provisional", "open", "contested", "retired"}
CONFIDENCES = {"high", "medium", "low"}
CLAIM_PREFIXES = {
    "fact": "C",
    "report": "C",
    "inference": "H",
    "hypothesis": "H",
    "judgement": "J",
}

SOURCE_FIELDS = {
    "id",
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
}
REQUIRED_SOURCE_FIELDS = SOURCE_FIELDS - {"snapshot_url"}
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


def _load_yaml(path: Path, root: Path, errors: list[str]) -> Any:
    label = _display(path, root)
    try:
        with path.open(encoding="utf-8") as stream:
            return yaml.load(stream, Loader=UniqueKeyLoader)
    except OSError as exc:
        errors.append(f"{label}: cannot read file: {exc}")
    except yaml.YAMLError as exc:
        errors.append(f"{label}: invalid YAML: {exc}")
    return None


def _is_blank(value: Any) -> bool:
    return value is None or isinstance(value, str) and not value.strip()


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
    if document.get("schema_version") != 1:
        errors.append(f"{location}.schema_version: expected 1")
    updated = document.get("updated")
    if not isinstance(updated, (str, dt.date)) or _is_blank(updated):
        errors.append(
            f"{location}.updated: expected a date or non-empty string"
        )
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


def _validate_sources(records: list[Any], errors: list[str]) -> set[str]:
    identifiers: set[str] = set()
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
        elif identifier in identifiers:
            errors.append(f"{location}.id: duplicate identifier {identifier}")
        else:
            identifiers.add(identifier)

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
        for name in ("published", "accessed"):
            value = record.get(name)
            if not isinstance(value, (str, int, dt.date)) or _is_blank(value):
                errors.append(
                    f"{location}.{name}: expected a date, year, or non-empty "
                    "string"
                )
        if "snapshot_url" in record:
            _check_non_empty_string(
                record["snapshot_url"], f"{location}.snapshot_url", errors
            )
    return identifiers


def _validate_claims(
    records: list[Any], source_ids: set[str], errors: list[str]
) -> set[str]:
    identifiers: set[str] = set()
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
        elif identifier in identifiers:
            errors.append(f"{location}.id: duplicate identifier {identifier}")
        else:
            identifiers.add(identifier)

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

        _check_string_list(
            record.get("caveats"), f"{location}.caveats", errors
        )
        reviewed = record.get("reviewed")
        if not isinstance(reviewed, (str, dt.date)) or _is_blank(reviewed):
            errors.append(
                f"{location}.reviewed: expected a date or non-empty string"
            )
    return identifiers


def _validate_markdown_ids(
    research_dir: Path,
    root: Path,
    source_ids: set[str],
    claim_ids: set[str],
    errors: list[str],
) -> None:
    if not research_dir.is_dir():
        errors.append("research: directory does not exist")
        return
    for path in sorted(research_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{_display(path, root)}: cannot read file: {exc}")
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in MARKDOWN_ID.finditer(line):
                identifier = match.group()
                known = source_ids if identifier.startswith("S") else claim_ids
                if identifier not in known:
                    errors.append(
                        f"{_display(path, root)}:{line_number}: unknown "
                        f"identifier {identifier}"
                    )


def validate_repository(root: Path) -> list[str]:
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
    source_ids = _validate_sources(source_records, errors)
    claim_ids = _validate_claims(claim_records, source_ids, errors)
    _validate_markdown_ids(research_dir, root, source_ids, claim_ids, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the validator's repository)",
    )
    arguments = parser.parse_args(argv)
    errors = validate_repository(arguments.root)
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
