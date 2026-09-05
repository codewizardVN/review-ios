# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added

- Backfilled `## Practice Questions` / `## Câu hỏi luyện tập` into every topic file that was missing it (18 topics missing it in English, 53 `.vi.md` files missing it in Vietnamese) — all 70 English and 70 Vietnamese topic files now carry this section
- `Docs/InterviewQA.md` / `Docs/InterviewQA.vi.md` — bilingual interview Q&A set, grouped by study day, compiled from every topic file's Practice Questions/Exercise section
- `Accessibility/` — Accessibility (VoiceOver, Dynamic Type) and Localization/Internationalization topics
- `Swift/ObjCInterop.md` — `@objc`, bridging headers, what can and can't cross the Objective-C bridge
- `UIKit/BackgroundExecution.md` — `BGTaskScheduler`, background URLSession, best-effort scheduling
- `SwiftUI/WidgetsLiveActivities.md` — `TimelineProvider`, App Group data sharing, ActivityKit Live Activities
- `Senior/AppStoreSubmission.md` — privacy manifest, common rejection causes, phased rollout
- `Senior/CrashReportingAnalytics.md` — dSYM symbolication, event schema discipline, alerting thresholds
- `Senior/FeatureFlagsExperimentation.md` — flag categories, A/B mechanics, flag lifecycle and cleanup
- `Docs/StudyPlan/Day10_Platform_Quality_Growth.md` — bonus study day tying the topics above together
- Updated root `README.md`/`README.vi.md` scope (new section 11: Accessibility and Localization), repository structure tree, and `PROGRESS.md`/`PROGRESS.vi.md` with a new Day 10 checklist
- `Persistence/` — Core Data and SwiftData topics
- `Security/` — Keychain and Network Security (ATS, certificate/public key pinning) topics
- `Concurrency/Combine.md` — Combine framework vs `async/await`
- `Senior/CICD.md` — CI/CD for mobile (Fastlane, code signing, build matrix)
- `UIKit/PushNotifications.md` — APNs, silent push, notification service extension
- `Performance/AppSizeOptimization.md` — app thinning, On-Demand Resources, static vs dynamic frameworks
- `Architecture/DesignPatterns.md` — Factory, Repository, Observer, Strategy, Adapter, Singleton trade-offs
- Updated root `README.md`/`README.vi.md` scope, structure, and quick review checklist to reflect the new topics

---

## [0.1.0] - 2026-03-16

### Added

- Initial repository setup with `README.md` (English) and `README.vi.md` (Vietnamese)
- Folder structure for study plans:
  - `Docs/` — General documentation and cheat sheets
  - `Swift/` — Swift Core topics
  - `SwiftUI/` — SwiftUI and state management
  - `UIKit/` — UIKit and app lifecycle
  - `Architecture/` — Architecture patterns and design
  - `Networking/` — Data and networking layer
  - `Concurrency/` — Concurrency with async/await, GCD, Combine, Actors
  - `Performance/` — Performance profiling and optimization
  - `Testing/` — Unit, UI, and snapshot testing
  - `Senior/` — Senior-level topics: code review, refactoring, mentoring
- `CHANGELOG.md` for change tracking
