# Build Doctrine

This repository holds the standards, enforcement, and verification procedures
that every project here starts from, and a scorer that measures any repository
against them. Most of it is executable configuration and checkpoint procedures
rather than written guidance: every rule records the incident that produced it
and the mechanism that enforces it, which is why it is called doctrine.

It exists so that decisions made once do not get re-derived, and so that an AI
agent works to a known standard from its first generated line.

**Contents:** [The documents](#the-documents) · [Start here](#start-here) · [Scoring a repository](#scoring-a-repository) · [How the standards are structured](#how-the-standards-are-structured) · [Verifying a project](#verifying-a-project) · [Keeping this accurate](#keeping-this-accurate)

-------------------------------------------------------------------------------

## The documents

| Document | Answers | Read it when |
|---|---|---|
| [STANDARDS.md](STANDARDS.md) | What good looks like | Building something |
| [ENFORCEMENT.md](ENFORCEMENT.md) | What actually checks each rule | Asking whether a rule is real |
| [REVIEW.md](REVIEW.md) | How to verify a finished thing | Approaching a release |
| [DECISIONS.md](DECISIONS.md) | Why each rule exists | Arguing with a rule |
| [COMPONENTS.md](COMPONENTS.md) | Pre-hardened blocks a project reuses, and where each is proven | Building a feature a block already covers |
| [ADOPTION.md](ADOPTION.md) | How to start a project from this, and what it commits you to | Starting a project |
| [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) | What this draws on, and why it exists | Understanding the sources and the intent |
| [AGENTS.md](AGENTS.md) | Pointer to the standards, in the format coding agents read | Directing an agent at this repository |
| [SCORES.md](SCORES.md) | The program's repositories scored against the scale, dated | Seeing where each repository actually stands |

Also `template/` for the files a project copies at scaffold time,
`scripts/verify.sh` for running the gates, and `.vale/` for the writing rules
as configuration.

-------------------------------------------------------------------------------

## Start here

Starting a project: [ADOPTION.md](ADOPTION.md).

Directing an AI agent: copy [STANDARDS.md](STANDARDS.md) into the project as
`AGENTS.md`, the format most coding agents read, with a one-line `CLAUDE.md`
pointing to it so Claude Code reads the same source.

Understanding why a rule exists: [DECISIONS.md](DECISIONS.md), which records the
failure behind each one.

-------------------------------------------------------------------------------

## Scoring a repository

```bash
python3 scripts/score.py /path/to/repo --repo owner/name
```

Standard library only; nothing to install. Every rule scores on a six-level
scale defined in [ENFORCEMENT.md](ENFORCEMENT.md#the-scale): 0 absent or
false, 1 stated, 2 attested with a date, 3 checked on demand by a committed
command, 4 gated in CI as a required check, 5 gated with recorded proof that
the gate has fired. The scorer decides levels 0 through 4 from the repository's
files, its history, and the platform's ruleset when `--repo` is given. Level 5
is never inferred: the repository records the proof in its own `doctrine.yml`,
which also names its kind so inapplicable rules are reported rather than
counted, and lets it exclude a rule with a written reason.

Every level up is one specific artifact to add, so the output reads as a to-do
list, and levels can fall when a claim proves false or an attestation expires.
The program's own repositories are scored in [SCORES.md](SCORES.md); this
repository scores itself in CI on every change.

The scorer also writes a badge: `--badge badges/<name>.json` emits a
shields.io endpoint document carrying the mean level and a color band, and
[badges/](badges/) holds one per program repository, regenerated with the
scores. A README embeds its own with the endpoint URL:

```markdown
![build-doctrine score](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tltaylor1/build-doctrine/main/badges/role-call.json)
```

-------------------------------------------------------------------------------

## How the standards are structured

**Every rule is paired with the thing that enforces it, and the unenforced
remainder is labeled.** A rule that depends on somebody remembering is not a
control. [ENFORCEMENT.md](ENFORCEMENT.md) sorts every rule into four tiers by
strength, and the honest bottom tier, the ones no tool checks yet, is written
down rather than implied. Maintaining this baseline means moving rules upward.

**Every tool states what it misses.** A secret scanner that has never been
tested against planted credentials provides confidence without evidence. The
limits recorded here were established by testing the tools, not by reading their
documentation.

**Every rule carries the failure that produced it.** [DECISIONS.md](DECISIONS.md)
records the incident behind each standard: the demo passwords that forced a
repository rebuild, the scanner that let a planted credential through, the
container that served stale code to a reader, the database error that told an
operator nothing.

**Controls are proven by removing them.** Coverage counts lines executed.
Mutation, deleting a control and confirming named tests fail, is the only
evidence that a security test suite would notice a control disappearing.

-------------------------------------------------------------------------------

## Verifying a project

```bash
scripts/verify.sh /path/to/project
```

Runs the real gates and reports what each found: full-history secret scanning,
a broader sweep for credential-shaped strings, tests, static analysis,
dependency audit, hash pinning, bill of materials freshness, workflow action
pinning, base image digest pinning, container image scanning, and whether an
environment file was ever committed. Exits non-zero when a blocking check fails,
so it works as a gate rather than as advice.

A skipped check is not a pass. The script says so.

The passes that need a human, fresh-clone setup, mutation testing, hostile
probing, and reading history as an outsider, are in [REVIEW.md](REVIEW.md).

-------------------------------------------------------------------------------

## Keeping this accurate

A standards repository that nothing is measured against stops describing
reality, and it does so without any visible signal. Two mechanisms prevent that,
and neither depends on anyone remembering.

`scripts/verify.sh` runs against a working project at every checkpoint, and its
exit code is what makes the tiers in [ENFORCEMENT.md](ENFORCEMENT.md) a
description of what happens rather than a statement of intent. Running it
against this repository proves nothing, because this repository has no
application to check.

Vale runs against this repository's own documents as a pre-commit hook and in
continuous integration, and fails on the language these standards prohibit.
gitleaks and the component tests run the same way. The standards are held to the
standard, by the same kind of mechanism they demand of every project.

A correction given during a build is written into these documents at that
moment. The same correction needed twice is a defect here, not in the project
that received it.
