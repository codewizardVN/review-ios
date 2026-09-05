[English](./ARC.md) | [Tiếng Việt](./ARC.vi.md)

[← Swift Core](./README.md)

# ARC and Memory Management

## 1. ARC

### Key Idea

ARC automatically tracks strong references and releases objects when their reference count reaches zero.

### What Matters In Practice

- Strong references keep objects alive
- Weak references do not keep objects alive
- Unowned references assume the object still exists
- ARC is not a garbage collector

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

- Closures capturing `self`
- Delegate relationships without `weak`
- Long-lived callbacks
- Timer / notification / observer patterns
- Async work that strongly retains objects longer than expected

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

## Exercise

Write a `DataLoader` class that fetches data and calls a completion closure. Introduce a retain cycle deliberately by having the closure capture `self` strongly and store the closure as a property. Verify the cycle exists using `deinit { print("deinit") }`. Then fix it using `[weak self]`. Explain in a comment why weak is the right choice here (not unowned).
