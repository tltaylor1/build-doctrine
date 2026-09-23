# The fundamentals

The handful of things that make code secure, each in plain words, with
the rule this doctrine states for it, what enforces the rule, and where
the enforcement is proven. The proof links point at
[manifest-identity](https://github.com/manifest-identity/manifest-identity), the application
built under this doctrine, because a rule is proven by a repository
that lives under it, not by the document that states it.

**Contents:** [Keep secrets out of the code](#keep-secrets-out-of-the-code) · [Check every input on the server](#check-every-input-on-the-server) · [Check who is asking, every time, for every record](#check-who-is-asking-every-time-for-every-record) · [Give everything the least it needs, and stop when something is wrong](#give-everything-the-least-it-needs-and-stop-when-something-is-wrong) · [Know exactly what you depend on](#know-exactly-what-you-depend-on) · [Test the code, then test the tests](#test-the-code-then-test-the-tests) · [Prove what you shipped](#prove-what-you-shipped) · [Write down what happened, and know what you will do](#write-down-what-happened-and-know-what-you-will-do) · [Write down what you decided and what you accepted](#write-down-what-you-decided-and-what-you-accepted) · [What is not here](#what-is-not-here)

-------------------------------------------------------------------------------

## Keep secrets out of the code

**In plain words.** A password or a key that is written into a file
ends up in the repository's history, and history is copied to every
clone forever. The only safe place for a secret is outside the
repository, and the only safe rule is one that a machine refuses to
let you break.

**The rule.** No secrets in the repository, ever. Configuration lives
in an ignored environment file, the application halts at startup when
a secret it needs is missing, and no credential-shaped string appears
in any tracked file, including demonstrations and tests.

**What enforces it.** Three layers that fail differently: a scanner
at commit time that refuses the commit, a full-history scan in the
pipeline that catches anyone who skipped the hook, and push
protection at the server that refuses the push. Beside them, a sweep
for credential-shaped strings the scanners miss, and a gate on the
local git configuration after a token was once written there.

**Where it is proven.** The secrets job in manifest-identity's pipeline, the
commit hooks in its configuration, and the incident record in its
[AI-USAGE.md](https://github.com/manifest-identity/manifest-identity/blob/main/AI-USAGE.md).

## Check every input on the server

**In plain words.** Anything a client sends can be anything at all.
Checks in the browser are a convenience; the server is the only place
a check counts, and the safest check is one that makes a whole class
of attack impossible rather than one that recognizes each attack.

**The rule.** Input is validated server side, typed, and bounded, with
maximum lengths on every text field. Input and output models are
separate, so a client cannot set a field it should only read. Uploads
are checked on the declared type and on the file's own leading bytes.
Injection is removed as a class: every query is parameterized, every
exit escapes for its destination, and spreadsheet formulas are
neutralized on the way out.

**What enforces it.** The framework's typed models, and tests that
send hostile, truncated, and mixed input and assert it is refused
whole and never echoed back.

**Where it is proven.** manifest-identity's ingest tests and the two
property-based suites that generate inputs nobody wrote by hand.

## Check who is asking, every time, for every record

**In plain words.** Knowing who someone is does not mean they may see
a given record. The most common serious defect in this kind of
application is a route that checks the user is signed in and forgets
to check the record is theirs.

**The rule.** The token is validated on every request, not trusted
once. Every owned record is checked for ownership before it is read
or changed. No actor completes a sensitive transaction alone.

**What enforces it.** A test that walks every route in the role
matrix with a real session per role and asserts both the allow and
the refusal, a test that the documented route list matches the live
one in both directions, and a mutation check that removes the
authorization check and confirms the tests notice.

**Where it is proven.** manifest-identity's matrix test and mutation check,
and the mutation table in its README that records the one mutation
that survived and the test that now exists because of it.

## Give everything the least it needs, and stop when something is wrong

**In plain words.** A process that can do anything will do anything an
attacker asks of it. A process that can do only its job limits the
damage to its job. And when something is missing or broken, stopping
is safer than continuing with a guess.

**The rule.** Missing configuration halts startup. Gates block rather
than warn. Containers run as a non-root user on a read-only
filesystem with every capability dropped and resources capped, and
publish no database port. The application's database role holds data
rights only; migrations run separately as a privileged role. Workflow
tokens are read-only unless a job must write.

**What enforces it.** Commands run at each checkpoint that read the
running container's user, filesystem, and capabilities; a pipeline
probe that attempts a schema change as the runtime role and fails the
build unless it is refused; a workflow audit that fails on a missing
or over-wide permissions block.

**Where it is proven.** The verified-by-command table in
[ENFORCEMENT.md](ENFORCEMENT.md), the schema probe in manifest-identity's
application job, and D-051 in its decisions record.

## Know exactly what you depend on

**In plain words.** Most of the code that runs is code somebody else
wrote. A name can point at different code tomorrow; a hash cannot. And
a package's install script runs on your machine before you have read
a line of it.

**The rule.** Every package is pinned by hash and installed with hash
enforcement. Every base image is pinned by digest, with the tag kept
beside it so the update bot follows the right family, and every copy
of a pin moves in one commit. Every workflow action is pinned by
commit and listed in a table the pipeline holds to the workflow files.
Updates arrive as reviewed pull requests, grouped, through the same
gates as code. Outside code of significance is vetted before adoption:
signals read, install-time code scanned, analyzers run, license
checked, pinned and built from source, run with the least it needs,
and what was skipped accepted with an owner and an expiry.

**What enforces it.** The install refuses an unpinned or altered
package. A parity check refuses a digest that moved in one file and
not its twin. An inventory check refuses an action the README does not
name. A vulnerability audit and a malware-shape scan run on every
change and on a schedule. The vetting tool produces the adoption
record.

**Where it is proven.** manifest-identity's writing job, which holds the
digest parity and the actions inventory; the pull requests where those
gates refused a half-moved pin; and [VETTING.md](VETTING.md) for what
the vetting tool reads.

## Test the code, then test the tests

**In plain words.** Tests prove the behavior somebody thought to write
down. Coverage says which lines ran, not whether anything was checked.
The only proof that a security test would notice a control
disappearing is to remove the control and watch the test fail.

**The rule.** Static analysis on every change and on a schedule, fast
pattern checks at commit and a semantic analyzer in the pipeline. A
coverage floor under the measured figure. A mutation check that breaks
one control at a time and requires the tests that claim it to fail.
Fuzz harnesses on every parser of untrusted input. The whole suite on
the oldest supported interpreter as well as the newest.

**What enforces it.** The pipeline: lint, types, the analyzer, the
suite with its floor, the mutation script, the fuzz workflow, and the
floor interpreter job, all in the required set so a failure cannot
merge.

**Where it is proven.** manifest-identity's pipeline and the "numbers, proven"
section of its README, which holds the commands behind each figure.

## Prove what you shipped

**In plain words.** A downloaded file is only as trustworthy as the
proof of where it came from. A release built by a workflow and
attested by the platform can be verified by anyone; a release built on
a laptop cannot.

**The rule.** Releases are cut from signed tags. Every asset and the
container image carry a build provenance attestation, verifiable with
the platform's own tooling. A release cut before the attestation step
existed is attested after the fact, dated the day it ran.

**What enforces it.** The release workflow's attestation step, and the
verification command in the checkpoint procedure.

**Where it is proven.** manifest-identity's release workflow, the attested
v0.2.0 release, and the Signed-Releases and Packaging rows in its
[scoring page](https://github.com/manifest-identity/manifest-identity/blob/main/SCORING.md).

## Write down what happened, and know what you will do

**In plain words.** When something goes wrong, the questions are who
did what, when, and to which record. If the log cannot answer them,
the investigation is guesswork. And a response plan that has never
been run is a plan that will be written during the incident.

**The rule.** Sensitive actions, denials, and sensitive reads are
logged as structured events, written in the same transaction as the
action so a failed action leaves no false record. Events are designed
by asking what an investigation would need. Detection queries are
written while the events are designed, and a query becomes a control
when it has a threshold and an owner. A response procedure is written
before it is needed and exercised at least once.

**What enforces it.** Tests that assert the audit row exists for each
governed action and is absent when the action is refused. The
response exercise is a human step, listed as such.

**Where it is proven.** manifest-identity's governance tests and the audit
rows in its data model; the exercise is recorded when it is run.

## Write down what you decided and what you accepted

**In plain words.** Secure by accident and secure on purpose look the
same in code. The only thing that tells them apart is a record of what
was chosen, what was rejected, and which risks were accepted with open
eyes. A risk accepted without a date is a risk forgotten.

**The rule.** Every decision that shapes the system is recorded with
its rejected alternatives. Accepted risk is written down with an owner
and an expiry. Threats are ranked, and what is out of scope is stated
rather than left silent. Every rule in this doctrine names the
incident that produced it.

**What enforces it.** A test that recounts the decisions against the
figure the README states, and a test on this repository that the
record's entries are numbered without gaps and each has a body. The
content of a decision is judged by a reader; no tool can.

**Where it is proven.** manifest-identity's [DECISIONS.md](https://github.com/manifest-identity/manifest-identity/blob/main/DECISIONS.md),
fifty-five entries at this writing, and this repository's
[DECISIONS.md](DECISIONS.md).

-------------------------------------------------------------------------------

## What is not here

Every fundamental above has a mechanism, except where the subject is a
human judgment, and those are listed as human steps rather than
claimed. The fundamentals this doctrine does not yet cover, each with
the condition that would make it a rule, are in the
[not yet covered](STANDARDS.md#not-yet-covered-and-why) section of the
standards: requirements traceability, misuse cases, data
classification, backup and retention, secure disposal, security
metrics, and availability engineering beyond resource caps. Two more
are known and unbuilt: an egress limit on the running container, and a
check that reads an accepted risk's expiry back.
