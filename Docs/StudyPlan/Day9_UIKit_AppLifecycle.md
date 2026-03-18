[English](./Day9_UIKit_AppLifecycle.md) | [Tiếng Việt](./Day9_UIKit_AppLifecycle.vi.md)

# Day 9: UIKit and App Lifecycle

## Goal

Review UIKit lifecycle and app-level navigation topics that still appear often in senior iOS interviews and production debugging.

## Topics

- App lifecycle
- ViewController lifecycle
- Coordinator / Router
- Auto Layout
- CollectionView and Diffable Data Source
- Deep links
- Universal links
- Notification flows

## What You Should Be Able To Explain

- What belongs in `AppDelegate` or `SceneDelegate`
- The difference between `viewDidLoad`, `viewWillAppear`, and `viewDidAppear`
- Why Coordinator helps with flow ownership
- How to reason about ambiguous or conflicting constraints
- How external routes should enter the app safely

## Practice Questions

- What should happen when the app returns from background?
- Why can a deep link be harder than a normal push flow?
- How do you decide when a screen should own navigation?

## Senior Notes

- UIKit questions are often really about ownership, lifecycle timing, and flow coordination.
- Strong answers connect callbacks to product behavior, not just API names.
