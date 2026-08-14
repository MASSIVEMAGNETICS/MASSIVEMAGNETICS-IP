# Truth Compiler Evidence Audit — Fulfillment SOP

## 1. Accept or reject intake

Validate the order against `order.schema.json`. Reject or request a corrected intake when required fields are absent, scope exceeds the pilot boundary, rights to audit are not affirmed, secrets cannot be transferred safely, or the requested conclusion exceeds the service limits.

## 2. Create a private case

- Allocate a non-identifying case ID: `TCEA-YYYY-NNNN`.
- Create the case only in encrypted private storage.
- Initialize an isolated MMIP root.
- Record the accepted scope, operator, source receipt, and custody event.
- Preserve the original source archive read-only and work from a verified copy.

## 3. Inventory and classify

- Inventory files, commits, documents, tests, releases, and supplied external evidence.
- Hash each material artifact.
- Extract no more than 25 material claims.
- Assign one allowed truth status to every claim.
- Record contradictions, missing evidence, and unverifiable external assertions.

## 4. Verify and review

- Run relevant existing tests; record commands, environment, output, and exit status.
- Separate reproduced results from repository-authored assertions.
- Run the MMIP integrity verifier.
- Run publication sanitization against the delivery candidate.
- Require human approval for the final report and any public-release recommendation.

## 5. Deliver

The encrypted delivery archive must match `deliverable.schema.json` and include:

- `executive-summary.md`
- `claim-register.json`
- `evidence-manifest.json`
- `lineage.mmd`
- `publication-readiness.json`
- `remediation-queue.md`
- `integrity-receipt.json`
- `limitations.md`

Transmit the archive and decryption secret through separate approved channels. Never email both together.

## 6. Close and retain

- Obtain an acceptance or correction receipt.
- Apply the included factual-correction pass when justified by evidence.
- Record the final case hash and closure event.
- Follow the order's retention request and delete working copies when the retention window ends.
- Preserve only operational metadata needed for accounting and proof of delivery unless the buyer authorizes more.

## Failure recovery

- Integrity failure: quarantine the case and rebuild from the verified source copy.
- Secret detected: deny delivery until removed and re-scan.
- Unsupported conclusion requested: label it unsupported; never upgrade the status to satisfy the buyer.
- Scope growth: pause and issue a written change order.
- Transfer failure: invalidate the partial delivery link and produce a new receipt.

