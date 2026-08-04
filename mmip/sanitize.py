from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SENSITIVE_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "secrets.json", "mmip-config.private.json"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"}
CONTENT_PATTERNS = {
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(rb"(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}"),
    "aws_access_key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "generic_secret_assignment": re.compile(rb"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*['\"][^'\"\r\n]{8,}"),
}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules", "dist", "build"}


def scan_path(target: Path) -> dict[str, Any]:
    target = target.resolve()
    findings: list[dict[str, str]] = []
    files = [target] if target.is_file() else [path for path in target.rglob("*") if path.is_file() and not any(part in SKIP_DIRS for part in path.parts)]
    for path in files:
        relative = str(path.relative_to(target)) if target.is_dir() else path.name
        lower_parts = {part.lower() for part in path.parts}
        if "vault" in lower_parts or "private" in lower_parts or ".mmip" in lower_parts:
            findings.append({"path": relative, "rule": "private_data_path"})
        if path.name.lower() in SENSITIVE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
            findings.append({"path": relative, "rule": "sensitive_filename"})
        try:
            data = path.read_bytes()
        except OSError as exc:
            findings.append({"path": relative, "rule": f"unreadable:{exc.__class__.__name__}"})
            continue
        if len(data) > 10 * 1024 * 1024:
            findings.append({"path": relative, "rule": "unreviewed_large_file"})
            continue
        for name, pattern in CONTENT_PATTERNS.items():
            if pattern.search(data):
                findings.append({"path": relative, "rule": name})
    return {"safe": not findings, "target": str(target), "files_scanned": len(files), "findings": findings}

