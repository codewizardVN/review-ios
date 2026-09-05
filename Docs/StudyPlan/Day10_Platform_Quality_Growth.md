[English](./Day10_Platform_Quality_Growth.md) | [Tiếng Việt](./Day10_Platform_Quality_Growth.vi.md)

# Day 10: Platform Quality and Growth

## Goal

Cover the topics that get skipped in a first pass but come up once an app has real users: accessibility, localization, legacy interop, background behavior, system-surface widgets, and the App Store/analytics/experimentation machinery around shipping.

## Topics

- Accessibility (VoiceOver, Dynamic Type)
- Localization and internationalization
- Objective-C interop
- Background execution (`BGTaskScheduler`, background URLSession)
- Widgets and Live Activities
- App Store submission and review
- Crash reporting and analytics
- Feature flags and experimentation

## What You Should Be Able To Explain

- How you'd test a screen with VoiceOver and at the largest Dynamic Type size, and what usually breaks
- Why layout, plural rules, and text expansion are localization problems, not just translation
- Which Swift features don't survive the bridge to Objective-C, and why
- Why background execution must be treated as best-effort, never guaranteed
- Why a widget or Live Activity is a separate process, not a live view into your app
- What causes the most common App Store rejections, and how to prevent them before submission
- Why a missing dSYM or an inconsistent analytics event schema costs real debugging time
- Why a feature flag needs an owner and a removal date, not just an `if` statement

## Practice Questions

- Your app looks fine visually but fails a VoiceOver pass — what's the first thing you check?
- A build was rejected for a privacy manifest issue you didn't know existed — what does that say about your release checklist?
- A kill-switch flag failed "open" during an incident — what should have been true about its default?

## Senior Notes

- These topics rarely show up as their own interview question, but they show up inside system design and "tell me about a production issue" questions.
- The common thread across all of them: something the system, the OS, or the review process controls — not your app — decides the outcome, and a senior engineer designs for that uncertainty instead of assuming control they don't have.
