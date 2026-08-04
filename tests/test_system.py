from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mmip.evidence import register_evidence
from mmip.firewall import evaluate_publication
from mmip.ledger import append_event, ledger_path, verify_ledger
from mmip.lineage import render_mermaid
from mmip.object_store import load_object, store_object, verify_objects
from mmip.records import create_invention, load_record, store_record
from mmip.sanitize import scan_path


class MMIPTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / ".mmip"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_hash_chain_detects_tampering(self) -> None:
        append_event(self.root, author="Tester", event_type="observation", summary="First")
        append_event(self.root, author="Tester", event_type="hypothesis", summary="Second")
        self.assertTrue(verify_ledger(self.root)["valid"])
        path = ledger_path(self.root)
        path.write_text(path.read_text(encoding="utf-8").replace("First", "Altered"), encoding="utf-8")
        report = verify_ledger(self.root)
        self.assertFalse(report["valid"])
        self.assertTrue(any("hash mismatch" in error for error in report["errors"]))

    def test_content_addressed_objects(self) -> None:
        value = {"z": 1, "a": [2, 3]}
        digest, path = store_object(self.root, value)
        self.assertEqual(load_object(self.root, digest), value)
        self.assertEqual(store_object(self.root, value)[0], digest)
        self.assertTrue(path.exists())
        self.assertTrue(verify_objects(self.root)["valid"])

    def test_invention_creation_and_evidence(self) -> None:
        result = create_invention(self.root, "Private test invention", ["Brandon Emery"], "2026-08-04", "Brandon Emery")
        identifier = result["invention"]["invention_id"]
        self.assertEqual(identifier, "MMIP-2026-0001")
        artifact = Path(self.temp.name) / "note.txt"
        artifact.write_text("original evidence", encoding="utf-8")
        evidence = register_evidence(self.root, artifact, invention_id=identifier, kind="source_document", author="Brandon Emery", copy_to_vault=True)
        self.assertTrue((self.root / evidence["manifest"]["stored_path"]).exists())
        self.assertTrue(verify_ledger(self.root)["valid"])

    def test_firewall_is_fail_closed(self) -> None:
        invention = create_invention(self.root, "Private test invention", ["Brandon Emery"], "2026-08-04", "Brandon Emery")["invention"]
        review = {"invention_id": invention["invention_id"], "decision": "publish", "checks": {}}
        denied = evaluate_publication(invention, review)
        self.assertEqual(denied["decision"], "DENY")
        invention["disclosure_policy"].update(public_release_allowed=True, patent_review_complete=True)
        review["checks"] = {
            "internal_disclosure_complete": True,
            "evidence_integrity_verified": True,
            "attribution_complete": True,
            "prior_art_review_complete": True,
            "patent_strategy_decided": True,
            "trade_secret_exposure_assessed": True,
            "trade_secrets_removed": True,
            "repository_sanitized": True,
        }
        allowed = evaluate_publication(invention, review)
        self.assertEqual(allowed["decision"], "ALLOW")

    def test_lineage_rendering(self) -> None:
        first = create_invention(self.root, "Parent", ["Brandon Emery"], "2026-08-04", "Brandon Emery")["invention"]
        second = create_invention(self.root, "Child", ["Brandon Emery"], "2026-08-04", "Brandon Emery")["invention"]
        second["lineage"]["parent_inventions"] = [first["invention_id"]]
        store_record(self.root, "inventions", second["invention_id"], second)
        diagram = render_mermaid(self.root)
        self.assertIn("Parent", diagram)
        self.assertIn("Child", diagram)
        self.assertIn("-->", diagram)

    def test_sanitizer_detects_secret(self) -> None:
        candidate = Path(self.temp.name) / "candidate"
        candidate.mkdir()
        simulated_secret = "API_" + 'KEY="definitely-secret-value"'
        (candidate / ".env").write_text(simulated_secret, encoding="utf-8")
        report = scan_path(candidate)
        self.assertFalse(report["safe"])
        self.assertGreaterEqual(len(report["findings"]), 1)


if __name__ == "__main__":
    unittest.main()
