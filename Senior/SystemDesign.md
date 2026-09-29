[English](./SystemDesign.md) | [Tiếng Việt](./SystemDesign.vi.md)

[← Senior Topics](./README.md)

# System Design for iOS Apps

## What To Focus On

- Feature boundaries and module ownership
- Data flow from API to storage to UI
- Offline and caching requirements
- Reliability, observability, and release risk

## A Good Senior Answer

Start from the product requirement, then explain:

- main components
- dependencies between them
- where state lives
- how failures are handled
- what you would defer for a smaller first version

## Example Scenario

Design a feed app with:

- authenticated API
- local cache for recent items
- pagination
- pull to refresh
- offline read support

One possible breakdown:

- `FeedAPIClient` for transport
- `FeedRepository` for mapping and cache coordination
- `FeedStore` for persistence
- `FeedViewModel` or reducer for screen state
- `FeedCoordinator` for navigation

## Practice Questions

- How do you split modules in a growing app?
- What would you simplify for a two-engineer team?

## Senior Take

System design answers are not about drawing the most boxes. They are about showing judgment: which complexity is justified now, which is deferred, and how the design stays operable as the product grows.

## Practice Question Answers

### How do you split modules in a growing app?

I split modules by feature and by dependency direction, but only once the boundaries are clear and there is a concrete reason, such as slow build times, many people editing the same area, or a real need to reuse code.

The split I usually use:

- **Core modules** (networking, persistence, design system, logging): they know nothing about features.
- **Feature modules** (Feed, Profile, Checkout): each owns its UI, view models, and repositories, and depends only on core.
- Features do not import each other directly. They talk through protocols or a small interface module, and the app target (or a coordinator) wires everything together.

For the feed example above: `FeedAPIClient` builds on core networking, while `FeedRepository`, `FeedStore`, `FeedViewModel`, and `FeedCoordinator` live in the Feed module. In current Xcode, the lightest way to do this is a local Swift Package with several targets, so the compiler blocks imports in the wrong direction instead of relying on convention.

Trade-off: every module adds cost — you have to design a public API, deal with access control and build configuration, and it is easy to create abstract protocols too early. Splitting too early while the domain is still changing means you keep moving code between modules. I usually start with clear folders plus dependency rules, and promote them to packages once the boundaries are stable.

### What would you simplify for a two-engineer team?

With two engineers, I cut everything whose operating cost is bigger than its benefit: fewer modules, fewer layers of abstraction, and more reliance on Apple's built-in tools and managed services.

Concretely:

- One app target with folders per feature; at most one Core package if it is really needed.
- Simple MVVM with `@Observable` instead of a multi-layer architecture like VIPER, unless the team already knows it well.
- Simple offline support: store the first few feed pages with SwiftData or a JSON file, instead of writing a two-way sync engine.
- Cursor-based pagination returned by the backend (the app just sends the cursor back to get the next page), instead of computing offsets/page numbers on the client; it is simple and avoids duplicated or skipped items when new items are inserted at the top of the feed.
- A single CI workflow: build, test, upload to TestFlight using Xcode Cloud or one Fastlane lane.
- Off-the-shelf crash reporting and analytics.

The rule is to keep an upgrade path: put boundaries where replacement is easy, for example `FeedRepository`, so the cache can be upgraded later without rewriting the UI. Things not to cut even on a small team: error handling, crash reporting, tests for critical logic, and feature flags or kill switches for risky parts.

Trade-off: simplifying creates debt once the team grows to 8–10 people. So write down in the design doc which parts will be split out when the team grows, so today's decision is deliberate rather than accidental.

## Interview Traps

### The interviewer gives the prompt and you start drawing architecture immediately

**Common wrong answer:** Jumping straight into Clean Architecture or VIPER boxes, listing layers and patterns before asking a single question about requirements. It shows you are applying a template instead of designing for the actual problem.

**Better answer:** Spend the first few minutes clarifying scope: who the users are, how much data, whether offline is needed, how auth works, and what is mandatory for version 1. Then state your assumptions and priorities, and only then move on to components. The interviewer is grading how you narrow the problem and reason about trade-offs, not how many boxes you draw.

### "How does offline work? What is the source of truth?"

**Common wrong answer:** "Just cache the responses and read the cache when there is no network." This ignores invalidation, conflicts on offline writes, and which user the cache belongs to.

**Better answer:** Pick one clear source of truth, usually the local store: the UI observes `FeedStore`, and `FeedRepository` fetches from the network and writes into the store. Explain when data expires, clear the cache on logout or account switch, and if there are offline writes (such as mark-as-read), use a queue with idempotency keys so retries are safe and conflicts are resolved by a clear rule.

### Designing as if the app were a backend service

**Common wrong answer:** Assuming you can deploy and roll back at any time and that every user always runs the latest version, so the API can change along with the app.

**Better answer:** A mobile app cannot be rolled back on the App Store, and users may stay on old versions for months. So the design needs backward-compatible APIs, feature flags or remote config to turn off a broken feature, a minimum-supported-version mechanism for the cases where it is unavoidable, and observability (crash reporting, logs, metrics) from day one. Mentioning these is a clear senior signal.

## Exercise

Sketch a notification inbox feature. Include sync strategy, read/unread updates, pagination, and push-notification entry points. Then explain which parts you would deliberately avoid building in version 1.
