# Build Doctrine

![build-doctrine: rules for coding agents, and the checks that prove them](images/build-doctrine-banner.png)

**Documentation site**, this document with side navigation and search:
<https://tltaylor1.github.io/build-doctrine/>.

## What this is

This is a rulebook for letting an AI coding agent write code in a
repository you are responsible for, and it comes with the commands that
measure any repository against it.

An agent produces work that looks right and passes review. Every rule
here came from something that actually went wrong, and how the rules
are held is stated once, under [How the standards are
structured](#how-the-standards-are-structured).

**What you can do with it**

- **Score a repository** from 0 to 5 on each rule and read the result as
  a to-do list: `python3 scripts/score.py /path/to/repo`
- **Vet a dependency** before you adopt it. The tool reads install-time
  scripts, committed binaries, known vulnerabilities, and public ratings,
  then prints an acceptance record with an owner and an expiry.
- **Start a project** from `template/`, which carries the hooks,
  pipeline, and container settings that block secrets, unpinned
  dependencies, and unreviewed merges from the first commit.
- **Point an agent at one file** so that the rules apply from the first
  line it writes.

**What is in it**

- **The standards**, opening with the handful of things that make code
  secure in plain words, then stating each as a rule across the code, the
  containers, the pipelines, the platforms, git practice, and working
  with an agent. Products that put a model in their serving path get
  their own rules, and so does the agent that writes the code, because a
  doctrine written by an agent that says nothing about prompt injection
  has a hole in the shape of its own method.
- **The enforcement record**, which pairs every rule with the thing that
  checks it across four tiers, from blocked at commit to checked by a
  human, and scores how far any repository has taken a rule on a
  six-level scale where a false claim scores below silence.
- **The framework coverage**, which reads seven published lists and asks
  what each item teaches rather than which rule can be pointed at it.
  Eighty items from the OWASP Top 10, the API and model lists, STRIDE,
  the NIST secure development framework, the verification standard, and
  SLSA. The rows worth reading are the ones where the honest answer is
  that nothing here does it, and each of those names what would trigger
  writing a rule.
- **The decisions**, forty of them, each recording what was chosen,
  what was rejected, and the failure that produced the rule.
- **The verification procedures**, six passes a person runs before a
  release, each producing evidence rather than an opinion.
- **The vetting reference and the block catalog**, covering what the tool
  reads about outside code, what it cannot see, and which pre-hardened
  blocks have cleared the bar for reuse.
- **The platform baseline**, which covers the settings no file can hold.

**Why you can trust it**

This repository is held to its own rules. It scores itself in its own
pipeline and publishes the number, which is 3.4 of 5. The claims
are checked by machine rather than by memory: one gate compares every
claim that a rule is enforced against the file that enforces it, and
another refetches all seven framework sources and fails when one
publishes a new edition.

Both gates earned their places immediately. The framework check found
that the coverage document had been written from memory and mapped two
superseded editions. The enforcement check found a step in the starter
pipeline named "Secret scan over full history" that scanned only the
commits in the push. It had been that way for months, it read correctly
to anyone reviewing it, and it was wrong.

**Contents:** [What this is](#what-this-is) · [The documents](#the-documents) · [Start here](#start-here) · [Scoring a repository](#scoring-a-repository) · [How the standards are structured](#how-the-standards-are-structured) · [Verifying a project](#verifying-a-project) · [Keeping this accurate](#keeping-this-accurate)

-------------------------------------------------------------------------------

## The documents

| Document | Answers | Read it when |
|---|---|---|
| [STANDARDS.md](STANDARDS.md) | What good looks like, opening with [the fundamentals](STANDARDS.md#the-fundamentals) in plain words | Reading this for the first time, and building something |
| [ENFORCEMENT.md](ENFORCEMENT.md) | What actually checks each rule, in four tiers, and the [checkpoint passes](ENFORCEMENT.md#when-to-run-the-passes) that verify a finished thing | Asking whether a rule is real, and approaching a release |
| [COVERAGE.md](COVERAGE.md) | What the published frameworks teach, and what this doctrine does about each item | Asking whether anything important is missing |
| [DECISIONS.md](DECISIONS.md) | Why each rule exists | Arguing with a rule |
| [USING.md](USING.md) | How to use this: score a project, vet outside code, direct an agent, or start from the template | Picking this up |
| [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) | What this draws on, and why it exists | Understanding the sources and the intent |
| [AGENTS.md](AGENTS.md) | Pointer to the standards, in the format coding agents read | Directing an agent at this repository |
| [VETTING.md](VETTING.md) | What proves code is fit to reuse here: what the vetting tool reads about outside code and what it cannot see, and which blocks of ours have qualified | Adopting a library, an application, or a tool, or building a feature a block already covers |

Also `template/` for the files a project copies at scaffold time,
`scripts/verify.sh` for running the gates, and `.vale/` for the writing rules
as configuration.

The same documents as a site with side navigation and search:
<https://tltaylor1.github.io/build-doctrine/>, generated from these files
at build time by `scripts/build_docs.py` so the site has nothing of its own
to drift.

-------------------------------------------------------------------------------

## Start here

Read these in order.

1. [STANDARDS.md](STANDARDS.md): the rules, opening with [the fundamentals](STANDARDS.md#the-fundamentals) in plain words.
2. [ENFORCEMENT.md](ENFORCEMENT.md): the check that holds each rule, and the rules with no check yet.
3. [COVERAGE.md](COVERAGE.md): what the rules cover and what they leave out.
4. [USING.md](USING.md): the four ways to use the repository.
5. [VETTING.md](VETTING.md): how a dependency or a tool is examined before it is adopted, and the records of each one.
6. [DECISIONS.md](DECISIONS.md): the failure behind each rule.

Directing an AI agent: copy [STANDARDS.md](STANDARDS.md) into the project as
`AGENTS.md`, the format most coding agents read, with a one-line `CLAUDE.md`
pointing to it so Claude Code reads the same source.

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
This repository scores itself in CI on every change, and every
repository that adopts the doctrine scores itself the same way in its
doctrine job. Scores live with the repository they describe, not here:
this tool measures, and it keeps no ledger of what it measured (D-038).

The scorer also writes a badge: `--badge <path>` emits a shields.io
endpoint document carrying the mean level and a color band. A
repository commits its own badge file, embeds it by name, and its
doctrine job scores to a temporary file and compares the two, so a
badge behind the scorer fails the build. manifest-identity's README
carries this line:

```markdown
![build-doctrine score](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/manifest-identity/manifest-identity/main/badges/build-doctrine-score.json)
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
probing, and reading history as an outsider, are the
[checkpoint passes](ENFORCEMENT.md#when-to-run-the-passes) in ENFORCEMENT.md.

Before adopting outside code, a library of significance, an application to
run as it is, or a tool the pipeline executes:

```bash
python3 scripts/vet.py OWNER/NAME --path /path/to/checkout
```

Prints the adoption record the standards require: the Scorecard result with
every check below seven, the Best Practices level, license, last push,
latest release, archived state, and published advisories, then a scan of
the checkout for install scripts, build hooks, fork-privileged workflows,
and committed binaries, and finally the acceptance block to fill in with an
owner and an expiry. Network reads are public; nothing is installed. The
rules it serves are in the "Adopting outside code" section of
[STANDARDS.md](STANDARDS.md); what each reading means and what the tool
cannot see is in [VETTING.md](VETTING.md); and the table of what Scorecard
checks against what the doctrine checks is in [ENFORCEMENT.md](ENFORCEMENT.md).

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
