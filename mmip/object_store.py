from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_bytes, sha256_bytes, sha256_file
from .storage import atomic_write_bytes


def object_path(root: Path, digest: str) -> Path:
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError("invalid SHA-256 digest")
    return root / "objects" / "sha256" / digest[:2] / f"{digest[2:]}.json"


def store_object(root: Path, value: Any) -> tuple[str, Path]:
    data = canonical_bytes(value)
    digest = sha256_bytes(data)
    destination = object_path(root, digest)
    if destination.exists():
        if destination.read_bytes() != data:
            raise RuntimeError("content-address collision or object corruption")
        return digest, destination
    atomic_write_bytes(destination, data, mode=0o600)
    return digest, destination


def load_object(root: Path, digest: str) -> Any:
    path = object_path(root, digest)
    if not path.exists():
        raise FileNotFoundError(f"missing object {digest}")
    if sha256_file(path) != digest:
        raise ValueError(f"object hash mismatch: {digest}")
    return json.loads(path.read_text(encoding="utf-8"))


def iter_objects(root: Path) -> Iterable[tuple[str, Path]]:
    base = root / "objects" / "sha256"
    if not base.exists():
        return
    for path in sorted(base.glob("??/*.json")):
        digest = path.parent.name + path.stem
        yield digest, path


def verify_objects(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    count = 0
    for digest, path in iter_objects(root):
        count += 1
        actual = sha256_file(path)
        if actual != digest:
            errors.append(f"object {path} hashes to {actual}, expected {digest}")
    return {"valid": not errors, "object_count": count, "errors": errors}

