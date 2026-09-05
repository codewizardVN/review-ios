[English](./README.md) | [Tiếng Việt](./README.vi.md)

# iOS Senior Review Source

A review source for senior-level iOS engineers, focused on `Swift`, `SwiftUI`, architecture, performance, testing, and common topics in interviews and technical design reviews.

## Goals

This repository is intended to:

- Systematize core iOS knowledge for senior engineers.
- Provide a fast review path before interviews.
- Serve as a practical reference when building real apps with Swift and SwiftUI.
- Collect useful checklists for code review, architecture, and quality.

## Target Audience

This repo is a good fit if you:

- Already have iOS experience and want to consolidate your fundamentals.
- Are preparing for a `Senior iOS Developer` interview.
- Want to review from a practical angle, not just syntax.

## Review Scope

### 1. Swift Core

- Value types vs reference types
- ARC, memory management, retain cycles
- Protocol-oriented programming
- Generics, associated types, opaque types
- Error handling
- Access control
- Concurrency with `async/await`, `Task`, and `Actor`
- Combine (`Publisher`/`Subscriber`, `@Published`, vs `async/await`)
- Objective-C interop (`@objc`, bridging headers, legacy codebases)

### 2. SwiftUI

- `View` lifecycle
- State management: `@State`, `@Binding`, `@ObservedObject`, `@StateObject`, `@EnvironmentObject`
- Navigation
- Lists, lazy stacks, and rendering performance
- Dependency injection in SwiftUI
- Interoperability between `SwiftUI` and `UIKit`
- Widgets, `TimelineProvider`, and Live Activities (`ActivityKit`)

### 3. UIKit and App Lifecycle

- App lifecycle
- ViewController lifecycle
- Coordinator / Router
- Auto Layout
- CollectionView and Diffable Data Source
- Deep links, universal links, and notification flows
- Push notifications (APNs, silent push, notification service extension)
- Background execution (`BGTaskScheduler`, background `URLSession`)

### 4. Architecture

- MVC, MVVM, Clean Architecture
- Modularization
- Dependency injection
- Design patterns (Factory, Repository, Observer, Strategy, Adapter, Singleton trade-offs)
- Separation of concerns
- State-driven UI
- Trade-offs between simplicity and scalability

### 5. Data and Networking

- URLSession
- Codable
- Pagination
- Retry / timeout / cancellation
- Cache strategy
- Offline-first thinking
- API client design

### 6. Persistence

- Core Data (contexts, merge policies, migrations)
- SwiftData (`@Model`, `ModelContainer`, `@Query`)
- Choosing between Core Data and SwiftData

### 7. Security

- Keychain (secure storage, access control, biometric protection)
- App Transport Security
- Certificate / public key pinning
- Jailbreak detection limits

### 8. Performance

- Main-thread discipline
- Basic Instruments usage
- Memory graph debugging
- Rendering performance
- Startup time
- Large-list optimization
- App size optimization (app thinning, ODR, static vs dynamic frameworks)

### 9. Testing

- Unit tests
- UI tests
- Mocking / stubbing
- Testable architecture
- Snapshot tests
- Regression prevention

### 10. Senior-Level Topics

- Code review mindset
- Refactoring strategy
- Debugging production issues
- Backward compatibility
- Release process
- CI/CD for mobile (Fastlane, code signing, pipeline reliability)
- Mentoring and technical ownership
- Trade-off analysis in technical decisions
- App Store submission and review (privacy manifest, rejection causes)
- Crash reporting and analytics (symbolication, event schema, alerting)
- Feature flags and experimentation (flag lifecycle, A/B mechanics)

### 11. Accessibility and Localization

- VoiceOver, Dynamic Type, custom accessibility actions
- Localization with String Catalogs, pluralization, `FormatStyle`
- Right-to-left layout and text-expansion pitfalls

## Repository Structure

```text
.
|-- README.md
|-- README.vi.md
|-- CHANGELOG.md
|-- Docs/
|-- Swift/
|-- SwiftUI/
|-- UIKit/
|-- Architecture/
|-- Networking/
|-- Concurrency/
|-- Persistence/
|-- Security/
|-- Performance/
|-- Testing/
|-- Senior/
`-- Accessibility/
```

Suggested review flow:

1. Revisit `Swift core` first.
2. Move to `SwiftUI` and state management.
3. Review UIKit lifecycle and navigation fundamentals.
4. Review architecture and dependency management.
5. Practice networking, concurrency, and testing topics.
6. Finish with performance, system design, and code review scenarios.

## Quick Review Checklist

- Can you clearly explain `struct` vs `class`?
- Do you know when to use `@StateObject` instead of `@ObservedObject`?
- Do you understand where retain cycles happen in closures, delegates, or tasks?
- Can you describe a cache strategy for a production app?
- Do you know how to split modules to reduce coupling?
- Can you write tests for ViewModels, use cases, and the network layer?
- Do you know how to debug crashes, leaks, and frame drops?
- Can you defend architectural trade-offs in front of a team?
- Do you know where tokens should (and should not) live, and why?
- Can you own a CI/CD pipeline end-to-end, including a broken signing setup?

## Possible Next Steps

This repo can be extended with:

- Small code examples for each topic
- ~~Interview Q&A sets~~ → done: [Interview Q&A Set](./Docs/InterviewQA.md), grouped by study day
- Mini projects built with `SwiftUI`
- Sample production-ready architecture
- iOS team code review checklist templates

## Quality Direction

The material in this repo should prioritize:

- Simplicity with clarity
- Practical examples
- Reasoning and trade-offs
- Maintainability, testability, and performance

## Notes

This repo can evolve into:

- A `Senior iOS interview handbook`
- A `Swift/SwiftUI practice playground`
- A `real-world architecture reference`
