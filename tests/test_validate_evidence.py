from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.validate_evidence import (
    _validate_identifier_history,
    validate_repository,
)


VALID_SOURCE = {
    "id": "S0001",
    "status": "active",
    "title": "Example source",
    "creators": ["Example Author"],
    "published": 2026,
    "kind": "manual",
    "publisher": "Example project",
    "url": "https://example.test/source",
    "version": "1.0",
    "accessed": "2026-09-06",
    "source_class": "contemporary-primary",
    "authority": "Versioned project documentation.",
    "scope": "The documented interface in version 1.0.",
    "rights_status": "not-assessed-for-republication",
    "intended_use": "citation-only",
    "notes": "Test fixture.",
}

VALID_CLAIM = {
    "id": "C0001",
    "statement": "The example manual documents an interface.",
    "kind": "report",
    "status": "supported",
    "confidence": "high",
    "attributed_to": "Example source",
    "scope": "The version 1.0 manual.",
    "evidence": [
        {
            "source": "S0001",
            "locator": "interface section",
            "relation": "supports",
        }
    ],
    "caveats": [],
    "relevance": "Validator test fixture.",
    "reviewed": "2026-09-06",
}


class EvidenceValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        (self.root / "research").mkdir()
        self.sources = [copy.deepcopy(VALID_SOURCE)]
        self.claims = [copy.deepcopy(VALID_CLAIM)]

    def write_fixture(self, markdown: str = "[C0001] [S0001]\n") -> None:
        source_document = {
            "schema_version": 2,
            "updated": "2026-09-06",
            "sources": self.sources,
        }
        claim_document = {
            "schema_version": 1,
            "updated": "2026-09-06",
            "claims": self.claims,
        }
        (self.root / "research" / "sources.yaml").write_text(
            yaml.safe_dump(source_document, sort_keys=False), encoding="utf-8"
        )
        (self.root / "research" / "claims.yaml").write_text(
            yaml.safe_dump(claim_document, sort_keys=False), encoding="utf-8"
        )
        (self.root / "research" / "notes.md").write_text(
            markdown, encoding="utf-8"
        )

    def errors(self, markdown: str = "[C0001] [S0001]\n") -> list[str]:
        self.write_fixture(markdown)
        return validate_repository(self.root)

    def assert_has_error(self, errors: list[str], text: str) -> None:
        self.assertTrue(
            any(text in error for error in errors),
            f"expected error containing {text!r}, got {errors!r}",
        )

    def test_valid_repository_passes(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_duplicate_source_identifier_is_rejected(self) -> None:
        self.sources.append(copy.deepcopy(VALID_SOURCE))
        self.assert_has_error(self.errors(), "duplicate identifier S0001")

    def test_malformed_claim_identifier_is_rejected(self) -> None:
        self.claims[0]["id"] = "C12"
        self.assert_has_error(self.errors(markdown=""), "four digits")

    def test_identifier_prefix_must_match_claim_kind(self) -> None:
        self.claims[0]["id"] = "H0001"
        self.assert_has_error(
            self.errors(markdown="[H0001]\n"),
            "report records require the C prefix",
        )

    def test_documented_enum_is_enforced(self) -> None:
        self.claims[0]["confidence"] = "absolute"
        self.assert_has_error(self.errors(), ".confidence: expected one of")

    def test_required_source_field_is_enforced(self) -> None:
        del self.sources[0]["rights_status"]
        self.assert_has_error(self.errors(), "rights_status")

    def test_source_requires_a_creator(self) -> None:
        self.sources[0]["creators"] = []
        self.assert_has_error(self.errors(), ".creators: must not be empty")

    def test_retired_source_is_retained_with_a_reason(self) -> None:
        self.sources[0]["status"] = "retired"
        self.sources[0]["lifecycle_note"] = "No longer competent evidence."
        self.assertEqual(self.errors(), [])

    def test_retired_source_requires_a_reason(self) -> None:
        self.sources[0]["status"] = "retired"
        self.assert_has_error(
            self.errors(), "retired sources require lifecycle_note"
        )

    def test_valid_source_supersession_passes(self) -> None:
        second = copy.deepcopy(VALID_SOURCE)
        second["id"] = "S0002"
        self.sources.append(second)
        self.sources[0]["status"] = "superseded"
        self.sources[0]["superseded_by"] = "S0002"
        self.sources[0]["lifecycle_note"] = "Replaced by a current edition."
        self.assertEqual(self.errors(), [])

    def test_supersession_target_must_exist(self) -> None:
        self.sources[0]["status"] = "superseded"
        self.sources[0]["superseded_by"] = "S0002"
        self.sources[0]["lifecycle_note"] = "Replaced by a current edition."
        self.assert_has_error(
            self.errors(), "unknown source identifier S0002"
        )

    def test_source_supersession_cycle_is_rejected(self) -> None:
        second = copy.deepcopy(VALID_SOURCE)
        second["id"] = "S0002"
        self.sources.append(second)
        for source, target in zip(self.sources, ("S0002", "S0001")):
            source["status"] = "superseded"
            source["superseded_by"] = target
            source["lifecycle_note"] = "Invalid test cycle."
        self.assert_has_error(self.errors(), "supersession cycle")

    def test_blank_intended_use_is_rejected(self) -> None:
        self.sources[0]["intended_use"] = ""
        self.assert_has_error(
            self.errors(), ".intended_use: must not be blank"
        )

    def test_report_requires_attribution(self) -> None:
        del self.claims[0]["attributed_to"]
        self.assert_has_error(self.errors(), ".attributed_to: expected")

    def test_unknown_evidence_source_is_rejected(self) -> None:
        self.claims[0]["evidence"][0]["source"] = "S9999"
        self.assert_has_error(self.errors(), "unknown source identifier S9999")

    def test_unknown_markdown_source_is_rejected(self) -> None:
        self.assert_has_error(
            self.errors(markdown="Research lead [S9999].\n"),
            "unknown identifier S9999",
        )

    def test_unknown_markdown_claim_is_rejected(self) -> None:
        self.assert_has_error(
            self.errors(markdown="Unsupported statement [H9999].\n"),
            "unknown identifier H9999",
        )

    def test_duplicate_yaml_mapping_key_is_rejected(self) -> None:
        self.write_fixture()
        claims_path = self.root / "research" / "claims.yaml"
        claims_path.write_text(
            claims_path.read_text(encoding="utf-8") + "updated: 2026-09-06\n",
            encoding="utf-8",
        )
        self.assert_has_error(
            validate_repository(self.root), "duplicate key 'updated'"
        )

    def test_allocated_identifiers_must_remain_in_registers(self) -> None:
        errors: list[str] = []
        _validate_identifier_history(
            {"S0001": copy.deepcopy(VALID_SOURCE)},
            {"C0001": copy.deepcopy(VALID_CLAIM)},
            {},
            {},
            errors,
        )
        self.assert_has_error(errors, "allocated identifier S0001")
        self.assert_has_error(errors, "allocated identifier C0001")

    def test_inactive_source_record_must_not_change(self) -> None:
        previous = copy.deepcopy(VALID_SOURCE)
        previous["status"] = "retired"
        previous["lifecycle_note"] = "Retained test record."
        current = copy.deepcopy(previous)
        current["title"] = "Repurposed source"
        errors: list[str] = []
        _validate_identifier_history(
            {"S0001": previous},
            {},
            {"S0001": current},
            {},
            errors,
        )
        self.assert_has_error(errors, "inactive record S0001 must not change")

    def test_retired_claim_record_must_not_change(self) -> None:
        previous = copy.deepcopy(VALID_CLAIM)
        previous["status"] = "retired"
        current = copy.deepcopy(previous)
        current["statement"] = "A different proposition."
        errors: list[str] = []
        _validate_identifier_history(
            {},
            {"C0001": previous},
            {},
            {"C0001": current},
            errors,
        )
        self.assert_has_error(errors, "retired record C0001 must not change")


if __name__ == "__main__":
    unittest.main()
