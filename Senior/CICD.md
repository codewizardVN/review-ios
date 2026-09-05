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
  increment_build_number(xcodeproj: "App.xcodeproj")
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

## Exercise

Design a CI/CD pipeline for a team with 3 build flavors (dev, staging, production), running on GitHub Actions with Fastlane. Specify: what triggers each lane, how signing certificates are shared across 5 engineers' machines and CI without committing them to the repo, and what happens automatically on a failed test run vs a failed code-signing step.
