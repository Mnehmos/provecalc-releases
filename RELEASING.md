# Publishing signed desktop releases

This public repository builds installers on GitHub's free standard runners.
The app source stays in `Mnehmos/mnehmos.worksheet.app`. The manual Release
workflow fetches an exact private-source commit using a read-only credential;
it does not upload source archives or checkout credentials. Job logs are public.

## One-time owner configuration

Create the `release` environment and set these secrets in this repository:

- `SOURCE_REPO_TOKEN`: a fine-grained token with Contents read access to
  `Mnehmos/mnehmos.worksheet.app` only.
- `TAURI_SIGNING_PRIVATE_KEY`: the original Tauri updater key already used by
  the app repository. Do not generate a replacement: existing apps trust it.
- `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`: the password for that same key.

GitHub will not return the values of existing stored secrets. Add them using
the original secure copy, through GitHub Settings; never put them in an issue,
commit, chat, workflow input or log. No release-write PAT is needed here:
publication uses this repository's short-lived `GITHUB_TOKEN`.

Restrict the environment to the `main` branch. Once the public workflow is
configured, set the private app repository variable `PUBLIC_RELEASE_BUILDS`
to `true` to stop the legacy private tag workflow from also publishing.

## Candidate and final

1. Prepare a numeric candidate on an app issue branch (next planned version:
   `0.1.10-1`), run the local gates and merge its release PR.
2. Tag that reviewed master commit. The workflow requires the full 40-character
   source SHA and a tag resolving to that exact commit on master.
3. Dispatch **Release** on this repository's `main`, with that source SHA and
   source tag. Leave `publish` false to keep the complete build in a draft.
   Set it true to publish a validated numeric candidate as a prerelease.
   Stable clients ignore prereleases through the official latest endpoint.
4. Test the candidate's actual public installers, updater signatures and an
   update from an old installed build. Preserve unsaved work and check the
   calculation engine, manual nodes, all templates, solve and save/reopen.
5. Only after acceptance, prepare the stable version in the private source,
   merge, tag, and dispatch with `publish` true. Stable publication happens
   last, after complete inventory, signatures, manifest, checksums and actual
   source/build provenance validate. Never publish a partial platform set.

Builds use native Windows x64, Mac ARM, Mac Intel, and Linux x64 runners;
Python host architecture is checked before freezing each calculation engine.
The actual frozen engines are smoke-tested, along with the packaged Linux app.

Do not publish unsigned local executables as updater assets. Do not reuse
published versions or append artifacts into an already public release.
Failures leave a draft and leave the stable feed unchanged. For infrastructure
failures, rerun failed jobs. Source repairs require a reviewed source change;
delete only the failed unpublished draft/tag before creating a new candidate.
