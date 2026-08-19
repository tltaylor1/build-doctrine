# Decisions

Why each standard exists. Most entries name the failure that produced the rule.
A rule with a recorded cause can be defended when someone argues against it; a
rule copied from another checklist cannot.

Entries are numbered and never deleted. A reversed decision gets a new entry
pointing back.

-------------------------------------------------------------------------------

## D-001: Rules are paired with mechanisms, and the unenforced remainder is labeled

An early standards document was a list of rules to follow. Review replaced it
with mechanisms that cannot be forgotten: a commit-blocking secret scanner
rather than a person remembering to check, hash-verified installs rather than
trusting a version number, verification by command rather than by reading.

The question that surfaced the rest was "what else in this list is a hope rather
than a mechanism." [ENFORCEMENT.md](ENFORCEMENT.md) exists so that question has a
permanent answer, and so the honest gaps are visible rather than implied.

-------------------------------------------------------------------------------

## D-002: No credential-shaped string in any tracked file

A project held three demo account passwords in its README and seed script. They
authenticated nothing outside a local database, a secret scanner correctly
ignored them, and by ordinary convention they were fine.

They were still wrong, for a reason that applies specifically to security work.
Anyone reading a security-focused project who sees a password-shaped string has
to stop and determine whether it matters, and raising that question at all is
the defect. The repository was rebuilt from scratch to remove them from history.

The rule is therefore stricter than "no secrets": nothing that looks like a
credential, including demo, sample, and test values. Demo credentials come from
the environment with fail-fast behavior, and test suites generate their own per
run.

-------------------------------------------------------------------------------

## D-003: Tools are trusted only as far as they have been tested

Before relying on a secret scanner, fake credentials were planted to prove it
fired. One passed through. Diagnosing the miss produced the documented picture of
what the scanner does and does not catch, and the three-layer approach where
architecture keeps secrets out, enforcement catches slips, and review catches
the rest.

The general form: a tool trusted beyond its demonstrated reach is worse than no
tool, because it buys confidence it has not earned. The
[what each tool misses](ENFORCEMENT.md#what-each-tool-misses) section is
maintained by testing, not by reading documentation.

-------------------------------------------------------------------------------

## D-004: Tests are proven by mutation, not by coverage

Coverage counts lines executed, which says nothing about whether a test would
notice a control disappearing. Three authorization defects were planted in a
finished application in turn, and each was caught by named tests.

That experiment takes minutes and it is the only evidence that a security test
suite does what it claims. It is now Pass 4 of [REVIEW.md](REVIEW.md), and the results
belong in the project README as a table.

-------------------------------------------------------------------------------

## D-005: Setup is verified from a fresh clone, by somebody with no memory

Two failures produced this rule. In one project, the README told a reader to
generate a key with a command requiring a library the documented setup path did
not install, so the reader's first experience would have been a crash. In
another, the documented start command did not rebuild the image, so a running
container kept serving code from a previous day while the reader read current
source.

Neither is findable by a test suite, and neither is findable by the author using
their own working copy, because the author's environment already has whatever is
missing. Only a clone into an empty directory finds them.

-------------------------------------------------------------------------------

## D-006: Documented figures are claims under test

A README stated a test count that had drifted by one after a test was added, in
the same document that warns about documentation drifting from the system it
describes. An earlier project stated a data figure that a final verification run
proved wrong.

Documents drift from systems by default. Pass 2 of [REVIEW.md](REVIEW.md) exists
because nothing else stops it.

-------------------------------------------------------------------------------

## D-007: Failure messages carry the fix

A database password changed after first start left an application unable to
authenticate to its own database. The stack started, answered its health check,
and returned a generic error on the first real request, which told an operator
nothing.

Startup now proves its dependencies before serving, and the failure names both
the likely cause and the command that resolves it. The general rule: a fail-fast
check is only half the control, and the message is the other half.

-------------------------------------------------------------------------------

## D-008: Gates block rather than warn

A warning gate accumulates ignored findings silently. A blocking gate makes each
finding an event that gets fixed or formally accepted.

The consequence is accepted deliberately: a build that does not ship is better
than a real security issue that does. False positives get an inline allowlist
marker with a written reason at the exact line, never a bypass flag, because
bypassing silences the check for everything rather than for the one finding.

-------------------------------------------------------------------------------

## D-009: Visibility is decided before the first commit

Git history is permanent, and removing a file does not remove it from history.
Rewriting history to remove something is unreliable, and a service that has
already received a push may retain the old objects.

So the standard is to decide visibility first and write to the public standard
from the first commit regardless. Starting private costs nothing under that
discipline.

-------------------------------------------------------------------------------

## D-010: The agent works from primary sources, not from its own summaries

An assistant asked to apply everything learned from a previous project kept
comparing against its own compressed recollection of that project. The same
class of gap was reported three times by the person who had to notice each one,
and each was traced to inference in place of verification.

The correction is procedural rather than a matter of effort: when a past effort
is the reference, open that effort's artifacts and transcripts and diff against
them. A summary is a lossy copy, and the lost parts are exactly the one-off
decisions that make a standard specific.

-------------------------------------------------------------------------------

## D-011: Corrections become standing rules

Every correction that stays a one-time fix will be needed again, and the person
giving it should not have to repeat themselves. A correction is therefore
written into the standards, and its cause is written here, at the moment it
happens.

This document is the evidence that the process improves rather than merely
holding steady.

-------------------------------------------------------------------------------

## D-012: The writing rules are enforced by a check, not by review

Superseded in part by D-014: the script named below was later replaced by Vale.
The reason the rules must be enforced at all, recorded here, still holds.

The writing rules sat in the human-checked tier, and they drifted in this
repository's own documents within hours of being written. Twelve instances of
figurative and marketing phrasing were present at the first push, including one
paragraph that described two controls as habits, which is the exact <!-- prose:allow (quotes the violation being recorded) -->
hope-in-place-of-mechanism failure D-001 exists to prevent. The same paragraph
claimed output appeared above it in a file that contains no output, which is the
drift D-006 covers.

The first enforcement was a hand-written script that failed on dashes, smart
quotes, arrows, a list of figurative phrases, and language describing a control
as an intention. It was verified by planting violations and confirming it
failed, then reverting.

The general rule this demonstrates: when a standard is violated by the document
that defines it, the standard was never enforced, and writing the rule more
firmly will not change that. Build the check.

-------------------------------------------------------------------------------

## D-013: The baseline is audited against an external list, not against itself

This baseline was built from failures encountered while building, which made it
strong where incidents happened and silent everywhere else. Checking it against
the domains of the Certified Secure Software Lifecycle Professional and the
Certified Information Systems Security Professional found seventeen absences out
of roughly forty items.

Three kinds appeared. Some were vocabulary only: least privilege, defense in
depth, non-repudiation, and the confidentiality, integrity, and availability
framing were all practiced and none were named, which reads to a qualified
practice without the vocabulary that describes it. Some were real
absences recoverable from work already done, notably cryptography and incident
response. The rest had no experience behind them at all.

The first two groups became rules. The third became the
[not yet covered](STANDARDS.md#not-yet-covered-and-why) section, because
inventing a rule with no mechanism is the failure D-001 exists to prevent, and a
documented gap is worth more than an invented control.

The general rule: completeness comes from checking against an external list,
never from asking the source of the list whether it was thorough. Re-run this
audit whenever a new domain of work begins.

-------------------------------------------------------------------------------

## D-014: A maintained tool replaces a hand-written check once one fits

The writing rules were first enforced by a hand-written script (D-012). That
script was unreviewed code with no maintainer, no vulnerability process, and no
users beyond this repository, which is the kind of dependency these standards
tell a project to avoid. It was replaced by Vale, a maintained, markup-aware
prose linter, with the rules expressed as configuration. Vale can also grow to
cover rules the script could not, such as defining an acronym at first use,
which is listed as a not-yet-built check rather than claimed as done.

The script was the right thing to build in the moment, because a mechanism in
hand beats a rule in prose, and it proved the checks were worth having. It was
the wrong thing to keep, because a maintained tool trusted only as far as it has
been tested (D-003) is a smaller surface than code nobody else runs.

The general rule: prefer a maintained tool over a hand-written one, and when a
hand-written check earns its keep, treat it as a placeholder to be replaced
rather than a permanent asset. Building the check first is not waste; keeping it
after a real tool fits is.

-------------------------------------------------------------------------------

## D-015: The agent doctrine uses AGENTS.md, with CLAUDE.md as a pointer

Instruction files for coding agents converged on a shared open format, AGENTS.md,
read natively by many tools rather than by one. The standards are therefore
carried into a project as AGENTS.md, and CLAUDE.md becomes a one-line pointer to
it so Claude Code reads the same source without a second copy to maintain.

Why: a project should not be tied to one agent, and two full copies of the
doctrine drift apart. One source with a pointer keeps the standards portable and
singular. This repository follows its own rule: AGENTS.md here is a copy of
STANDARDS.md, and CLAUDE.md points to it.

Consequence: when the doctrine changes, STANDARDS.md is the source and the
AGENTS.md copy is regenerated from it, never edited directly.

-------------------------------------------------------------------------------

## D-016: The component library is a catalog, not built code, until reuse justifies it

A packaged component library was built and then removed within the same
sitting. It held four pure functions extracted from one project, which is not a
library, it is a few helpers. Packaging them pulled language-specific Python code
into a repository whose value is portable doctrine, and it did so before any
second project needed the blocks.

That reversed two of this baseline's own principles: build what is justified,
not what is speculative, and keep the doctrine portable. A shared library earns
its place at the second use, when copying a block becomes the friction worth
removing, not at the first.

COMPONENTS.md is therefore a catalog and a roadmap: it names each vetted block,
states the property it protects, and points to the project where it is proven and
copied from. The runtime layer stays documented as a concept without premature
code. When a block is needed in a second project it is copied, and when the copy
becomes friction it is extracted, at which point a per-language library repository
is the likely home rather than this one.

The general rule: a delivery layer can be real as a concept before it is real as
code, and documenting it is not the same as building it.

-------------------------------------------------------------------------------

## D-017: Secret scanning runs at three layers, including the server

The "no secrets" rule was enforced by a pre-commit hook and a pipeline scan.
Both run on code the developer or the pipeline controls, so a developer who
skips the hook is caught only later, in continuous integration, after the push
already happened. Push protection, the hosting platform's server-side secret
scanning, closes that window: it refuses a push carrying a detected secret
before the commit lands on the server, and no local flag bypasses it.

Enabled on the public repositories once the feature became available at no cost.
It is the strongest layer because it is the one the developer cannot turn off
from their own machine. The pre-commit hook stays for fast feedback, and the
pipeline scan stays for full-history coverage; each fails in a different place,
which is why all three are kept.

The general rule: enforce an important rule at more than one layer, and prefer
the layer the person being checked cannot disable.

-------------------------------------------------------------------------------

## D-018: Publication waits for a full human read

Two repositories were made public before their text had been read end to end.
Both were clean by every automated check, and both still contained sentences the
author would not have written: language that told the reader what to conclude,
and framing that described who might read the work rather than what the work is.
Neither is the kind of defect a tool detects, and both required rewriting history
after the fact.

The rule is therefore that making a repository public is gated on a person
reading the whole thing, not on the checks passing. The checks and the read
answer different questions. A scanner answers whether anything dangerous is
present; only a reader answers whether the writing says what it should.

Consequence: no visibility change is proposed or made until the read is done,
however long that takes. Publishing is the one action that cannot be undone, so
it is the one that waits.

## D-019: Fourteen rules from one build's incident record

A downstream build (role-call, August 2026) produced a session review
whose confirmed findings and running incident record earned rules the
standards did not have. Each was verified absent from the standards
before writing, and each cites its incident where it now stands:
request-path documentation in Writing; single-source enforcement and
verifier construction in Code; bounded attacker-writable records and
suppressions-with-reasons in Security; pins-name-their-watchers in
Dependencies; out-of-band state rituals and the refusal of process
theater in Git practice; environment parity in the definition of done;
and in the agent section, the externally-verifiable provenance trailer
correcting this repository's own earlier rule, read-back verification,
narration verified at writing, the strongest opposing read supplied
unprompted, and execution transcripts with failures kept.

The mechanism working as designed: principle six says every incident
review catches becomes a rule, and this entry is that principle
executing at batch size. The enforcement file gains the honest tier
four rows for what no tool checks yet, with the environment parity
comparison named as the next candidate to move up.

## D-020: The standards prescribe naming a planning method, never a method

A downstream build was asked which planning method its work
decomposition followed and could not answer without reconstructing it
after the fact, though the sequence turned out to be deliberate in
every step. The gap was the record, not the thinking.

The rule that follows from it prescribes the naming and not the choice.
Prescribing a method here would be doctrine without evidence: one
project has been built to this baseline by one person, a walking
skeleton and ordered layers served it, and a team shipping increments
to users would be right to slice vertically instead. A baseline that
mandated either would be enforcing a preference formed on a sample of
one, which is the failure the "not yet covered" section exists to
prevent.

Naming is prescribed because it costs a paragraph and answers the
question the second principle already asks of everything else: from
outside, a considered sequence and an accidental one look identical.
The rule also asks for what the sequence gives up, because a stated
cost is what lets a later reader judge the choice rather than take it
on faith. It sits in the human-checked tier, since no tool can judge
whether a named method suits a project, and it earns its place there
only until a second project makes the check mechanical.

## D-021: Five rules about what happens after a catch

The rules added with D-019 were about defects. These five are about the
loop that follows one: what becomes permanent once something has been
found. They were identified by checking the standards against a build's
incident record rather than against memory of writing them, which is
also how the gap was found, since the author of a rule is the worst
judge of what it omits.

Fixtures derived rather than typed, because hand-made demonstration
input was wrong three times in one build while the system was right
every time. A fix verified by re-running the check that found the
defect, because a repair introduced while repairing is ordinary. The
second identical hand-fix becoming automation, because a tax paid twice
and scheduled a third time is a decision nobody made. A manual check
pinned into configuration, because a check in one person's shell
history has already told its only truth. And bulk edits ordered so no
replacement rewrites an earlier one's output, from a renumbering that
shifted three references twice.

All five sit in the human-checked tier today. The last two are the ones
worth watching: each becomes a tier-one gate the moment somebody writes
the hook, and the rule exists partly to make that omission visible.

<!-- vale BuildGuidelines.Audience = NO -->
<!-- vale BuildGuidelines.Figurative = NO -->
<!-- Scoped exception: this entry documents the rule tokens themselves,
     so it necessarily quotes the words the rules forbid. Mentioning a
     banned word to govern it is not using it. -->
## D-022: The audience rule narrows, and the idiom rule learns

Two writing-rule changes from one review session, recorded with their
causes the way every rule change is.

The word "reviewer" comes off the audience token list. The rule
existed to keep job-search framing out of public documents, and for a
while every use of the word was that framing. Then a governed product
gained a reviewer role and review campaigns, and the word became
product vocabulary; the scoped exceptions multiplied until the
exception was the norm, which is the signal a rule has outlived its
scope. The remaining tokens, hiring, recruiter, interview, portfolio,
resume, have no legitimate product sense and stay.

The figurative rule gains the idioms a person had to catch by hand in
one session: hand-rolled, the rubber-stamping figure, cries wolf,
straight face, earned its keep, the wearing-a constructions, and
footgun. A token list can never enumerate every idiom, so the human
read stays the first line; but each phrase a person flags joins the
list, because the second identical hand-fix becomes automation
(D-021), and this entry is that rule applied to the rules themselves.
<!-- vale BuildGuidelines.Figurative = YES -->
<!-- vale BuildGuidelines.Audience = YES -->
