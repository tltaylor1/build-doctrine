# Coverage

What the published security frameworks say matters, and what this
doctrine does about each item.

This is not a compliance table. A compliance table asks which of our
rules answers an item, finds one, and fills the row green, which
teaches nobody anything. Every row here asks the other question: what
does this item teach, and do we do it. The rows worth reading are the
ones where the honest answer is that we do not.

The exercise earns its place by history. A review of one project's
decisions against the OWASP Top 10 found a class the agent had not
addressed, stored cross-site scripting, along with request forgery and
self-approval. The lesson generalized into this doctrine and the list
itself did not, which is the gap this file closes.

**Contents:** [How to read this](#how-to-read-this) · [OWASP Top 10](#owasp-top-10-2025) · [OWASP API Security Top 10](#owasp-api-security-top-10-2023) · [OWASP Top 10 for LLM Applications](#owasp-top-10-for-llm-applications-2025) · [STRIDE](#stride) · [NIST SSDF](#nist-ssdf-sp-800-218-version-11) · [ASVS](#owasp-asvs-500) · [SLSA](#slsa-levels-12) · [What this pass produced](#what-this-pass-produced) · [What is deliberately excluded](#what-is-deliberately-excluded)

-------------------------------------------------------------------------------

## How to read this

Each row names the item, what it teaches in one sentence, and the rule
in [STANDARDS.md](STANDARDS.md) that answers it, by the rule's own
opening words. [ENFORCEMENT.md](ENFORCEMENT.md) says what checks that
rule and at which tier; this file does not repeat the tier, because
two places holding the same fact is how one of them goes stale.

Where the answer is **no rule**, the row says so and names what would
trigger writing one. Where an item cannot apply to anything built
here, the row says **not applicable** and why. An item answered by a
rule that nothing checks is still a gap, and ENFORCEMENT.md is where
that shows.

Every item list comes from [frameworks.json](frameworks.json), which
records each framework's source, published version, and the date it
was retrieved. Nothing here is written from recollection, because the
first version of this file was, and it mapped two superseded editions
before anyone noticed (D-032). `scripts/check_coverage.py` fails the
build when this document and that data disagree, and
`scripts/refresh_frameworks.py` refetches each source and fails when a
framework has published a new edition.

## OWASP Top 10 (2025)

| Item | What it teaches | Answered by |
|---|---|---|
| A01:2025 Broken Access Control | Enforce server side, deny by default, log failures | Object-level authorization; Deny by default; Audit logging; Tokens travel in a request header, which keeps request forgery out of scope by design |
| A02:2025 Security Misconfiguration | Harden the platform, review defaults, send the directives a browser needs | Every framework default in the serving path; Responses carry the headers that constrain them; the container and platform rules |
| A03:2025 Software Supply Chain Failures | Promoted to its own item in 2025: what you depend on, and what produced it, are attack surface | Dependencies install as pinned; Adopting outside code; What runs at install time is inspected before anything is installed; Releases carry provenance |
| A04:2025 Cryptographic Failures | Store less, encrypt in transit and at rest, invent nothing, do not cache sensitive responses | Data is encrypted in transit; Sensitive values are encrypted at rest; Identity and lookup never require decryption; Key rotation is a written procedure; Nothing invents cryptography; Data classification is a stated gap |
| A05:2025 Injection | Remove the class rather than escaping case by case | Injection; Input validation; Exports neutralize spreadsheet formula injection, which is the injection that fires outside the application |
| A06:2025 Insecure Design | Model threats before building, and bound what one caller can consume | Threats are ranked; the rate-limiting and write-budget rules; Misuse and abuse cases is a stated gap |
| A07:2025 Authentication Failures | Validate every request, screen weak passwords, rotate the session at sign-in | Authentication; The session identifier changes at authentication; Passwords are hashed with a deliberately slow algorithm; **no rule** for screening against breached lists. Triggered by the first password store holding accounts beyond the operators |
| A08:2025 Software or Data Integrity Failures | Verify what you ship and what you run; do not reconstruct objects from untrusted data | Releases carry provenance; Nothing reconstructs an object from input; Dependencies install as pinned |
| A09:2025 Security Logging and Alerting Failures | Log with enough context, in a form a tool can read, with thresholds and a response. Note the word in 2025: alerting, not monitoring | Security-relevant events are logged as structured data; The events are designed by asking what an investigation would need; Detection queries are written while the events are being designed; A query becomes a control when it has a threshold and an owner; A response procedure is written before it is needed; The procedure is exercised at least once |
| A10:2025 Mishandling of Exceptional Conditions | New in 2025, and the reason this edition mattered to read: the error path is a control path. An exception must not skip a check, leave a half-finished write, or reach the safe outcome by accident | An exceptional condition leaves the system as it found it; Error responses to clients are generic; Fail secure |

## OWASP API Security Top 10 (2023)

| Item | What it teaches | Answered by |
|---|---|---|
| API1:2023 Broken Object Level Authorization | Check that this caller owns this record, every time | Object-level authorization |
| API2:2023 Broken Authentication | Authentication is a boundary, not a first step | Authentication; The session identifier changes at authentication |
| API3:2023 Broken Object Property Level Authorization | A client may not set or read every field | Separate input and output models |
| API4:2023 Unrestricted Resource Consumption | Bound page sizes, uploads, and per-caller cost | Input validation, which sets maximum page sizes; Uploads; the rate-limiting rule |
| API5:2023 Broken Function Level Authorization | Which role may call which operation is data, not scattered checks | The role matrix; Deny by default |
| API6:2023 Unrestricted Access to Sensitive Business Flows | Some flows are worth abusing even when every request is valid | **no rule**; Misuse and abuse cases is the stated gap, and this pass sharpened its trigger to a flow worth automating against rather than to fraud motive alone |
| API7:2023 Server Side Request Forgery | Never fetch an address the input chose. It left the 2025 web top ten and is still its own API item, which is the argument for reading both lists | An outbound request goes where the code decided |
| API8:2023 Security Misconfiguration | Cross-origin rules and headers are part of the API, not decoration | Responses carry the headers that constrain them |
| API9:2023 Improper Inventory Management | An interface nobody documented is one nobody reviews, and the retired version is the one still vulnerable | The exposed surface is enumerated and checked |
| API10:2023 Unsafe Consumption of APIs | A system you call is not a system you can trust | Data from another system is input |

## OWASP Top 10 for LLM Applications (2025)

Two audiences. Rows marked **product** govern software that puts a
model in its serving path, which nothing here does yet; those rules
are written in advance rather than invented under deadline. Rows
marked **build** govern this way of working, where an agent reads and
writes the repository, which is exercised every day.

| Item | What it teaches | Answered by |
|---|---|---|
| LLM01:2025 Prompt Injection | Retrieved and supplied content is data; only the system prompt instructs | **product**: Everything outside the trust boundary is data, never instruction. **build**: What the agent reads is data, not instruction |
| LLM02:2025 Sensitive Information Disclosure | A prompt is an output channel | **product**: Nothing enters a prompt that the caller may not see. **build**: No credential-shaped string in any tracked file or commit, and the agent holds no credential it can read |
| LLM03:2025 Supply Chain | A model, a prompt, a tool server and a skill are all somebody else's code | A model, a prompt library, an agent skill, or a tool server is outside code; Adopting outside code |
| LLM04:2025 Data and Model Poisoning | What you train or ground on is an input | **no rule**. Nothing here trains, tunes, or maintains a retrieval corpus. Triggered by the first project that grounds a model on data it stores |
| LLM05:2025 Improper Output Handling | Model output is untrusted input | **product**: Model output is untrusted input. **build**: Whether generated code was understood before it was accepted, which is a human-tier check |
| LLM06:2025 Excessive Agency | Capability, not intent, bounds the damage | **product**: The model holds no authority of its own; Every model call is logged with its decision-relevant context. **build**: The agent's capability is bounded and its changes are reviewed |
| LLM07:2025 System Prompt Leakage | Treat the prompt as readable and put no secret in it | **product**: Nothing enters a prompt that the caller may not see, which covers the secret; the prompt's own text is assumed readable |
| LLM08:2025 Vector and Embedding Weaknesses | Retrieval is an access-control surface | **no rule**. No project here retrieves. Triggered by the first retrieval corpus, where the question becomes whose documents a query may reach |
| LLM09:2025 Misinformation | Fluent output is not correct output | Agent narration is verified at the moment of writing; The agent works from primary sources, not from its own summaries |
| LLM10:2025 Unbounded Consumption | A loop with a model in it costs money | **product**: Consumption is bounded |

## STRIDE

| Item | What it teaches | Answered by |
|---|---|---|
| S Spoofing | Identity is asserted on every request, not once | Authentication; Complete mediation |
| T Tampering | Stored history must be hard to alter quietly | The audit chain rules; append-only observations |
| R Repudiation | The category most designs skip: who did this, provably | Audit logging; Records that change state carry attribution |
| I Information Disclosure | What leaves is chosen, not whatever the row happened to hold | Separate input and output models; Error responses to clients are generic |
| D Denial of Service | Bound what one caller can consume | The rate-limiting and write-budget rules; Availability engineering beyond resource caps is a stated gap |
| E Elevation of Privilege | The deny path is the one to get right | Object-level authorization; Deny by default; Separation of duties |

## NIST SSDF (SP 800-218 version 1.1)

The only framework here about how software is built rather than how it
breaks, which is this doctrine's own subject, so it is also where the
doctrine scores best. Version 1.1 retired PW.3 into PW.4, so the
practices skip it.

| Item | What it teaches | Answered by |
|---|---|---|
| PO.1 Define Security Requirements for Software Development | Write the requirements down where they govern | This document set, and the standards themselves |
| PO.2 Implement Roles and Responsibilities | Someone owns each practice | **no rule**. One person and one agent build everything here, so the practice has no content yet. Triggered by a second contributor |
| PO.3 Implement Supporting Toolchains | The tools that check the work are part of the work | The pipeline rules; ENFORCEMENT.md names every tool against its rule |
| PO.4 Define and Use Criteria for Software Security Checks | Decide in advance what passing means | The definition of done; the six-level scale in ENFORCEMENT.md |
| PO.5 Implement and Maintain Secure Environments for Software Development | The build environment is part of the posture | The agent's capability is bounded; the workflow token rules; the container rules |
| PS.1 Protect All Forms of Code from Unauthorized Access and Tampering | Code and its history are assets | Git practice; the branch protection rules in the platforms section |
| PS.2 Provide a Mechanism for Verifying Software Release Integrity | A consumer must be able to check what you shipped | Releases carry provenance |
| PS.3 Archive and Protect Each Software Release | Keep what you released and what produced it | Releases carry provenance; **partial**, since retention is a stated gap |
| PW.1 Design Software to Meet Security Requirements and Mitigate Security Risks | Threat model before building | Threats are ranked; Plan before code |
| PW.2 Review the Software Design to Verify Compliance with Security Requirements and Risk Information | Somebody else reads the design | Small reviewable diffs; every change reaches a mainline through a pull request |
| PW.4 Reuse Existing, Well-Secured Software When Feasible Instead of Duplicating Functionality | Prefer maintained components, and check them | Adopting outside code; the dependency rules |
| PW.5 Create Source Code by Adhering to Secure Coding Practices | The rules in the security section | The security section entire |
| PW.6 Configure the Compilation, Interpreter, and Build Processes to Improve Executable Security | Build settings are security settings | The container rules; Dependencies install as pinned |
| PW.7 Review and/or Analyze Human-Readable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements | Read it, with tools and with eyes | The analyzers in the pipeline; the human tier in ENFORCEMENT.md |
| PW.8 Test Executable Code to Identify Vulnerabilities and Verify Compliance with Security Requirements | Prove the controls, do not assert them | Behavior matches its tests; Controls are actually defended by tests, through mutation |
| PW.9 Configure Software to Have Secure Settings by Default | The default is what most people run | Every framework default in the serving path; the secure-defaults settings rules |
| RV.1 Identify and Confirm Vulnerabilities on an Ongoing Basis | Watch for what arrives after you shipped | The dependency scanning rules; the scheduled scanner runs |
| RV.2 Assess, Prioritize, and Remediate Vulnerabilities | Have a way to act on what you find | The advisory and update rules; SECURITY.md |
| RV.3 Analyze Vulnerabilities to Identify Their Root Causes | Fix the class, not the instance | **partial**. The decisions record and the caught-mistakes record do it by practice, and no rule requires it. Triggered by the second finding sharing a root cause with an earlier one |

## OWASP ASVS (5.0.0)

Mapped by chapter rather than by requirement: the standard holds
several hundred, and a row per requirement would be a document nobody
maintains. Version 5.0.0 reorganized the standard into seventeen
chapters, renamed and reordered from version 4's fourteen, so this is
a fresh reading rather than a renumbering of the previous one.

| Item | What it teaches | Answered by |
|---|---|---|
| V1 Encoding and Sanitization | Output encoding is where injection is actually stopped | Injection; Exports neutralize spreadsheet formula injection |
| V2 Validation and Business Logic | Validate server side, and think about the flow as well as the field | Input validation; Separation of duties; Misuse and abuse cases is a stated gap |
| V3 Web Frontend Security | The browser has to be told what to allow | Responses carry the headers that constrain them; the page renders every value as text, never markup |
| V4 API and Web Service | An API's surface and its authorization are the review | The role matrix; The exposed surface is enumerated and checked |
| V5 File Handling | A file is hostile until it is parsed and bounded | Uploads; Sensitive downloads; the bounded ingestion rules |
| V6 Authentication | Authentication is a boundary with its own failure modes | Authentication; Passwords are hashed with a deliberately slow algorithm; **thin**: no breached-password screening |
| V7 Session Management | A session is an identity over time | The session identifier changes at authentication; the session rules |
| V8 Authorization | The deny path, and who may do what where | Object-level authorization; Deny by default |
| V9 Self-contained Tokens | A token carrying its own claims can be forged, replayed, or trusted too long | **not applicable by design**. Sessions here are opaque random values stored as hashes, so there are no self-contained claims to verify. It applies the day a token carries anything |
| V10 OAuth and OIDC | Delegated authorization has its own attack surface | **no rule**. Nothing here uses OAuth or an identity provider. Triggered by the first single sign-on integration |
| V11 Cryptography | Use standard constructions, correctly | Nothing invents cryptography; Sensitive values are encrypted at rest; Key rotation is a written procedure |
| V12 Secure Communication | What travels between systems is exposed | Data is encrypted in transit; **thin**: nothing in a pipeline here can verify it |
| V13 Configuration | The configuration is part of the application | Every framework default in the serving path; the secrets and configuration rules |
| V14 Data Protection | Hold less, and choose what leaves | Separate input and output models; **thin**: data classification is a stated gap |
| V15 Secure Coding and Architecture | Design and code habits that remove classes of defect | The design principles; the security section entire; Nothing reconstructs an object from input |
| V16 Security Logging and Error Handling | Logging and error handling are one chapter for a reason | Security-relevant events are logged as structured data; An exceptional condition leaves the system as it found it; Error responses to clients are generic |
| V17 WebRTC | Real-time peer connections carry their own surface | **not applicable**. Nothing here uses WebRTC. Triggered by the first peer-to-peer media feature |

## SLSA levels (1.2)

Version 1.2 is current, and it adds a source track to the build track
that version 1.1 held alone. The source track is the half this program
had never read, and it is the half that describes what protects a
repository rather than what protects a release.

| Item | What it teaches | Answered by |
|---|---|---|
| Build L0 No guarantees | The baseline is the absence of any claim | **not applicable**: it is the level describing having none, and this program is past it |
| Build L1 Provenance exists | Say how the artifact was produced | Releases carry provenance |
| Build L2 Hosted build platform | The claim must be verifiable by a stranger | Releases carry provenance, attested by the platform and verifiable with one command |
| Build L3 Hardened builds | The builder itself resists tampering, with isolation between builds and protected signing keys | **partial**. Workflow tokens hold least permission and no job runs fork code with the token; isolation between builds belongs to the platform and is not verified here |
| Source L1 Version controlled | Revisions are discrete and consumable, which is the floor everything else stands on | Git practice entire: the ignore rules and the hook exist before the first commit, and every change is a commit |
| Source L2 History | Change history is preserved by a control rather than by intention, and the revision carries provenance | Never force push or rewrite history, enforced on both repositories by an active ruleset that blocks non-fast-forward pushes and branch deletion. **partial**: no source provenance attestation is produced, so a consumer takes the history on trust. Triggered by the first consumer who needs the history proved rather than shown |
| Source L3 Continuous technical controls | What a consumer can rely on is what the platform enforces every time, not what the contributing guide asks for | State that lives outside files gets a named ritual, and the rulesets are that state: pull requests required, one approving review, five status checks required to pass. **partial** in the same place as L2: the controls are real and continuous, and no attestation publishes them, so verifying them means reading the settings |
| Source L4 Two-party review | Two people see every change, which is the control against a single actor, insider or compromised | A solo process never simulates a second person. The agent proposes under its own installed identity and a human approval is required, so author and reviewer are different actors and the approval is the review's record |

-------------------------------------------------------------------------------

## What this pass produced

The value of the exercise is the gaps, not the green rows. Nine rules
that did not exist before it:

1. **Deny by default**, the access-control half of fail secure, which
   the doctrine held only as a configuration principle.
2. **The exposed surface is enumerated and checked**, which one
   project already gated and the doctrine never stated.
3. **Responses carry the headers that constrain them**, practiced in a
   project and unwritten here.
4. **The session identifier changes at authentication.** Expiry and
   revocation are not the same control.
5. **Nothing reconstructs an object from input.** Current safety was
   an accident of format choice.
6. **An outbound request goes where the code decided**, written before
   the first live connection makes it possible to violate.
7. **Data from another system is input**, for the same reason.
8. **An exceptional condition leaves the system as it found it**, from
   the item the 2025 edition added. An error path that skips a check
   or leaves half a write is a control failure, not a bug report.
9. **A section for products that put a model in their serving path**,
   and two rules for the agent's own exposure, because a doctrine for
   building software that says nothing about prompt injection while
   being written by an agent has a hole in the shape of its own
   method.

Five items have no rule and say so, each with a trigger:
breached-password screening, sensitive business flows, model and data
poisoning, retrieval access control, and OAuth. Three are not
applicable and say why: self-contained tokens, WebRTC, and the SLSA
level that describes having no guarantees.

The refresh command earned its place on its first run. It found that
SLSA had published version 1.2 while this document mapped 1.1, and the
new version adds a source track, four levels about what protects a
repository rather than what protects a release. Two of those four are
answered only in part, and the shortfall is the same in both: the
controls are real and continuously enforced, and nothing attests to
them, so a consumer who wants proof has to be given read access to the
settings instead.

## What is deliberately excluded

**MITRE ATT&CK.** Asked the same question as everything else, what it
teaches is how to detect an adversary already inside: which techniques
they use, in what order, leaving what evidence. That is a property of
a running estate and of the tooling that watches it, not of rules
about how code is written. Mapping it here would produce rows nobody
could act on while building.

It belongs where the evidence lives. In manifest-identity, the
identity governance project built to this doctrine, each finding class
names the technique it gives evidence of, and that mapping is stated
with its limit: reading configuration shows exposure to a technique,
never its use.
