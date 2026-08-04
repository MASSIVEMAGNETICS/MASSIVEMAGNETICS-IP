# Contributing

Contributions must contain public-safe engine code, schemas, tests, or documentation only. Do not submit undisclosed inventions, confidential architecture details, claim drafts, evidence artifacts, personal data, secrets, or attorney communications.

Every change should:

1. preserve append-only and fail-closed behavior;
2. avoid weakening canonicalization or integrity checks;
3. include tests for security-relevant behavior;
4. state whether the change affects record compatibility;
5. pass `python -m unittest discover -s tests -v`; and
6. pass `python -m mmip sanitize .`.

By contributing, you represent that you have authority to submit the material. No contributor license or patent grant is implied beyond a separately executed written agreement.

