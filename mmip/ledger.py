from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .canonical import canonical_bytes, sha256_bytes, utc_now, validate_utc_timestamp
from .object_store import object_path
from .storage import ExclusiveLock

ZERO_HASH = "0" * 64
EVENT_TYPE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
INVENTION_ID = re.compile(r"^MMIP-[0-9]{4}-[0-9]{4,}$")


def ledger_path(root: Path) -> Path:
    return root / "ledger" / "events.jsonl"


def _hash_event(event_without_hash: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(event_without_hash))


def verify_ledger(root: Path, verify_references: bool = True) -> dict[str, Any]:
    path = ledger_path(root)
    if not path.exists():
        return {"valid": True, "event_count": 0, "head_hash": ZERO_HASH, "errors": [], "warnings": ["ledger does not yet exist"]}

    errors: list[str] = []
    warnings: list[str] = []
    previous = ZERO_HASH
    previous_time = None
    count = 0
    for line_number, raw_line in enumerate(path.read_bytes().splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"line {line_number}: blank lines are not permitted")
            continue
        try:
            event = json.loads(raw_line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc}")
            continue
        count += 1
        required = {"event_version", "sequence", "timestamp", "author", "event_type", "summary", "previous_hash", "payload", "event_hash"}
        missing = sorted(required - event.keys())
        if missing:
            errors.append(f"line {line_number}: missing fields {missing}")
            continue
        if event["event_version"] != "MMIP-EVENT-1":
            errors.append(f"line {line_number}: unsupported event version")
        if event["sequence"] != count:
            errors.append(f"line {line_number}: sequence {event['sequence']} should be {count}")
        if event["previous_hash"] != previous:
            errors.append(f"line {line_number}: previous hash mismatch")
        if not isinstance(event["author"], str) or not event["author"].strip():
            errors.append(f"line {line_number}: author is required")
        if not EVENT_TYPE.fullmatch(str(event["event_type"])):
            errors.append(f"line {line_number}: invalid event type")
        invention_id = event.get("invention_id")
        if invention_id is not None and not INVENTION_ID.fullmatch(str(invention_id)):
            errors.append(f"line {line_number}: invalid invention ID")
        try:
            current_time = validate_utc_timestamp(event["timestamp"])
            if previous_time is not None and current_time < previous_time:
                errors.append(f"line {line_number}: timestamp moves backward")
            previous_time = current_time
        except (TypeError, ValueError) as exc:
            errors.append(f"line {line_number}: {exc}")
        claimed = event.pop("event_hash")
        actual = _hash_event(event)
        event["event_hash"] = claimed
        if claimed != actual:
            errors.append(f"line {line_number}: event hash mismatch")
        previous = claimed

        if verify_references:
            digest = event.get("payload", {}).get("object_sha256") if isinstance(event.get("payload"), dict) else None
            if digest:
                try:
                    candidate = object_path(root, digest)
                    if not candidate.exists():
                        errors.append(f"line {line_number}: referenced object {digest} is missing")
                    elif sha256_bytes(candidate.read_bytes()) != digest:
                        errors.append(f"line {line_number}: referenced object {digest} is corrupt")
                except ValueError as exc:
                    errors.append(f"line {line_number}: {exc}")

    return {"valid": not errors, "event_count": count, "head_hash": previous, "errors": errors, "warnings": warnings}


def append_event(
    root: Path,
    *,
    author: str,
    event_type: str,
    summary: str,
    payload: dict[str, Any] | None = None,
    invention_id: str | None = None,
    source_artifact: str | None = None,
    relationships: list[dict[str, str]] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    if not author.strip() or not summary.strip():
        raise ValueError("author and summary are required")
    if not EVENT_TYPE.fullmatch(event_type):
        raise ValueError("event type must be lowercase snake_case")
    if invention_id is not None and not INVENTION_ID.fullmatch(invention_id):
        raise ValueError("invalid invention ID")
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with ExclusiveLock(path.with_suffix(".lock")):
        report = verify_ledger(root)
        if not report["valid"]:
            raise RuntimeError(f"refusing to append to invalid ledger: {report['errors']}")
        core: dict[str, Any] = {
            "event_version": "MMIP-EVENT-1",
            "sequence": report["event_count"] + 1,
            "timestamp": timestamp or utc_now(),
            "author": author.strip(),
            "event_type": event_type,
            "summary": summary.strip(),
            "previous_hash": report["head_hash"],
            "payload": payload or {},
        }
        if invention_id:
            core["invention_id"] = invention_id
        if source_artifact:
            core["source_artifact"] = source_artifact
        if relationships:
            core["relationships"] = relationships
        validate_utc_timestamp(core["timestamp"])
        event = {**core, "event_hash": _hash_event(core)}
        encoded = canonical_bytes(event) + b"\n"
        fd = os.open(path, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        try:
            os.write(fd, encoded)
            os.fsync(fd)
        finally:
            os.close(fd)
        return event

