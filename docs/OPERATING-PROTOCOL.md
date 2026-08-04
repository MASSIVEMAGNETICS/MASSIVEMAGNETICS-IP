# Operating Protocol

## 1. Capture privately

Create the invention record at first written disclosure. Use the factual conception date; never backdate, estimate silently, or rewrite history. If the exact date is uncertain, state the uncertainty in the record and preserve the earliest independently verifiable evidence.

## 2. Register evidence without altering it

Hash source artifacts before editing or converting them. Preserve the original file, filename, relevant metadata, source location, contributor, and collection method. Store derivatives as separate evidence records linked to the original.

## 3. Append events

Record material transitions: observation, hypothesis, architecture, implementation, experiment, revision, validation, disclosure, patent decision, licensing decision, abandonment, and supersession. Corrections are new events; prior events are never rewritten.

## 4. Map prior art honestly

Save queries, databases, dates, identifiers, documents reviewed, shared mechanisms, differentiators, and uncertainty. “No match found” means only that the recorded search did not find one. It is not proof that prior art does not exist.

## 5. Map claims to evidence

Every technical claim should point to supporting disclosure, implementation evidence, closest known prior art, the differentiating mechanism, and a measurable advantage. Unsupported adjectives are marketing, not evidence.

## 6. Verify and anchor

Run `mmip verify` after every material capture session. Periodically anchor the current ledger head through independent systems such as signed Git tags, trusted timestamp receipts, counsel-controlled copies, or witnessed declarations. Store each receipt as evidence and record the anchoring event.

## 7. Publish only after explicit approval

Run the sanitizer on the exact candidate bytes. Complete a publication review against the exact repository branch, commit, paper revision, release archive, or media asset. The firewall denies publication unless every check is explicitly satisfied.

## 8. Preserve superseded work

Mark superseded records; do not delete them. Lineage is the proof that an architecture evolved rather than appearing from nowhere.

