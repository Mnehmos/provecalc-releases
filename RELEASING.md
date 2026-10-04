# Publishing desktop releases

Standard public GitHub runners build unsigned Windows x64, Mac ARM, Mac Intel,
and Linux x64 installers. Signing and publication run through the private app's
manual Release workflow on a one-job ephemeral local Windows runner. That job
uses the existing private release environment signing keys and release token.
Do not copy those secrets here or replace the updater key.

The app source remains private. `scripts/stage_release_source.py` in the app
repository archives the exact reviewed tag and encrypts it into `Source.enc` in
an unpublished draft. It sets a temporary `SOURCE_ARCHIVE_KEY` in this repository's
release environment, restricted to main. This is a source-decryption credential,
not an updater key. Build inputs bind the capsule checksum and full source SHA.
Public job logs must not print source contents or secrets.

1. Prepare the candidate version on an app issue branch, pass local checks,
   merge the release PR and tag the reviewed master commit.
2. Set the private app variable `PUBLIC_RELEASE_BUILDS=true` before tagging to
   prevent the legacy hosted publisher running simultaneously.
3. From that tagged app checkout, run `scripts/stage_release_source.py --tag
   <tag> --out <private-output-folder>` with OpenSSL available. Keep its
   `build-input.json` for the three nonsecret workflow inputs.
4. Dispatch this repository's Release workflow on main with those inputs.
   It checks source identity, versions, tooling, frontend, Rust and Python,
   native frozen engines and the packaged Linux app. All platforms remain draft.
5. Register a verified official ephemeral Windows runner for the private app
   with label `provecalc-release-local`, then dispatch its Release workflow on
   the reviewed numeric tag. Supply the successful public build run ID and its
   public workflow commit SHA. Leave publish false to validate a signed draft.
6. The private job binds source, build and every downloaded byte, signs with
   the original updater key, verifies signatures, creates the complete
   manifest/checksums/provenance, uploads and verifies the downloaded inventory.
   With publish true, it removes `Source.enc` before publication. Numeric
   candidates become prereleases and leave the stable latest feed unchanged.
7. Test actual candidate installers and an old-to-new update, including
   unsaved-work handling, relaunch, nodes, templates, solve and save/reopen.
   Only after acceptance prepare and publish a new stable version the same way.

The runner processes one job and removes its registration. Do not install a
persistent runner service. Do not reuse a published version, publish a partial
platform set, or use unsigned local executables as updater assets. Failures leave
the draft unpublished. Infrastructure retries keep the same reviewed source;
source repairs require a new reviewed candidate. Source and public builder
provenance are recorded separately.
