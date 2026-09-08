# Contributing

This repository is a set of rules, and the rule about rules is that each
one records the incident that produced it and the mechanism that enforces
it. A proposed rule without an incident is advice, and a proposed rule
without an enforcer belongs in the human-checked tier of ENFORCEMENT.md
with that gap named.

The contributions that fit:

- A correction to a rule that reads wrong or has drifted from what the
  program actually does. Open an issue naming the rule and the evidence.
- A scorer check for a rule that is decidable but not yet scored, in
  `scripts/score.py`, with a test in `tests/` that builds a small
  repository and holds the check to a stated level. The scorer is standard
  library only, and stays that way.
- A rejected alternative added to a decision record where one was left
  out, because the record exists to save re-deriving it.

Every change travels a branch and a pull request and must pass the gates
the repository runs on itself: the writing rules, the link check, the
workflow audit, the secret scan, and the scorer's own tests. Commit
subjects lead with an identifier, `D-012:` or `ENFORCEMENT:`, and the body
says why. The writing rules apply to everything, including this file.

By contributing you agree your work is licensed under the repository's
license.
