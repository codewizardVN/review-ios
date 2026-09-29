[English](./ViewControllerLifecycle.md) | [Tiếng Việt](./ViewControllerLifecycle.vi.md)

[← UIKit and App Lifecycle](./README.md)

# View Controller Lifecycle

## Key Idea

Each lifecycle method has a different purpose. Bugs appear when networking, layout work, analytics, or binding logic is placed in the wrong phase.

## What To Review

- `viewDidLoad` for one-time setup: runs exactly once after the view is loaded into memory, before it is attached to a window. Good for creating subviews, constraints, the data source, and bindings.
- `viewWillAppear` for state that must refresh before display: runs every time the screen is about to appear (including coming back after the screen on top is popped), before the transition animation.
- `viewIsAppearing` (iOS 17, back-deployed to iOS 13): runs after `viewWillAppear`, when the view is in the hierarchy and has the correct trait collection and size, but still before the animation. A good place for UI updates that depend on size or traits.
- `viewDidAppear` for tracking or work that needs the view on screen: runs after the transition has finished and the view is actually on screen.
- `viewWillDisappear`/`viewDidDisappear` and cleanup timing: stop timers, pause video, cancel subscriptions tied to the screen being visible. Note that disappearing does not mean the view controller is deallocated (another screen may just have been pushed on top), so "permanent" cleanup still belongs in `deinit`.
- `viewWillLayoutSubviews`/`viewDidLayoutSubviews`: can run many times (rotation, size changes, layout changes), so the code there must be light and safe to run repeatedly.

## Practice Questions

- What is the difference between `viewWillAppear` and `viewDidAppear`?
- Which work should never happen in `viewDidLoad`?

## Senior Take

The lifecycle is really about ownership and timing. A strong answer explains why a piece of work belongs to a phase instead of memorizing callbacks.

## Practice Question Answers

### What is the difference between `viewWillAppear` and `viewDidAppear`?

`viewWillAppear` runs before the view shows up, before the transition starts. `viewDidAppear` runs after the transition has finished and the view is actually on screen. So each callback suits a different kind of work:

- `viewWillAppear`: update what the user must see the moment the screen slides in, such as the title, button states, and data that may have changed while the user was on another screen. If you update later, the user sees the old UI and then watches it jump to the new one.
- `viewDidAppear`: work that needs the view fully visible, such as sending a "screen viewed" analytics event, starting animations, calling `becomeFirstResponder` to bring up the keyboard, or presenting an alert or onboarding tooltip.

Two follow-up details come up often. First, `viewWillAppear` can run without a `viewDidAppear` after it, for example when the user swipes back halfway and lets go (a cancelled interactive pop). Second, in `viewWillAppear` the view may not yet have its final trait collection and size. iOS 17 added `viewIsAppearing(_:)` (back-deployed to iOS 13). It runs after the view is added to the hierarchy and has correct geometry, but still before the animation. It is a better place for UI updates that depend on size or traits.

Trade-off: avoid heavy synchronous work in either method, because both run on the main thread in the middle of the transition and will make the animation stutter.

### Which work should never happen in `viewDidLoad`?

Do not put anything in `viewDidLoad` that depends on the view's final size, needs to run again every time the screen appears, or needs the view to be on screen. `viewDidLoad` runs only once, right after the view is loaded into memory. At that moment the view is not attached to a window yet, and `view.bounds` is often still the storyboard size or a default value.

Specifically, avoid:

- Computing frames manually from `view.bounds`. The result is wrong on other devices, on rotation, or in iPad split view. Use constraints, or compute in `viewDidLayoutSubviews`.
- Presenting an alert or another view controller. UIKit logs a warning like "view is not in the window hierarchy" and nothing appears.
- Sending a "screen viewed" analytics event. A view can be loaded without ever being shown, and this runs only once even if the user returns to the screen many times.
- Heavy synchronous work such as decoding a large file or querying the database. It blocks the push transition and the app feels frozen.

One-time setup, like creating subviews, adding constraints, configuring the data source, binding the ViewModel, and starting an asynchronous data load, fits `viewDidLoad` well.

## Interview Traps

### "After a sheet is dismissed, does the underlying screen's viewWillAppear run?"

**Common wrong answer:** Yes. Every time a screen reappears `viewWillAppear` is called, so just reload data there.

**Better answer:** Since iOS 13 the default presentation style is `.pageSheet`. The screen underneath stays in the hierarchy, so it does not receive `viewWillDisappear`/`viewWillAppear` when the sheet opens and closes. Only presentation styles that remove the underlying view from the hierarchy, such as `.fullScreen` or `.currentContext`, trigger the appearance callbacks. `.overFullScreen` also keeps the underlying view, so it does not trigger them. To learn that a sheet closed, use a delegate or closure from the child screen, or `UIAdaptivePresentationControllerDelegate.presentationControllerDidDismiss(_:)` for the swipe-down case.

### "viewWillAppear is always followed by viewDidAppear, right?"

**Common wrong answer:** Right, the two always come as a pair, so you can start something in `viewWillAppear` and be sure it "completes" in `viewDidAppear`.

**Better answer:** When the user swipes back halfway and cancels, the screen underneath receives `viewWillAppear`, then `viewWillDisappear` and `viewDidDisappear`, with no `viewDidAppear` at all. If you turn something on in `viewWillAppear` and rely on `viewDidAppear` to turn it off or "complete" it (for example showing a loading overlay in `viewWillAppear` and hiding it in `viewDidAppear`), it gets stuck when the pop is cancelled. Pair start/stop symmetrically: `viewWillAppear` with `viewWillDisappear`, `viewDidAppear` with `viewDidDisappear`. The stop code should also be safe to call without a matching start (idempotent), because in the cancelled-pop case above `viewDidDisappear` is called even though `viewDidAppear` never was. Also, geometry-dependent updates belong in `viewIsAppearing`.

### "NotificationCenter observers are removed in deinit, so it's safe?"

**Common wrong answer:** Just call `removeObserver` in `deinit` and there is no leak.

**Better answer:** With the block-based API `addObserver(forName:object:queue:using:)`, NotificationCenter retains the closure, and if the closure captures `self` strongly the view controller is never released, so `deinit` never runs. You need `[weak self]` and must keep the token to remove it. Selector-based observers have been removed automatically on deallocation since iOS 9. The cleanest option today is `for await` over `NotificationCenter.default.notifications(named:)` inside a `Task`, and cancelling that Task when the screen goes away.

## Exercise

Review a controller that starts an API call in `viewDidAppear`, sets constraints in `viewWillAppear`, and subscribes to notifications in `viewDidLoad` without cleanup. Move each responsibility to a better place and explain why.
