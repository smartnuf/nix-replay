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
        self.source_schema_version: object = 2
        self.claim_schema_version: object = 1
        self.updated: object = "2026-09-06"

    def write_fixture(self, markdown: str = "[C0001] [S0001]\n") -> None:
        source_document = {
            "schema_version": self.source_schema_version,
            "updated": self.updated,
            "sources": self.sources,
        }
        claim_document = {
            "schema_version": self.claim_schema_version,
            "updated": self.updated,
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

    def test_malformed_markdown_identifier_is_rejected(self) -> None:
        self.assert_has_error(
            self.errors(markdown="Mistyped claim [C001].\n"),
            "malformed identifier C001",
        )
        self.assert_has_error(
            self.errors(markdown="Mistyped source [S00001].\n"),
            "malformed identifier S00001",
        )
        self.assert_has_error(
            self.errors(markdown="Mistyped claim [C00O1].\n"),
            "malformed identifier C00O1",
        )
        self.assert_has_error(
            self.errors(markdown="Mistyped claim [C0001a].\n"),
            "malformed identifier C0001a",
        )

    def test_identifier_prefix_must_match_claim_kind(self) -> None:
        self.claims[0]["id"] = "H0001"
        self.assert_has_error(
            self.errors(markdown="[H0001]\n"),
            "report records require the C prefix",
        )

    def test_documented_enum_is_enforced(self) -> None:
        self.claims[0]["confidence"] = "absolute"
        self.assert_has_error(self.errors(), ".confidence: expected one of")

    def test_schema_version_requires_an_integer(self) -> None:
        self.source_schema_version = 2.0
        self.claim_schema_version = True
        errors = self.errors()
        self.assert_has_error(errors, "sources.yaml.schema_version")
        self.assert_has_error(errors, "claims.yaml.schema_version")

    def test_register_update_requires_a_real_date(self) -> None:
        self.updated = "2026-02-30"
        self.assert_has_error(self.errors(), ".updated: expected an ISO")

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

    def test_supersession_chain_may_end_at_a_retired_source(self) -> None:
        second = copy.deepcopy(VALID_SOURCE)
        second["id"] = "S0002"
        second["status"] = "retired"
        second["lifecycle_note"] = "No longer competent evidence."
        self.sources.append(second)
        self.sources[0]["status"] = "superseded"
        self.sources[0]["superseded_by"] = "S0002"
        self.sources[0]["lifecycle_note"] = "Replaced by the later source."
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

    def test_source_access_requires_a_real_date(self) -> None:
        self.sources[0]["accessed"] = True
        self.assert_has_error(self.errors(), ".accessed: expected an ISO")

    def test_report_requires_attribution(self) -> None:
        del self.claims[0]["attributed_to"]
        self.assert_has_error(self.errors(), ".attributed_to: expected")

    def test_supported_claim_requires_evidence(self) -> None:
        self.claims[0]["evidence"] = []
        self.assert_has_error(
            self.errors(), "supported claims require evidence"
        )

    def test_supported_claim_requires_a_supporting_relation(self) -> None:
        self.claims[0]["evidence"][0]["relation"] = "contradicts"
        self.claims[0]["evidence"].append(
            {
                "source": "S0001",
                "locator": "research question",
                "relation": "motivates",
            }
        )
        self.assert_has_error(
            self.errors(), "require at least one supporting evidence relation"
        )

    def test_historical_support_can_support_a_claim(self) -> None:
        self.claims[0]["evidence"][0]["relation"] = "historical-support"
        self.assertEqual(self.errors(), [])

    def test_evidence_relation_enum_is_enforced(self) -> None:
        self.claims[0]["evidence"][0]["relation"] = "suports"
        self.assert_has_error(self.errors(), ".relation: expected one of")

    def test_claim_review_requires_a_real_date(self) -> None:
        self.claims[0]["reviewed"] = 2026
        self.assert_has_error(self.errors(), ".reviewed: expected an ISO")

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

    def test_planned_derived_view_paths_are_scanned(self) -> None:
        self.write_fixture()
        derived_paths = (
            self.root / "docs" / "research-synthesis.md",
            self.root / "experiments" / "result.md",
            self.root / "publishing" / "rights.md",
        )
        for path in derived_paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Unknown claim [C9999].\n", encoding="utf-8")
        errors = validate_repository(self.root)
        for path in derived_paths:
            self.assert_has_error(errors, str(path.relative_to(self.root)))

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

    def test_invalid_yaml_timestamp_is_reported(self) -> None:
        self.write_fixture()
        sources_path = self.root / "research" / "sources.yaml"
        sources_path.write_text(
            sources_path.read_text(encoding="utf-8").replace(
                "updated: '2026-09-06'", "updated: 2026-02-30"
            ),
            encoding="utf-8",
        )
        self.assert_has_error(
            validate_repository(self.root), "sources.yaml: invalid YAML"
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

    def test_active_source_identity_must_not_change(self) -> None:
        previous = copy.deepcopy(VALID_SOURCE)
        current = copy.deepcopy(previous)
        current["title"] = "A different source"
        errors: list[str] = []
        _validate_identifier_history(
            {"S0001": previous},
            {},
            {"S0001": current},
            {},
            errors,
        )
        self.assert_has_error(errors, "source identity S0001")

    def test_active_source_reassessment_metadata_can_change(self) -> None:
        previous = copy.deepcopy(VALID_SOURCE)
        current = copy.deepcopy(previous)
        current["scope"] = "A narrower documented interface."
        errors: list[str] = []
        _validate_identifier_history(
            {"S0001": previous},
            {},
            {"S0001": current},
            {},
            errors,
        )
        self.assertEqual(errors, [])

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

    def test_active_claim_identity_must_not_change(self) -> None:
        previous = copy.deepcopy(VALID_CLAIM)
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
        self.assert_has_error(errors, "claim identity C0001")

    def test_active_claim_reassessment_metadata_can_change(self) -> None:
        previous = copy.deepcopy(VALID_CLAIM)
        current = copy.deepcopy(previous)
        current["confidence"] = "medium"
        errors: list[str] = []
        _validate_identifier_history(
            {},
            {"C0001": previous},
            {},
            {"C0001": current},
            errors,
        )
        self.assertEqual(errors, [])

    def test_new_evidence_link_to_retired_source_is_rejected(self) -> None:
        source = copy.deepcopy(VALID_SOURCE)
        source["status"] = "retired"
        source["lifecycle_note"] = "No longer competent evidence."
        errors: list[str] = []
        _validate_identifier_history(
            {"S0001": source},
            {},
            {"S0001": copy.deepcopy(source)},
            {"C0001": copy.deepcopy(VALID_CLAIM)},
            errors,
        )
        self.assert_has_error(errors, "new evidence link to retired source")

    def test_existing_retired_source_link_is_preserved(self) -> None:
        source = copy.deepcopy(VALID_SOURCE)
        source["status"] = "retired"
        source["lifecycle_note"] = "No longer competent evidence."
        claim = copy.deepcopy(VALID_CLAIM)
        errors: list[str] = []
        _validate_identifier_history(
            {"S0001": source},
            {"C0001": claim},
            {"S0001": copy.deepcopy(source)},
            {"C0001": copy.deepcopy(claim)},
            errors,
        )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
