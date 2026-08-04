from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

from .canonical import utc_now
from .ledger import INVENTION_ID, append_event
from .object_store import load_object, store_object
from .storage import ExclusiveLock, atomic_write_json, read_json

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,127}$")
STATUSES = {"draft_private", "active_research", "validated", "patent_review", "trade_secret", "published", "licensed", "abandoned", "superseded"}
PRIOR_ART_RELATIONSHIPS = {"identical", "overlapping", "adjacent", "influential", "independently_developed", "materially_different"}


def initialize(root: Path) -> dict[str, Any]:
    for relative in (
        "ledger",
        "objects/sha256",
        "views/inventions",
        "views/prior_art",
        "views/claims",
        "views/publication_reviews",
        "views/evidence",
        "vault/private",
        "reports",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)
    config = root / "mmip-config.json"
    if not config.exists():
        atomic_write_json(config, {"format": "MMIP-DATA-1", "created_at": utc_now(), "public_release_default": False})
    return {"root": str(root.resolve()), "format": "MMIP-DATA-1"}


def _required_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def validate_invention(record: dict[str, Any]) -> None:
    required = {"record_type", "schema_version", "invention_id", "title", "status", "inventors", "dates", "problem", "proposed_invention", "novel_elements", "prior_art", "evidence", "claims", "disclosure_policy", "lineage"}
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"invention record missing fields: {missing}")
    if record["record_type"] != "invention" or record["schema_version"] != "MMIP-INVENTION-1":
        raise ValueError("unsupported invention record type or version")
    if not INVENTION_ID.fullmatch(str(record["invention_id"])):
        raise ValueError("invalid invention_id")
    if not isinstance(record["title"], str) or not record["title"].strip():
        raise ValueError("title is required")
    if record["status"] not in STATUSES:
        raise ValueError(f"invalid status: {record['status']}")
    if not isinstance(record["inventors"], list) or not record["inventors"] or not all(isinstance(item, str) and item.strip() for item in record["inventors"]):
        raise ValueError("inventors must contain at least one name")
    for name in ("dates", "problem", "proposed_invention", "prior_art", "evidence", "claims", "disclosure_policy", "lineage"):
        _required_mapping(record[name], name)
    for name in ("novel_elements",):
        if not isinstance(record[name], list):
            raise ValueError(f"{name} must be an array")
    policy = record["disclosure_policy"]
    if not isinstance(policy.get("public_release_allowed"), bool) or not isinstance(policy.get("patent_review_required"), bool):
        raise ValueError("disclosure policy values must be booleans")
    for name in ("parent_inventions", "child_inventions", "supersedes"):
        if not isinstance(record["lineage"].get(name), list):
            raise ValueError(f"lineage.{name} must be an array")


def validate_prior_art(record: dict[str, Any]) -> None:
    required = {"record_type", "schema_version", "comparison_id", "invention_id", "searched_at", "searched_by", "sources", "query_log", "candidate", "relationship", "shared_elements", "differentiators", "claim_implications", "review_status"}
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"prior-art record missing fields: {missing}")
    if record["record_type"] != "prior_art_comparison" or record["schema_version"] != "MMIP-PRIOR-ART-1":
        raise ValueError("unsupported prior-art record type or version")
    if not SAFE_ID.fullmatch(str(record["comparison_id"])) or not INVENTION_ID.fullmatch(str(record["invention_id"])):
        raise ValueError("invalid comparison or invention ID")
    if record["relationship"] not in PRIOR_ART_RELATIONSHIPS:
        raise ValueError("invalid prior-art relationship")
    for name in ("sources", "query_log", "shared_elements", "differentiators", "claim_implications"):
        if not isinstance(record[name], list):
            raise ValueError(f"{name} must be an array")
    _required_mapping(record["candidate"], "candidate")


def validate_claim(record: dict[str, Any]) -> None:
    required = {"record_type", "schema_version", "claim_id", "invention_id", "claim_text", "supporting_disclosures", "implementation_evidence", "closest_prior_art", "differentiating_mechanism", "measurable_advantage", "status", "reviewed_by_counsel"}
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"claim record missing fields: {missing}")
    if record["record_type"] != "claim_map" or record["schema_version"] != "MMIP-CLAIM-1":
        raise ValueError("unsupported claim record type or version")
    if not SAFE_ID.fullmatch(str(record["claim_id"])) or not INVENTION_ID.fullmatch(str(record["invention_id"])):
        raise ValueError("invalid claim or invention ID")
    for name in ("supporting_disclosures", "implementation_evidence", "closest_prior_art"):
        if not isinstance(record[name], list):
            raise ValueError(f"{name} must be an array")
    _required_mapping(record["measurable_advantage"], "measurable_advantage")
    if not isinstance(record["reviewed_by_counsel"], bool):
        raise ValueError("reviewed_by_counsel must be boolean")


def validate_publication_review(record: dict[str, Any]) -> None:
    required = {"record_type", "schema_version", "review_id", "invention_id", "target", "reviewer", "decision", "checks"}
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"publication review missing fields: {missing}")
    if record["record_type"] != "publication_review" or record["schema_version"] != "MMIP-PUBLICATION-1":
        raise ValueError("unsupported publication-review type or version")
    if not SAFE_ID.fullmatch(str(record["review_id"])) or not INVENTION_ID.fullmatch(str(record["invention_id"])):
        raise ValueError("invalid publication-review or invention ID")
    if record["decision"] not in {"publish", "hold", "file_first", "trade_secret", "abandon"}:
        raise ValueError("invalid publication decision")
    checks = _required_mapping(record["checks"], "checks")
    if any(not isinstance(value, bool) for value in checks.values()):
        raise ValueError("publication checks must be booleans")


def next_invention_id(root: Path, year: int) -> str:
    if year < 1900 or year > 9999:
        raise ValueError("invalid invention year")
    view_root = root / "views" / "inventions"
    maximum = 0
    for path in view_root.glob(f"MMIP-{year}-*.json"):
        try:
            maximum = max(maximum, int(path.stem.rsplit("-", 1)[1]))
        except (IndexError, ValueError):
            continue
    return f"MMIP-{year}-{maximum + 1:04d}"


def make_invention(title: str, inventors: list[str], first_conception: str, invention_id: str) -> dict[str, Any]:
    date.fromisoformat(first_conception)
    today = date.today().isoformat()
    return {
        "record_type": "invention",
        "schema_version": "MMIP-INVENTION-1",
        "invention_id": invention_id,
        "title": title.strip(),
        "status": "draft_private",
        "inventors": [name.strip() for name in inventors],
        "contributors": [],
        "dates": {
            "first_conception": first_conception,
            "first_documented": today,
            "first_implementation": None,
            "first_public_disclosure": None,
        },
        "problem": {"description": ""},
        "proposed_invention": {"summary": ""},
        "novel_elements": [],
        "prior_art": {"searched": [], "closest_matches": [], "differentiators": [], "review_complete": False},
        "evidence": {"source_documents": [], "commits": [], "experiments": [], "diagrams": [], "witnesses": []},
        "claims": {"provisional": []},
        "disclosure_policy": {
            "public_release_allowed": False,
            "patent_review_required": True,
            "patent_review_complete": False,
            "trade_secret_candidate": True,
        },
        "lineage": {"parent_inventions": [], "child_inventions": [], "supersedes": []},
    }


def _view_path(root: Path, category: str, record_id: str) -> Path:
    if category not in {"inventions", "prior_art", "claims", "publication_reviews", "evidence"}:
        raise ValueError("invalid record category")
    if not SAFE_ID.fullmatch(record_id):
        raise ValueError("unsafe record ID")
    return root / "views" / category / f"{record_id}.json"


def store_record(root: Path, category: str, record_id: str, record: dict[str, Any]) -> tuple[str, Path]:
    initialize(root)
    if category == "inventions":
        validate_invention(record)
        if record["invention_id"] != record_id:
            raise ValueError("record ID does not match invention_id")
    elif category == "prior_art":
        validate_prior_art(record)
        if record["comparison_id"] != record_id:
            raise ValueError("record ID does not match comparison_id")
    elif category == "claims":
        validate_claim(record)
        if record["claim_id"] != record_id:
            raise ValueError("record ID does not match claim_id")
    elif category == "publication_reviews":
        validate_publication_review(record)
        if record["review_id"] != record_id:
            raise ValueError("record ID does not match review_id")
    digest, _ = store_object(root, record)
    view = _view_path(root, category, record_id)
    atomic_write_json(view, {"record_id": record_id, "category": category, "object_sha256": digest, "updated_at": utc_now()})
    return digest, view


def load_record(root: Path, category: str, record_id: str) -> dict[str, Any]:
    view = read_json(_view_path(root, category, record_id))
    return load_object(root, view["object_sha256"])


def create_invention(root: Path, title: str, inventors: list[str], first_conception: str, author: str) -> dict[str, Any]:
    initialize(root)
    year = date.fromisoformat(first_conception).year
    allocation_lock = root / "views" / "inventions" / ".id-allocation.lock"
    with ExclusiveLock(allocation_lock):
        invention_id = next_invention_id(root, year)
        record = make_invention(title, inventors, first_conception, invention_id)
        validate_invention(record)
        digest, view = store_record(root, "inventions", invention_id, record)
        event = append_event(
            root,
            author=author,
            event_type="first_written_disclosure",
            summary=f"Created private invention record: {title}",
            invention_id=invention_id,
            source_artifact=str(view.relative_to(root)),
            payload={"object_sha256": digest, "record_schema": "MMIP-INVENTION-1"},
        )
    return {"invention": record, "object_sha256": digest, "event_hash": event["event_hash"]}
