# Review

Procedures a human runs at a checkpoint. Each one produces evidence, not an
opinion. Nothing here asks whether something is secure; every step names a
command and an expected result.

**Contents:** [When to run these](#when-to-run-these) · [Pass 1, does it run](#pass-1-does-it-run) · [Pass 2, claims against reality](#pass-2-claims-against-reality) · [Pass 3, hostile probes](#pass-3-hostile-probes) · [Pass 4, mutation](#pass-4-mutation) · [Pass 5, history and hygiene](#pass-5-history-and-hygiene) · [Pass 6, the first fifteen minutes](#pass-6-the-first-fifteen-minutes)

-------------------------------------------------------------------------------

## When to run these

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

-------------------------------------------------------------------------------

## Pass 1, does it run

Clone into an empty directory and follow the README literally. Do not use
knowledge you have that a reader does not. Every documented path gets tried,
including the one for readers who have only containers and no local language
runtime.

Failures found this way, which no test suite catches: setup steps that assume a
tool the reader was never told to install, key generation that cannot run before
the thing it configures exists, and a stale container serving old code because
the documented command does not rebuild.

Record how long it took. A reader's patience is the real limit.

-------------------------------------------------------------------------------

## Pass 2, claims against reality

Take every factual claim in the documents and check it against the running
system: test counts, record counts, control behavior, the container assertions.
Correct the document, not the memory.

The rule is that a number in a document is a claim under test. Documents drift
from systems by default; only a check stops it.

-------------------------------------------------------------------------------

## Pass 3, hostile probes

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

-------------------------------------------------------------------------------

## Pass 4, mutation

The only way to know whether tests defend behavior rather than measure coverage.

For each significant control: remove it, run the suite, confirm named tests
fail, then revert and confirm the suite returns to green. Record the results as
a table in the project README.

A control whose removal breaks nothing has no test behind it. That is a finding,
and the fix is a test, not a note.

-------------------------------------------------------------------------------

## Pass 5, history and hygiene

- Scan the full history for secrets, not just the working tree.
- Search every tracked file for credential-shaped strings, which a secret
  scanner correctly ignores but a person reading the file will notice.
- Confirm the author identity on every commit is the intended one.
- Read every commit message as an outsider. Names of employers, clients,
  interview processes, and internal systems do not belong in history.
- Look for debug output, placeholder text, and dead code.

Anything found here is a rewrite or a rebuild, not an edit, because history is
permanent. Decide before publication, never after.

-------------------------------------------------------------------------------

## Pass 6, the first fifteen minutes

Read the repository as somebody encountering it for the first time, with fifteen
minutes and no prior context.

- Does the README's first screen say what this is and how to run it?
- Does the repository layout explain itself?
- Is there anything that would need to be overlooked or excused?
- Pick the fifty lines most likely to raise a question. Can every line be
  explained aloud?
