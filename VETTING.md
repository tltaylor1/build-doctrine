# Vetting outside code

The tool does not tell you whether outside code is safe. Nothing that
reads only what a project publishes about itself and the shapes in a
checkout can. It tells you whether there is a reason to stop before
reading, puts the evidence in one place, and makes the adopter write
down what was checked, what was not, and who owns the gap until the
review that was skipped is done. The security of the adoption is the
sum of the ten rules in the standards, and the tool serves the first
three.

Reuse is one subject with two halves, and this document holds both. Code
from outside is judged before adoption, which is most of what follows.
Code of ours that a project reuses is judged by a different bar, and the
blocks that have cleared it are catalogued at the end. The question is
the same either way: what proves this is fit to use here.

What `scripts/vet.py` reads, what each reading means, what it cannot
tell you, and how the record it prints turns into a decision. The rules
this serves are the "Adopting outside code" section of
[STANDARDS.md](STANDARDS.md); this document is the reference for the
tool, in the shape the Scorecard project uses for its own checks: what
is read, why it matters, and how it is judged.

```bash
python3 scripts/vet.py OWNER/NAME --path /path/to/checkout
```

Every network read is public and unauthenticated. Nothing is installed,
executed, or sent anywhere. The output is a Markdown record meant to be
pasted into the adopting repository's decisions record with the
acceptance block filled in.

-------------------------------------------------------------------------------

## How secure is it

The tool does not answer that with a number, on purpose. A single score
for outside code would be a claim the tool cannot support: it reads
what the project and the platform publish about themselves, and it
reads a checkout for the shapes that hide, but it never reads the code
for what it does. What it gives instead is the evidence in one place,
a list of concerns any of which is reason to stop and look, and the
questions the adopter must answer in writing before the code is
trusted. The security of the adoption is the sum of the acceptance
block: what is pinned, what was analyzed, what runs with what
privilege, and what was not reviewed, with an owner and an expiry.

A record with no concerns and every acceptance line filled is an
adoption made safe. A record with a concern left standing is an
adoption made with a known reason to stop; the decision record must say
why the reason was overruled.

-------------------------------------------------------------------------------

## What is read, and what each reading means

### Scorecard

Source: the OpenSSF Scorecard public API, which scans the repository
weekly. The record prints the overall score and every check below 7,
with the scanner's own reason line. Checks the scanner could not judge
are listed as inconclusive and left out of the score.

| Check below 7 | What it means for adoption | Concern |
|---|---|---|
| Dangerous-Workflow | A workflow pattern lets untrusted input or fork code run with the repository token; the project's own pipeline can be hijacked, and its releases with it | Yes |
| Token-Permissions | Workflow tokens hold more than they need; a compromised step can write to the repository | Yes |
| Vulnerabilities | Open, unfixed vulnerabilities in the project or its dependencies, which you inherit | Yes |
| Binary-Artifacts | Executables committed to the repository, which no reviewer and no scanner reads | Yes |
| Pinned-Dependencies | Their build can change under them without a commit, so what you pin today is not what they built with | Look |
| Maintained | Few commits and no issue activity in ninety days; a fix for the next vulnerability may never come | Look |
| Code-Review | Changes land without a second person; a compromised maintainer account is a compromised release | Look |
| Signed-Releases, Packaging | What you download cannot be tied to their build; build from a pinned commit instead of taking their artifact | Look |
| Branch-Protection, CI-Tests, SAST, Fuzzing | Their own gates are weak; more of the review burden is yours | Look |
| Security-Policy, License, SBOM, CII-Best-Practices, Contributors | Presence checks and self-attestations; informative, not decisive | No |

Where the public scanner has never rated the repository, which is the
case for most small projects, the tool runs the same checks itself if
the Scorecard command is installed and a `GITHUB_AUTH_TOKEN` is in the
environment; the record names which source it read. Install it from
the [Scorecard releases](https://github.com/ossf/scorecard/releases)
with its checksum, the way the pipelines here install every tool. With
neither source the record says so, and that is itself a reading: no
outside rater has looked at the project.

### The platform

Source: the GitHub repository API and its releases and advisories.

| Field | What it means for adoption | Concern |
|---|---|---|
| Archived | The project is closed; nothing will be fixed | Yes |
| License | None detected means you have no right to use it; a detected license is checked for compatibility by the adopter | Yes when none |
| Last push | More than a year ago means the Maintained reading above is the whole story | Yes past a year |
| Latest release | None means every consumer runs from a branch and there is no version to pin a decision to | Look |
| Published advisories | How many vulnerabilities the project has disclosed; zero can mean secure or can mean nobody looked | Look |
| Stars, open issues | Scale of use and of backlog; context only | No |

### Best Practices

Source: the OpenSSF Best Practices badge API. The level is printed
where an entry exists. It is a self-attestation by the maintainers, so
it says what they claim, not what a scanner found, and the doctrine
declines to score a claim as evidence. It is informative about whether
the maintainers think in these terms at all.

### The checkout scan

Source: the files in a local checkout, read without executing anything.
This is the part no rater does, and the part where a compromised
package does its work.

| Finding | What it is | Why it matters | Concern |
|---|---|---|---|
| install script | `preinstall`, `install`, `postinstall`, `prepare` entries in a `package.json` | Runs on the machine of everyone who installs, before any code of theirs is called; the standard vector for a malicious package | Yes |
| build hook | `setup.py` calling `subprocess`, `os.system`, network modules, or a custom `cmdclass`; build hooks declared in `pyproject.toml` | Runs at build or install time with the builder's privileges | Yes |
| workflow | A workflow triggered on `pull_request_target` | Runs fork-supplied code with the repository's token; a contributor can exfiltrate secrets or push | Yes |
| committed binary | A file whose leading bytes are an ELF, Windows, or Mach-O executable | Code nobody can read in review and every text scanner skips | Yes |
| unreadable file | A file the scan could not open | Nothing in it was scanned, so the reading is incomplete until it is | Look |

A finding is a prompt to read the file, not a verdict. A `postinstall`
that compiles a native module and one that fetches a payload look the
same to the scanner. The reading is the control; the finding makes
sure the reading happens.

The scan does not run static analysis or secret scanning. Those are
the adopter's own analyzers, pointed at the checkout, and the
acceptance block asks for the result.

### The dependency scan

Source: the checkout's manifests and lock files, read by trivy when it
is installed, against the public vulnerability databases. Install it
from the [trivy releases](https://github.com/aquasecurity/trivy/releases)
with its checksum, the way the pipelines here install it.

| Reading | What it means for adoption | Concern |
|---|---|---|
| Critical or high with a published fix | The project ships a dependency its own maintainers could have updated and did not; you inherit the vulnerability on day one | Yes |
| Critical or high with no fix | Nothing anyone can do yet; the question is whether the vulnerable path is reachable from how you will run it | Look |
| Medium and low | Recorded for the review; not a reason to stop | No |
| No manifest or lock file found | The scanner had nothing to read; the dependencies are vendored, compiled in, or absent, and the reading is the adopter's | Look |

Where trivy is not installed the record says the tree was not scanned,
and that line is itself a gap the acceptance block must answer.

-------------------------------------------------------------------------------

## Concerns

The record ends its evidence with a list of concerns, each one a line
from the tables above marked "Yes", so the reasons to stop are in one
place instead of scattered across the readings. An empty list means the
tool found nothing that is on its face a reason to stop. It does not
mean the code is safe; it means the remaining questions are the ones
only a reader can answer.

-------------------------------------------------------------------------------

## The acceptance block

The tool prints the block with its fields named and empty. The adopter
fills every line; an empty line is an unanswered question, and the
record is not complete until none remain.

| Line | What goes there |
|---|---|
| Pinned to | The commit or the digest, never a tag or a branch |
| Fetched through | The controlled source, such as a registry mirror or artifact repository; where none exists, say so, and the pin with its checksum is the control |
| Static analysis and secret scan of the checkout | The date the adopter's own analyzers ran on it, and what they found |
| License compatible | Yes or no against the adopting repository's license, with the reasoning |
| Runs with | The privilege, the secrets, and the network destinations it is given; the container rules apply, and egress is limited to what it must reach |
| Sign-in | Behind the program's identity provider, so no account lives only in the adopted application; or a statement that it exposes no sign-in |
| Logs | Which events its audit and access logs produce, and where they are collected so detection can read them |
| Major dependencies | The advisory history of each major dependency, read in the platform's advisory database, and what it showed |
| Not reviewed | What was skipped, in plain words |
| Accepted by | A named owner |
| Expires | The date after which this acceptance no longer stands and the decision is re-made |
| Full review scheduled | The date the review that was skipped will be done |

An expired acceptance decays the way an expired attestation does on the
doctrine's scale: to a claim with nothing behind it.

-------------------------------------------------------------------------------

## What the tool cannot see

- Whether the code does what it says. Nothing here reads intent.
- Whether a maintainer account is compromised. Code-Review and
  Signed-Releases lower the odds; nothing rules it out.
- Whether a dependency is malicious rather than vulnerable. The
  dependency scan reads published vulnerabilities; a package that
  behaves like malware before any advisory exists is caught only by the
  malware-shape scan the adopting pipeline runs, and only once the tree
  is pinned there.
- Anything on a registry that differs from the repository. A package
  published from a different tree than the one on GitHub is invisible
  here; build from the pinned commit rather than taking the published
  artifact, and the difference cannot reach you.

-------------------------------------------------------------------------------

## What qualifies a block of ours as vetted

These are the runtime layer of the three delivery layers, alongside the
scaffold-time `template/` and the pipeline-time workflow: pre-hardened blocks a
project reuses instead of reimplementing. The list is a catalog, not a home for
code. A block lives in the project that proved it until a second project needs
it, which is when a shared library starts removing friction rather than adding
ceremony, and it keeps language-specific code out of a repository whose value is
portable doctrine (D-016).

A block is listed only when it meets every bar below. Anything short of all
four is roadmap, because an unproven block reused widely is a single point of
failure rather than a control.

- It was used in a shipped, reviewed project, not written to fill a catalog.
- It survived that project's mutation testing or hostile probing.
- It has a test in its home project asserting the security property, not just
  behavior.
- It carries no third-party dependency, so there is nothing to pin and the whole
  block can be read in one sitting.

-------------------------------------------------------------------------------

## Tools vetted for the program

The scanners the doctrine's own rules stand on, each read with
`scripts/vet.py` and accepted here, so the acceptance and the reading
sit together. Each expires and is re-read.

### CodeQL, the command line bundles (github/codeql-cli-binaries)

Read September 30, 2026. Scorecard 5 of 10: branch protection,
code review, fuzzing, and signed releases score zero, which is how
GitHub publishes its own analyzer. It is the engine the pipeline
already runs through the platform's action, so running it locally
adds no trust the pipeline had not already placed.

- Pinned to: the bundle release codeql-bundle-v2.27.1, with the
  SHA-256 of each language bundle in the application's `scripts/scan.sh`.
- Fetched through: the release asset on GitHub; no controlled source
  exists, so the checksum is the control.
- Static analysis and secret scan of the checkout: not run; the bundle
  is a compiled tool and the pipeline's own action fetches the same
  release.
- License compatible: the CodeQL terms permit use on public open
  source repositories, which this program is; nothing links to it.
- Runs with: the developer's account locally and the pipeline's
  token; egress to the release host for one fetch; no secret.
- Sign-in: none exposed.
- Logs: the SARIF it writes locally, and the code scanning alerts in
  the pipeline.
- Major dependencies: none beyond the bundle.
- Not reviewed: the bundle's contents.
- Accepted by: Terry Taylor, September 30, 2026.
- Expires: September 30, 2027.
- Full review scheduled: none; the bundle is re-pinned at each
  release the pipeline's action moves to.

### Semgrep (semgrep/semgrep)

Read September 30, 2026. No Scorecard result. LGPL-2.1, last push
the same day, no published advisories, 16,800 stars.

- Pinned to: version 1.178.0 by hash in the application's hashed
  development tree.
- Fetched through: the package index with `--require-hashes`.
- Static analysis and secret scan of the checkout: not run; the
  package installs from hashes and runs only the rules under
  `.semgrep/`, which the repository writes.
- License compatible: LGPL-2.1 for a tool run at commit time, not
  linked into the application; yes.
- Runs with: the developer's environment and the pipeline; metrics
  off; no network at run time; no secret.
- Sign-in: none exposed.
- Logs: its findings on the terminal and in the pipeline log.
- Major dependencies: the hashed tree's audit reads them on every
  change.
- Not reviewed: the engine's source.
- Accepted by: Terry Taylor, September 30, 2026.
- Expires: September 30, 2027.
- Full review scheduled: none.

### ESLint and typescript-eslint (eslint/eslint, typescript-eslint/typescript-eslint)

Read September 30, 2026. Scorecard 6.4 of 10 for each; both score
zero on workflow token permissions, which is their own pipeline's
concern and not this program's. MIT, last push the same day, no
published advisories.

- Pinned to: eslint 10.11.0, typescript-eslint 8.71.0, typescript
  5.9.3, each with its integrity hash in the application's lockfile.
- Fetched through: the package registry, installed with `npm ci
  --ignore-scripts` so no install-time script runs.
- Static analysis and secret scan of the checkout: not run; installed
  from the lockfile, scripts off.
- License compatible: MIT and Apache-2.0 for the checker; yes.
- Runs with: the developer's environment through the hook runner's
  own Node, and the pipeline's pinned Node; no secret.
- Sign-in: none exposed.
- Logs: its findings on the terminal and in the pipeline log.
- Major dependencies: ninety-five packages in the lockfile, audited
  by the registry at install; none flagged September 30, 2026.
- Not reviewed: the ninety-five packages' sources.
- Accepted by: Terry Taylor, September 30, 2026.
- Expires: September 30, 2027.
- Full review scheduled: none.

-------------------------------------------------------------------------------

## Blocks that qualified, and where they live

Each block is proven in secure-expense-mvp. The path is the home to copy from
until reuse justifies extraction.

| Block | Property it protects | Where it is proven |
|---|---|---|
| Formula-injection neutralization for exports | A spreadsheet cell cannot execute as a formula | `app/main.py`, tested in `tests/test_reports.py` |
| Upload validation by declared type, leading bytes, and size | A hostile or mistyped upload is refused before it touches disk | `app/main.py`, tested in `tests/test_receipts.py` |
| Server-generated storage names | A client filename never becomes a filesystem path | `app/main.py`, tested in `tests/test_receipts.py` |
| Rejection reasons that never echo content | A rejected file's bytes never appear in a response | `tests/test_receipts.py` |

Because runtime code is language-specific, this table is Python and FastAPI, the
stack of the only project that has cleared the bar. A block in another language
appears here when a shipped, reviewed project in that language proves one.

-------------------------------------------------------------------------------

## When a shared library is justified

Copy a block from its home project the first time a second project needs it. The
second use is the signal that a shared library removes real friction rather than
adding structure for its own sake. At that point, decide whether the library
lives in its own per-language repository rather than inside this doctrine, so the
doctrine stays portable.

-------------------------------------------------------------------------------

## Blocks not shared yet

Blocks worth sharing once reuse justifies it, recorded rather than built. Each
names why it is not a shared block yet.

- **Object-level authorization dependency.** The single most valuable control,
  but it is coupled to the web framework and the data model, so a reusable form
  needs design rather than extraction. It lives as a documented pattern in the
  standards and a reference implementation in a project.
- **Audited sensitive-download helper.** Proven, but it depends on the
  framework's response type and the project's audit and authorization functions.
  Extracting it cleanly means defining those seams first.
- **Fail-fast configuration loader.** Proven, but its value is in the specific
  variables a project requires, so a generic version risks being a thin wrapper
  that adds a dependency without adding a control.
- **Atomic action-and-audit transaction helper.** Proven as a pattern, but it is
  tied to the database session library, so a reusable form waits until a second
  project confirms the seam.

When one of these is needed in a second project, it is copied, and when the copy
becomes friction, it is extracted and recorded in [DECISIONS.md](DECISIONS.md).
