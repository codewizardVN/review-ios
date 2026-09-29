[English](./CICD.md) | [Tiếng Việt](./CICD.vi.md)

[← Senior Topics](./README.md)

# CI/CD for Mobile

## What A Senior Should Cover

- Automated build, test, and code-signing pipeline (Fastlane + GitHub Actions/GitLab CI/Bitrise)
- Code signing strategy — manual vs `match`/fastlane-managed certificates and profiles
- Distribution automation — TestFlight, Firebase App Distribution, internal beta tracks
- Build matrix — multiple schemes/configurations (dev/staging/prod), multiple targets
- Secrets management — API keys, signing certificates, not committed to source control
- Pipeline speed — caching (`DerivedData`, SPM/CocoaPods), parallelizing test targets, incremental builds

## Typical Pipeline

1. PR opened → lint (SwiftLint/SwiftFormat) + unit tests run on CI
2. Merge to main → build, run full test suite, upload dSYMs to crash reporting
3. Tag/release branch → Fastlane lane builds, signs, and uploads to TestFlight
4. Manual or automated promotion → App Store submission with release notes and phased rollout

## Example (Fastlane lane)

```ruby
lane :beta do
  setup_ci if ENV["CI"]   # creates a temporary keychain on CI so match can install certificates without a locked-keychain error
  app_store_connect_api_key(
    key_id: ENV["ASC_KEY_ID"],
    issuer_id: ENV["ASC_ISSUER_ID"],
    key_content: ENV["ASC_KEY_P8"]   # contents of the .p8 file, injected from CI secrets
  )
  # the build number must be higher than any uploaded build; read it from TestFlight so CI doesn't need to commit it back
  increment_build_number(
    xcodeproj: "App.xcodeproj",
    build_number: latest_testflight_build_number + 1
  )
  match(type: "appstore", readonly: true)
  build_app(scheme: "App-Production")
  upload_to_testflight(skip_waiting_for_build_processing: true)
  slack(message: "New beta build uploaded to TestFlight ✅")
end
```

## Practice Questions

- How do you keep signing credentials in sync across a team without emailing `.p12` files around?
- What is your strategy when a CI build passes locally but fails in the pipeline?
- How would you speed up a 40-minute CI pipeline without cutting test coverage?

## Senior Take

CI/CD ownership is often what separates senior from mid-level mobile engineers in practice — being able to debug a flaky pipeline, own the signing setup (`match` + a shared certificate repo), and design a build matrix that doesn't turn into 20 minutes of redundant builds per PR. The interview signal isn't "have you used Fastlane" — it's whether you can reason about failure modes: a provisioning profile expiring silently, a cache poisoning a build, a race between two lanes writing to the same keychain.

## Practice Question Answers

### How do you keep signing credentials in sync across a team without emailing `.p12` files around?

I use one shared, encrypted source with clear access control — most commonly fastlane `match`, or cloud-managed signing in Xcode and Xcode Cloud.

With `match`:

- Certificates and provisioning profiles are stored encrypted in a separate private Git repo (or S3, Google Cloud Storage), locked with the `MATCH_PASSWORD` passphrase.
- One person with admin rights creates the certificate once; other engineers and CI run `match(type: "development", readonly: true)` to download and install it into the keychain.
- CI always uses `readonly: true`, as in the `beta` lane above, so it never accidentally creates or revokes certificates.
- The passphrase and the App Store Connect API key (`.p8` file) live in CI secrets (GitHub Actions secrets), not in the repo.

Alternative: automatic signing with cloud-managed certificates — Xcode obtains the distribution certificate through the account or an App Store Connect API key when archiving and exporting, and Xcode Cloud manages signing entirely. This suits small teams with less to operate themselves.

On CI, prefer an App Store Connect API key over an Apple ID and password, because it isn't blocked by 2FA and each key can be revoked individually.

Trade-off: `match` centralizes everything, so if someone runs `match nuke` or the passphrase leaks, the whole team is affected. Limit write access to the certificate repo to 1–2 people, and rotate the passphrase when someone leaves the team.

### What is your strategy when a CI build passes locally but fails in the pipeline?

I treat it as an environment difference until proven otherwise, and look for that difference systematically instead of hitting re-run.

Steps:

1. **Read the log to see which step fails:** package resolution, compile, signing, or tests. Save the `.xcresult` bundle from CI as an artifact to inspect details.
2. **Compare environments:** Xcode version (the runner image may change its default Xcode), simulator runtime, Ruby and fastlane versions, whether `Package.resolved` is committed.
3. **Check for a clean state:** local machines often have stale DerivedData, uncommitted files, or schemes not marked as shared. Make a fresh clone, delete DerivedData, and run exactly the command CI runs.
4. **If it's tests:** CI is usually slower and runs in parallel and in a different order, which exposes race conditions, tests that depend on each other, timeouts that are too short, or dependence on the machine's timezone and locale.
5. **If it's signing:** an expired profile, a locked keychain on CI, a missing secret.

Once found, fix the root cause: pin the Xcode version, commit `Package.resolved`, make tests deterministic.

Trade-off: automatically retrying flaky tests keeps the pipeline green but hides problems. If you use retries, mark and track flaky tests so they get fixed; don't let retrying become a habit.

### How would you speed up a 40-minute CI pipeline without cutting test coverage?

I measure first and then optimize the most expensive part; the time usually goes to dependency resolution, rebuilding from scratch several times, and running tests serially.

Options:

- **Measure:** per-step timings in the pipeline, and `xcodebuild -showBuildTimingSummary` to see whether compile, link, or build scripts cost the most.
- **Build once, test many times:** `build-for-testing` once, then `test-without-building` across multiple jobs or simulators in parallel; enable parallel testing in the test plan.
- **Cache selectively:** cache SPM packages (`-clonedSourcePackagesDirPath`) and Ruby gems, keyed on `Package.resolved` and `Gemfile.lock`.
- **Run the right things at the right time:** PRs run unit tests and tests for affected modules; the full UI test suite runs on merge or nightly. Coverage doesn't drop; it just runs at a different time.
- **Remove waste:** don't rebuild the same thing in several jobs; run SwiftLint in a separate job or only on changed files.
- **Faster machines:** pick Apple Silicon runners with more CPU/RAM (for example GitHub Actions larger runners or a self-hosted Mac mini). The default macOS runners of the major services are already Apple Silicon today; if the team is still on old Intel runners, moving to Apple Silicon is usually noticeably faster, and newer Xcode/macOS releases are phasing out Intel support.

Trade-off: moving UI tests to nightly means failures are found a few hours later, so you need a clear rule about who fixes a red nightly. Caching also makes the pipeline more complex — when a build fails strangely, the first step is to rerun without cache.

## Interview Traps

### "CI reports a signing error. What do you do?"

**Common wrong answer:** "Run `match nuke` and recreate all certificates to start clean." That revokes the certificates and invalidates every profile using them, for the whole team and CI.

**Better answer:** Read the specific error first: an expired profile, a missing device in the development profile, a missing new entitlement (for example Push or App Groups just enabled), or a keychain on CI that wasn't unlocked. Most of the time it is enough for someone with rights to run `match` without readonly to refresh the profiles. Revoking a certificate is a last resort that needs a heads-up to the whole team, because internal builds (development, ad hoc) using it may be affected. Apps already released on the App Store are not affected, because Apple re-signs apps distributed through the App Store; what gets blocked is mainly signing and uploading new builds until a new certificate exists.

### "Where do you keep API keys safe?"

**Common wrong answer:** "In an `.xcconfig` or Info.plist, just don't commit it." Or believing that obfuscating a key inside the app keeps it secret.

**Better answer:** CI secrets (signing, App Store Connect API key) live in the CI secret store and are injected only at run time. But any key embedded in the app binary can be extracted, obfuscated or not. Truly sensitive keys must stay on the backend, with the app calling through your server; keys that must live on the client should be scoped down and rotatable.

### "Caching all of DerivedData between runs is always faster?"

**Common wrong answer:** "Yes, the more you cache the faster it gets." This is exactly the source of confusing broken builds.

**Better answer:** DerivedData is very large, and uploading and downloading the cache can take longer than it saves. If the cache key isn't tied to the Xcode version and lockfiles, a stale cache can cause failing or incorrect builds (cache poisoning). Caching SPM packages and gems is safer and more effective; if you cache build output, use a strict key and always keep a way to run without cache.

## Exercise

Design a CI/CD pipeline for a team with 3 build flavors (dev, staging, production), running on GitHub Actions with Fastlane. Specify: what triggers each lane, how signing certificates are shared across 5 engineers' machines and CI without committing them to the repo, and what happens automatically on a failed test run vs a failed code-signing step.
