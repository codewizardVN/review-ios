[English](./UIKitInterop.md) | [Tiếng Việt](./UIKitInterop.vi.md)

[← SwiftUI](./README.md)

# UIKit Interoperability

## Two Directions

### SwiftUI → UIKit: `UIViewRepresentable` / `UIViewControllerRepresentable`

Wrap a UIKit component for use inside a SwiftUI view hierarchy.

```swift
struct MapView: UIViewRepresentable {
    func makeUIView(context: Context) -> MKMapView {
        MKMapView()
    }

    func updateUIView(_ view: MKMapView, context: Context) {
        // sync SwiftUI state → UIKit view
    }
}
```

### UIKit → SwiftUI: `UIHostingController`

Embed a SwiftUI view inside a UIKit view controller hierarchy.

```swift
let hostingVC = UIHostingController(rootView: FeedView())
addChild(hostingVC)
view.addSubview(hostingVC.view)
```

## When to Use

- UIKit: when you need functionality not yet available in SwiftUI (complex gestures, custom drawing, camera, maps with advanced features)
- Hosting Controller: when incrementally migrating an existing UIKit app to SwiftUI

## Practice Questions

- Why is a Coordinator needed when wrapping UIColorPickerViewController with UIViewControllerRepresentable to pass the selected UIColor back via a @Binding<Color>, and what is its lifecycle relative to the Representable?

## Senior Take

Interop adds complexity. Prefer native SwiftUI where possible. When wrapping UIKit, keep the `Representable` thin — move logic into a view model or coordinator, not into `makeUIView`.

## Exercise

Wrap `UIColorPickerViewController` using `UIViewControllerRepresentable`. Use a `Coordinator` conforming to `UIColorPickerViewControllerDelegate` to pass the selected `UIColor` back to SwiftUI via a `@Binding<Color>`. Dismiss the picker after selection. Explain in a comment why a `Coordinator` is needed here and what its lifecycle is relative to the `Representable`.
