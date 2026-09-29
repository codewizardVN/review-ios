[English](./MemoryLeaks.md) | [Tiếng Việt](./MemoryLeaks.vi.md)

[← Performance](./README.md)

# Memory Leaks and Retain Cycles

## Finding Leaks

1. **Instruments → Leaks** — detects memory that was allocated but is no longer referenced from any root (globals, stacks, registers), e.g. two objects holding each other in a retain cycle with nothing else pointing at them. Objects that are "legitimately" held (by the run loop, a singleton, a cache) are not reported — see Interview Traps
2. **Memory Graph Debugger** — pause app in Xcode, click the memory graph button to visualize all live objects and their reference paths
3. **`deinit` logging** — add `print("deinit \(Self.self)")` during development to verify objects are released

## Common Sources in iOS Apps

- Block-based observers (`addObserver(forName:object:queue:using:)`): the notification center retains the closure, and the closure captures `self` strongly — if you only plan to remove the observer in `deinit`, `deinit` never runs. (Selector-based observers are not retained strongly since iOS 9 and don't need manual removal.)
- Delegate properties without `weak`: A holds B, B holds A back through the delegate → a cycle
- `Timer`: the run loop retains the timer, and the timer retains its target (target/selector API) or its closure — if the closure captures `self` strongly, the view controller lives until the timer is `invalidate()`d
- `Task { }` capturing `self` and running for a very long time (an endless `for await` loop, polling): `self` is held until the task finishes

## Example

```swift
// Leak: Timer retains self strongly
class BadViewController: UIViewController {
    var timer: Timer?
    override func viewDidLoad() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            self.update() // strong capture
        }
    }
}

// Fixed: weak capture + invalidate when leaving the screen
override func viewDidAppear(_ animated: Bool) {
    super.viewDidAppear(animated)
    timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
        // Swift 6: the Timer closure is @Sendable; the timer is scheduled on the
        // main run loop, so assumeIsolated is used to call the @MainActor method
        MainActor.assumeIsolated { self?.update() }
    }
}

override func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    timer?.invalidate() // the run loop releases the timer, it stops firing
    timer = nil
}
```

## Practice Questions

- If a view controller's deinit never fires after navigating away because of a Timer or NotificationCenter observer, how would you use the Memory Graph Debugger to find and fix the retain cycle?

## Senior Take

Leaks in production are often subtle — not in obvious closures, but in observer chains, analytics hooks, or background tasks that outlive the screen. Use the Memory Graph during QA, not just during development.

## Practice Question Answers

### If a view controller's deinit never fires after navigating away because of a Timer or NotificationCenter observer, how would you use the Memory Graph Debugger to find and fix the retain cycle?

Open the Memory Graph Debugger right after leaving the screen, find the view controller instance that is still alive, then follow the strong references pointing at it to see who is holding it. Concrete steps:

- Before running, enable Scheme → Diagnostics → Malloc Stack Logging (Live Allocations Only) so Xcode records the backtrace where each object was allocated.
- Open and close the screen a few times, then press the Debug Memory Graph button in the debug bar.
- Type the class name into the filter in the left navigator. If you opened it 3 times and there are 3 instances, there is definitely a problem.
- Select an instance: the graph in the centre shows the objects pointing at it; bold lines are strong references. With a Timer you usually see the chain `NSRunLoop → __NSCFTimer → closure → ViewController`; with a block-based observer it is `NSNotificationCenter → observer → closure → ViewController`.
- The inspector on the right shows the backtrace where the closure was created, leading straight to the offending line.

The fix: capture `[weak self]` in the closure, and more importantly end the lifetime of the holder: call `timer?.invalidate()` when the screen goes away (e.g. `viewDidDisappear`), and call `NotificationCenter.default.removeObserver(token)` for block-based observers. Run again and confirm `deinit` prints.

Note: this case is usually not flagged as a "leak" (the purple "!" marker), because the view controller is still reachable from the run loop or notification center. So you must detect it yourself by counting instances rather than waiting for the tool to warn you.

## Interview Traps

### "Adding `[weak self]` to the Timer closure is enough, right?"

**Common wrong answer:** `[weak self]` breaks the retain cycle, so nothing else needs to be done with the Timer.

**Better answer:** `[weak self]` lets the view controller be released, but the run loop still retains the timer, so it keeps firing forever with `self` being `nil` — wasting CPU and battery. You must `invalidate()` the timer when the screen goes away. With the `Timer.scheduledTimer(timeInterval:target:selector:...)` API the timer retains its target strongly and `[weak self]` doesn't apply; calling `invalidate()` in `deinit` is useless because `deinit` never runs while the timer holds `self`.

### "The Leaks instrument reports nothing, so the app doesn't leak?"

**Common wrong answer:** A clean Leaks instrument means no memory is being wrongly retained.

**Better answer:** Leaks only finds memory that is no longer reachable from any root. Objects held by the run loop, a singleton, a cache or the notification center are still reachable, so they aren't reported — this is abandoned memory, the most common kind in real apps. Use Allocations with Mark Generation: mark, open/close the screen, mark again; memory that grows steadily across generations indicates objects being kept alive.

### "Using `[weak self]` in a `Task { }` and then `guard let self` at the top is safe?"

**Common wrong answer:** Since it's captured weakly, the task never holds `self`.

**Better answer:** `guard let self` at the top creates a strong reference that lives for the whole duration of the task. For a short task that's fine — `self` is released when the task finishes, which is also why a short `Task` often doesn't need `[weak self]` at all. But with a long loop such as `for await note in NotificationCenter.default.notifications(named:)`, `self` is held indefinitely. The right approach: store the handle and `cancel()` the task when the screen goes away (SwiftUI's `.task` cancels automatically), or only unwrap `self` inside each loop iteration.

## Exercise

Add `deinit { print("deinit \(Self.self)") }` to a ViewController that uses a `Timer` and a `NotificationCenter` observer. Navigate away and confirm deinit fires. If it does not, use the Memory Graph Debugger to find the retain cycle and fix it.
