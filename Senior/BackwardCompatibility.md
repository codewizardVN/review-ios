[English](./BackwardCompatibility.md) | [Tiếng Việt](./BackwardCompatibility.vi.md)

[← Senior Topics](./README.md)

# Backward Compatibility

## Key Idea

Backward compatibility means new code should not break older clients, persisted data, or supported OS versions without an intentional migration plan.

## What To Review

- API contract changes and fallback behavior
- Database or cache migrations
- Feature flags for staged rollout
- OS availability checks and graceful degradation

## Example

If the server adds a new field to a response, old apps are usually fine, because `Codable` ignores extra keys. The real risks are other changes: the server starts **requiring** a new field in the request (old apps don't send it, so the request is rejected), renames or removes a field that old apps decode as required, lets a field come back as `null`, or adds a new enum value. In those cases older app versions may fail, unless decoding is tolerant or the backend supports a transition period (accepting both old and new requests).

## Practice Questions

- How do you ship a new feature while supporting older app versions?
- When do you need a migration instead of a silent fallback?

## Senior Take

Compatibility work is product work. A strong senior answer considers real users on older builds, staged releases, and recovery paths when assumptions fail in production.

## Practice Question Answers

### How do you ship a new feature while supporting older app versions?

I assume old versions will stay around for months, so API changes must be additive, and on the app side the feature is enabled through a flag and guarded by OS availability checks.

Concretely:

- **API:** only add new fields as optional; never change the meaning of or remove existing fields. If a breaking change is unavoidable, create a new endpoint or API version and keep the old one until most users have updated. The backend can read an app-version header to return the right response.
- **Decoding in the app:** new fields are optional or have defaults; enums have an `unknown` case so that when the server adds a new value, old versions don't fail to decode.
- **Feature flags / remote config:** new code ships turned off, is enabled gradually by percentage or by version, and always has a kill switch.
- **OS:** use `if #available` with a fallback UI for APIs that only exist on newer iOS versions.
- **Minimum supported version** (force update) is reserved for cases where you truly must drop old versions, such as a security issue.

Trade-off: staying compatible means the backend must maintain several logic branches, and feature flags must be cleaned up after rollout, otherwise the code fills up with dead branches. I usually set a clear condition: once an old version falls below a threshold (for example 2–5% of active users), the old path is removed.

### When do you need a migration instead of a silent fallback?

You need a migration when the old data matters to the user or when misreading it causes harm; a silent fallback only fits data that can be recreated and whose loss nobody would notice.

Examples:

- **Fallback is fine:** feed cache, thumbnails, responses that can be refetched. If decoding fails, clear the cache and reload from the server; the user just sees a slightly slower load.
- **Migration needed:** unsent drafts, offline data not yet synced, user settings, locally stored purchase data. A silent fallback here means data loss.
- **Fallback is dangerous:** when the meaning of the data changes, for example switching an amount from `Double` to an integer number of cents. The app can still read it but interprets it wrongly.

A migration should have a schema version, be idempotent, work when users jump several versions (2.1 straight to 2.5), and be tested with real data from old versions. With Core Data, use lightweight migration when it is enough and staged migration (iOS 17+) when it is more complex; with SwiftData, use a `SchemaMigrationPlan`.

Even when you choose a fallback, don't make it completely "silent": log a non-fatal event so you know the fallback rate in production. Trade-off: migrations take effort and can slow down the first launch after an update; with large data sets, consider running them in the background with a waiting state.

## Interview Traps

### "The server adds a new value to an enum field. Is that breaking?"

**Common wrong answer:** "Adding is never breaking, only removing is." That is true for new fields but wrong for new enum values.

**Better answer:** With `Codable`, extra keys in JSON are ignored, so adding a field is usually safe. But if the app decodes a strict `enum`, an unknown value fails the whole object, and often the entire array containing it — an old version can lose a whole screen. Similarly, changing a field from always-present to possibly `null` breaks old versions. The defenses are an `unknown` case, tolerant per-element decoding, and agreeing with the backend on what counts as a breaking change.

### "Wrapping code in `if #available` is all it takes to support older iOS, right?"

**Common wrong answer:** "Yes, the compiler already warns about everything." `#available` only ensures you don't call an API that doesn't exist; it doesn't ensure correct behavior.

**Better answer:** You still have to test on the lowest supported OS (install the matching simulator runtime or use a real device), because the same API can behave differently across iOS versions. Also, when you raise the deployment target, users on older OS versions don't lose the app: the installed app keeps working, it just stops receiving updates; and if they have downloaded the app before, the App Store still lets them re-download the last version compatible with their OS. That means that old version keeps calling your API for a long time, and the backend must keep supporting it.

### "How do you test a migration?"

**Common wrong answer:** "Install the new build on a dev device and check the app runs." That is a fresh install, not a migration.

**Better answer:** Test the upgrade path: install the old version (from TestFlight or an old build tag), create real data, then install the new version over it and verify the data. Also test jumping several versions, a fresh install, and a migration interrupted halfway (the app gets killed). If possible, write migration unit tests with sample store files from old versions so CI runs them every time.

## Exercise

Your team wants to replace a local cache schema and ship a new onboarding step in the same release. Describe the compatibility risks and how you would sequence the rollout safely.
