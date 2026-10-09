# Using this

How to use this repository: score a project, vet outside code, direct an agent, or start a project from the template, and what the last one commits you to.

**Contents:** [Four ways to use this](#four-ways-to-use-this) · [Starting a project](#starting-a-project) · [What is in template](#what-is-in-template) · [Pointing an AI agent at this](#pointing-an-ai-agent-at-this) · [What adoption commits you to](#what-adoption-commits-you-to) · [Adapting rather than following](#adapting-rather-than-following)

-------------------------------------------------------------------------------

## Four ways to use this

In increasing order of commitment:

1. **Score a repository you already have.** `python3 scripts/score.py
   /path/to/repo --repo owner/name` prints a level per rule and reads as
   a to-do list. Standard library only; nothing to adopt.
2. **Vet outside code before taking it.** `python3 scripts/vet.py
   OWNER/NAME --path /path/to/checkout` prints the adoption record;
   [VETTING.md](VETTING.md) explains every reading.
3. **Point an AI agent at it.** Copy `STANDARDS.md` into the project as
   `AGENTS.md`, so the rules apply from the first generated line. This
   is the use the doctrine was built for; the section below says how.
4. **Start a project from the template.** The steps below. This commits
   the project to the gates, the decision record, and the verification
   passes, and the section on what adoption commits you to says what
   that costs and when not to do it.

-------------------------------------------------------------------------------

## Starting a project

Two decisions come before anything is committed. Visibility, per D-009.
And the name, per D-028: the day a name is chosen, check that it is
free as a GitHub account or organization name, on the package index
the project would publish to, and as a domain if one will ever matter,
and hold whichever of those the project will use. Checking is not
holding: GitHub and the package indexes remove names held empty, so a
hold is an organization with a profile that points at the project, or
a minimal real package under the name.

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://github.com/<name>       # 404 means free
curl -s -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/<name>/json  # 404 means free
```

```bash
# 1. Create the project and copy the enforcement files in.
mkdir my-project && cd my-project
git init -b main
cp -r /path/to/build-doctrine/template/. .

# 2. Copy the standards in as the agent's instructions. AGENTS.md is the
#    portable format that many coding agents read; CLAUDE.md points to it so
#    Claude Code reads the same single source.
cp /path/to/build-doctrine/STANDARDS.md AGENTS.md
printf 'The project standards are in AGENTS.md. Read it before doing anything.\n' > CLAUDE.md

# 3. Install the commit-blocking hooks. Without this they do not exist.
pre-commit install

# 4. First commit, before any application code.
git add -A && git commit -m "Add project standards and repository hygiene"
```

The order matters. The ignore rules and the secret hook exist before the first
line of application code, so there is no window during which a mistake is
permanent.

Then run `scripts/verify.sh` from this repository against the project at each
checkpoint, and the full [checkpoint passes](ENFORCEMENT.md#when-to-run-the-passes) before any release
or visibility change.

-------------------------------------------------------------------------------

## What is in template

| File | Role |
|---|---|
| `.gitignore` | Environment files, keys, local state, build artifacts |
| `.pre-commit-config.yaml` | Secret scanning that blocks the commit |
| `.github/workflows/ci.yml` | Tests, static analysis, dependency audit, full-history secret scan, image build and scan |
| `.github/dependabot.yml` | Dependency updates as reviewed pull requests |
| `Dockerfile` | Digest-pinned base, hash-verified install, non-root user |
| `docker-compose.yml` | Read-only filesystem, dropped capabilities, resource caps, no published database port |
| `.dockerignore` | Keeps environment files, tests, and local state out of the build context |
| `pyproject.toml` | Test configuration |

These are copied unchanged and then adjusted for the project. Adjustments that
weaken a control get recorded as decisions in the project, with the reason.

The runtime layer is separate: [VETTING.md](VETTING.md) describes the proven
patterns a project builds from, each with the property it protects and the test
that proves it, so a control is built to a known shape rather than invented
again.

-------------------------------------------------------------------------------

## Pointing an AI agent at this

Copy `STANDARDS.md` into the project as `AGENTS.md`, the open instruction-file
format that many coding agents read natively, and add a one-line `CLAUDE.md`
pointing to it so Claude Code reads the same source. That doctrine is what makes
the standards apply from the first generated line rather than being retrofitted
in review. Keeping one file as the source, with the other as a pointer, avoids
two copies drifting apart.

For work that spans projects, point the agent at this repository directly and
tell it which document applies:

- Building something new: `STANDARDS.md`, then `USING.md`.
- Judging whether something is finished: the checkpoint passes in
  `ENFORCEMENT.md`.
- Asking why a rule exists, or arguing against one: `DECISIONS.md`.
- Asking what actually checks a rule: `ENFORCEMENT.md`.
- Reaching for a control before building it: the proven patterns in
  `VETTING.md`.

The agent is expected to work from these documents rather than from its
recollection of them, per D-010.

-------------------------------------------------------------------------------

## Keeping agent-written code clean

An agent writes code that works and still leaves the codebase worse.
These checks catch the four ways it does that. You reach for them in any
repository where an agent writes code.

**It writes a second copy instead of finding the first.**
`scripts/check_repetition.py` fails when a change adds duplicated lines.
It compares the change with the branch it merges into, so old copies do
not block you, and editing one does not either. On a branch that copies
a ten-line function from `orders.py` into `refunds.py`, it prints:

```text
Clone found (python)
 - orders.py [1:10 - 10:19] (10 lines, 63 tokens)
   refunds.py [1:17 - 10:19]
Found 1 clones.
repetition: the change adds to it, 0 duplicated lines on main and 10 with it; the findings listed above show where
```

The fix is to call the code that exists, or to move the shared part into
one place both callers use. To keep a copy on purpose, put it between
`jscpd:ignore-start` and `jscpd:ignore-end` comments with the reason
beside it.

**It leaves code nothing uses.**
`scripts/check_dead_code.py` fails when a change adds code nothing
calls. It counts only what jscpd is sure of: unused files, exports,
functions, variables, and imports. On a branch that adds a function
nothing calls to an application with two such lines already, it prints:

```text
dead code: the change adds to it, 2 dead lines on origin/main and 4 with it; the findings listed above show where
```

The fix is to delete it. An import kept for what it does when it loads,
such as registering database tables, gets a comment saying so.

**It adds one more branch to a long function.**
Turn on the linter's complexity limit at ten branches, ruff's C901 for
Python. Mark each function already past it and count the marks in a
test, so the list can only shrink on purpose. The fix for a new one is
to split the function.

**It makes two parts depend on each other.**
A short test that reads the imports fails when two parts of the
application import each other. List the pairs that exist, each with its
reason. The fix is to move what both need into a part both can use.

**When a check fails.** Fix the code before reaching for a mark. A mark
is for a choice, and its reason belongs where a reviewer reads it.

**What they do not do.** They do not judge whether a design is good,
and they do not replace reading the change. The first two run in this
repository's pipeline and in any that adopts it; the last two are set up
in a repository's own linter and tests. The example outputs leave out
jscpd's summary table and the line naming its temporary report.

**Running them locally.** Each script fetches the pinned jscpd release,
checks its checksum, and runs the same comparison the pipeline does:

```bash
python3 scripts/check_repetition.py /path/to/repo --base origin/main
python3 scripts/check_dead_code.py /path/to/repo --base origin/main
```

**Looking further.** jscpd can also find renamed copies, copies with a
few lines changed, and code that does the same job written differently.
Those passes also find code that only looks alike, so run them by hand
and read what they report as leads:

```bash
jscpd . --ignore-identifiers --ignore-literals    # renamed copies
jscpd . --max-gap-lines 2                         # copies with a few lines changed
jscpd . --semantic                                # the same job, written differently
```

-------------------------------------------------------------------------------

## Installing the skills

How to give a coding agent this repository's procedures as skills, and
what a skill does not replace. You reach for it when an agent will
adopt outside code, which every project does sooner or later.

This repository is a Claude Code plugin marketplace with one plugin. In
a Claude Code session:

```text
/plugin marketplace add tltaylor1/build-doctrine
/plugin install build-doctrine@build-doctrine
```

The plugin holds one skill, `vet-dependency`. Asked to adopt or
evaluate a library, an application, or a tool, the agent runs
`scripts/vet.py` on a shallow checkout, reads each concern against
[VETTING.md](VETTING.md), and hands back the adoption record with the
acceptance block unfilled, because only a person accepts. It can also be
run by name as `/build-doctrine:vet-dependency`.

**What a skill does not do.** It loads only when the agent judges a
request matches it, so it carries procedures and never the rules. The
rules stay in the project's `AGENTS.md`, which is in force for every
line. The plugin tracks this repository's main branch; add
`#<tag>` to the marketplace address to hold one version instead.
Installing any plugin runs its files with your privileges, so read it
first, as you would any outside code.

-------------------------------------------------------------------------------

## What adoption commits you to

Adopting the baseline is not free, and the costs are real:

- Every dependency change becomes a recompile, a bill of materials
  regeneration, and an audit.
- Blocking gates mean a broken gate stops work until it is fixed or formally
  accepted.
- The decision record must be maintained during the build. Written afterward, it
  records what someone remembers rather than what was decided.
- Fresh-clone verification and mutation testing take time that produces no
  features.

The trade is that the resulting work can be defended line by line. For a
regulated environment, or any system whose failure modes matter, that is worth
the cost. For a weekend experiment it is overhead, and the honest answer is not
to adopt the whole baseline.

-------------------------------------------------------------------------------

## Adapting rather than following

These standards came from web applications handling sensitive records. Some
rules are specific to that shape.

Where a rule does not apply, record why in the project's own decision record.
An entry saying a control was considered and does not apply is worth more than
silence, because silence and oversight look identical.

Where the baseline is wrong, fix it here and record the reason, so the next
project inherits the improvement rather than rediscovering the problem.
