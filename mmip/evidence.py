from __future__ import annotations

import mimetypes
import shutil
from pathlib import Path
from typing import Any

from .canonical import sha256_file, utc_now
from .ledger import append_event
from .records import initialize, store_record


def register_evidence(
    root: Path,
    artifact: Path,
    *,
    invention_id: str,
    kind: str,
    author: str,
    copy_to_vault: bool = False,
    source_uri: str | None = None,
) -> dict[str, Any]:
    initialize(root)
    artifact = artifact.expanduser().resolve()
    if not artifact.is_file():
        raise FileNotFoundError(f"evidence artifact not found: {artifact}")
    digest = sha256_file(artifact)
    evidence_id = f"EVD-{digest[:20].upper()}"
    stored_path = None
    if copy_to_vault:
        destination = root / "vault" / "private" / invention_id / f"{digest}{artifact.suffix.lower()}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and sha256_file(destination) != digest:
            raise RuntimeError("vault destination exists with different content")
        if not destination.exists():
            shutil.copy2(artifact, destination)
        if sha256_file(destination) != digest:
            raise RuntimeError("vault copy failed integrity verification")
        stored_path = str(destination.relative_to(root))
    manifest: dict[str, Any] = {
        "record_type": "evidence",
        "schema_version": "MMIP-EVIDENCE-1",
        "evidence_id": evidence_id,
        "invention_id": invention_id,
        "kind": kind,
        "registered_at": utc_now(),
        "registered_by": author,
        "sha256": digest,
        "size_bytes": artifact.stat().st_size,
        "media_type": mimetypes.guess_type(artifact.name)[0] or "application/octet-stream",
        "original_filename": artifact.name,
        "source_uri": source_uri,
        "stored_path": stored_path,
    }
    object_digest, view = store_record(root, "evidence", evidence_id, manifest)
    event = append_event(
        root,
        author=author,
        event_type="evidence_registered",
        summary=f"Registered {kind} evidence {evidence_id}",
        invention_id=invention_id,
        source_artifact=str(view.relative_to(root)),
        payload={"object_sha256": object_digest, "artifact_sha256": digest, "evidence_id": evidence_id},
    )
    return {"manifest": manifest, "object_sha256": object_digest, "event_hash": event["event_hash"]}


def verify_evidence_objects(root: Path) -> dict[str, Any]:
    from .object_store import iter_objects

    errors: list[str] = []
    warnings: list[str] = []
    checked = 0
    for _, path in iter_objects(root):
        import json

        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("record_type") != "evidence":
            continue
        checked += 1
        stored = value.get("stored_path")
        if not stored:
            warnings.append(f"{value.get('evidence_id')}: external evidence was not copied into this vault")
            continue
        artifact = (root / stored).resolve()
        try:
            artifact.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{value.get('evidence_id')}: stored path escapes the vault root")
            continue
        if not artifact.is_file():
            errors.append(f"{value.get('evidence_id')}: stored artifact is missing")
        elif sha256_file(artifact) != value.get("sha256"):
            errors.append(f"{value.get('evidence_id')}: stored artifact hash mismatch")
    return {"valid": not errors, "evidence_checked": checked, "errors": errors, "warnings": warnings}
