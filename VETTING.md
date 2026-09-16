# Vetting outside code

The tool does not tell you whether outside code is safe. Nothing that
reads only what a project publishes about itself and the shapes in a
checkout can. It tells you whether there is a reason to stop before
reading, puts the evidence in one place, and makes the adopter write
down what was checked, what was not, and who owns the gap until the
review that was skipped is done. The security of the adoption is the
sum of the seven rules in the standards, and the tool serves the first
two.

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

Where the scanner has never rated the repository, the record says so.
That is itself a reading: the project is small or new enough that no
outside rater has looked at it.

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

A finding is a prompt to read the file, not a verdict. A `postinstall`
that compiles a native module and one that fetches a payload look the
same to the scanner. The reading is the control; the finding makes
sure the reading happens.

The scan does not run static analysis or secret scanning. Those are
the adopter's own analyzers, pointed at the checkout, and the
acceptance block asks for the result.

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
- Whether the project's dependencies carry the same problems. Run the
  tool on the ones that matter, or rely on the vulnerability audit and
  the malware-shape scan the adopting pipeline already runs.
- Anything on a registry that differs from the repository. A package
  published from a different tree than the one on GitHub is invisible
  here; build from the pinned commit rather than taking the published
  artifact, and the difference cannot reach you.
