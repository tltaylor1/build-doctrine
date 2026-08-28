# Platform baseline

The standards in this repository govern what gets built; this document
governs what it gets built on. Every platform the work depends on is
enumerated here, and every baseline item sits in exactly one of three
states, so the person accountable can never say they did not know:

- **Checked**: a mechanism verifies it, named here, failing loudly
  when the answer changes.
- **Attested**: a person verified it by hand on a stated date, and the
  attestation expires on a stated schedule; an expired attestation is
  a red check, not a memory.
- **Accepted**: the gap is deliberate, with its reason and, where one
  exists, its exit condition.

An item in none of these states is a finding against this document.
The enumeration grows a section per platform as the work adopts one;
a platform in use without a section here is the same finding.

-------------------------------------------------------------------------------

## GitHub

The account is the root of trust for every repository, ruleset, and
installed identity below it.

| Item | State | Evidence and schedule |
|---|---|---|
| Account MFA with phishing-resistant factors | Attested August 19, 2026: three hardware keys, an authenticator app, a passkey; primary key tested on the working machine | Re-attest quarterly, next by November 19, 2026 |
| Recovery codes held offline | Attested August 19, 2026, stored in the password manager | Re-attest quarterly with the above |
| No classic personal access tokens with broad scope outstanding | Attested August 19, 2026 during identity work | Re-attest quarterly; the exit is migrating remaining agent operations to installed apps |
| Agent identities are installed apps with named permissions on named repositories | Checked: the installation permission sets are read from the API at each permission change and recorded in the decision entries (need, request, approval) | Standing |
| Commit and tag signing with account-registered keys | Checked: unsigned commits are visible per commit; the application repository's history states its signing boundary | Standing |
| Branch rulesets: pull requests required, checks required, one approving review, no force push or deletion | Checked: the rulesets are readable by API; changing them is an audited account action | Standing |
| Stale approvals dismissed on new pushes, and the newest push requires its own approval | Attested August 24, 2026: both settings verified true by API after enabling; earned by two merge races in one week where content changed after review | Checked: readable by API with the ruleset above |
| Secret scanning and push protection on public repositories | Attested August 19, 2026 for all public repositories | Re-attest quarterly |
| Repository visibility flips are deliberate acts | Accepted as a manual act: the flip is a one-way exposure decision a person makes, recorded in the journal and decisions | No mechanism sought |
| Merged head branches delete automatically at merge | Attested August 28, 2026: enabled by API on all nine repositories in one pass and read back true; the one pre-approved branch deletion under D-024 | Re-verify by API, as delete_branch_on_merge, whenever a repository is added |
| Actions workflow permissions default to read | Checked per repository: workflows declare least privilege inline and the workflow audit gate reviews them | Standing |

## AWS

Written before the account work begins, which is the point: the
checklist exists first, and the console session fills it. States
below are the expected end state; each flips to checked or attested
as the organization stands up.

| Item | Target state | Mechanism or schedule |
|---|---|---|
| The organization exists; the management account is near-empty, billing and policy root only | Attested at creation, then checked by Config once enabled | Config rule set in the foundation stack |
| Root credentials on hardware keys; no root access keys exist | Attested at creation; root access key absence is API-checkable | Checked by the account baseline once code exists |
| Root use alarmed | Checked: the organization trail plus an alarm on root sign-in events | Foundation stack |
| Identity Center on; zero IAM users, ever | Checked: an IAM-user count of zero is API-checkable and becomes a Config rule | Foundation stack |
| Budgets and alarms exist before any resource | Attested at creation with the thresholds recorded (10, 25, 50 dollars monthly) | Re-attest when thresholds change |
| Region-deny and root-deny service control policies attached | Checked: SCP attachment is API-readable; drift detection covers the policy documents | Foundation stack |
| Organization CloudTrail into a locked bucket | Checked by Config and by the trail's own status API | Foundation stack |
| No stored cloud credential anywhere: humans through Identity Center sessions, pipelines through OIDC federation | Checked: the credential report shows no access keys; the gate that watches local git configuration extends to AWS credential files | Foundation stack plus the local gate |
| The cloud's own reviewers on: Config with a conformance baseline, Security Hub foundational standard, organization Access Analyzer, GuardDuty on the sandbox | Checked: each service's enablement is API-readable | Foundation stack |
| Encryption at rest on state and trail buckets | Checked by Config | Foundation stack |

-------------------------------------------------------------------------------

## The rule this document enforces

A platform's hygiene is somebody's job, and this document names whose
and by when. The mechanically checkable rows migrate into pipelines
and Config rules as the phases land them; the attested rows expire on
their schedules; and the accepted rows are re-read whenever this
document changes, because acceptance is a decision that ages like any
other.
