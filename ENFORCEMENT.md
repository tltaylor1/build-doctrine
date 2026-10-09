# Enforcement

Every rule in [STANDARDS.md](STANDARDS.md) appears here with the thing that
actually checks it. A rule with no mechanism is not a standard, it is a hope,
and hopes are labeled as such below so nobody mistakes one for a control.

**Contents:** [How to read this](#how-to-read-this) · [The scale](#the-scale) · [What the scorer reads, rule by rule](#what-the-scorer-reads-rule-by-rule) · [Blocked at commit](#blocked-at-commit) · [Blocked in the pipeline](#blocked-in-the-pipeline) · [Every repository's pipeline](#every-repositorys-pipeline) · [Verified by running it](#verified-by-running-it) · [The checkpoint passes](#when-to-run-the-passes) · [Checked by a human](#checked-by-a-human) · [What each tool misses](#what-each-tool-misses) · [What Scorecard checks, and who checks it here](#what-scorecard-checks-and-who-checks-it-here) · [Moving rules up](#moving-rules-up)

-------------------------------------------------------------------------------

## How to read this

Rules sit in one of four tiers, strongest first:

1. **Blocked at commit.** The commit does not happen. Fastest feedback, and the
   defect never enters history.
2. **Blocked in the pipeline.** The merge does not happen. Catches what needs a
   full environment, and catches anyone who worked around tier one.
3. **Verified by running it.** A command produces evidence. Not automatic, so it
   belongs to a checkpoint, and the passes of that checkpoint are in the same
   section as the commands.
4. **Checked by a human.** No tool exists yet. These are the honest gaps.

The work of maintaining this file is moving rules upward. A rule that stays in
tier four for a year is either unenforceable or not really a standard.

## The scale

The tiers say where a rule is enforced. The scale says how far a given
repository has actually taken a given rule, as one number a scorer can
establish by procedure rather than by judgment:

| Level | Name | Decided by |
|---|---|---|
| 0 | Absent, or false | No committed document states the practice, or a document states it and verification finds the claim untrue. A false claim scores as nothing, whatever machinery surrounds it. |
| 1 | Stated | A committed document states the practice; no procedure, no command, no date verifies it. Truth unknown. |
| 2 | Attested | A documented manual procedure with a dated record of its last run, inside its validity window. An expired attestation decays to 1. |
| 3 | Checked on demand | A committed script or command verifies the claim and exits clean when run. Drift is catchable, but only when someone runs the check. |
| 4 | Gated | The check runs in CI on every change and sits in the platform's required set, so a violating change cannot merge. |
| 5 | Gated and proven | Level 4 plus evidence the gate fires: a recorded run where it caught a real violation, or a planted-violation test proving it notices absence. |

Two properties give the number meaning. Every step up is a specific
artifact someone can add, so a score doubles as a to-do list. And a
score can fall: the falsity rule and attestation expiry pull levels
down, which is what stops the scale from being a trophy case.

`scripts/score.py` establishes levels 0 through 4 for any repository
from its files, its history, and the platform's ruleset API when
reachable. It never infers level 5: a repository earns 5 only by
recording the proof, a link to the run or test where the gate fired,
in its `doctrine.yml`, and only for a rule already standing at 4. The
same manifest names the repository's kind, so rules the kind does not
need are reported as not applicable, and lets a repository exclude a
rule with a written reason, because an undocumented gap and a
considered exclusion look identical in a score. Each repository commits
the badge the scorer writes for it, and its doctrine job compares a
fresh one against the committed file (D-038).

The standards are organized by layer; the tiers here cut across them.
Where each layer's enforcement lives:

| Layer | Mechanical enforcement | Human attestation |
|---|---|---|
| The code | Tiers one and two: hooks, scanners, tests, audits | Decision records and intent, in review |
| The containers | Tier two image scans; tier three verify-by-command | The printed commands run at each release |
| The pipelines | Pinned actions, checksummed tools, workflow lint, required checks | The ruleset's configuration, in the platform baseline |
| The platforms | None yet | Every row of [PLATFORM-BASELINE.md](PLATFORM-BASELINE.md), dated, with expiry |

-------------------------------------------------------------------------------

## What the scorer reads, rule by rule

One entry per rule in `scripts/score.py`, in the order the scorer
applies them: what it reads, the risk the rule answers, how each level
is earned, and what to add to move up. A test holds this list to the
scorer's, so a rule cannot exist in one place and not the other. Three
things apply to every rule. A repository's `doctrine.yml` names its
kind, and a rule the kind does not need reports as not applicable
rather than as a zero. The same file may exclude a rule with a written
reason, reported as excluded. And level 5 is never inferred: it is
granted only when `doctrine.yml` records a proof for a rule already at
4, a link to the run or test where the gate fired.

### readme

Reads the repository root for a file whose name starts with README.
The risk is a repository nobody can orient in: no statement of what it
is, what it does, or how to run it. Level 0 when no such file exists.
Level 3 when it exists and the scorer verifies that on demand. Level 4
when a workflow runs the scorer, because then the check runs on every
change. To move up, add the file, then name `scripts/score.py` in a workflow.

### license

Reads the root for a file starting with LICENSE. The risk is content
nobody may lawfully reuse, which is the same as content nobody may
use. Not applicable to a profile. Levels as for readme.

### security-policy

Reads the root for a file starting with SECURITY. The risk is a
vulnerability reported nowhere, or in public, because the reporter had
no route. Applies to application, doctrine, reference, and study
repositories. Levels as for readme.

### contributing

Reads the root for a file starting with CONTRIBUTING. The risk is a
contribution that arrives in a shape nobody can accept. Applies when
`doctrine.yml` sets `invites_contributions` to true, or by default for
application, doctrine, reference, and study kinds when it says
nothing. Levels as for readme.

### decisions-record

Reads `DECISIONS.md` and counts headings of the form `## D-n`, then
reads every file under `tests/` for the word DECISIONS. The risk is a
choice with no rejected alternative beside it, so the next person
re-argues it from nothing. Applies to application and doctrine
repositories. Level 0 when the file is absent. Level 1 when entries
exist and nothing recounts them. Level 4 when a test names the file,
because a test that recounts the entries makes a stated count a
verified one. To move up, add a test that counts the entries and
compares the count to what the documents state.

### commit-subjects

Reads the last thirty commit subjects, leaving out merge commits and
the named dependency bots, and requires each to lead with an
identifier: a decision number, a subphase number, or a capitalised
area, followed by a colon. An agent's own commits count, because they
are the changes this rule exists to judge (D-029). The risk is a
history that narrow panels truncate to nothing readable. Level 0 when
any subject fails or no history is readable. Level 3 when every
subject leads with an identifier and the scorer verified it on demand.
Level 4 when a workflow runs `check_commit_message`, because then a
bad subject cannot merge. To move up, add the commit message check to
the pipeline.

### pinned-actions

Reads every workflow file and compares the count of `uses:` lines to
the count pinned to a forty-character commit hash. The risk is a tag
that moves under a pipeline, which is how a compromised action reaches
every consumer at once. Not applicable when there are no workflows.
Level 0 when any use is unpinned. Level 3 when every use is pinned.
Level 4 when a workflow also runs an audit tool (zizmor, pinact, or
the actions inventory check), because then an unpinned use cannot
merge. To move up, pin every use, then add the audit to the pipeline.

### ci-gate

Reads the platform's rulesets through the API, with `--repo`, and
collects the required status checks. The risk is a pipeline that runs
and never blocks: every check visible, none of them a gate. Not
applicable to a profile, or to a diagrams repository with no
workflows. Level 0 with no workflows. Level 1 when workflows exist but
either nothing is required to merge or the platform could not be
reached, because the truth is unknown. Level 4 when at least one check
is required. To move up, add the checks to the ruleset's required set,
and re-score with platform access so the level is read rather than
assumed. A check that runs and is not in the set stays at 1 in
substance whatever its job name says, which is why this document names
the required set for each repository.

### dependency-updates

Reads for `.github/dependabot.yml` or for Renovate's configuration
file at the root. The risk is a
dependency that ages until a known vulnerability finds it. Applies to
application and doctrine repositories. Level 0 when neither exists.
Level 3 when one does, because the configuration is a committed,
checkable artifact and the updates arrive through the gates. The
scorer does not read whether the updates are being merged.

### run-instructions

Reads the README for a heading that names running the thing (run,
running, quick start, getting started, how to run, getting the deck,
using) and for at least one code block. The risk is a repository that
works only on its author's machine. Applies to application,
reference, and study repositories. Level 0 without the heading. Level
1 with it, and no higher, because the scorer cannot run the
instructions; the fresh clone drill in
[Pass 6](#pass-6-the-first-fifteen-minutes) is the attestation that
would earn 2, and it is recorded in the repository's own documents
rather than read by the scorer.

### troubleshooting

Reads the README for a heading containing troubleshoot. The risk is a
known failure met by a stranger with nothing to read. Applies to
application repositories. Level 0 without the heading, level 1 with
it, for the same reason as run-instructions.

### counted-figures

Reads the README for bold figures, a number in bold followed by a
noun, then reads every file under `tests/` for the word README. The
risk is a document stating a number the system no longer reports, and
being believed. Applies to application repositories. Level 0 when the
README states no figures. Level 1 when it does and nothing recounts
them. Level 4 when a test names the README, because a test that
recounts the figures from the source fails the pipeline when they
drift. To move up, add the test that reads each figure and compares it
to what the code, the suite, and the decisions record report.

### generated-artifact-parity

Reads `scripts/*.py` for a script that both names a `--check` flag and
handles arguments, then reads the workflows for that script's name.
The risk is a generated document, a scores page or a coverage table,
edited by hand or left behind by its generator, so the committed copy
and the truth part ways. Applies to reference, study, and doctrine
repositories. Level 0 with no such script. Level 3 when the script
exists, checked on demand. Level 4 when a workflow names that same
script, credited per script so a checker is never credited for a
different checker's pipeline run (D-034). To move up, give the
generator a check mode that fails on drift, then run it in the
pipeline.

-------------------------------------------------------------------------------

## Blocked at commit

Installed with `pre-commit install` in a fresh clone. Without that command the
hooks do not exist, which is itself a gap worth knowing about: the pipeline is
what catches a developer who never ran it.

Which of these a project starts with: `template/.pre-commit-config.yaml`
carries the secret hook only. The writing hooks and the commit-message hook are
configured in this repository, because they need the Vale configuration and the
vendored style files under `.vale/styles`, and a template that referenced files
it did not ship would fail on a project's first commit. A project adopting them
copies `.vale.ini`, `.vale/styles`, and `scripts/check_commit_message.sh`
alongside the hook entries. Stated here because the table otherwise reads as
though the whole set travels with the template, and it does not.

| Rule | Mechanism | Behavior on failure |
|---|---|---|
| No secrets in a commit | gitleaks, via `.pre-commit-config.yaml` | Commit refused |
| No secrets anywhere in history | gitleaks `git`, or trufflehog with verification on, over the full history | Run at checkpoints and in the pipeline |
| Writing rules hold | Vale, via `.pre-commit-config.yaml` and CI | Commit refused, and the pipeline fails |
| No common idioms or corporate speak | The vendored proselint lists, via Vale | Commit refused, and the pipeline fails; the house figurative list still catches coined phrases no public list knows |
| Every lesson a scanner taught after a push is a rule at commit time | Semgrep with the repository's own rules under `.semgrep/`, one per incident, via `.pre-commit-config.yaml` and again in the pipeline | Commit refused, and the pipeline fails |
| The pipeline's semantic analysis runs before the push | The analyzer's pinned bundles run by a pre-push hook, `scripts/scan.sh` in the application repository | Push refused |
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

Every gate fails the build rather than warning. A warning gate accumulates
ignored findings; a blocking gate makes each one an event that gets fixed or
formally accepted.

Where each one lives, because this section used to claim a single file held
them all and three rows were somewhere else (D-033). The first nine rows are
defined in `template/.github/workflows/ci.yml`, which is what a new project
starts from; the retired-name row is this repository's own script, run by
each repository's doctrine job. The fuzz harnesses and the release attestation are defined in the
application repository built to this doctrine, as `.clusterfuzzlite/` with
`cflite.yml` and as `attest-release.yml`; a template cannot carry a harness for
a parser that does not exist yet. The rows from the role matrix downward are
that application's own tests, named here so the doctrine states what a project
is expected to have rather than leaving each project to invent the list.

| Rule | Tool | What it catches |
|---|---|---|
| Behavior matches its tests | pytest | Broken controls, broken features |
| No known-vulnerable dependency | pip-audit | Published vulnerabilities in the pinned tree |
| No obvious insecure code pattern | bandit | Hardcoded credentials, weak randomness, shell injection shapes, assert in production paths |
| No secret in any commit | the gitleaks binary over `git`, pinned and checksum-verified, or trufflehog with verification on; never the gitleaks action, whose source scans the event's commit range and not the history | Credential patterns across every commit, not just the tip |
| Dependencies install as pinned | `pip install --require-hashes` | A substituted or tampered package fails the install |
| No fixable vulnerability in the image | trivy, `ignore-unfixed` | Operating system and library findings that have a released fix |
| Third-party actions cannot change under us | commit-hash pins in the workflow | A moved tag pointing at new code |
| Dependency updates are reviewed, not automatic | Dependabot pull requests | Drift, with the same gates run before merge |
| Workflow tokens hold least permission, and no workflow runs fork code with the token | workflow lint and audit | A missing permissions block, a write the job never uses, a `pull_request_target` trigger |
| Parsers survive input nobody wrote a test for | fuzz harnesses under an address sanitizer, on changes and on a schedule | A crash or an exception the parser never promised |
| Releases carry provenance | the attestation step of the release workflow | An asset or image published with nothing to verify it against |
| A promise nobody awaits in a page script | ESLint with typescript-eslint's rule, installed from the lockfile with integrity hashes, at commit time and in the pipeline | A failed load with nowhere to report but the console |
| A path containment check as a string prefix | Semgrep, the repository's own rule, at commit time and in the pipeline | A sibling path accepted by an extraction guard (October 2026) |
| A handler that catches everything and says nothing | Semgrep, the repository's own rule, at commit time and in the pipeline | A hook that returned silence on every error (October 2026) |
| A commit that names a cause without its reproduction | `scripts/check_commit_message.sh`, the commit-msg hook and the pipeline's writing step | Three messages in one day asserting causes the next commit disproved (October 2026) |
| The standards copy behind the source | `scripts/check_doctrine_copy.py` in every repository's doctrine job, against a rendering whose links point here; `--write` produces the copy | A 358-line copy against a 995-line source (October 2026) |
| A committed score badge behind the scorer | The doctrine job scores to a temporary file and compares it with the committed badge; `scripts/score.py --badge` | A README showing a level the repository no longer holds (October 2026) |
| A test the pipeline's runner skips without a word | `tests/test_discovery.py`, refusing any test written as a bare function where the runner finds only TestCase methods | Twelve tests that never ran in this repository's pipeline for four days (October 2026) |
| A change that adds duplicated code | `scripts/check_repetition.py` in the pipeline: the pinned jscpd in exact mode, run on the base branch and on the change, failing when the change has more duplicated lines, so an edit inside an old copy passes and a new copy fails; renamed, near-miss, and semantic copies are leads a person reads, never a gate | The same input bound in six parsers and the same revocation rule in three records (October 2026) |
| A change that adds code nothing uses | `scripts/check_dead_code.py` in the pipeline: jscpd's dead-code analysis, run on the base branch and on the change, failing when the change has more dead lines; only findings at confidence 85 or above in unused files, exports, symbols, and imports count | Four constants nothing read, one restating a rule the running code stated elsewhere (October 2026) |
| A runtime package with no record, or a record with no package | `scripts/check_dependency_records.py` in the doctrine job, reading the trees doctrine.yml names and the repository's DEPENDENCIES.md | A framework update that brought a new runtime package into two applications unvetted (October 2026) |
| Bulk disclosure, bulk change, or credential creation on a stale session | The application's own tests: the named step-up list held to the routes' declarations, a stale session refused on each, and a mutation removing the refusal | Any live session able to export everything and mint credentials (October 2026) |
| A bulk export that leaves no record | The application's own test that every export writes an audit record naming who took what | Exports that were the one read leaving no trace (October 2026) |
| Rejected input that comes back | The application's own test that sends every input door a marker in shapes it rejects and finds it in no response, log, or audit record | Rejected input can carry a live credential (October 2026) |
| No retired project name in active text | `scripts/check_names.py` over the tracked text files, skipping license texts and the imported cliche lists, reading the shared retired-names list from `deprecated-names.yml` and each repository's allowlist of history files from its `doctrine.yml` | An old name or address that survived a rename in a related-projects section, a hook, a badge, or a description |
| Every route answers to the role matrix, and none answers without a session | the matrix test, calling every registered route as each role and with no session | A route that shipped without its authorization dependency, and a route missing from the matrix entirely |
| The documented route surface matches the live one, in both directions | the surface test, comparing the documented enumeration against the application's own route table | A route added without documentation, and a documented route that no longer exists |
| The spreadsheet exit stays escaped | the export tests, and the mutation set, which removes the escape and requires the suite to fail | A cell beginning with an equals sign, plus, minus, or at sign that would execute on open |
| Ingestion stays bounded and in memory | the parser tests and their property suites | A file past the size, row, column, or cell bound; input that is not valid UTF-8; a shape the parser never promised |
| Sensitive reads carry their headers and their audit row | the response-header tests and the audit tests | A download served without `X-Content-Type-Options: nosniff`, or a read that leaves no trail |
| Security-relevant events are structured and parseable | the logging tests | An event emitted as prose, or one missing the fields an investigation reads |

-------------------------------------------------------------------------------

## Every repository's pipeline

Every active repository built under this doctrine is gated the same way: nothing
lands without the required checks and a human approval, every tool
arrives from its canonical release and is checksum-verified before it
runs, and what a gate may block on is decided and recorded, because
an alarm that is always red teaches the eye to skip it. A finished
reference keeps the gates it was finished with and is not retrofitted
unless the reference itself changes; a study repository carries the
writing rules and its own parity checks and no more, because it holds
no code that runs.

The shared method:

- Changes travel branches and pull requests; the mainline refuses
  direct pushes, force pushes, and deletion.
- The coding agent proposes under its own installed-app identity with
  named permissions; a human approving review is required, and the
  approve button sits past the diff, so the diff gets read.
- Commits and release tags are signed; releases carry build provenance
  attestations verifiable against the platform's transparency log.
- Writing rules, status-truth gates, and secret scans run at commit
  time and again in the pipeline.
- Weekly scheduled runs cover what changes while the code does not: a
  base image fix shipping, a new advisory against a pinned tree, a
  figure another repository states.

What each kind of repository adds beyond the shared set:

| Kind | The gates beyond the shared set |
|---|---|
| Application | Tests with a coverage floor, strict typing, a mutation check that breaks one control at a time and requires the tests to notice, migration drift against a real database, dependency audits, container lint, base image scan, manifest schema and posture checks, and a documented route surface asserted against the live route table |
| Doctrine | The writing rules enforced on the documents that define them, the scorer run on itself, the mechanism and coverage checks, the retired-name check |
| Platform | Format and validation, misconfiguration scanning of the infrastructure code with the vetted scanner's configuration mode, a cost delta stated on every pull request, drift detection on the weekly clock, and the cloud's own reviewers, a configuration baseline, a security standard, an access analyzer, checking what exists independently of what any plan claimed |
| Reference and study | The writing rules and a parity check that the generated artifact matches its source |

The posture for infrastructure as code: Terraform as the primary
tool, state in versioned object storage with native locking, no
account identifier in a shipped module (identity is discovered from
credentials, and the estate's own values live in a thin layer apart),
and no stored cloud credential anywhere, with people authenticating
through short-lived sessions and pipelines federating through OpenID
Connect into scoped roles. A plan is a claim about intent, so the
cloud's own configuration record is the independent reviewer of what
exists, the same relationship an application's tests have to its
controls.

-------------------------------------------------------------------------------

## Verified by running it

These need a running system or a deliberate experiment, so they belong to a
checkpoint rather than to every commit. The table is the per-rule view: what
command produces what evidence. The passes after it are the per-session view,
the order a person actually works in, and they used to be a separate document
whose content was this tier twice over (D-034). Where a pass and a row hold the
same command, the pass is where it is written.

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
| An outside component was vetted before adoption | `python3 scripts/vet.py OWNER/NAME --path checkout` | The adoption record, pasted into the decisions record with its acceptance block filled in |
| Egress is limited to what the service needs | From inside the container, attempt a connection to a host the service has no reason to reach | Refused |
| A release's provenance verifies | `gh attestation verify ASSET --repo OWNER/NAME` | The attestation names this repository's workflow |
| No actor completes a sensitive transaction alone | Authenticate as the actor who created a record and attempt to approve it | Refused, whatever the actor's role |
| The serving framework's defaults were walked | Walk the framework's defaults against its own documentation at the release checkpoint, recording each as changed deliberately or accepted with a reason | A default nobody chose, which is the class that ships silently |
| Every published framework item has a coverage row, and every governed rule appears in one | `python3 scripts/check_coverage.py` | A rule added and mapped nowhere, a row left behind after an edition dropped its item, and a gap that names no trigger |
| The recorded framework editions are still the published ones | `python3 scripts/refresh_frameworks.py` | A renamed item, an item added upstream, and a newer edition than the one the documents map |
| Every blocking row here names a mechanism that exists and still does the job | `python3 scripts/check_mechanisms.py` | A row whose mechanism was never implemented, a row reworded away from its mechanism, a mechanism swapped for something weaker, and a path named in this document that exists nowhere |

The third is this document's own gate, and it exists because the sentence at the
top of this file, that every rule appears here with the thing that checks it,
was true nowhere a machine could see. An audit found six places where it was
false, five of them the same shape: a control implemented where it was learned,
generalized by a table to an artifact it had never reached (D-033). The pairing
now lives in [mechanisms.json](mechanisms.json), each blocking row naming the
files that hold its mechanism and a pattern that must still appear in them.
Artifacts in an application repository are reported as declared and never as
verified, because this repository cannot read that one.

The first two are the pair that answers [COVERAGE.md](COVERAGE.md), and the
split between them is the point. The first needs no network and runs in the `score`
job on every change, so drift inside the repository is caught as it arrives.
The second needs the network and runs on a schedule in
`.github/workflows/frameworks.yml`,
because a new edition is not caused by a commit. Neither is tier two yet: the
`score` job is not in the repository's required set, so a failing coverage gate
is visible on a pull request and does not block the merge. Adding `score` to
the required checks is the one settings change that moves it, and it moves the
test suite and the scorer with it.

### When to run the passes

- **Passes 1, 4, and 5** before any release or visibility change. They are the
  ones that find defects nothing else finds.
- **Pass 2** whenever documents change, because documented figures drift from
  the system silently.
- **All six** before the work is published or shown.

Run them against a fresh clone in a scratch directory, never against the working
copy. A working copy has state a fresh clone does not.

**Making a repository public is gated on a human reading it end to end.** The
automated passes check what a tool can check. They cannot tell whether a
sentence says something the author would not say, whether a section belongs, or
whether the whole thing reads the way it should. That judgment happens once, in
full, before visibility changes, and publication waits for it. See D-018.


### Pass 1, does it run

Clone into an empty directory and follow the README literally. Do not use
knowledge you have that a reader does not. Every documented path gets tried,
including the one for readers who have only containers and no local language
runtime.

Failures found this way, which no test suite catches: setup steps that assume a
tool the reader was never told to install, key generation that cannot run before
the thing it configures exists, and a stale container serving old code because
the documented command does not rebuild.

Record how long it took. A reader's patience is the real limit.


### Pass 2, claims against reality

Take every factual claim in the documents and check it against the running
system: test counts, record counts, control behavior, the container assertions.
Correct the document, not the memory.

The rule is that a number in a document is a claim under test. Documents drift
from systems by default; only a check stops it.


### Pass 3, hostile probes

Authenticate as two ordinary users and one privileged user, then attempt what an
attacker would. Each line states the expectation.

- Unknown account and wrong password produce byte-identical responses.
- A token forged with the algorithm set to none is refused.
- One user requests another user's list, and receives only their own rows.
- One user acts on another user's record, and is refused.
- A create request smuggles owner and status fields, and is rejected.
- Out-of-range and oversized values are rejected.
- A file whose contents contradict its declared type is refused.
- A filename containing path traversal is accepted but the name is discarded,
  and nothing is written outside the intended directory.
- A user downloads another user's file, and is refused.
- A text field beginning with a formula character arrives neutralized in any
  export.
- A request with no credentials is refused with the correct status.


### Pass 4, mutation

The only way to know whether tests defend behavior rather than measure coverage.

For each significant control: remove it, run the suite, confirm named tests
fail, then revert and confirm the suite returns to green. Record the results as
a table in the project README.

A control whose removal breaks nothing has no test behind it. That is a finding,
and the fix is a test, not a note.


### Pass 5, history and hygiene

- Scan the full history for secrets, not just the working tree.
- Search every tracked file for credential-shaped strings, which a secret
  scanner correctly ignores but a person reading the file will notice.
- Confirm the author identity on every commit is the intended one.
- Read every commit message as an outsider. Names of employers, clients,
  interview processes, and internal systems do not belong in history.
- Look for debug output, placeholder text, and dead code.

Anything found here is a rewrite or a rebuild, not an edit, because history is
permanent. Decide before publication, never after.


### Pass 6, the first fifteen minutes

Read the repository as somebody encountering it for the first time, with fifteen
minutes and no prior context.

- Does the README's first screen say what this is and how to run it?
- Does the repository layout explain itself?
- Is there anything that would need to be overlooked or excused?
- Pick the fifty lines most likely to raise a question. Can every line be
  explained aloud?
-------------------------------------------------------------------------------

## Checked by a human

No mechanism exists for these yet. They are listed rather than hidden, because
an undocumented gap and a considered exclusion look identical in code.

- Whether an intent comment explains why rather than restating what.
- Whether an identity check reads a value the platform sets rather than
  one the author sets; no analyzer knows which values are which.
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
- Whether an adoption's accepted risk still has an owner and an unexpired
  date, and whether the full review it promised was done. The vetting
  script writes the block; nothing yet reads the dates back. A check that
  fails on an expired acceptance would move this to tier three.
- Whether a license found compatible is still compatible after the
  component's next major version, which is when licenses change.
- Whether the threats a component faces were ranked, and whether what
  was put out of scope says why. A tool can check that a threat model
  exists and carries its columns; no tool can judge whether the
  ranking is honest.
- Whether transport encryption is actually in force. The rule belongs
  to the deployment layer rather than the application, so nothing in
  this repository's pipeline can see it. The honest tier until a
  deployment exists whose configuration can be read back.
- Whether sensitive values are encrypted at rest. Same shape: the
  storage layer supplies it, and these projects minimize what they
  store rather than encrypting more of it, so the claim is checked
  where the deployment is described and nowhere else.
- Whether a password was screened against known-breached and common
  lists. No project here has a password store beyond its own
  operators, and the screening list is a dependency nobody has
  adopted. A test asserting a known-breached sample is refused would
  move this to tier two the day the list arrives.
- Whether the cryptography in use is a standard construction from a
  maintained library rather than something assembled here. Nothing
  invents cryptography is a rule a reader enforces by recognizing a
  construction somebody assembled here instead of taking a standard
  one, and no analyzer reliably does.
- Whether an exceptional condition leaves the system as it found it.
  Partly visible: a test that fails a write part-way and requires no row
  to survive covers the rollback half, and the application repositories
  have those. What no tool judges is whether an error path skips a check
  on its way out, which is read rather than detected.
- Whether a session identifier actually changes at authentication and at
  any change of authority. A test that signs in holding a
  pre-authentication identifier and requires it to be refused afterwards
  would move this to tier two; nothing asserts it yet.
- Whether any parser reconstructs an object rather than reading data. A
  check failing on an import of a deserializing interface would move this
  to tier three; the safety is an accident of format choice.
- Whether outbound destinations are decided by the code. No project here
  makes an outbound request, so there is nothing to check yet. Triggered
  by the first live connection to a provider, which is also the first time
  the rule can be violated.
- Whether a response from another system passed the same validation as a
  file a stranger uploaded. Same trigger as the rule above, and the same
  reason it is empty now.
- Whether the rules for a product that uses a model hold. Nothing here
  puts a model in a serving path, so every rule in that section is
  unexercised. They are written in advance deliberately, and they are
  labeled here as unchecked rather than counted as coverage.
- Whether the agent treated what it read as data rather than instruction.
  No tool judges this from a diff; it shows in the execution transcript,
  where a change nobody asked for is the signal. The bounded capability
  in tier three is the control that keeps the consequence to a proposal
  somebody rejects.

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
- **Scorecard** reads a repository's files and settings through the
  platform's interfaces. It sees whether a practice is configured, never
  whether the code behaves; it returns inconclusive when every recent
  change was authored by a bot, which includes an agent app, so a
  one-person program's code review is invisible to it; and it scores a
  self-attested badge as if it were evidence. Verified against manifest-identity
  (September 2026), where the review requirement in the ruleset earned
  points under Branch-Protection and nothing under Code-Review.
- **scripts/vet.py** reads what the raters and the platform publish and
  what a checkout contains. It cannot tell a well-rated abandoned project
  from a well-rated maintained one beyond the dates it prints, and it
  cannot read intent: a postinstall script that compiles a native module
  and one that fetches a payload look the same to it. The finding is the
  prompt to read the script; the reading is the control.

-------------------------------------------------------------------------------

## What Scorecard checks, and who checks it here

manifest-identity carries the OpenSSF Scorecard badge, and a badge from a rater
whose checks the doctrine never names is a number nobody here can explain.
Each of the scanner's checks, the doctrine rule that covers the same
ground, and which of the two enforces it. Where the doctrine has no rule,
the table says so and says why, so the scanner's coverage and the
doctrine's coverage can be told apart.

| Scorecard check | Doctrine rule | Enforced here by | Scorecard's role |
|---|---|---|---|
| Binary-Artifacts | No executable binary is committed (the code, dependencies) | `scripts/vet.py --path` on demand | Weekly scan; the only scheduled check |
| Branch-Protection | Every change through a pull request with required checks; review by the code owner (git practice, platforms) | The ruleset, attested in the platform baseline | Reads the ruleset; the outside witness to the attestation |
| CI-Tests | Every merge passes the required checks (the pipelines) | The ruleset's required set; the scorer's `ci-gate` rule | Reads recent merges |
| CII-Best-Practices | None. The badge is a self-attestation; the doctrine's own attested level is its counterpart | Nothing | Scores the badge level as evidence, which it is not |
| Code-Review | Every change is read before it lands (working with an agent, git practice) | The ruleset's code-owner review requirement | Inconclusive for bot-authored changes, so it does not see it |
| Contributors | None. A one-person program has one contributor by definition | Nothing | Scores organizations, not practice |
| Dangerous-Workflow | No workflow runs fork code with the token; no untrusted input in a run step (the pipelines) | Workflow lint and audit in the pipeline | Weekly scan, same patterns |
| Dependency-Update-Tool | Updates arrive as pull requests through the gates (dependencies) | The scorer's `dependency-updates` rule; the update configuration | Reads the configuration file |
| Fuzzing | Every parser of untrusted input carries a fuzz harness (the code) | The fuzz workflow on changes and on a schedule | Reads whether a fuzz integration exists |
| License | A license fitting the content (repository kinds) | The scorer's `license` rule | Reads the file |
| Maintained | What never changes is unmaintained (principles); branches merge within days (git practice) | Nothing measures activity | The only measure of it here; time is the input |
| Packaging | The image is the deployable artifact, published at release (containers, pipelines) | The release workflow | Reads the release workflow |
| Pinned-Dependencies | Every pin by hash or digest, inventoried, paired pins moving together (dependencies, pipelines) | Hash-enforced install, the inventory gate, the parity gate, the scorer's `pinned-actions` rule | Reads the files, same conclusion |
| SAST | Static analysis on every change and on a schedule (the code) | Pattern checks at commit, the semantic analyzer in the pipeline | Reads whether an analyzer ran on recent commits |
| SBOM | The bill of materials is regenerated after every dependency change (dependencies) | `scripts/verify.sh` freshness check | Looks for a published bill in releases, which the doctrine does not require; a gap by choice, noted here |
| Security-Policy | A security policy wherever code or data is served (repository kinds) | The scorer's `security-policy` rule | Reads the file |
| Signed-Releases | Every release carries a provenance attestation (the pipelines) | The release workflow's attestation step; `gh attestation verify` on demand | Reads the release assets |
| Token-Permissions | Workflow tokens hold least permission (the pipelines) | Workflow audit in the pipeline | Reads the permission blocks |
| Vulnerabilities | No known-vulnerable dependency; a finding forces an update (dependencies) | pip-audit and the image scan in the pipeline, both on a schedule | Reads the advisory database against the tree |
| Webhooks | None. No repository here has a webhook | Nothing | Nothing to read |

Three rules in the table were written in September 2026 because this
table showed them missing: static analysis, fuzzing, and release
provenance were practiced in every pipeline and stated in no document.
Two checks have no rule on purpose, Contributors and Webhooks, and one,
the Best Practices badge, is a self-attestation the doctrine declines to
treat as evidence. Maintained is the one check the scanner measures and
nothing here does, because its input is the passage of time.

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
