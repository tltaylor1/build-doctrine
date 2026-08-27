# Enforcement

Every rule in [STANDARDS.md](STANDARDS.md) appears here with the thing that
actually checks it. A rule with no mechanism is not a standard, it is a hope,
and hopes are labeled as such below so nobody mistakes one for a control.

**Contents:** [How to read this](#how-to-read-this) · [Blocked at commit](#blocked-at-commit) · [Blocked in the pipeline](#blocked-in-the-pipeline) · [Verified by running it](#verified-by-running-it) · [Checked by a human](#checked-by-a-human) · [What each tool misses](#what-each-tool-misses) · [Moving rules up](#moving-rules-up)

-------------------------------------------------------------------------------

## How to read this

Rules sit in one of four tiers, strongest first:

1. **Blocked at commit.** The commit does not happen. Fastest feedback, and the
   defect never enters history.
2. **Blocked in the pipeline.** The merge does not happen. Catches what needs a
   full environment, and catches anyone who worked around tier one.
3. **Verified by running it.** A command produces evidence. Not automatic, so it
   belongs to a checkpoint in [REVIEW.md](REVIEW.md).
4. **Checked by a human.** No tool exists yet. These are the honest gaps.

The work of maintaining this file is moving rules upward. A rule that stays in
tier four for a year is either unenforceable or not really a standard.

The standards are organized by layer; the tiers here cut across them.
Where each layer's enforcement lives:

| Layer | Mechanical enforcement | Human attestation |
|---|---|---|
| The code | Tiers one and two: hooks, scanners, tests, audits | Decision records and intent, in review |
| The containers | Tier two image scans; tier three verify-by-command | The printed commands run at each release |
| The pipelines | Pinned actions, checksummed tools, workflow lint, required checks | The ruleset's configuration, in the platform baseline |
| The platforms | None yet | Every row of [PLATFORM-BASELINE.md](PLATFORM-BASELINE.md), dated, with expiry |

-------------------------------------------------------------------------------

## Blocked at commit

Installed with `pre-commit install` in a fresh clone. Without that command the
hooks do not exist, which is itself a gap worth knowing about: the pipeline is
what catches a developer who never ran it.

| Rule | Mechanism | Behavior on failure |
|---|---|---|
| No secrets in a commit | gitleaks, via `.pre-commit-config.yaml` | Commit refused |
| No secrets anywhere in history | gitleaks in full-history mode | Run at checkpoints and in the pipeline |
| Writing rules hold | Vale, via `.pre-commit-config.yaml` and CI | Commit refused, and the pipeline fails |
| No common idioms or corporate speak | The vendored proselint lists, via Vale | Commit refused, and the pipeline fails; the house figurative list still catches coined phrases no public list knows |
| Commit messages follow the writing rules | `scripts/check_commit_message.sh` as a commit-msg hook | Commit refused; Vale never reads messages, so this is the only gate on them |

Never bypass a hook with `--no-verify`. A false positive gets an inline
`gitleaks:allow` marker on the flagged line with the reason beside it, which
keeps the hook guarding everything else. Bypassing silences it for the whole
commit, not just the finding.

The "no secrets" rule has three layers, because each fails differently. The
pre-commit hook gives fast local feedback but a developer can skip it. The
pipeline scan catches anyone who did. Push protection, a hosting-platform
feature enabled on the repository, refuses a push containing a detected secret
at the server, which no local bypass defeats. Three layers for one rule is
defense in depth, not redundancy. See D-017.

-------------------------------------------------------------------------------

## Blocked in the pipeline

Defined in `template/.github/workflows/ci.yml`. Every gate fails the build
rather than warning. A warning gate accumulates ignored findings; a blocking
gate makes each one an event that gets fixed or formally accepted.

| Rule | Tool | What it catches |
|---|---|---|
| Behavior matches its tests | pytest | Broken controls, broken features |
| No known-vulnerable dependency | pip-audit | Published vulnerabilities in the pinned tree |
| No obvious insecure code pattern | bandit | Hardcoded credentials, weak randomness, shell injection shapes, assert in production paths |
| No secret in any commit | gitleaks action, full history | Credential patterns across every commit, not just the tip |
| Dependencies install as pinned | `pip install --require-hashes` | A substituted or tampered package fails the install |
| No fixable vulnerability in the image | trivy, `ignore-unfixed` | Operating system and library findings that have a released fix |
| Third-party actions cannot change under us | commit-hash pins in the workflow | A moved tag pointing at new code |
| Dependency updates are reviewed, not automatic | Dependabot pull requests | Drift, with the same gates run before merge |

-------------------------------------------------------------------------------

## Verified by running it

These need a running system or a deliberate experiment, so they belong to the
checkpoints in [REVIEW.md](REVIEW.md) rather than to every commit.

| Rule | Command or method | Evidence produced |
|---|---|---|
| A stranger can run it from the README alone | Clone into an empty directory, follow the document literally, change nothing | It works, or the document is wrong |
| A reader can return to a clean state | Follow the documented teardown, then start again | The stack rebuilds from nothing |
| Controls are actually defended by tests | Mutation: remove a control, run the suite, confirm failures, revert | Named tests fail for each removed control |
| The container runs unprivileged | `docker compose exec app id` | Reports a non-root user |
| The root filesystem is read only | `docker compose exec app sh -c "echo x > /app/probe"` | Fails with a read-only error |
| Capabilities are dropped | `docker compose exec app sh -c "grep CapEff /proc/1/status"` | Reads all zeros |
| The database is not host-reachable | Attempt a connection to the database port on the host | Refused |
| Authorization holds between users | Authenticate as two users, request each other's records | 403 or an empty result, never data |
| Documented figures match reality | Re-run the counts the documents claim | Numbers agree, or the document gets corrected |

-------------------------------------------------------------------------------

## Checked by a human

No mechanism exists for these yet. They are listed rather than hidden, because
an undocumented gap and a considered exclusion look identical in code.

- Whether an intent comment explains why rather than restating what.
- Whether a decision record entry is accurate about what was rejected.
- Whether an acronym was defined at first use, and whether a sentence a machine
  accepts is actually clear to a reader.
- Whether the deliberate exclusions are genuinely deliberate.
- Whether generated code was understood before it was accepted.
- Whether each test asserts the designed property and owns its own state;
  mutation runs prove a control's absence is noticed, but cannot catch a test
  that asserts the wrong property against a correct system.
- Whether the local gate set matches the pipeline's, analyzers included. A
  command comparing tool inventories would move this to tier three; until it
  exists, this is checked when a local pass and a pipeline failure disagree,
  which is one failure too late.
- Whether every pinned surface's watcher claim is true, and whether the
  unwatched pins are still listed as unwatched.
- Whether out-of-band repository state, the description, the rulesets, the
  settings, matches what the documents claim, at each phase close.
- Whether agent narration matched the artifacts it described, checked against
  the execution transcript, not the summary.
- Whether demonstration input was derived from the system or typed from
  assumption. The failure is invisible in a diff and shows up as a finding
  that blames the code for the fixture's mistake.
- Whether the second identical hand-fix was automated, and whether a manual
  check that caught something was pinned into configuration. Both are
  candidates for tier one the moment somebody writes the hook.
- Whether a project's decomposition names its planning method, its rejected
  alternatives, and what the sequence gives up. No tool can judge whether a
  named method is the right one; a tool could at most check that the naming
  exists, which is a candidate for tier three once a second project needs it.
- Whether any unmerged branch has aged past the days a small pull request
  needs. A scheduled listing of stale branches would move this to tier three;
  until it exists, this is seen only when branches are enumerated for another
  reason, which is how twenty-three merged ones went unnoticed. The merged
  half of the rule needs no human check, because the platform deletes at
  merge once the setting is attested in the baseline.

-------------------------------------------------------------------------------

## What each tool misses

A tool trusted beyond its actual reach is worse than no tool, because it buys
confidence it has not earned. These limits were established by testing the
tools, not by reading their documentation.

- **gitleaks** catches high-entropy tokens and credentials next to keyword-like
  names. It misses low-entropy passwords and credentials embedded inside
  database connection strings. Verified by planting fake credentials and
  watching one pass through. The control is keeping secrets out of the
  repository entirely; the hook is a net under that control.
- **bandit** reads Python syntax only. It does not understand authorization, so
  it cannot see a missing ownership check, which is the single most likely
  serious defect in this kind of application.
- **pip-audit** reports published vulnerabilities. It says nothing about a
  package that is malicious, abandoned, or simply the wrong choice. Verifying a
  package resolves to its canonical project remains a human step.
- **trivy** scans what is in the image. It cannot see a misconfiguration in how
  the container is run, which is why the container claims are verified by
  command instead.
- **pytest** proves the behavior somebody thought to write down. Mutation
  testing is what proves the tests would notice a control disappearing.

-------------------------------------------------------------------------------

## Moving rules up

When a human check catches the same class of problem twice, it becomes a
candidate for automation. Record the promotion in
[DECISIONS.md](DECISIONS.md) with the incidents that motivated it.

Two rules have already been promoted this way. The credential-shaped string
sweep in `scripts/verify.sh` exists because demo passwords passed a secret
scanner correctly, and the writing rules moved from the human tier to Vale
because they drifted in this repository's own documents. Vale replaced a
hand-written script once a maintained tool proved it could do the job better;
see D-014.

Known candidates, not yet built:

- A check that fails when a number claimed in a document disagrees with the
  system, such as a test count.
- Ruff for lint and format, which removes style from human review entirely.
- A check that every acronym is defined before its first use.
