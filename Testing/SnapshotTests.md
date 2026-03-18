[English](./SnapshotTests.md) | [Tiếng Việt](./SnapshotTests.vi.md)

[← Testing](./README.md)

# Snapshot Tests

## Key Idea

Snapshot tests render a view and compare it against a stored reference image. They catch unintended visual regressions automatically.

## What To Review

- swift-snapshot-testing (Point-Free) — most common library
- Recording vs asserting mode
- Testing on simulator vs device — images differ by device/OS
- What to snapshot: components, not full screens

## Example

```swift
import SnapshotTesting

final class ItemRowSnapshotTests: XCTestCase {
    func test_itemRow_default() {
        let view = ItemRow(item: .fixture())
        assertSnapshot(of: view, as: .image(layout: .fixed(width: 375, height: 80)))
    }
}
```

## Practice Questions

- When do snapshot tests provide real value?

## Senior Take

Snapshot tests are high value for design systems and reusable components. They are lower value for full screens that change frequently. Run them in CI on a fixed simulator configuration to avoid false positives from rendering differences between machines.

## Exercise

Add a snapshot test for a `PriceTagView` that displays a price string with a currency symbol. Test three variants: regular price, discounted price, and free. Then describe what CI setup is required to keep these tests from producing false positives across different machines.
