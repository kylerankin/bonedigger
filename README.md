# bonedigger 🦴

> Shared bug-reporting specifications, privacy contracts, and canonical intake templates for Project Bluefin.

## Current scope

| Responsibility | Owner |
|----------------|-------|
| Reporting specifications, privacy requirements, and proposed extensions | bonedigger — `docs/skills/` |
| Canonical issue forms and template-sync workflow | bonedigger — `templates/` and `.github/workflows/sync-templates.yml` |
| Executable `ujust report` client and image packaging | [projectbluefin/common](https://github.com/projectbluefin/common) |
| Issue triage, labels, assignments, and queue lifecycle | Hive |

Bonedigger does not ship a lifecycle workflow or composite action. QR output and
screenshot analysis are proposals, not features of the shipped reporting client.

## How it works

```text
User's machine: ujust report (shipped by common)
  → collect baseline diagnostics and optional smart-log profiles
  → scrub system logs locally and preview the report
  → obtain submission consent
  → publish selected smart logs to the user's gist, if any
  → create the issue directly through GitHub CLI
GitHub Issues: Hive manages triage and lifecycle
```

A gist is optional. The client does not open or prefill a GitHub issue form.
GitHub Issues is the only state backend; there is no central diagnostic server.

## Usage

### As a user

Run on an image that ships the reporting client:

```bash
ujust report                     # collect, review, and submit a report
ujust report --confirm 42        # post the deployed system's fingerprint
ujust report --resume /path/to/draft  # resume a preserved report draft
```

`--confirm` also accepts a GitHub issue URL. A fingerprint is evidence for
triage; it does not by itself assert that the issue is fixed.

### Downstream repos

The sync workflow is triggered by changes under `templates/` pushed to `main`.
It opens downstream PRs; templates are not deployed until those PRs are merged.
See the [template guide](docs/skills/bonedigger-templates.md) for the declared
consumer roster, authentication, and delivery verification. Do not equate the
configured workflow with a successful synchronization.

## Repository structure

- `templates/` — canonical issue forms and chooser configuration
- `.github/workflows/sync-templates.yml` — downstream template PR automation
- `docs/skills/` — architecture, current client behavior, and proposed extensions
- [AGENTS.md](AGENTS.md) — ownership boundaries and contribution verification

## Privacy

- System-log redaction happens locally before submission; users review the result.
- Regex scrubbing is not a guarantee that all identifying information is removed.
- Issues and selected smart-log gists are public and created under the user's account.
- The current client does not derive an identifier from `machine-id`, capture OTel
  telemetry, or upload screenshots.

Start with the [overview](docs/skills/bonedigger-overview.md) and the
[client guide](docs/skills/bonedigger-ujust.md) for the actual implementation.

## Part of Project Bluefin

- [projectbluefin/common](https://github.com/projectbluefin/common) — ships `ujust report` and common system files
- [projectbluefin/dakota](https://github.com/projectbluefin/dakota) — reference implementation
