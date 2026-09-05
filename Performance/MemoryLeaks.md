[English](./MemoryLeaks.md) | [Tiếng Việt](./MemoryLeaks.vi.md)

[← Performance](./README.md)

# Memory Leaks and Retain Cycles

## Finding Leaks

1. **Instruments → Leaks** — detects objects that are allocated but never freed
2. **Memory Graph Debugger** — pause app in Xcode, click the memory graph button to visualize all live objects and their reference paths
3. **`deinit` logging** — add `print("deinit \(Self.self)")` during development to verify objects are released

## Common Sources in iOS Apps

- Closures in `NotificationCenter` not removed on `deinit`
- Delegate properties without `weak`
- `Timer` holding a strong reference to its target
- `Task { }` capturing `self` strongly across a long lifecycle

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

// Fixed
timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
    self?.update()
}
```

## Practice Questions

- If a view controller's deinit never fires after navigating away because of a Timer or NotificationCenter observer, how would you use the Memory Graph Debugger to find and fix the retain cycle?

## Senior Take

Leaks in production are often subtle — not in obvious closures, but in observer chains, analytics hooks, or background tasks that outlive the screen. Use the Memory Graph during QA, not just during development.

## Exercise

Add `deinit { print("deinit \(Self.self)") }` to a ViewController that uses a `Timer` and a `NotificationCenter` observer. Navigate away and confirm deinit fires. If it does not, use the Memory Graph Debugger to find the retain cycle and fix it.
