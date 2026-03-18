[English](./DeepLinks.md) | [Tiếng Việt](./DeepLinks.vi.md)

[← UIKit and App Lifecycle](./README.md)

# Deep Links, Universal Links, and Notification Flows

## Key Idea

External entry points should map into app routes predictably, even when the app is cold-launched, backgrounded, or already inside another flow.

## What To Review

- URL parsing and route modeling
- Authentication gating
- Deferred navigation until app state is ready
- Push notifications as navigation intents

## Practice Questions

- What happens if a deep link arrives before login finishes?
- Where should route parsing live?

## Senior Take

Deep link handling is an app-level coordination problem. Strong answers talk about route modeling, readiness checks, fallback behavior, and analytics, not just opening a screen directly.

## Exercise

Design routing for `myapp://orders/123` and a universal link to the same order. Explain how the app behaves when launched cold, when already on another tab, and when the user is not authenticated.
