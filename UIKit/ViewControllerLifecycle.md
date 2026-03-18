[English](./ViewControllerLifecycle.md) | [Tiếng Việt](./ViewControllerLifecycle.vi.md)

[← UIKit and App Lifecycle](./README.md)

# View Controller Lifecycle

## Key Idea

Each lifecycle method has a different purpose. Bugs appear when networking, layout work, analytics, or binding logic is placed in the wrong phase.

## What To Review

- `viewDidLoad` for one-time setup
- `viewWillAppear` for state that must refresh before display
- `viewDidAppear` for tracking or work that needs the view on screen
- `viewDidDisappear` and cleanup timing

## Practice Questions

- What is the difference between `viewWillAppear` and `viewDidAppear`?
- Which work should never happen in `viewDidLoad`?

## Senior Take

The lifecycle is really about ownership and timing. A strong answer explains why a piece of work belongs to a phase instead of memorizing callbacks.

## Exercise

Review a controller that starts an API call in `viewDidAppear`, sets constraints in `viewWillAppear`, and subscribes to notifications in `viewDidLoad` without cleanup. Move each responsibility to a better place and explain why.
