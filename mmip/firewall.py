from __future__ import annotations

from pathlib import Path
from typing import Any

from .canonical import utc_now
from .ledger import append_event
from .records import load_record, store_record

REQUIRED_CHECKS = (
    "internal_disclosure_complete",
    "evidence_integrity_verified",
    "attribution_complete",
    "prior_art_review_complete",
    "patent_strategy_decided",
    "trade_secret_exposure_assessed",
    "trade_secrets_removed",
    "repository_sanitized",
)


def evaluate_publication(invention: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    checks = review.get("checks")
    if not isinstance(checks, dict):
        checks = {}
        reasons.append("review.checks is missing or invalid")
    for name in REQUIRED_CHECKS:
        if checks.get(name) is not True:
            reasons.append(f"required check is not explicitly true: {name}")
    policy = invention.get("disclosure_policy", {})
    if policy.get("public_release_allowed") is not True:
        reasons.append("invention policy does not explicitly allow public release")
    if policy.get("patent_review_required") is True and policy.get("patent_review_complete") is not True:
        reasons.append("required patent review is incomplete")
    if review.get("decision") != "publish":
        reasons.append("review decision is not publish")
    if review.get("invention_id") != invention.get("invention_id"):
        reasons.append("review invention_id does not match invention record")
    return {
        "schema_version": "MMIP-FIREWALL-1",
        "invention_id": invention.get("invention_id"),
        "evaluated_at": utc_now(),
        "decision": "ALLOW" if not reasons else "DENY",
        "reasons": reasons,
        "target": review.get("target"),
        "reviewer": review.get("reviewer"),
    }


def check_publication(root: Path, invention_id: str, review: dict[str, Any], author: str, record: bool = True) -> dict[str, Any]:
    invention = load_record(root, "inventions", invention_id)
    report = evaluate_publication(invention, review)
    review_id = str(review.get("review_id") or f"PUB-{invention_id}-{report['evaluated_at'].replace(':', '').replace('-', '')}")
    review_record = {**review, "record_type": "publication_review", "schema_version": "MMIP-PUBLICATION-1", "review_id": review_id, "firewall_report": report}
    digest, view = store_record(root, "publication_reviews", review_id, review_record)
    if record:
        append_event(
            root,
            author=author,
            event_type="publication_reviewed",
            summary=f"Publication firewall decision: {report['decision']}",
            invention_id=invention_id,
            source_artifact=str(view.relative_to(root)),
            payload={"object_sha256": digest, "decision": report["decision"]},
        )
    return report

