# Coverage

What the published security frameworks say matters, and what this
doctrine does about each one.

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

**Contents:** [How to read this](#how-to-read-this) · [OWASP Top 10](#owasp-top-10-2021) · [OWASP API Security Top 10](#owasp-api-security-top-10-2023) · [OWASP Top 10 for LLM Applications](#owasp-top-10-for-llm-applications-2025) · [STRIDE](#stride) · [NIST SSDF](#nist-ssdf-sp-800-218) · [ASVS](#owasp-asvs-by-chapter) · [SLSA](#slsa-build-levels) · [What this pass produced](#what-this-pass-produced) · [What is deliberately excluded](#what-is-deliberately-excluded)

-------------------------------------------------------------------------------

## How to read this

Each row names the item, what it teaches in one sentence, and the rule
in [STANDARDS.md](STANDARDS.md) that answers it, by the rule's own
opening words. [ENFORCEMENT.md](ENFORCEMENT.md) says what checks that
rule and at which tier; this file does not repeat the tier, because
two places holding the same fact is how one of them goes stale.

Where the answer is **no rule**, the row says so and names what would
trigger writing one. An item answered by a rule nothing checks is
still a gap, and ENFORCEMENT.md is where that shows.

`scripts/check_coverage.py` fails the build when a rule named here is
not in the standards, when a rule in the standards appears in neither
this file nor the stated gaps, or when a framework loses a row.

## OWASP Top 10 (2021)

| Item | What it teaches | Answered by |
|---|---|---|
| A01 Broken Access Control | Enforce server side, deny by default, and log failures | Object-level authorization; Deny by default; Audit logging; Tokens travel in a request header, which keeps request forgery out of scope by design |
| A02 Cryptographic Failures | Classify data, store less of it, encrypt in transit and at rest, do not cache sensitive responses | Data is encrypted in transit; Sensitive values are encrypted at rest; Identity and lookup never require decryption; Key rotation is a written procedure, not an aspiration; Nothing invents cryptography; Responses carry the headers that constrain them; Data classification is a stated gap |
| A03 Injection | Remove the class rather than escaping case by case | Injection; Input validation; Exports neutralize spreadsheet formula injection, which is the injection class that fires outside the application |
| A04 Insecure Design | Model threats before building, and bound what one caller can consume | Threats are ranked; A per-user write budget is in the rate-limiting rule; Misuse and abuse cases is a stated gap |
| A05 Security Misconfiguration | Harden the platform, review defaults, send the directives a browser needs | Every framework default in the serving path; Responses carry the headers that constrain them |
| A06 Vulnerable and Outdated Components | Know what you depend on and whether it is patched | The dependency rules; Adopting outside code |
| A07 Identification and Authentication Failures | Validate every request, screen weak passwords, rotate the session at sign-in, bound failed attempts | Authentication; The session identifier changes at authentication; Passwords are hashed with a deliberately slow algorithm; **no rule** for screening against breached lists. Triggered by the first password store holding accounts beyond the operators, which is also when adopting a screening list is worth its dependency |
| A08 Software and Data Integrity Failures | Verify what you ship and what you run; do not deserialize untrusted data | Releases carry provenance; Nothing reconstructs an object from input; Dependencies install as pinned |
| A09 Security Logging and Monitoring Failures | Log with enough context, in a form a tool can read, with thresholds and a response | Security-relevant events are logged as structured data; The events are designed by asking what an investigation would need; Detection queries are written while the events are being designed; A query becomes a control when it has a threshold and an owner; A response procedure is written before it is needed; The procedure is exercised at least once |
| A10 Server-Side Request Forgery | Never fetch an address the input chose | An outbound request goes where the code decided |

## OWASP API Security Top 10 (2023)

| Item | What it teaches | Answered by |
|---|---|---|
| API1 Broken Object Level Authorization | Check that this caller owns this record, every time | Object-level authorization |
| API2 Broken Authentication | Authentication is a boundary, not a first step | Authentication; The session identifier changes at authentication |
| API3 Broken Object Property Level Authorization | A client may not set or read every field | Separate input and output models |
| API4 Unrestricted Resource Consumption | Bound page sizes, uploads, and per-caller cost | Input validation, which sets maximum page sizes; Uploads; the rate-limiting rule |
| API5 Broken Function Level Authorization | Which role may call which operation is data, not scattered checks | The role matrix, in the pipelines section |
| API6 Unrestricted Access to Sensitive Business Flows | Some flows are worth abusing even when every request is valid | **no rule**; Misuse and abuse cases is the stated gap, with its trigger now sharpened to a flow worth automating rather than to fraud motive alone |
| API7 Server Side Request Forgery | Same as A10, and APIs are where it usually lives | An outbound request goes where the code decided |
| API8 Security Misconfiguration | Cross-origin rules and headers are part of the API, not decoration | Responses carry the headers that constrain them |
| API9 Improper Inventory Management | An interface nobody documented is one nobody reviews, and the old version is the one still vulnerable | The exposed surface is enumerated and checked |
| API10 Unsafe Consumption of APIs | A system you call is not a system you can trust | Data from another system is input |

## OWASP Top 10 for LLM Applications (2025)

Two audiences. Rows marked **product** govern software that puts a
model in its serving path, which nothing here does yet; the rules are
written in advance rather than invented under deadline. Rows marked
**build** govern this way of working, where an agent reads and writes
the repository, which is exercised every day.

| Item | What it teaches | Answered by |
|---|---|---|
| LLM01 Prompt Injection | Retrieved and supplied content is data; only the system prompt instructs | **product**: Everything outside the trust boundary is data, never instruction. **build**: What the agent reads is data, not instruction |
| LLM02 Sensitive Information Disclosure | A prompt is an output channel | **product**: Nothing enters a prompt that the caller may not see. **build**: No credential-shaped string in any tracked file or commit, and the agent holds no credential it can read |
| LLM03 Supply Chain | A model, a prompt, a tool server, and a skill are all somebody else's code | A model, a prompt library, an agent skill, or a tool server is outside code; Adopting outside code |
| LLM04 Data and Model Poisoning | What you train or ground on is an input | **no rule**. Nothing here trains, tunes, or maintains a retrieval corpus. Triggered by the first project that grounds a model on data it stores |
| LLM05 Improper Output Handling | Model output is untrusted input | **product**: Model output is untrusted input. **build**: Whether generated code was understood before it was accepted, which is a human-tier check |
| LLM06 Excessive Agency | Capability, not intent, bounds the damage | **product**: The model holds no authority of its own; Every model call is logged with its decision-relevant context, so what it was permitted to do and what it did are both answerable. **build**: The agent's capability is bounded and its changes are reviewed |
| LLM07 System Prompt Leakage | Treat the prompt as readable and put no secret in it | **product**: Nothing enters a prompt that the caller may not see, which covers the secret; the prompt's own text is assumed readable |
| LLM08 Vector and Embedding Weaknesses | Retrieval is an access-control surface | **no rule**. No project here retrieves. Triggered by the first retrieval corpus, where the question becomes whose documents a query may reach |
| LLM09 Misinformation | Fluent output is not correct output | Agent narration is verified at the moment of writing; The agent works from primary sources, not from its own summaries |
| LLM10 Unbounded Consumption | A loop with a model in it costs money | **product**: Consumption is bounded |

## STRIDE

| Category | What it teaches | Answered by |
|---|---|---|
| Spoofing | Identity is asserted on every request, not once | Authentication; Complete mediation |
| Tampering | Stored history must be hard to alter quietly | Audit rows are hash-chained, in the audit rules; append-only observations |
| Repudiation | The category most designs skip: who did this, provably | Audit logging; Records that change state carry attribution |
| Information disclosure | What leaves is chosen, not whatever the row held | Separate input and output models; Error responses to clients are generic |
| Denial of service | Bound what one caller can consume | The rate-limiting and write-budget rules; Availability engineering beyond resource caps is a stated gap |
| Elevation of privilege | The deny path is the one to get right | Object-level authorization; Deny by default; Separation of duties |

## NIST SSDF (SP 800-218)

Mapped at practice level. The only framework here about how software
is built rather than how it breaks, which is this doctrine's subject,
so it is also where the doctrine scores best.

| Practice | What it teaches | Answered by |
|---|---|---|
| PO.1 Define security requirements | Write the requirements down where they govern | This document set, and the standards themselves |
| PO.2 Roles and responsibilities | Someone owns each practice | **no rule**. One person and one agent build everything here, so the practice has no content yet. Triggered by a second contributor |
| PO.3 Supporting toolchains | The tools that check the work are part of the work | The pipeline rules; ENFORCEMENT.md exists to name every tool against its rule |
| PO.4 Criteria for software security checks | Decide in advance what passing means | The definition of done; the six-level scale in ENFORCEMENT.md |
| PO.5 Secure build environments | The build environment is part of the posture | The agent's capability is bounded; the workflow token rules; the container rules |
| PS.1 Protect all forms of code | Code and its history are assets | Git practice; the branch protection rules in the platforms section |
| PS.2 Verify software integrity | A consumer must be able to check what you shipped | Releases carry provenance |
| PS.3 Archive and protect each release | Keep what you released and what produced it | Releases carry provenance; **partial**, since retention is a stated gap |
| PW.1 Design to meet requirements | Threat model before building | Threats are ranked; Plan before code |
| PW.2 Review the design | Somebody else reads it | Small reviewable diffs; every change reaches a mainline through a pull request |
| PW.4 Reuse well-secured software | Prefer maintained components, and check them | Adopting outside code; the dependency rules |
| PW.5 Create secure source code | The rules in the security section | The security section entire |
| PW.6 Configure the build to improve security | Build settings are security settings | The container rules; Dependencies install as pinned |
| PW.7 Review human-readable code | Read it, with tools and with eyes | The analyzers in the pipeline; the human tier in ENFORCEMENT.md |
| PW.8 Test executable code | Prove the controls, do not assert them | Behavior matches its tests; Controls are actually defended by tests, through mutation |
| PW.9 Configure with secure default settings | The default is what most people run | Every framework default in the serving path; secure defaults in the settings rules |
| RV.1 Identify vulnerabilities | Watch for what arrives after you shipped | The dependency scanning rules; the scheduled scanner runs |
| RV.2 Assess and remediate | Have a way to act on what you find | The advisory and update rules; SECURITY.md |
| RV.3 Analyze root causes | Fix the class, not the instance | **partial**. The decisions record and the caught-mistakes record do it by practice, and no rule requires it. Triggered by the second finding that shares a root cause with an earlier one, which is the point at which practice needs to become a rule |

## OWASP ASVS, by chapter

Mapped by chapter rather than by requirement: the standard holds
several hundred, and a row per requirement would be a document nobody
maintains. The chapters say where this doctrine is thin.

| Chapter | Answered by |
|---|---|
| V1 Architecture and threat modeling | Threats are ranked; the architecture documents in the definition of done |
| V2 Authentication | Authentication; Passwords are hashed with a deliberately slow algorithm; **thin**: no breached-password screening |
| V3 Session management | The session identifier changes at authentication; the session rules in the security section |
| V4 Access control | Object-level authorization; Deny by default; the role matrix |
| V5 Validation, sanitization, encoding | Input validation; Injection |
| V6 Stored cryptography | Sensitive values are encrypted at rest; Nothing invents cryptography |
| V7 Error handling and logging | Error responses to clients are generic; Security-relevant events are logged as structured data |
| V8 Data protection | Separate input and output models; Responses carry the headers that constrain them; **thin**: data classification is a stated gap |
| V9 Communications | Data is encrypted in transit; **thin**: nothing in a pipeline here can verify it |
| V10 Malicious code | Adopting outside code; the install-time inspection rule |
| V11 Business logic | Separation of duties; **thin**: Misuse and abuse cases is a stated gap |
| V12 Files and resources | Uploads; Sensitive downloads |
| V13 API and web service | The exposed surface is enumerated and checked; the route matrix |
| V14 Configuration | Every framework default in the serving path; the secrets and configuration rules |

## SLSA build levels

| Level | What it teaches | Answered by |
|---|---|---|
| Build L1 Provenance exists | Say how the artifact was produced | Releases carry provenance |
| Build L2 Signed provenance from a hosted builder | The claim must be verifiable by a stranger | Releases carry provenance, attested by the platform and verifiable with one command |
| Build L3 Hardened build platform | The builder itself resists tampering | **partial**. Workflow tokens hold least permission and no job runs fork code with the token; isolation between builds is the platform's and is not verified here |

-------------------------------------------------------------------------------

## What this pass produced

Written down because the value of the exercise is the gaps, not the
green rows. Eight rules that did not exist before this pass:

1. **Deny by default**, the access-control half of fail secure, which
   the doctrine had only as a configuration principle.
2. **The exposed surface is enumerated and checked**, which one
   project already gated and the doctrine never stated.
3. **Responses carry the headers that constrain them**, practiced in a
   project and unwritten here, which is the easiest kind of rule to
   lose.
4. **The session identifier changes at authentication.** Expiry and
   revocation are not the same control.
5. **Nothing reconstructs an object from input.** Current safety was
   an accident of format choice.
6. **An outbound request goes where the code decided**, written before
   the first live connection makes it possible to violate.
7. **Data from another system is input**, for the same reason.
8. **A section for products that put a model in their serving path**,
   and two rules for the agent's own exposure, because a doctrine for
   building software that says nothing about prompt injection while
   being written by an agent has a hole in the shape of its own
   method.

Four items have no rule and say so: breached-password screening,
sensitive business flows, model and data poisoning, and retrieval
access control. Each names what would trigger writing one.

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
