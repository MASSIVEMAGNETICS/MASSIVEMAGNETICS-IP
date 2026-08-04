# MASSIVEMAGNETICS-IP

> The cryptographically verifiable chain of custody for every invention, architecture, experiment, and technical disclosure created within the Massive Magnetics ecosystem.

MASSIVEMAGNETICS-IP is the authoritative intellectual-property ledger for Massive Magnetics. It records conception, architectural evolution, implementation evidence, prior-art analysis, authorship, public disclosures, and commercialization status for material inventions produced across Victor, Ethica AI, B Heard Network, and related research systems.

This repository contains the **public-safe custody engine**. It deliberately does **not** contain live confidential invention records, unpublished claim drafts, trade secrets, private evidence, or signing keys.

## The custody chain

```text
observation
→ hypothesis
→ first written disclosure
→ architecture
→ implementation
→ experiment
→ revision
→ validated result
→ public disclosure
→ licensing, patent, trade-secret, or abandonment decision
```

## What the engine enforces

- **Append-only disclosure ledger:** canonical JSON events linked by SHA-256 hashes.
- **Content-addressed record store:** every invention, claim, comparison, and evidence manifest is preserved as an immutable object.
- **Evidence vault registry:** artifacts are hashed, described, optionally copied into a private vault, and linked to ledger events.
- **Prior-art and claim records:** structured mappings connect claims to supporting disclosure, implementation evidence, closest art, differentiators, and measurable advantage.
- **Architecture lineage graph:** parent, child, and supersession relationships render as validated Mermaid graphs.
- **Fail-closed publication firewall:** release is denied unless every required review is explicitly satisfied.
- **Publication sanitizer:** detects common secret files, credentials, private keys, and vault material before release.
- **Integrity verification:** one command checks the ledger chain, object hashes, referenced objects, and stored evidence.

## Security architecture

The repository is public. The authoritative data root should be private, access-controlled, encrypted at rest, backed up, and—when appropriate—versioned in a separate private repository.

```text
public source repository          private authoritative data root
────────────────────────          ───────────────────────────────
engine and schemas                append-only event ledger
safe templates                    content-addressed records
tests and CI                      evidence and signed declarations
publication rules                claim drafts and patent strategy
no live disclosures              confidential architecture details
```

The default `.mmip/` data root is ignored by Git. Removing that protection without an approved publication review is a release-control violation.

## Quick start

```bash
python -m mmip --root .mmip init

python -m mmip --root .mmip new-invention \
  --title "Internal invention title" \
  --inventor "Brandon Emery" \
  --first-conception 2026-08-04 \
  --author "Brandon Emery"

python -m mmip --root .mmip append-event \
  --invention-id MMIP-2026-0001 \
  --event-type architecture \
  --summary "Recorded architecture revision" \
  --author "Brandon Emery" \
  --payload-json '{"revision":"R1","source":"private-note-identifier"}'

python -m mmip --root .mmip add-evidence \
  --invention-id MMIP-2026-0001 \
  --artifact /absolute/path/to/artifact \
  --kind source_document \
  --author "Brandon Emery" \
  --copy-to-vault

python -m mmip --root .mmip verify
python -m mmip --root .mmip lineage --output lineage.mmd
python -m mmip sanitize /path/to/publication-candidate
```

Run the test suite without third-party dependencies:

```bash
python -m unittest discover -s tests -v
```

## Publication firewall

The firewall never publishes anything. It only returns `ALLOW` or `DENY`, writes a review report, and optionally records the decision. `ALLOW` requires all of the following:

1. internal disclosure is complete;
2. evidence integrity has been verified;
3. attribution is complete;
4. prior art has been reviewed;
5. patent strategy has been decided;
6. any required patent review is complete;
7. trade-secret exposure has been assessed and removed from the candidate;
8. the candidate has passed repository sanitization;
9. the invention record explicitly permits public release; and
10. the review decision is `publish`.

Unknown, omitted, or ambiguous values deny release. There is no optimistic default.

## Evidence strength and limits

The ledger is **tamper-evident**, not magically immutable. SHA-256 chaining exposes modification, deletion, insertion, and reordering after capture. Stronger proof comes from independent anchors: signed Git commits or tags, trusted timestamp authorities, counsel-controlled copies, witnessed declarations, publication receipts, and redundant read-only backups.

Repository timestamps and self-authored records can support chronology, but they do not by themselves prove patentability, inventorship, novelty, ownership, enablement, or legal priority. See [LEGAL-NOTICE.md](LEGAL-NOTICE.md).

## Existing portfolio material

Historical portfolio documents remain part of this repository. They are strategic research artifacts, not verified legal conclusions. Any novelty or patentability statement must be tied to a documented prior-art search and qualified review.

## Relationship to the Victor architecture

| System | Proof function |
|---|---|
| Chronos / TRACE-0 | What happened during execution |
| Bando Continuity Graph | How knowledge, decisions, and systems connect |
| MASSIVEMAGNETICS-IP | What was disclosed as an invention and what evidence supports it |
| Victor | Generates, tests, and evolves candidate architectures |
| Universe OS | Converts validated architectures into products |
| Massive Magnetics | Owns, protects, licenses, commercializes, or publishes approved work |

## Status

Version `0.1.0` establishes the custody kernel: hash-chained events, immutable objects, invention IDs, evidence registration, integrity verification, lineage rendering, publication checks, sanitization, schemas, tests, and CI.

