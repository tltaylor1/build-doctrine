# Scores

The repositories built under this doctrine, against [the scale](ENFORCEMENT.md#the-scale),
scored on 2026-10-04 by `scripts/score.py`, one run per repository from a
local clone with platform access.

This file is written by `scripts/render_scores.py`, and
`scripts/render_scores.py --check` fails when the committed copy no longer
matches what the scorer produces. It is a checkpoint command rather than a
pipeline gate, because it reads clones and the platform that a runner does
not have, which is why this document sits at level 3 of its own scale and
not at 4.

## manifest-identity: 3.5 of 5 across 12 rules (application)

| Rule | Level | Evidence |
|---|---|---|
| readme | 4 | README.md present; this scorer runs in CI |
| license | 4 | LICENSE present; this scorer runs in CI |
| security-policy | 4 | SECURITY.md present; this scorer runs in CI |
| contributing | 4 | CONTRIBUTING.md present; this scorer runs in CI |
| decisions-record | 4 | 88 numbered entries; a test recounts them |
| commit-subjects | 4 | all 15 recent subjects lead with an identifier; CI walks the messages |
| pinned-actions | 5 | all 30 uses are pinned by commit; a workflow audit gates it; proven: https://github.com/manifest-identity/manifest-identity/actions/runs/33565119678 |
| ci-gate | 4 | 12 required checks on the mainline: analyze (actions), analyze (python), application, browser, container, doctrine, floor, links, page, secrets, workflows, writing |
| dependency-updates | 3 | update automation configured |
| run-instructions | 1 | README has a run section with a command block |
| troubleshooting | 1 | README names the likely failures |
| counted-figures | 4 | 4 bold figures; a test recounts them from the source |
| generated-artifact-parity | n/a | not applicable to an application repository |

## build-doctrine: 3.7 of 5 across 10 rules (doctrine)

| Rule | Level | Evidence |
|---|---|---|
| readme | 4 | README.md present; this scorer runs in CI |
| license | 4 | LICENSE present; this scorer runs in CI |
| security-policy | 4 | SECURITY.md present; this scorer runs in CI |
| contributing | 4 | CONTRIBUTING.md present; this scorer runs in CI |
| decisions-record | 4 | 37 numbered entries; a test recounts them |
| commit-subjects | 3 | all 15 recent subjects lead with an identifier; verified by this scorer |
| pinned-actions | 4 | all 15 uses are pinned by commit; a workflow audit gates it |
| ci-gate | 4 | 6 required checks on the mainline: analyze, links, prose, score, secrets, workflows |
| dependency-updates | 3 | update automation configured |
| run-instructions | n/a | not applicable to a doctrine repository |
| troubleshooting | n/a | not applicable to a doctrine repository |
| counted-figures | n/a | not applicable to a doctrine repository |
| generated-artifact-parity | 3 | render_scores.py verifies the generated artifact, checked on demand |

## aws-azure-security-mapping: 2.9 of 5 across 9 rules (reference)

| Rule | Level | Evidence |
|---|---|---|
| readme | 3 | README.md present; checked on demand by this scorer |
| license | 3 | LICENSE present; checked on demand by this scorer |
| security-policy | 3 | SECURITY.md present; checked on demand by this scorer |
| contributing | 3 | CONTRIBUTING.md present; checked on demand by this scorer |
| decisions-record | n/a | not applicable to a reference repository |
| commit-subjects | 3 | all 7 recent subjects lead with an identifier; verified by this scorer |
| pinned-actions | 3 | all 3 uses are pinned by commit; verified by this scorer |
| ci-gate | 4 | 1 required check on the mainline: table |
| dependency-updates | n/a | not applicable to a reference repository |
| run-instructions | 0 | README has no run section |
| troubleshooting | n/a | not applicable to a reference repository |
| counted-figures | n/a | not applicable to a reference repository |
| generated-artifact-parity | 4 | render_table.py verifies the generated artifact and CI runs it |

## SampleDiagrams: 2.0 of 5 across 5 rules (diagrams)

| Rule | Level | Evidence |
|---|---|---|
| readme | 3 | README.md present; checked on demand by this scorer |
| license | 3 | LICENSE present; checked on demand by this scorer |
| security-policy | n/a | not applicable to a diagrams repository |
| contributing | n/a | not applicable to a diagrams repository |
| decisions-record | n/a | not applicable to a diagrams repository |
| commit-subjects | 0 | 2 of 4 recent subjects lack a leading identifier |
| pinned-actions | 3 | all 2 uses are pinned by commit; verified by this scorer |
| ci-gate | 1 | workflows exist but nothing is required to merge |
| dependency-updates | n/a | not applicable to a diagrams repository |
| run-instructions | n/a | not applicable to a diagrams repository |
| troubleshooting | n/a | not applicable to a diagrams repository |
| counted-figures | n/a | not applicable to a diagrams repository |
| generated-artifact-parity | n/a | not applicable to a diagrams repository |

## anki-decks: 1.8 of 5 across 9 rules (study)

| Rule | Level | Evidence |
|---|---|---|
| readme | 3 | README.md present; checked on demand by this scorer |
| license | 3 | LICENSE present; checked on demand by this scorer |
| security-policy | 3 | SECURITY.md present; checked on demand by this scorer |
| contributing | 3 | CONTRIBUTING.md present; checked on demand by this scorer |
| decisions-record | n/a | not applicable to a study repository |
| commit-subjects | 0 | 2 of 15 recent subjects lack a leading identifier |
| pinned-actions | 3 | all 3 uses are pinned by commit; verified by this scorer |
| ci-gate | 1 | workflows exist but nothing is required to merge |
| dependency-updates | n/a | not applicable to a study repository |
| run-instructions | 0 | README has no run section |
| troubleshooting | n/a | not applicable to a study repository |
| counted-figures | n/a | not applicable to a study repository |
| generated-artifact-parity | 0 | no parity check for generated artifacts |

## secure-expense-mvp: 1.6 of 5 across 11 rules (application)

| Rule | Level | Evidence |
|---|---|---|
| readme | 3 | README.md present; checked on demand by this scorer |
| license | 3 | LICENSE present; checked on demand by this scorer |
| security-policy | 3 | SECURITY.md present; checked on demand by this scorer |
| contributing | n/a | excluded: finished on purpose; the README says so and no contributions are invited |
| decisions-record | 0 | no DECISIONS.md |
| commit-subjects | 0 | 1 of 9 recent subjects lack a leading identifier |
| pinned-actions | 4 | all 7 uses are pinned by commit; a workflow audit gates it |
| ci-gate | 1 | workflows exist but nothing is required to merge |
| dependency-updates | 3 | update automation configured |
| run-instructions | 1 | README has a run section with a command block |
| troubleshooting | 0 | README has no troubleshooting section |
| counted-figures | 0 | README states no figures |
| generated-artifact-parity | n/a | not applicable to an application repository |

## tltaylor1: 2.0 of 5 across 3 rules (profile)

| Rule | Level | Evidence |
|---|---|---|
| readme | 3 | README.md present; checked on demand by this scorer |
| license | n/a | not applicable to a profile repository |
| security-policy | n/a | not applicable to a profile repository |
| contributing | n/a | not applicable to a profile repository |
| decisions-record | n/a | not applicable to a profile repository |
| commit-subjects | 0 | 1 of 19 recent subjects lack a leading identifier |
| pinned-actions | 3 | all 2 uses are pinned by commit; verified by this scorer |
| ci-gate | n/a | not applicable to a profile repository |
| dependency-updates | n/a | not applicable to a profile repository |
| run-instructions | n/a | not applicable to a profile repository |
| troubleshooting | n/a | not applicable to a profile repository |
| counted-figures | n/a | not applicable to a profile repository |
| generated-artifact-parity | n/a | not applicable to a profile repository |
