# Adoption

How to start a project from this baseline, and what adopting it commits you to.

**Contents:** [Starting a project](#starting-a-project) · [What is in template](#what-is-in-template) · [Pointing an AI agent at this](#pointing-an-ai-agent-at-this) · [What adoption commits you to](#what-adoption-commits-you-to) · [Adapting rather than following](#adapting-rather-than-following)

-------------------------------------------------------------------------------

## Starting a project

Decide repository visibility first, before anything is committed, per D-009.

```bash
# 1. Create the project and copy the enforcement files in.
mkdir my-project && cd my-project
git init -b main
cp -r /path/to/build-guidelines/template/. .

# 2. Copy the standards in as the agent's instructions. AGENTS.md is the
#    portable format that many coding agents read; CLAUDE.md points to it so
#    Claude Code reads the same single source.
cp /path/to/build-guidelines/STANDARDS.md AGENTS.md
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
checkpoint, and the full procedures in [REVIEW.md](REVIEW.md) before any release
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

The runtime layer is separate: [COMPONENTS.md](COMPONENTS.md) catalogs the
pre-hardened blocks a project reuses and points to where each is proven, so a
block is copied from its home project rather than reimplemented.

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

- Building something new: `STANDARDS.md`, then `ADOPTION.md`.
- Judging whether something is finished: `REVIEW.md`.
- Asking why a rule exists, or arguing against one: `DECISIONS.md`.
- Asking what actually checks a rule: `ENFORCEMENT.md`.
- Reaching for a control before building it: `COMPONENTS.md`.

The agent is expected to work from these documents rather than from its
recollection of them, per D-010.

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
