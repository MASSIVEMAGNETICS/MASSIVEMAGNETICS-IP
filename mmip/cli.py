from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .canonical import sha256_file
from .evidence import register_evidence, verify_evidence_objects
from .firewall import check_publication
from .ledger import append_event, verify_ledger
from .lineage import render_mermaid
from .object_store import verify_objects
from .records import create_invention, initialize, store_record
from .sanitize import scan_path


def _json_value(raw: str | None) -> dict[str, Any]:
    if raw is None:
        return {}
    if raw.startswith("@"):
        return json.loads(Path(raw[1:]).read_text(encoding="utf-8"))
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON payload must be an object")
    return value


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mmip", description="MASSIVEMAGNETICS-IP custody kernel")
    parser.add_argument("--root", type=Path, default=Path(".mmip"), help="private MMIP data root")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="initialize a private data root")

    new = sub.add_parser("new-invention", help="allocate an invention ID and create the first immutable record")
    new.add_argument("--title", required=True)
    new.add_argument("--inventor", action="append", required=True)
    new.add_argument("--first-conception", required=True, help="YYYY-MM-DD; enter the factual date, never a guess")
    new.add_argument("--author", required=True)

    event = sub.add_parser("append-event", help="append a hash-chained disclosure event")
    event.add_argument("--invention-id")
    event.add_argument("--event-type", required=True)
    event.add_argument("--summary", required=True)
    event.add_argument("--author", required=True)
    event.add_argument("--source-artifact")
    event.add_argument("--payload-json", help="JSON object or @path/to/file.json")

    evidence = sub.add_parser("add-evidence", help="hash and register an evidence artifact")
    evidence.add_argument("--invention-id", required=True)
    evidence.add_argument("--artifact", type=Path, required=True)
    evidence.add_argument("--kind", required=True)
    evidence.add_argument("--author", required=True)
    evidence.add_argument("--copy-to-vault", action="store_true")
    evidence.add_argument("--source-uri")

    register = sub.add_parser("register", help="store an immutable structured record and update its view")
    register.add_argument("--category", choices=["inventions", "prior_art", "claims", "publication_reviews"], required=True)
    register.add_argument("--record-id", required=True)
    register.add_argument("--file", type=Path, required=True)
    register.add_argument("--author", required=True)
    register.add_argument("--invention-id")

    sub.add_parser("verify", help="verify ledger, object store, references, and vault evidence")

    lineage = sub.add_parser("lineage", help="render invention lineage as Mermaid")
    lineage.add_argument("--output", type=Path)

    firewall = sub.add_parser("publication-check", help="run the fail-closed publication firewall")
    firewall.add_argument("--invention-id", required=True)
    firewall.add_argument("--review", type=Path, required=True)
    firewall.add_argument("--author", required=True)

    sanitize = sub.add_parser("sanitize", help="scan a release candidate for private or secret material")
    sanitize.add_argument("target", type=Path)

    hash_command = sub.add_parser("hash", help="compute an artifact SHA-256 digest")
    hash_command.add_argument("artifact", type=Path)
    return parser


def run(args: argparse.Namespace) -> int:
    root: Path = args.root
    if args.command == "init":
        _print(initialize(root))
    elif args.command == "new-invention":
        _print(create_invention(root, args.title, args.inventor, args.first_conception, args.author))
    elif args.command == "append-event":
        _print(append_event(root, author=args.author, event_type=args.event_type, summary=args.summary, payload=_json_value(args.payload_json), invention_id=args.invention_id, source_artifact=args.source_artifact))
    elif args.command == "add-evidence":
        _print(register_evidence(root, args.artifact, invention_id=args.invention_id, kind=args.kind, author=args.author, copy_to_vault=args.copy_to_vault, source_uri=args.source_uri))
    elif args.command == "register":
        record = json.loads(args.file.read_text(encoding="utf-8"))
        digest, view = store_record(root, args.category, args.record_id, record)
        event = append_event(root, author=args.author, event_type={"inventions": "revision", "prior_art": "prior_art_reviewed", "claims": "claim_mapped", "publication_reviews": "publication_reviewed"}[args.category], summary=f"Registered {args.category} record {args.record_id}", invention_id=args.invention_id, source_artifact=str(view.relative_to(root)), payload={"object_sha256": digest})
        _print({"object_sha256": digest, "view": str(view), "event_hash": event["event_hash"]})
    elif args.command == "verify":
        ledger = verify_ledger(root)
        objects = verify_objects(root)
        evidence = verify_evidence_objects(root)
        report = {"valid": ledger["valid"] and objects["valid"] and evidence["valid"], "ledger": ledger, "objects": objects, "evidence": evidence}
        _print(report)
        return 0 if report["valid"] else 2
    elif args.command == "lineage":
        output = render_mermaid(root)
        if args.output:
            args.output.write_text(output, encoding="utf-8")
            _print({"output": str(args.output), "bytes": len(output.encode())})
        else:
            print(output, end="")
    elif args.command == "publication-check":
        review = json.loads(args.review.read_text(encoding="utf-8"))
        report = check_publication(root, args.invention_id, review, args.author)
        _print(report)
        return 0 if report["decision"] == "ALLOW" else 3
    elif args.command == "sanitize":
        report = scan_path(args.target)
        _print(report)
        return 0 if report["safe"] else 4
    elif args.command == "hash":
        _print({"path": str(args.artifact.resolve()), "sha256": sha256_file(args.artifact)})
    return 0


def main() -> None:
    parser = build_parser()
    try:
        code = run(parser.parse_args())
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc), "type": exc.__class__.__name__}), file=sys.stderr)
        code = 2
    raise SystemExit(code)


if __name__ == "__main__":
    main()

