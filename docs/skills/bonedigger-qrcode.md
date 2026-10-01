---
name: bonedigger-qrcode
description: Use when designing or reviewing proposed terminal QR links for the ujust report flow.
---

# bonedigger — QR links (proposal)

**Not implemented in the pinned common client.** This guide specifies an optional
phone handoff, not a shipped reporting feature. Bonedigger owns this contract;
implementation belongs in `projectbluefin/common`'s `bonedigger-report`, not its
`60-bonedigger.just` entry-point wrapper.

## When to Use

- Designing terminal QR output for opening a report on another device.
- Reviewing URL payload privacy, rendering fallbacks, or scan verification.

## When NOT to Use

- Describing current QR support or adding a required upload step.
- Moving diagnostics into QR payloads or duplicating image-routing logic.

## Core Process

1. **Use the actual reporting hooks.** `start_bug_report()` resolves `BUG_REPO`
   through `route_issue_repo()` and the shared `ublue-image-repo` helper.
   `submit_draft()` calls `preview_draft()` to review `$DRAFT_DIR/issue.md` and
   selected profile files (a `gum pager` on a terminal, plain output otherwise),
   then requests publication consent. `publish_smart_logs()` publishes only
   selected profile files to a public gist, if any. `create_issue()` creates the
   issue directly through GitHub CLI/API using `issue.md`; the returned issue URL
   is printed and optionally opened by `offer_browser()`.
2. **Proposed pre-submission handoff:** after draft preview and before publication
   consent, optionally show `https://github.com/${BUG_REPO}/issues/new` for bug
   reports. Feature requests use `projectbluefin/common`. For resumed drafts,
   use the persisted `repo.txt`, not a newly inferred machine route. This opens a
   separate manual form: it does not transfer or submit the local draft. Explain
   this to avoid duplicate reports. Do not seed query parameters with report
   bodies or diagnostic data. There is no existing `BONEDIGGER_ISSUE_URL` knob.
3. **Proposed post-publication handoff:** show a gist QR only when
   `publish_smart_logs()` has produced or reused `gist-url.txt` for selected
   profiles. With no profiles there is no gist and no gist QR. After successful
   `create_issue()`, the returned issue URL is the primary report handoff.
4. **Encode only the intended URL**, never logs, identifiers, tokens, report
   content, or personal query parameters. A URL can still disclose its destination
   and public report identifier; URL-only is not a promise of anonymity. QR output
   must not bypass preview, authentication, or publication consent.
5. **Render as an optional enhancement.** A proposed `print_qrcode <url>` helper
   can use `qrencode -t ANSIUTF8 -m 4 -o - "$url"`. Upstream supports `ANSIUTF8`,
   `-m` for margins, and `-o -` for stdout. `-s` specifies dots/pixels; do not
   assume it scales terminal UTF-8 output. Verify terminal readability and scans
   with the actual backend. Always print a labeled plain URL for accessibility,
   unsupported terminals, and users without a camera. If `qrencode` is absent or
   fails, keep the plain URL and continue reporting; no mandatory generator or
   new reporting dependency is required.
6. **Require round-trip proof before shipping.** Decode the rendered symbol and
   compare the decoded bytes with the exact input URL. Use an image representation
   of the same symbol and an optional decoder such as `zbarimg`; ANSI terminal
   escape text is not an image that can simply be piped into an image decoder.
   Also scan the actual terminal rendering on a phone.

### Existing versus proposed dependencies and knobs

The existing flow uses `gum` for review/consent and `gh` for publication; the
wrapper supplies brand/version. Routing comes from `BUG_REPO`, not a new URL
override. `qrencode` and a verification decoder are **proposed optional** tools,
not verified image-installed dependencies. This proposal requires no new
environment variable, clipboard integration, or upload mechanism.

## Common Rationalizations

- “Every report has a gist.” Only selected smart logs create one.
- “A QR is consent to publish.” It is navigation, not consent.
- “The encoder succeeded, so the terminal QR works.” Exact decoding and an actual
  terminal scan are required.

## Red Flags

- QR payloads containing report text, credentials, or identifying query values.
- A pre-submission form portrayed as the directly created report.
- Missing plain URLs, mandatory QR tools, or a gist QR when no gist exists.

## Verification

For a future implementation, exercise no-profile and selected-profile reports,
resumed drafts, declined publication, gist/issue failures, missing renderer, and
non-terminal output. Confirm only real successful URLs are offered, reporting
continues without QR tools, and both exact decoding and phone scans succeed.
These are acceptance requirements, not evidence of shipped QR support.

## Sources

- [Pinned common client](https://github.com/projectbluefin/common/blob/cc6734876a6549340d2979d95771752d718f6f0f/system_files/bluefin/usr/libexec/bonedigger-report): `preview_draft`, `submit_draft`, `publish_smart_logs`, `create_issue`, `route_issue_repo`.
- [Pinned wrapper](https://github.com/projectbluefin/common/blob/cc6734876a6549340d2979d95771752d718f6f0f/system_files/bluefin/usr/share/ublue-os/just/60-bonedigger.just) and [routing helper](https://github.com/projectbluefin/common/blob/cc6734876a6549340d2979d95771752d718f6f0f/system_files/shared/usr/libexec/ublue-image-repo).
- [Official qrencode CLI source/help](https://github.com/fukuchi/libqrencode/blob/master/qrenc.c): `ANSIUTF8`, margin, size, and stdout options. Context7 library `/websites/fukuchi_works_qrencode` had no matching CLI documentation; upstream source is the fallback authority.
