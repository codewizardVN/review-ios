[English](./ARC.md) | [Tiếng Việt](./ARC.vi.md)

[← Swift Core](./README.md)

# ARC and Memory Management

## 1. ARC

### Key Idea

ARC automatically tracks strong references and releases objects when their reference count reaches zero.

### What Matters In Practice

- **Strong references** (the default) keep objects alive: each strong reference adds to the reference count, and an object is freed only when no strong references remain.
- **Weak references** (`weak var`) do not keep objects alive: they do not add to the strong count, are always optional, and automatically become `nil` when the object is deallocated.
- **Unowned references** (`unowned`) also do not keep objects alive, but they are non-optional and assume the object is still alive whenever you access them. Accessing one after the object has been freed crashes the app (with `unowned(unsafe)` it is undefined behavior).
- ARC is not a garbage collector: the compiler inserts the retain/release calls at compile time, and an object is freed as soon as its count reaches zero (predictable, no GC "pauses"). The trade-off is that ARC does not detect or clean up retain cycles on its own — that is the developer's job.

### Example

```swift
final class Owner {
    var child: Child?
}

final class Child {
    weak var owner: Owner?
}
```

### Senior Take

What matters is not memorizing keywords. It is knowing object ownership and lifecycle, especially across delegates, closures, async tasks, and view/controller relationships.

---

## 2. Retain Cycles

### Common Places They Happen

- A closure captures `self` strongly and that closure is in turn kept by `self` (directly via a property, or indirectly via an object `self` owns)
- Delegate relationships without `weak`: A holds B, and B's `delegate` points back to A
- Long-lived callbacks (stored in a singleton, service, or cache) keep objects alive longer than needed
- Timer / notification / observer patterns: e.g. `Timer.scheduledTimer(target:selector:...)` strongly retains its `target`, and the run loop retains the timer until `invalidate()`; the block-based `NotificationCenter.addObserver(forName:object:queue:using:)` keeps the closure until you remove the observer token
- Async work (`Task`, network callbacks) that strongly retains objects longer than expected — usually that just extends the lifetime, and it becomes a real leak if the work never finishes

### Example

```swift
final class ProfileViewModel {
    var onUpdate: (() -> Void)?

    func bind() {
        onUpdate = { [weak self] in
            self?.reload()
        }
    }

    private func reload() {}
}
```

### Senior Take

Do not blindly write `[weak self]` everywhere. Explain why the capture exists, who owns whom, and whether `self` should actually stay alive for the operation.

## Practice Questions

- How would you demonstrate a retain cycle caused by a DataLoader's completion closure capturing self strongly, and why is [weak self] the right fix instead of unowned?

## Practice Question Answers

### How would you demonstrate a retain cycle caused by a DataLoader's completion closure capturing self strongly, and why is [weak self] the right fix instead of unowned?

I demonstrate it by creating a `DataLoader` in a short scope, calling `load()`, and observing that `deinit` never prints after the scope ends; after adding `[weak self]`, `deinit` prints right away.

The mechanism: `DataLoader` holds a strong reference to the closure through its `onComplete` property, and the closure captures `self` strongly, i.e. it holds a strong reference back to `DataLoader`. They keep each other alive, so the reference count never reaches zero even when nobody outside uses the loader. Besides `deinit`, you can keep a `weak var probe = loader` and check `probe != nil` after the scope, or open Xcode's Memory Graph Debugger to see the cycle.

```swift
weak var probe: DataLoader?
do {
    let loader = DataLoader()
    loader.load()
    probe = loader
}
print(probe == nil) // false with the cycle, true after the fix
```

`[weak self]` is right because the closure no longer adds to the strong count; when `DataLoader` is deallocated, `self` inside the closure simply becomes `nil`. `unowned` assumes `self` is definitely alive whenever the closure runs. In practice a completion closure is often passed along (into URLSession, into an async callback) and can run after the loader has been freed — accessing an `unowned` reference then crashes. Use `unowned` only when the lifetime is clearly guaranteed, for example a closure that is owned and called only by `self`.

## Interview Traps

### "Every closure that uses self needs [weak self], right?"

**Common wrong answer:** Yes, write `[weak self]` in every closure to be safe, including `map`, `UIView.animate` or `DispatchQueue.main.async`.

**Better answer:** A retain cycle only happens when the closure is stored (directly or indirectly) by the very object it captures. A non-escaping closure like `map` cannot create a cycle. `UIView.animate` or `DispatchQueue.main.async` hold `self` temporarily until the closure finishes and then release it — that extends the lifetime, it is not a leak. Sprinkling `[weak self]` everywhere adds optionals and can silently skip work that must happen (such as saving data).

### "Does a Task { } inside a ViewModel create a retain cycle?"

**Common wrong answer:** Never, because a Task finishes on its own; or adding `[weak self]` followed by `guard let self` at the top is enough.

**Better answer:** A `Task` closure captures `self` strongly (Swift allows implicit self there). For a short task that just keeps `self` alive until the task finishes. But if the task runs forever, such as a `for await` over a stream that never ends, the running task keeps `self` alive forever — whether or not you store the task in a property of `self` — and `deinit`, where you planned to call `task.cancel()`, never runs. `[weak self]` with `guard let self` right at the top does not help, because that strong reference lives for the whole loop; unwrap `self` inside each iteration or cancel the task from outside (e.g. `onDisappear`, or SwiftUI's `.task` modifier).

### "Does guard let self = self inside a [weak self] closure bring the retain cycle back?"

**Common wrong answer:** Yes, because it creates a strong reference to `self`, so the cycle returns.

**Better answer:** No. The closure still stores only a weak reference; `guard let self` creates a local strong reference that exists only for one execution of the closure and is released when the closure returns. It even helps: it guarantees `self` is not freed halfway through several lines of work. The only thing to remember is that if the closure body runs for a long time (a loop, a long await), `self` is kept alive for that whole time.

## Exercise

Write a `DataLoader` class that fetches data and calls a completion closure. Introduce a retain cycle deliberately by having the closure capture `self` strongly and store the closure as a property. Verify the cycle exists using `deinit { print("deinit") }`. Then fix it using `[weak self]`. Explain in a comment why weak is the right choice here (not unowned).
