# Components

The runtime layer of the three delivery layers: the pre-hardened blocks a
project reuses instead of reimplementing, alongside the scaffold-time `template/`
and the pipeline-time workflow.

This file is a catalog and a roadmap, not a home for code. A block lives in the
project that proved it until the same block is needed in a second project, which
is the point at which a shared library is justified. Standing up a packaged
library before that reuse exists adds ceremony without removing friction, and it
would pull language-specific code into a repository whose value is portable
doctrine. See D-016.

**Contents:** [What qualifies as vetted](#what-qualifies-as-vetted) · [Vetted blocks and where they live](#vetted-blocks-and-where-they-live) · [When a shared library is justified](#when-a-shared-library-is-justified) · [Roadmap](#roadmap)

-------------------------------------------------------------------------------

## What qualifies as vetted

A block is listed here only when it meets every bar below. Anything short of all
four is roadmap, because an unproven block reused widely is a single point of
failure rather than a control.

- It was used in a shipped, reviewed project, not written to fill a catalog.
- It survived that project's mutation testing or hostile probing.
- It has a test in its home project asserting the security property, not just
  behavior.
- It carries no third-party dependency, so there is nothing to pin and the whole
  block can be read in one sitting.

-------------------------------------------------------------------------------

## Vetted blocks and where they live

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

## Roadmap

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
