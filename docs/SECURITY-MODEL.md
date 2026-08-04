# Security and Evidence Model

## Guarantees provided

- deterministic record serialization;
- SHA-256 content addressing;
- sequential hash chaining;
- detection of modified, deleted, inserted, or reordered ledger events;
- atomic record-view updates;
- lock-guarded ID allocation and ledger appends;
- fail-closed publication review;
- optional evidence copying with post-copy hash verification.

## Guarantees not provided

- trusted time from a self-authored timestamp alone;
- proof that the named author performed the action;
- protection from a hostile administrator deleting the entire vault and every backup;
- confidentiality without encrypted storage and access controls;
- legal conclusions about priority, novelty, ownership, or patentability;
- post-publication restoration of trade-secret status.

## Strong deployment profile

1. Encrypted private storage with least-privilege access.
2. Offline or private-network evidence vault.
3. Hardware-backed signing keys controlled by authorized people.
4. Redundant encrypted backups with restoration tests.
5. Independent periodic timestamp anchors.
6. Private Git history with signed commits or tags.
7. Separate public-source and private-record repositories.
8. Documented contributor and assignment agreements.
9. Counsel review before patent-sensitive disclosure.
10. Incident-response rehearsals for accidental publication.

