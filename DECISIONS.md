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
suite does what it claims. It is now Pass 4 of the [checkpoint passes](ENFORCEMENT.md#pass-4-mutation), and the results
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

Documents drift from systems by default. Pass 2 of the
[checkpoint passes](ENFORCEMENT.md#pass-2-claims-against-reality) exists
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

What exists instead is a catalog and a roadmap, kept in
[VETTING.md](VETTING.md) alongside the bar for outside code because both answer
whether code is fit to reuse here. It names each vetted block, states the
property it protects, and points to the project where it is proven and copied
from. The runtime layer stays documented as a concept without premature
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

## D-023: This repository lives under the method it prescribes

The standards here demand review-gated changes, scoped identities, and
signed work of every repository in the program, while landing on this
one through direct pushes signed by nothing. That gap closes now, and
the record of closing it is this entry arriving as the repository's
first pull request.

The arrangement, matching the application repository's: changes travel
branches and pull requests; the pull request is proposed by the
program's agent identity, an installed app scoped to the program's
repositories with named permissions; commits are signed with the
program's key, which serves this repository and the program repository
and never the application's, because identity is scoped to what it
works on; and the mainline ruleset requires the passing checks and one
approving human review, refuses direct pushes, force pushes, and
deletion. The ruleset lands immediately after this entry merges, so
the one review-free merge that admits this decision is the last
review-free merge this repository ever performs.

## D-024: A branch merges within days and is deleted at merge

The standards required small diffs and pull requests but said nothing
about the branch carrying them: how long it may live, or what becomes
of it after merge. Practice produced short branches on its own, and
the cleanup half not at all. One repository was found carrying
twenty-three fully merged branches, and an earlier cleanup of exactly
such accumulation closed three open pull requests on an unverified
claim, recorded in the standards as the narration incident. Both merge
races this month also happened inside the window where an open branch
drifted behind a moving mainline, and that window is the branch's age.

The rule states what the small-diff rule already implied and adds the
half that was missing: a branch exists to become one small pull
request and merges or closes within days, and a merged head branch is
deleted at merge by the platform's automatic deletion. That deletion
is the one pre-approved case under the rule that branch deletion asks
first; every other deletion still asks. The setting has no diff, so it
lives as an attested row in the platform baseline, and the stale
branch question joins the human checklist until a scheduled listing
exists.

Rejected: a hard age limit enforced by a gate, because a branch's
correct lifespan is its review time, which a person controls and a
tool would misjudge. Also rejected: leaving the practice unstated,
because the twenty-three accumulated branches show the cleanup half
does not happen on its own.

## D-025: The repository is build-doctrine, and it scores

Two things changed together. The name: guidelines are advice, and
nothing here is advice. Every rule records the incident that produced
it and the mechanism that enforces it, which is doctrine, and the name
now says so. The old name redirects, and every reference in the
program's repositories moved in the same pass.

The scoring: the enforcement tiers said where a rule is checked but
not how far a given repository had taken a given rule, and the answer
to that was always a judgment call. It is now a six-level scale with
a decidable definition per level, from absent through stated,
attested, checked on demand, gated, and gated with proof, and a
scorer that establishes the first five levels from a repository's
files, history, and platform ruleset. The sixth level is never
inferred; a repository earns it by recording where its gate fired.

Rejected: a separate repository for the scorer, on the argument that
doctrine and tool serve different audiences. The counter that won:
the scorer is the doctrine's own enforcement made portable, and a
rule that ships with the thing that measures it is the whole idea of
this repository. Also rejected: adopting an existing repository linter,
because the ones that exist stop at whether a file is present, and
the scale's point is whether the claim inside the file is true.

## D-026: Repository kinds, the presence baseline, and two earned rules

The standards described an application. The program then built a
reference table, a set of exported flashcard decks, a drawings
repository, and a profile page, and each needed rules the standards
never mentioned while ignoring rules that had no meaning for it. A
presence audit in September 2026 then found a hardened application
with no security policy and a drawings repository with no license,
gaps that had hidden in plain sight because nothing listed what every
repository must carry.

Repository kinds fix the first problem: each repository declares its
kind, and the kind decides which rules apply, so an inapplicable rule
is reported as such rather than confused with a gap. The presence
baseline fixes the second: README, a license fitting the content, a
security policy wherever code or data is served, and a contributing
file wherever contributions are invited, with a code of conduct
deliberately excluded and the reason written down. Two rules were
earned along the way: a generated artifact carries a parity check,
from the mapping table and the deck exports, and a README names its
likely failures, from the hands-on session where a stale stylesheet
hid a deployed change and nothing in the documents said so.

Rejected: requiring a code of conduct because tooling looks for one.
A file that claims a community where none exists is exactly the
false statement the scale scores as zero.

## D-027: Outside code is vetted before adoption, and the rater's checks are mapped

A question the doctrine could not answer exposed two gaps at once. Asked
how to adopt an outside application safely when there is no time for a
full review, the standards had rules for a package in a lockfile and
nothing for the larger case: an application cloned to run, a library of
significance, a tool the pipeline executes. At the same time, role-call
had carried the OpenSSF Scorecard badge since August without any
document naming what the scanner checks, so the doctrine was displaying
a rater's number it could not explain.

The first gap is closed by a section in the standards, "Adopting outside
code", with `scripts/vet.py` as its mechanism: the outside signals are
read and recorded, install-time code and committed binaries are scanned,
the analyzers run on the checkout, the license is checked for
compatibility, the code is pinned and built from source through a
controlled source where one exists, it runs with the privilege and
egress it needs, and what was skipped is accepted with an owner and an
expiry date. The second gap is closed by a table in the enforcement
document mapping each Scorecard check to the doctrine rule that covers
it, the mechanism that enforces it here, and the scanner's own role.
Building the table found three practices in force in every pipeline and
written in no document: static analysis, fuzzing of untrusted-input
parsers, and release provenance. They are rules now, cited to the
mapping.

Rejected: recording the adoption case under "Not yet covered" with a
trigger, which the agent proposed. That list exists for rules with no
mechanism, and every mechanism this needed already existed: the scorer,
the raters' public interfaces, the analyzers, and the container rules.
A gap entry beside a working mechanism is a rule someone declined to
write.

Rejected: a separate repository for the vetting tool. D-025 settled the
same question for the scorer: the tooling that proves the doctrine
belongs beside the doctrine that explains why the checks are the
checks. If the tool ever serves people who do not use the doctrine, one
script moves.

Rejected: requiring a full review before any adoption. It is the
standard, and a rule nobody can meet under time pressure is bypassed in
silence; the section instead makes the shortcut visible, bounded, and
dated.

## D-028: A name is checked and held the day it is chosen

role-call was named in August 2026 and nothing checked whether the
name was free anywhere but under the one account it was created in. In
September, when a companion project made a matching organization
name worth having, the `role-call` organization belonged to another
account, idle since April 2025, and GitHub's Username Policy releases
a held name only for a trademark claim. The project is being renamed
to head-count to get an organization name that matches, which is a
rename of a package, six environment variables, a database, an image,
an app, and every document and outside service that names it.

The check takes seconds: the account namespace, the package index, a
domain. It now happens the day a name is proposed, beside the
visibility decision, and the result is stated in the same reply. A
free name is then held, because checking is not holding: GitHub and
the package indexes both remove names that are reserved and left
empty. A hold is a real use, an organization with a profile pointing
at the project or a minimal published package under the name.

Rejected: reserving names speculatively across every namespace, which
the platforms forbid and which would be the squatting this rule is
written against; and treating the account-scoped repository name as
enough, which it was until the day it was not.

## D-029: An agent app's commits are history, and the scorer reads them

The commit-subjects rule checks that recent subjects lead with an
identifier. It skipped every author whose name carried `[bot]`,
because when it was written a bot meant an update bot, and those
answer to their own subject conventions.

manifest-identity now proposes every change through an agent app, so
the platform records that app as the author. Combined with merge
commits, which the rule also skips, the last human-written subject
fell out of the thirty the rule reads, and the scorer reported "no git
history readable" and scored zero on a repository whose subjects all
conform. The gate failed the compliant case, which is worse than not
gating at all: the rule stopped measuring subjects and started
measuring the presence of humans.

The exclusion is now by name, a short list of dependency bots, rather
than by the `[bot]` suffix that every app carries. An update bump is
also caught by its subject, which is the stable signal and already
tested, so the two together cover what the author test was for.

Found when it blocked a merge, which is the right way for a gate to be
wrong: loudly, on work that was correct.

Rejected: dropping the rule from the required set, which removes a
check rather than fixing it; and having a person author a commit to
refill the window, which games the measure this doctrine exists to
keep honest.

## D-030: A subphase number is an identifier

The commit-subjects rule accepted a decision identifier or a
capitalised area, `D-017:` or `CI:`. A repository built to a phase
plan also commits work as the subphase it belongs to, `1.5:`, and the
rule scored those as having no identifier at all.

The rule's purpose is that the identifying part of a subject survives
a narrow panel, which truncates around thirty characters. A subphase
number does that as well as either accepted form, and it points at the
plan entry that says what the change was for, which is more than a
capitalised area name carries.

Recorded plainly because the form arrived by accident rather than by
design: an agent wrote five subjects that way in one day while the
only check on the rule was blind for the reason D-029 records, and the
established convention in that repository, ninety-eight commits of it,
had always been the other two forms. The choice was to widen the rule
or to treat the five as wrong. They are not wrong; the rule was
narrower than its own reason.

What did go wrong is that nothing caught the new form at the time. The
scorer reads the last thirty subjects after the fact, and the
commit-message hook checks the writing rules without checking the
identifier at all, so the only check on this rule was a slow one. The
hook is where it belongs, and that is the next change rather than this
one.

Rejected: leaving the pattern and letting the non-conforming subjects
age out of the window, which blocks every merge for a month over
subjects that serve the rule; and rewriting the merged subjects, which
is public history rewritten to satisfy a regular expression.

## D-031: The published frameworks are read to learn from, not to map against

The doctrine credited OWASP, ASVS, NIST and SLSA in its
acknowledgements and connected none of them to a rule. That is the
weaker half of what those lists are for.

Mapping asks which of our rules answers an item. The answer is almost
always that one does, the table fills with green, and nothing is
learned; the artifact produced is the compliance wallpaper this
doctrine refuses everywhere else. Learning asks what the item teaches
and whether we do it, and that question produces gaps. It has produced
them here before: reviewing one project's decisions against the OWASP
Top 10 found stored cross-site scripting, request forgery and
self-approval, none of which had been addressed. The lesson became
doctrine and the list did not.

So COVERAGE.md is a reading of seven lists, and nine rules came out
of it that did not exist before. Deny by default, which the doctrine
held only as a configuration principle and not as an access-control
rule. The exposed surface enumerated and checked, which a project
already gated and the doctrine never stated. Response headers and
cross-origin policy, practiced and unwritten. The session identifier
changing at authentication, which expiry and revocation do not cover.
Nothing reconstructing an object from input, where safety was an
accident of format choice. Outbound requests going where the code
decided, and responses from other systems treated as input, both
written before the first live connection makes them violable. An
exceptional condition leaving the system as it found it, from the item
the 2025 edition added, because an error path that skips a check or
leaves half a write is a control failure and not a bug report. And a
section for products that put a model in their serving path, plus two
rules for the agent's own exposure to what it reads.

That last one is the answer to a question worth stating plainly. This
doctrine is written by an agent that reads repository files,
dependency documentation, build logs and review text, all of which
are written by other people. Saying nothing about instruction
injection while being produced that way would be a hole in the shape
of the method. The rules are that what the agent reads is data, and
that its capability is bounded so a successful injection produces a
proposal somebody rejects rather than a commit that lands.

Five items have no rule and say so with a trigger: breached-password
screening, sensitive business flows, model and data poisoning,
retrieval access control, and delegated authorization. An item
answered by nothing is the most useful row in the table, and hiding it
would defeat the exercise.

A gate holds four properties a machine can decide: every published
item has a row, no row survives an item the frameworks no longer
publish, every governed rule appears in the table, and a row claiming
no rule names its trigger. It deliberately does not judge whether a
cited rule actually answers its item, because that is judgment, it
belongs to the human tier, and a script pretending to decide it would
be the wallpaper one level up. The counts in this entry were corrected
by the redo recorded in D-032, which is also where the first version of
that gate is described: it compared the document against numbers typed
from recollection, which is not the same thing at all.

MITRE ATT&CK is excluded, and the exclusion is recorded rather than
silent. Asked the same question, what it teaches is how to detect an
adversary already inside: a property of a running estate and the
tooling that watches it, not of rules about writing code. It belongs
where the evidence lives, and in the identity project built to this
doctrine each finding class names the technique it gives evidence of,
stated with its limit, that configuration shows exposure to a
technique and never its use.

Found on the way, and fixed first because everything else stood on
it: ENFORCEMENT.md opened by claiming every rule in STANDARDS.md
appears there with the thing that checks it, and ten of the
twenty-seven security rules did not appear at all. Most were enforced
in the application repositories and never written down. A coverage
table built on that record would have inherited every hole.

Rejected: a row per ASVS requirement, which is several hundred rows
nobody maintains, so chapters instead; mapping at SSDF task level for
the same reason; and adding ATT&CK to reach a rounder number of
frameworks, which is the impulse this whole document is written
against.

-------------------------------------------------------------------------------

## D-032: A coverage claim is checked against the source, not against memory

The first version of COVERAGE.md was written from recollection. It
mapped the 2021 OWASP Top 10 while 2025 was the current edition, and
version 4 of the Application Security Verification Standard while
5.0.0 was, and it recorded SLSA at three build levels when the
published spec had four. Sixty-five rows, none of them read from a
source that day.

The gate written alongside it made that permanent rather than
temporary. It held the expected item count for each framework as a
number in the script, and the numbers were the same recollection, so
the check compared the document against its author's memory of the
document. It passed. It would have kept passing for years while every
row aged, which is worse than having no gate: a failing check is a
task, and a passing check that verifies nothing is a false assurance
that stops anyone looking.

Terry found it by asking the obvious question, whether the Top 10 in
the table was the current one. His objection was not that the rows were
wrong. It was that verifying them was work he would have to do himself,
and that a document he has to re-derive is worth less than no document.
That is the standard this entry is written to.

So the item lists move out of the prose and into
[frameworks.json](frameworks.json), where each framework carries its
published version, the source it was read from, and the date it was
read. Two checks stand on it, and each catches what the other cannot.

`scripts/check_coverage.py` reads that file and needs no network. Every
published item must have a row, no row may survive an item the
frameworks no longer publish, every governed rule in STANDARDS.md must
appear somewhere in the table, and a row claiming no rule must name
what would trigger writing one. Nothing in it is a number typed by
hand.

`scripts/refresh_frameworks.py` refetches every source and asks the
question presence cannot answer. The 2021 Top 10 page still exists and
still says 2021, so a document mapping it stays internally consistent
forever; a check that only confirms the recorded items are still there
would have called the original table correct. Each framework therefore
has a second probe against the index that lists its editions, and a
version higher than the recorded one fails and names itself. Where a
source cannot be read, the framework is reported unchecked and the run
still fails, because an unverified claim and a verified one must not
look alike.

It earned itself on the first run. SLSA has published version 1.2,
which this document had recorded as 1.1, and 1.2 adds a source track:
four levels describing what protects a repository rather than what
protects a release. Two of the four are answered here only in part, and
the shortfall is the same in both. The controls are real and
continuously enforced by an active ruleset, and nothing attests to
them, so a consumer who wants proof has to be given read access to the
settings. That is a finding the old table could not have produced,
because it did not know the track existed.

The refresh runs monthly and on a change to the data file, not on every
commit. A new edition is not caused by a commit, and a gate that blocks
unrelated work on an upstream event teaches people to ignore it.

Rejected: keeping the counts in the script and promising to check them
by hand at each release, which is the promise that failed; scraping the
item lists at check time, so the build depends on seven websites being
up and a page redesign reads as a coverage failure; and pinning the
sources by content hash, which fails on every unrelated edit to a
marketing page and says nothing about editions. The data file is
committed, so what the document is checked against is reviewable in a
diff, and the network check is a separate job whose failure is a task.

-------------------------------------------------------------------------------

## D-033: A claim that a rule is enforced is checked against the artifact

ENFORCEMENT.md opens by saying that every rule in STANDARDS.md appears
there with the thing that actually checks it, and that a rule with no
mechanism is a hope rather than a standard. Nothing checked that
sentence. Asked to go looking after the coverage gate turned out to
verify its author's recollection (D-032), an audit of every mechanism
the documents name found the sentence false in six places.

Five of the six were one shape. A control was implemented in the
repository where its lesson was learned, and a table generalized it to
an artifact it had never reached. Nothing was invented and written up as
done; the failure was propagation, and it survived because no check
compared a claim about the template against the template.

The worst of them had been running for months. Both `template/` and the
reference application carried a step named "Secret scan over full history
(gitleaks)" that used the gitleaks action. The action's own source settles
what it does: it passes `--log-opts=--no-merges --first-parent
baseRef^..headRef`, and `--log-opts=-1` when base and head match, so it
scans the event's commits. Above it sat `fetch-depth: 0`, fetching a
history nothing then read, which is what made the step look proved.
This repository had already found that and switched to the pinned binary,
with a comment in its own workflow explaining why. The fix never reached
the file every new project starts from.

The others: an enforcement row naming the gitleaks action for a scope it
does not cover, while the three repositories actually run three different
things; a pipeline table asserting that one file defined all of its rows
when three were elsewhere; `scripts/vet.py` sitting in the tier that
means the merge does not happen, run by no pipeline anywhere; the
workflow lint and audit claimed for a template that had neither; and a
template shipping one of the five commit-time hooks the table lists.

Adding the lint job to the template then found two more, which is the
argument for the job in one sentence. The template declared no
permissions block at all, so every job ran with the repository default
while the doctrine's own row claimed least privilege, and two checkouts
left their credential in the workspace.

The fixes for those are instances. The mechanism against the class is
`scripts/check_mechanisms.py`, and it is the coverage gate's shape
applied one level in: the pairing between a row and its implementation
moves out of prose and into mechanisms.json, where each blocking row
names the files that hold its mechanism and a pattern that must still
appear in them. Every row must have an entry and every entry a row, so
rewording a row fails until somebody looks at the mechanism again. Every
path the document names in prose must exist. Artifacts that live in an
application repository are reported as declared, never as verified,
because this repository cannot read that one and an unverified claim must
not look like a verified one.

Its limit is stated where it is written: a pattern proves a mechanism is
present, not that it works. Mutation runs answer that question, and the
human tier answers what neither can.

Rejected: auditing by hand at each release, which is the promise that
failed here and failed for coverage; a gate that runs each project's
tests from this repository, which would make a doctrine repository depend
on every repository built to it; and dropping the application rows from
the tables to make the gate's job easy, which would leave the doctrine
silent about what a project is expected to have, so the rows stay and
carry their repository instead.

-------------------------------------------------------------------------------

## D-034: One fact, one home, and fewer documents holding it

Seventeen markdown files, and six of them described the rules and how
well they are held. The overlap was not spread thinly across the
repository; it was concentrated, and two files were a second and third
telling of what two others already said.

FUNDAMENTALS.md gave nine subjects in plain words, then restated the rule
for each, then named its enforcer, then linked a proof. The rule was
already in STANDARDS.md and the enforcer was already in ENFORCEMENT.md,
which itself says that two places holding the same fact is how one of
them goes stale. REVIEW.md held six checkpoint passes whose commands were
the verification tier of ENFORCEMENT.md in a different order and
different words, so that tier lived in two files and the container probes
appeared in both.

Neither was wrong. Both were a copy, and a copy decays in one direction
while its original moves in another.

So the plain words open the standards, as the section a reader lands on
first, carrying only what is theirs: what the danger actually is, a
pointer to the rule below, and a pointer to the repository where the
check runs. The passes become the verification tier's procedures, with
the per-rule table above them and the per-session order below, and a
command that appeared in both is written once. COMPONENTS.md joins
VETTING.md, because both answer whether code is fit to reuse here, one
for code from outside and one for blocks of ours that cleared a bar.

SCORES.md was the fourth, and its problem was different. Its content is
entirely a claim about other repositories, and it was assembled by
running the scorer seven times and pasting seven tables. Regenerating it
with the new `scripts/render_scores.py` moved five of seven repositories:
one had gained a required check, another had gained a workflow and a
pinned action, a third had climbed off zero on commit subjects, and the
decision counts were twenty and six entries behind. Twelve days had done
that. It now has a command that writes it and a `--check` that fails when
the committed copy no longer matches the scorer, and the four figures in
it that tests can hold offline are held.

Seventeen files are fourteen. What was not merged, and why: README,
SECURITY and CONTRIBUTING are surfaced by the platform and two of them
are scored; AGENTS.md and CLAUDE.md are pointers that exist because
different tools read different filenames, so collapsing them breaks
whichever tool reads the name that disappears; COVERAGE.md answers a
different question from what the rules are and now carries a data file
and two gates of its own.

One rule of the scale moved with this, and it took three attempts to
make it tell the truth. Generated-artifact parity applied to reference and
study repositories, the kinds whose content is a view of data, and not to
a doctrine repository, which had no generated artifact until now. Adding
this kind made the rule score itself, and each version of the detector was
wrong in a different way.

It looked for a script whose source mentions the parity flag, so it
matched the scorer, whose own source holds that flag in the line doing the
matching. This repository scored four for owning a checker that was the
thing doing the scoring. Narrowing it to a declared argparse flag fixed
that and broke something else: the reference repository handles the flag by
reading the arguments directly, and a working checker its pipeline runs
scored as absent. And the credit for running in a pipeline was computed
across all candidates while the sentence named the first one, so the rule
could name one script and credit a pipeline for a different one, which is
exactly the true-sounding sentence this scale exists to refuse.

What it does now: a candidate names the flag and handles it, by either
idiom; the flag is assembled at runtime so a detector cannot be its own
instance; and the pipeline credit is per script and names the script the
pipeline actually runs. Four tests hold each of those, one per way it was
wrong. This repository scores three: the command exists and runs at a
checkpoint rather than in the pipeline, because it reads clones and a
platform that a runner does not have.

Found while regenerating the scores, and fixed because the document is
published: the scorer wrote "1 required checks" and "all 1 uses pinned by
commit". Nobody edits a generated file on the way past, so the agreement
belongs in the generator.

Rejected: leaving the plain-words file alone because it reads well, which
is true and is also what a decaying copy does; merging COVERAGE.md into
ENFORCEMENT.md to reach a rounder number, which would put the framework
reading inside the mechanism record and make both harder to hold; and a
single STANDARDS.md holding rules, enforcement and procedures together,
which is one file nobody can review and would undo the separation that
lets a rule be stated once and checked somewhere else.

## D-035: A retired name is refused in active text, and history is allowed by name

A rename leaves the old name behind wherever nobody was looking: a
related-projects section in another repository, a hook's label, a
badge, a repository description, an outside project record. The
September 2026 audit found five of those for one rename, weeks after
it, by reading. The doctrine already says a name is checked the day
it is chosen; nothing said what happens to the name that was given
up.

So the program keeps one list of retired names with what replaced
each, and a script walks a repository's tracked text files and fails
on any line that carries one. The list lives here because a rename
is a program fact and not a repository fact. Each repository names
the files that keep the old name as history in its own doctrine.yml,
whole or by the phrase on the lines that may keep it, because the
decision record, the usage record, a migration note, and a lesson
that names the incident are supposed to carry the old name, and an
allowlist written per repository says which ones and why.

Binary files are skipped by content, because a check on written text
that reads an image's bytes finds words nobody wrote, which is how the
site's marker check failed on a banner the same week.

Rejected: a grep in each repository's own pipeline with its own list,
because the list would drift the first time a second name retired;
searching by hand after each rename, which is what the audit was; and
rewriting history so the old name disappears, which the doctrine
forbids and which would remove the record of why the rename happened.

The cost is one more line in each repository's doctrine job and a
pin bump when the script lands, paid once.
