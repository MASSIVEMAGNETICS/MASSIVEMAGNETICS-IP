# Security Policy

## Never commit

- live unpublished invention records;
- claim drafts or counsel communications;
- source evidence containing trade secrets;
- private keys, credentials, access tokens, or recovery codes;
- personal data that is not strictly required for attribution;
- the private `.mmip/` data root.

## Reporting

Do not open a public issue for a suspected leak. Preserve the URL, commit SHA, file path, discovery time, and a local hash of the exposed artifact, then contact the repository owner privately.

## Incident response

1. Stop further publication and disable affected credentials.
2. Preserve forensic evidence before rewriting or deleting anything.
3. Identify every clone, fork, cache, release, package, and deployment that received the material.
4. Rotate secrets and assess whether trade-secret or patent strategy was affected.
5. Record the incident and remediation in the private ledger.
6. Coordinate takedown or history-rewrite decisions with qualified counsel.

Deleting a GitHub file does not guarantee that previously public content has become secret again.

