# Truth Compiler Evidence Audit

An evidence-grade audit for founders, independent research teams, and AI builders who need to separate demonstrated facts from generated claims before publishing, pitching, licensing, or shipping.

## Buyer outcome

One bounded project is converted into a portable audit pack containing:

- a source and artifact inventory;
- a claim register labeled `VERIFIED`, `ATTRIBUTED`, `INFERENCE`, `UNSUPPORTED`, or `CONFLICT`;
- SHA-256 evidence manifests and a tamper-evident custody ledger;
- a provenance and architecture lineage map;
- a publication-readiness report with fail-closed findings;
- a remediation queue ranked by evidence risk and commercial impact; and
- a final integrity verification receipt.

The audit does not determine patentability, inventorship, legal ownership, regulatory compliance, scientific truth, or investment value. It identifies what the supplied evidence supports and what remains unproven.

## Pilot scope

| Field | Included |
|---|---|
| Projects | One repository or one bounded document/code archive |
| Source volume | Up to 2 GB supplied by the buyer |
| Claims | Up to 25 material claims |
| Delivery | Encrypted digital audit pack |
| Turnaround target | Five business days after accepted intake |
| Revision | One factual-correction pass within seven calendar days |
| Price | USD 750 one-time pilot |

Anything outside this boundary requires a written change order before work starts.

## Operating pipeline

```text
accepted order
→ private intake
→ source inventory
→ claim extraction
→ evidence mapping
→ conflict and gap analysis
→ publication firewall
→ integrity verification
→ encrypted delivery
→ buyer acceptance receipt
```

Repo Brain may assist discovery. Truth Compiler classifications govern claim status. MASSIVEMAGNETICS-IP records evidence custody and publication decisions. No model prediction can promote a claim to verified without linked evidence.

## Acceptance test

The service is complete only when:

1. every reported claim has a stable ID and classification;
2. every `VERIFIED` claim references at least one hashed evidence item;
3. conflicts and unsupported claims are never silently omitted;
4. the MMIP ledger and object store pass `python -m mmip --root CASE_ROOT verify`;
5. the release candidate passes the sanitizer or is explicitly denied;
6. the delivered manifest lists every file and its SHA-256 digest; and
7. the buyer receives a plain-language limitations statement.

## Required buyer inputs

Use `product/order.schema.json`. Never request credentials, signing keys, live secrets, or unrelated personal data. Private source material must not enter the public repository.

