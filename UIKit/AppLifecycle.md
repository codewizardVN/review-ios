[English](./AppLifecycle.md) | [Tiếng Việt](./AppLifecycle.vi.md)

[← UIKit and App Lifecycle](./README.md)

# App Lifecycle

## Key Idea

App lifecycle events tell you when the app launches, becomes active, goes to background, and returns to foreground. These transitions are where persistence, refresh, analytics, and security behavior often live.

## What To Review

- `UIApplicationDelegate` responsibilities
- Scene-based lifecycle with `UISceneDelegate`
- Foreground/background transitions
- What should and should not happen on launch

## Practice Questions

- What should happen when the app enters background?
- Where do you refresh critical state on returning to foreground?

## Senior Take

Lifecycle code should stay thin. The delegate layer coordinates app-level services, but feature logic should remain in dedicated objects so the app is testable and maintainable.

## Exercise

List the actions your app should take on cold launch, when moving to background, and when returning to foreground. Then identify which of those actions are app-level orchestration versus feature-level behavior.
