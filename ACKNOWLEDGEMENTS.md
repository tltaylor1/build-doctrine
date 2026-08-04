# Credits and rationale

This baseline stands on established work. It assembles and connects ideas that
others built, and its only original part is the connection itself. This file
records what it draws on, why it exists, and what is different about the way it
is put together.

**Contents:** [Why this exists](#why-this-exists) · [What is different here](#what-is-different-here) · [Standards and bodies of knowledge](#standards-and-bodies-of-knowledge) · [Tools](#tools) · [Patterns and prior art](#patterns-and-prior-art) · [A note on honesty](#a-note-on-honesty)

-------------------------------------------------------------------------------

## Why this exists

Security added at the end of a build is expensive and partial. Security present
from the first commit is neither. This baseline is an attempt to make the
secure path the default path for the projects built here, so that good decisions
are inherited rather than relitigated each time.

It exists for a second reason too. Building software with an artificial
intelligence agent is now ordinary, and doing it well is a skill of its own:
constraining the agent with standards it reads every session, reviewing every
change, and enforcing the rules with mechanisms rather than trusting either the
person or the agent to remember. This baseline is how that discipline is written
down and made repeatable, so the next project starts where the last one ended
instead of rediscovering the same lessons.

-------------------------------------------------------------------------------

## What is different here

The individual pieces are not new. Standards catalogs exist, security tools
exist, and instruction files for coding agents are now a shared format. What is
uncommon is the connection this repository insists on: every rule is tied to
both the tool that enforces it and the specific failure that produced it, and
the whole thing is measured against real projects rather than described in the
abstract.

Concretely, that means [ENFORCEMENT.md](ENFORCEMENT.md) maps each rule to a
mechanism and labels the gaps honestly, [DECISIONS.md](DECISIONS.md) records the
incident behind each rule, and [REVIEW.md](REVIEW.md) verifies by running tools
and removing controls rather than by asking whether something is secure. A rule
here can be traced from the standard that motivates it, to the failure that
proved it necessary, to the check that now catches it. That traceability, kept
current against shipped work, is the part that did not already exist in this
form.

-------------------------------------------------------------------------------

## Standards and bodies of knowledge

- The Open Worldwide Application Security Project (OWASP), for the Top 10 and the
  Application Security Verification Standard (ASVS), used as the external
  checklists the security rules are audited against.
- The National Institute of Standards and Technology (NIST), for the control
  families and the software supply chain guidance that shape the doctrine.
- The International Information System Security Certification Consortium, known
  as (ISC)squared, for the Certified Information Systems Security Professional
  and Certified Secure Software Lifecycle Professional common bodies of
  knowledge, used to audit the standards for coverage gaps.
- The Federal Plain Language Guidelines, which the writing rules follow, because
  a control a reader cannot parse is a control they cannot challenge.
- Supply chain formats: CycloneDX for the software bill of materials, and the
  Supply-chain Levels for Software Artifacts (SLSA) framing for build
  provenance.

-------------------------------------------------------------------------------

## Tools

These are used rather than reimplemented, and each is held to the dependency
standards in [STANDARDS.md](STANDARDS.md).

- gitleaks, for secret scanning at commit and across history.
- Vale, for enforcing the writing rules as configuration instead of a
  hand-written script.
- Trivy, for container image scanning.
- Dependabot, for dependency updates delivered as reviewed pull requests.
- bandit and pip-audit, for static analysis and dependency vulnerabilities.
- CycloneDX, for the software bill of materials.

Selected but not yet in use, listed here so the distinction is visible: Semgrep
for structural code rules a syntax scanner cannot see, Checkov for
infrastructure configuration, hadolint for container build definitions, zizmor
and actionlint for pipeline definitions, and the OpenSSF Scorecard and Allstar
projects for repository practice scoring and enforcement.

-------------------------------------------------------------------------------

## Patterns and prior art

<!-- vale BuildGuidelines.Figurative = NO -->
<!-- The next line names industry patterns by their proper terms; the writing
     rule bans them only as figurative phrasing in our own voice. -->
- The paved road and golden path patterns from platform engineering, including
  Netflix's published work on making the secure path the default and delivering
  it at scaffold time, pipeline time, and runtime. That three-layer model is the
  structure this baseline uses.
<!-- vale BuildGuidelines.Figurative = YES -->

- The secure by design and secure by default principles as articulated by the
  Cybersecurity and Infrastructure Security Agency and others.
- AGENTS.md, the open instruction-file format for coding agents stewarded under
  the Linux Foundation, adopted here as the portable doctrine format.
- Claude Code hooks, used as the deterministic layer that enforces rules at the
  agent's lifecycle rather than only at the repository.

-------------------------------------------------------------------------------

## A note on honesty

Nothing here claims to be the first of its kind. It assembles existing tools and
standards, ties each rule to the failure behind it, and is measured against real
projects. Where a rule is not yet enforced, [ENFORCEMENT.md](ENFORCEMENT.md) says so. Where
a domain is not yet covered, [STANDARDS.md](STANDARDS.md) says so. Where a
component is not yet vetted, [COMPONENTS.md](COMPONENTS.md) says so. The credit
above is owed; the gaps are owned.
