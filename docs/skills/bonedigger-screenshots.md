---
name: bonedigger-screenshots
description: Use when designing or reviewing proposed screenshot capture, local OCR, or screenshot privacy rules for ujust report.
---

# bonedigger — screenshot analysis (proposal)

**Not implemented in the pinned common client.** This optional enhancement would
extract useful text from screenshots or phone photos of a display. Bonedigger
owns the privacy contract; executable capture/OCR belongs in
`projectbluefin/common`'s `bonedigger-report`. The `60-bonedigger.just` wrapper
only invokes that client with brand/version; do not put analysis there or edit
downstream template copies.

## When to Use

- Designing local screenshot/OCR input for a bug report.
- Reviewing consent, asynchronous portal capture, cleanup, and draft ordering.
- Handling phone photos when login screens, TTYs, crashes, or display faults
  prevent normal capture.

## When NOT to Use

- Claiming screenshot capture is currently available.
- Building a remote image-analysis service or uploading raw images.
- Requiring screenshots or a gist to submit an otherwise valid report.

## Core Process

1. **Obtain explicit, reversible consent first.** Disclose local analysis, the
   extracted text to be included, and that no image will be uploaded. Use an
   explicit `gum confirm` before capture, reading a supplied image, or analysis.
   Decline or withdrawal skips only this enhancement. Portal permission is not a
   substitute for report consent. There is no current remembered-consent system.
2. **Acquire an image locally.** Prefer the desktop Screenshot portal; optionally
   offer a `gum file` picker for a user-supplied image. Missing portal/backend,
   dismissed dialogs, or capture errors skip capture silently and leave normal
   reporting available. Never mutate or delete the user's original input file.
3. **Classify conservatively, if optional local tools exist.** Candidate labels
   are `clean-screenshot`, `photo-of-screen`, `unusable`, and `unknown`.
   Pillow/numpy sharpness, aspect/edge-angle, and phone-overlay heuristics are
   best-effort only: calibrate thresholds against real images before trusting
   them; full perspective estimation is outside this proposal. Missing tools
   mean `unknown`, with disclosure. Warn on phone photos and offer re-capture.
   For `unusable`, offer re-capture; if declined or still unusable, discard this
   step's intermediates and text and continue the report, never abort it.
4. **Extract text locally with optional `tesseract`.** If unavailable or failing,
   explain that OCR was skipped and continue without screenshot context. Do not
   substitute a Flatpak app, generic app finder, or network OCR service. Pass OCR
   text through `scrub_journal_log()` (which includes `scrub_kernel_log()`) before
   adding a "Screenshot context" section to `$DRAFT_DIR/issue.md`. Existing
   regexes cover certain addresses, emails, home paths, UUIDs and serial patterns;
   they do not reliably remove secrets, names, window titles, filenames, or
   arbitrary chat/terminal contents. Scrubbing is not a completeness guarantee.
5. **Keep classification advisory.** Optional `error-dialog`, `blank-screen`,
   `visual-glitch`, `color-issue`, or `unknown` labels must be marked heuristic,
   low-confidence where appropriate, and never diagnostic or a replacement for
   the user's description. Do not infer blank screens or tearing conclusively
   from poor photos or absent OCR text.
6. **Finish before user review and publication.** The existing `submit_draft()`
   invokes `preview_draft()` on `issue.md` and selected profile files, then asks
   for public submission consent. Put capture, classification, OCR, scrubbing,
   and image cleanup before that review. If OCR text is added after any preview,
   preview again before consent. Review uses `gum pager` on a terminal and plain
   output otherwise; allow correction/removal of sensitive OCR text before
   submission. Only scrubbed, reviewed text may persist, never pixels.
7. **Use the actual submission path.** `BUG_REPO` is resolved by the shared
   routing helper and saved as `repo.txt`; `create_issue()` creates the public
   issue directly via `gh issue create` using `issue.md`. `publish_smart_logs()`
   creates a public gist only for selected smart-log profile files; it does not
   upload `issue.md` or images. A gist is optional, not the primary or required
   report. Resume runs `load_draft()` then `submit_draft()`; do not reacquire an
   image or presume fresh consent on resume. Any new acquisition needs a new
   explicit consent prompt and review.

### Asynchronous portal requirements

`org.freedesktop.portal.Screenshot.Screenshot(parent_window, options)` returns a
Request object path, **not an image**. The URI arrives in
`org.freedesktop.portal.Request::Response` on that request.

- Prefer a single-connection helper (optional Python plus Gio or a D-Bus binding).
  Subscribe before calling; use a unique, unguessable `handle_token` and
  `interactive=true` (a customization hint, not a consent guarantee). The
  predictable request path uses that connection's unique bus name. Verify the
  returned handle and adjust the subscription if it differs.
- A separate `gdbus monitor` / `gdbus call` pair cannot predict the caller's bus
  name from the monitor connection. If using that approach, listen before the
  call, buffer Response signals, then match the returned request path exactly;
  never accept an unrelated request or busy-poll a guessed image pathname.
- Use a bounded wait (60 seconds is a proposed default) and explicit cancel/abort
  handling. Response `0` means success; `1` is cancellation; `2` is another
  termination/error. Non-success skips the screenshot step silently. On timeout
  or abort, call `Request.Close` where possible, stop listeners, and clean up;
  `Close` emits no Response, so do not wait for one afterwards.
- Validate success results and resolve the returned URI as a local file using
  proper URI decoding, not simple `file://` string stripping. Copy portal output
  into private scratch, then delete the portal-produced image immediately.
  A backend that cannot satisfy image cleanup must not enable this enhancement.

### Privacy and cleanup requirements

**No raw image upload anywhere:** no gist, issue attachment, external analysis,
telemetry, or retained draft pixels. OCR, geometry checks, and classification
remain local. Optional dependencies must never make reporting fail.

The existing client deliberately preserves drafts under
`${XDG_STATE_HOME:-$HOME/.local/state}/ujust-report/drafts` through `keep_draft()`
and `--resume`, and saves a local `last` copy after submission. It has no existing
image cleanup mechanism or EXIT trap. Never store images in `$DRAFT_DIR` or the
local report copy.

Use a private `mktemp -d` scratch directory under `$XDG_RUNTIME_DIR` for copied
inputs and every crop/downscale/OCR image intermediate. If safe runtime scratch
is unavailable, skip the enhancement, not the report. Delete all owned image
intermediates **before the step returns on every path**: success, declined or
withdrawn consent, unusable-skip, acquisition/OCR failure, timeout, and abort.
Use function-scoped cleanup plus interrupt handling; do not defer cleanup until
process exit. Delete portal-produced output immediately after copying. Cleanup
must stop/cancel asynchronous work so a late result cannot recreate an orphan
image. Do not promise synchronous cleanup after an uncatchable kill or power
loss; runtime scratch limits persistence but does not replace return-path cleanup.
Withdrawal must remove this step's OCR additions as well as owned images; only
scrubbed text the user still consents to include may remain in a resumable draft.

### Existing versus proposed knobs and dependencies

Existing client knobs include `IMAGE_INFO_FILE`, `BONEDIGGER_BRAND`, state paths,
and `UBLUE_IMAGE_REPO_BIN`; `BUG_REPO` is routing state, not a consent setting.
There is no existing `BONEDIGGER_ISSUE_URL` or screenshot knob.

The proposed **new** `BONEDIGGER_SCREENSHOT` accepts `ask` (default) or `never`;
unrecognized values mean `ask`. There is deliberately no automatic "yes" or
remembered consent: environment settings can be applied without user awareness.

New optional tools would be Python with Gio/D-Bus bindings for capture,
`python3-pillow`/`python3-numpy` for heuristics, and `tesseract` for OCR. The pinned
client uses none of these for screenshots. Missing capture tools permits a
consented file-picker path; missing heuristics yields `unknown`; missing OCR
omits extracted context. No new template field is required by this proposal;
any future canonical field must be optional and text-only, with no raw-image
invitation or required gist.

## Common Rationalizations

- “The portal dialog or environment variable already gave consent.” Neither
  replaces explicit disclosure and consent for this analysis/submission.
- “The scrubber catches everything.” Arbitrary OCR text needs human review.
- “The draft is temporary.” Cancelled/failed drafts intentionally survive resume.
- “Cleanup at process exit is enough.” Images must be gone before each return.

## Red Flags

- Pixels in a draft, local report copy, gist, attachment, or network request.
- OCR appended after preview without another review before publication consent.
- Raw URI stripping, accepting unrelated Response signals, unbounded waits,
  guessed output polling, or missing abort/late-result cleanup.
- Auto-consent, deleting the user's source image, or treating missing tools as a
  fatal report error.

## Verification

For a future implementation, exercise successful portal capture and supplied
photos; cancellation, timeout, abort and late Response; missing dependencies;
unusable images with declined/failed re-capture; OCR errors; consent withdrawal;
and resumed drafts. Inspect scratch, portal output, preserved drafts, local
copies, and public submission payloads. Prove no owned images survive any return,
no raw image leaves the machine, and only scrubbed text reviewed before consent
reaches `issue.md`. Check both terminal and non-terminal preview paths and
normal reporting with no screenshot and no selected profiles. These are acceptance
requirements, not evidence of shipped screenshot support.

## Sources

- [Pinned common client](https://github.com/projectbluefin/common/blob/cc6734876a6549340d2979d95771752d718f6f0f/system_files/bluefin/usr/libexec/bonedigger-report): `scrub_journal_log`, `create_draft`, `keep_draft`, `preview_draft`, `submit_draft`, `publish_smart_logs`, `create_issue`.
- [Pinned wrapper](https://github.com/projectbluefin/common/blob/cc6734876a6549340d2979d95771752d718f6f0f/system_files/bluefin/usr/share/ublue-os/just/60-bonedigger.just).
- [Official Screenshot API](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Screenshot.html): handle, options, URI result.
- [Official Request API](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html): path convention, Response codes, Close semantics. Context7 `/flatpak/xdg-desktop-portal` confirmed the subscribe-before-call pattern via [requests.rst](https://github.com/flatpak/xdg-desktop-portal/blob/main/doc/requests.rst); official API pages supplied the Screenshot-specific details.
